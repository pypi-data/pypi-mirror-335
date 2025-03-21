#!/usr/bin/env python
# coding: utf-8

# SICOR is a freely available, platform-independent software designed to process hyperspectral remote sensing data,
# and particularly developed to handle data from the EnMAP sensor.

# This file contains some tools for building the prior covariance matrix and state vector needed for optimal estimation.

# Copyright (C) 2018  Niklas Bohn (GFZ, <nbohn@gfz-potsdam.de>),
# German Research Centre for Geosciences (GFZ, <https://www.gfz-potsdam.de>)

# This software was developed within the context of the EnMAP project supported by the DLR Space Administration with
# funds of the German Federal Ministry of Economic Affairs and Energy (on the basis of a decision by the German
# Bundestag: 50 EE 1529) and contributions from DLR, GFZ and OHB System AG.

# This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later
# version.

# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with this program.
# If not, see <https://www.gnu.org/licenses/>.


import numpy as np
from isofit.core.common import expand_path, json_load_ascii, svd_inv
from scipy.io import loadmat, savemat
from scipy.linalg import norm
from scipy.interpolate import interp1d
from os.path import split, abspath
from spectral.io import envi
from sklearn.cluster import KMeans


def covkern(x, x_tag, sigma, width):
    """
    Calculates a squared exponential covariance function.

    :param x:     row index of covariance matrix
    :param x_tag: column index of covariance matrix
    :param sigma: sigma, maximum noise level of the covariance matrix
    :param width: width of the kernel
    :return:      value of the covariance function
    """
    cov_func = sigma ** 2 * np.exp(-0.5 * (x - x_tag) ** 2 / width ** 2)

    return cov_func


def construct_cov_matrix(sig, width, n):
    """
    This function uses a Gaussian process to construct a covariance matrix. Specifically, it uses a squared exponential
    covariance function in the Gaussian process, allowing to control the maximum noise level, sigma, and the width of
    the kernel.

    :param sig:     sigma, maximum noise level of the covariance matrix
    :param width:   width of the kernel
    :param n:       dimension of the covariance matrix
    :return:        smoothed covariance matrix
    """
    if len(sig) < 2:
        sig = np.tile(sig, (1, n))

    covs = np.zeros((n, n))

    for i in range(n):
        for j in range(n):
            covs[i, j] = covkern(x=i, x_tag=j, sigma=sig[i], width=width)

    covout = covs

    return covout


class MultiComponentSurface(object):
    """
    A model of the surface based on a collection of multivariate Gaussians, with one or more equiprobable components
    and full covariance matrices.

    To evaluate the probability of a new spectrum, we calculate the Mahalanobis distance to each component cluster, and
    use that as our Multivariate Gaussian surface model.
    """
    def __init__(self, config):
        # Models are stored as dictionaries in .mat format
        config = json_load_ascii(config)
        model_dict = loadmat(config['output_model_file'])
        self.components = list(zip(model_dict['means'], model_dict['covs']))
        self.n_comp = len(self.components)
        self.wl = model_dict['wl'][0]
        self.n_wl = len(self.wl)

        # Set up normalization method
        self.normalize = model_dict['normalize']
        if self.normalize == 'Euclidean':
            self.e_norm = lambda r: norm(r)
        elif self.normalize == 'RMS':
            self.e_norm = lambda r: np.sqrt(np.mean(pow(r, 2)))
        elif self.normalize == 'None':
            self.e_norm = lambda r: 1.0
        else:
            raise ValueError('Unrecognized Normalization: %s\n' %
                             self.normalize)

        self.selection_metric = 'Mahalanobis'

        # This field, if present and set to true, forces us to use any initialization state and never change.
        # The state is preserved in the geometry object so that this object stays stateless.
        self.select_on_init = False

        # Reference values are used for normalizing the reflectances. In the VSWIR regime, reflectances are normalized
        # so that the model is agnostic to absolute magnitude.
        self.refwl = np.squeeze(model_dict['refwl'])
        self.idx_ref = [np.argmin(abs(self.wl-w))
                        for w in np.squeeze(self.refwl)]
        self.idx_ref = np.array(self.idx_ref)

        # Cache some important computations
        self.Covs, self.Cinvs, self.mus = [], [], []
        for i in range(self.n_comp):
            Cov = self.components[i][1]
            self.Covs.append(np.array([Cov[j, self.idx_ref]
                                      for j in self.idx_ref]))
            self.Cinvs.append(svd_inv(self.Covs[-1]))
            self.mus.append(self.components[i][0][self.idx_ref])

        # Variables retrieved: each channel maps to a reflectance model parameter
        rmin, rmax = 0, 10.0
        self.statevec = ['RFL_%04i' % int(w) for w in self.wl]
        self.bounds = [[rmin, rmax] for w in self.wl]
        self.scale = [1.0 for w in self.wl]
        self.init = [0.15 * (rmax-rmin)+rmin for v in self.wl]
        self.idx_lamb = np.arange(self.n_wl)
        self.n_state = len(self.statevec)

    def component(self, x):
        """
        We pick a surface model component using the Mahalanobis distance.

        This always uses the Lambertian (non-specular) version of the surface reflectance. If the forward model
        initialize via heuristic (i.e. algebraic inversion), the component is only calculated once based on that first
        solution. That state is preserved in the geometry object.
        """
        x_surface = x

        # Get the (possibly normalized) reflectance
        lamb = self.calc_lamb(x_surface)
        lamb_ref = lamb[self.idx_ref]
        lamb_ref = lamb_ref / self.e_norm(lamb_ref)

        # Mahalanobis or Euclidean distances
        mds = []
        for ci in range(self.n_comp):
            ref_mu = self.mus[ci]
            ref_Cinv = self.Cinvs[ci]
            if self.selection_metric == 'Mahalanobis':
                md = (lamb_ref - ref_mu).T.dot(ref_Cinv).dot(lamb_ref - ref_mu)
            else:
                md = sum(pow(lamb_ref - ref_mu, 2))
            mds.append(md)
        closest = np.argmin(mds)

        return closest

    def xa(self, x_surface):
        """
        Mean of prior distribution, calculated at state x. We find the covariance in a normalized space (normalizing by
        z) and then unnormalize the result for the calling function. This always uses the Lambertian (non-specular)
        version of the surface reflectance.
        """
        lamb = self.calc_lamb(x_surface)
        lamb_ref = lamb[self.idx_ref]
        ci = self.component(x_surface)
        lamb_mu = self.components[ci][0]
        lamb_mu = lamb_mu * self.e_norm(lamb_ref)
        mu = lamb_mu

        return mu

    def Sa(self, x_surface):
        """
        Covariance of prior distribution, calculated at state x. We find the covariance in a normalized space
        (normalizing by z) and then unnormalize the result for the calling function.
        """
        lamb = self.calc_lamb(x_surface)
        lamb_ref = lamb[self.idx_ref]
        ci = self.component(x_surface)
        Cov = self.components[ci][1]
        Cov = Cov * (self.e_norm(lamb_ref)**2)

        return Cov

    def calc_lamb(self, x_surface):
        """
        Lambertian reflectance.
        """
        return x_surface[self.idx_lamb]


def surface_model(config):
    configdir, configfile = split(abspath(config))
    config = json_load_ascii(config)

    # Determine top level parameters
    for q in ['output_model_file', 'sources', 'normalize', 'wavelength_file']:
        if q not in config:
            raise ValueError("Missing parameter: %s" % q)

    wavelength_file = expand_path(configdir, config['wavelength_file'])
    normalize = config['normalize']
    reference_windows = config['reference_windows']
    outfile = expand_path(configdir, config['output_model_file'])

    # load wavelengths file
    q = np.loadtxt(wavelength_file)
    if q.shape[1] > 2:
        q = q[:, 1:]
    if q[0, 0] < 100:
        q = q * 1000.0
    wl = q[:, 0]
    nchan = len(wl)

    # build global reference windows
    refwl = []
    for wi, window in enumerate(reference_windows):
        active_wl = np.logical_and(wl >= window[0], wl < window[1])
        refwl.extend(wl[active_wl])
    refwl = np.array(refwl, dtype=float)

    # create basic model template
    model = {'normalize': normalize, 'wl': wl, 'means': [], 'covs': [], 'refwl': refwl}

    for si, source_config in enumerate(config['sources']):

        # Determine source parameters
        for q in ['input_spectrum_files', 'windows', 'n_components', 'windows']:
            if q not in source_config:
                raise ValueError(
                    'Source %i is missing a parameter: %s' % (si, q))

        # Determine whether we should synthesize our own mixtures
        if 'mixtures' in source_config:
            mixtures = source_config['mixtures']
        elif 'mixtures' in config:
            mixtures = config['mixtures']
        else:
            mixtures = 0

        infiles = [expand_path(configdir, fi) for fi in
                   source_config['input_spectrum_files']]
        ncomp = int(source_config['n_components'])
        windows = source_config['windows']

        # load spectra
        spectra = []
        for infile in infiles:

            print('Loading  ' + infile)
            hdrfile = infile + '.hdr'
            rfl = envi.open(hdrfile, infile)
            nl, nb, ns = [int(rfl.metadata[n]) for n in ('lines', 'bands', 'samples')]
            swl = np.array([float(f) for f in rfl.metadata['wavelength']])

            # Maybe convert to nanometers
            if swl[0] < 100:
                swl = swl * 1000.0

            rfl_mm = rfl.open_memmap(interleave='source', writable=True)
            if rfl.metadata['interleave'] == 'bip':
                x = np.array(rfl_mm[:, :, :])
            if rfl.metadata['interleave'] == 'bil':
                x = np.array(rfl_mm[:, :, :]).transpose((0, 2, 1))
            x = x.reshape(nl * ns, nb)

            # import spectra and resample
            for x1 in x:
                p = interp1d(swl, x1[:len(swl)], kind='linear', bounds_error=False, fill_value='extrapolate')
                spectra.append(p(wl))

        # calculate mixtures, if needed
        n = float(len(spectra))
        nmix = int(n * mixtures)
        for mi in range(nmix):
            s1, m1 = spectra[int(np.rand() * n)], np.rand()
            s2, m2 = spectra[int(np.rand() * n)], 1.0 - m1
            spectra.append(m1 * s1 + m2 * s2)

        spectra = np.array(spectra)
        use = np.all(np.isfinite(spectra), axis=1)
        spectra = spectra[use, :]

        # accumulate total list of window indices
        window_idx = -np.ones((nchan), dtype=int)
        for wi, win in enumerate(windows):
            active_wl = np.logical_and(wl >= win['interval'][0], wl < win['interval'][1])
            window_idx[active_wl] = wi

        # add grain size parameter to resampled surface model
        x = x.reshape(nl, nb, 1)
        spectra = np.append(spectra, x[:, len(swl):, 0], axis=1)

        # Two step model.  First step is k-means initialization
        kmeans = KMeans(init='k-means++', n_clusters=ncomp, n_init=10)
        kmeans.fit(spectra)
        Z = kmeans.predict(spectra)

        for ci in range(ncomp):

            m = np.mean(spectra[Z == ci, :], axis=0)
            C = np.cov(spectra[Z == ci, :], rowvar=False)

            for i in range(nchan):
                window = windows[window_idx[i]]
                if window['correlation'] == 'EM':
                    C[i, i] = C[i, i] + float(window['regularizer'])
                elif window['correlation'] == 'decorrelated':
                    ci = C[i, i]
                    C[:, i] = 0
                    C[i, :] = 0
                    C[i, i] = ci + float(window['regularizer'])
                else:
                    raise ValueError('I do not recognize the source  ' + window['correlation'])

            # Normalize the component spectrum if desired
            if normalize == 'Euclidean':
                z = np.sqrt(np.sum(pow(m[:len(wl)], 2)))
            elif normalize == 'RMS':
                z = np.sqrt(np.mean(pow(m[:len(wl)], 2)))
            elif normalize == 'None':
                z = 1.0
            else:
                raise ValueError('Unrecognized normalization: %s\n' % normalize)
            m_norm = m / z
            C_norm = C / (z ** 2)

            model['means'].append(m_norm)
            model['covs'].append(C_norm)

    model['means'] = np.array(model['means'])
    model['covs'] = np.array(model['covs'])

    savemat(outfile, model)
    print("saving results to", outfile)
