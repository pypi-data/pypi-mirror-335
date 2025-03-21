#!/usr/bin/env python
# coding: utf-8

# SICOR is a freely available, platform-independent software designed to process hyperspectral remote sensing data,
# and particularly developed to handle data from the EnMAP sensor.

# This file contains the radiative transfer forward operator for the 'lazy Gaussian inversion' of atmosphere and snow
# surface properties.

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


import logging
import numpy as np
from multiprocessing.pool import ThreadPool as Pool
from itertools import product
from time import time
import scipy as sp
import warnings
from contextlib import closing
from tqdm import tqdm
import os
import pkgutil
import platform
from scipy.interpolate import interp1d

from py_tools_ds.processing.progress_mon import ProgressBar

from sicor.Tools.EnMAP.metadata import varsol
from sicor.Tools.EnMAP.LUT import read_lut_enmap_formatted, interpol_lut
from sicor.Tools.EnMAP.conversion import generate_filter
from sicor.Tools.EnMAP.optimal_estimation import invert_function
from sicor.Tools.EnMAP.multiprocessing import SharedNdarray, initializer, mp_progress_bar
from sicor.Tools.EnMAP.first_guess import wv_band_ratio_snow
from sicor.Tools.EnMAP.a_priori import surface_model, MultiComponentSurface
from sicor.Tools.EnMAP.segmentation import SLIC_segmentation


class FoSnow(object):
    """
    Forward operator for the 'lazy Gaussian inversion' of atmosphere and snow surface properties.
    """
    def __init__(self, data, options, dem=None, logger=None):
        """
        Instance of forward operator object.

        :param data:    ndarray containing data
        :param options: dictionary with EnMAP specific options
        :param logger:  None or logging instance
        :param dem:     digital elevation model to be provided in advance; default: None
        """
        self.logger = logger or logging.getLogger(__name__)
        self.cpu = options["retrieval"]["cpu"]
        self.disable_progressbars = options["retrieval"]["disable_progressbars"]
        self.instrument = options["sensor"]["name"]
        self.data = data

        # get observation metadata
        self.logger.info("Getting observation metadata...")
        self.jday = options["metadata"]["jday"]
        self.month = options["metadata"]["month"]
        self.dsol = varsol(jday=self.jday, month=self.month)
        self.dn2rad = self.dsol * self.dsol * 0.1
        self.fac = 1 / self.dn2rad

        self.sza = np.full(self.data.shape[:2], options["metadata"]["sza"])
        self.vza = np.full(self.data.shape[:2], options["metadata"]["vza"])
        if dem is None:
            self.hsf = np.full(self.data.shape[:2], options["metadata"]["hsf"])
        else:
            self.hsf = dem

        self.saa = np.full(self.data.shape[:2], options["metadata"]["saa"])
        self.raa = np.abs(self.vza - self.saa)
        for ii in tqdm(range(self.raa.shape[0])):
            for jj in range(self.raa.shape[1]):
                if self.raa[ii, jj] > 180:
                    self.raa[ii, jj] = 360 - self.raa[ii, jj]

        # check if observation metadata values are within LUT value ranges
        self.logger.info("Checking if observation metadata values are within LUT value ranges...")
        try:
            assert np.min(self.vza) >= 0 and np.max(self.vza) <= 40
        except AssertionError:
            raise AssertionError("vza not in LUT range, must be between 0 and 40. check input value!")

        try:
            assert np.min(self.sza) >= 0 and np.max(self.sza) <= 70
        except AssertionError:
            raise AssertionError("sza not in LUT range, must be between 0 and 70. check input value!")

        try:
            assert np.min(self.hsf) >= 0 and np.max(self.hsf) <= 8
        except AssertionError:
            raise AssertionError("surface elevation not in LUT range, must be between 0 and 8. check input value!")

        self.pt = np.zeros((self.data.shape[0], self.data.shape[1], 4))
        self.pt[:, :, 0] = self.vza
        self.pt[:, :, 1] = self.sza
        self.pt[:, :, 2] = self.hsf
        self.pt[:, :, 3] = self.raa

        self.par_opt = options["retrieval"]["state_params"]
        self.rho_idx = len(self.par_opt) - 3
        self.state_dim = len(self.par_opt) - 1 + self.data.shape[2]

        self.prior_mean, self.use_prior_mean, self.ll, self.ul, self.prior_sigma, self.unknowns = [], [], [], [], [], []
        for key in options["retrieval"]["atmosphere"]["state_vector"].keys():
            self.prior_mean.append(options["retrieval"]["atmosphere"]["state_vector"][key]["prior_mean"])
            self.use_prior_mean.append(options["retrieval"]["atmosphere"]["state_vector"][key]["use_prior_mean"])
            self.ll.append(options["retrieval"]["atmosphere"]["state_vector"][key]["ll"])
            self.ul.append(options["retrieval"]["atmosphere"]["state_vector"][key]["ul"])
            self.prior_sigma.append(options["retrieval"]["atmosphere"]["state_vector"][key]["prior_sigma"])

        # build the surface model in terms of numerical regularization, k-means clustering of multiple Gaussian
        # components and normalization of the library spectra
        self.logger.info("Building multiple Gaussian components of surface model...")
        self.surface_model_config = options["retrieval"]["surface"]["config"]
        surface_model(config=self.surface_model_config)
        self.mcs = MultiComponentSurface(config=self.surface_model_config)

        self.surface_fg, self.surface_ll, self.surface_ul = [], [], []
        for key in options["retrieval"]["surface"]["state_vector"].keys():
            if key in self.par_opt:
                self.surface_fg.append(options["retrieval"]["surface"]["state_vector"][key]["fg"])
                self.surface_ll.append(options["retrieval"]["surface"]["state_vector"][key]["ll"])
                self.surface_ul.append(options["retrieval"]["surface"]["state_vector"][key]["ul"])

        # Thompson et al. (2018) and Kou et al. (1993)
        for key in options["retrieval"]["unknowns"].keys():
            self.unknowns.append(options["retrieval"]["unknowns"][key]["sigma"])

        self.oe_gnform = options["retrieval"]["inversion"]["gnform"]
        self.oe_full = options["retrieval"]["inversion"]["full"]
        self.oe_maxiter = options["retrieval"]["inversion"]["maxiter"]
        self.oe_eps = options["retrieval"]["inversion"]["eps"]

        # wvl
        self.wvl = np.array(options["sensor"]["wvl_center"])
        self.fwhm = np.array(options["sensor"]["fwhm"])

        # snr
        if self.instrument == "AVIRIS":
            self.noise_file = options["sensor"]["snr"]
            coeffs = np.loadtxt(self.noise_file, delimiter=' ', comments='#')
            p_a, p_b, p_c = [interp1d(coeffs[:, 0], coeffs[:, col], fill_value='extrapolate') for col in (1, 2, 3)]
            self.snr = np.array([[p_a(w), p_b(w), p_c(w)] for w in self.wvl])
        else:
            self.snr = np.array(options["sensor"]["snr"])

        # load RT LUT
        self.logger.info("Loading RT LUT...")
        if os.path.isfile(options["retrieval"]["fn_LUT"]):
            self.fn_table = options["retrieval"]["fn_LUT"]
        else:
            self.path_sicorlib = os.path.dirname(pkgutil.get_loader("sicor").path)
            if os.path.isfile(os.path.join(self.path_sicorlib, "AC", "data", "EnMAP_LUT_MOD5_formatted_1nm")):
                self.fn_table = os.path.join(self.path_sicorlib, "AC", "data", "EnMAP_LUT_MOD5_formatted_1nm")
            else:
                raise FileNotFoundError("LUT file was not found. Make sure to indicate path in options file or to "
                                        "store the LUT at /sicor/AC/data/ directory, otherwise, the AC will not work.")

        luts, axes_x, axes_y, wvl, lut1, lut2, xnodes, nm_nodes, ndim, x_cell = read_lut_enmap_formatted(
            file_lut=self.fn_table)
        self.wvl_lut = wvl

        # resample LUT to instrument wavelengths
        self.logger.info("Resampling LUT to instrument wavelengths...")

        self.s_norm = generate_filter(wvl_m=self.wvl_lut, wvl=self.wvl, wl_resol=self.fwhm)

        self.xnodes = xnodes
        self.nm_nodes = nm_nodes
        self.ndim = ndim
        self.x_cell = x_cell

        lut2_all_res = np.zeros((5, 6, 4, 6, 1, 7, len(self.wvl), 4))

        lut1_res = lut1[:, :, :, :, :, :, :, 0] @ self.s_norm
        for ii in range(4):
            lut2_all_res[:, :, :, :, :, :, :, ii] = lut2[:, :, :, :, :, :, :, ii] @ self.s_norm

        self.lut1 = lut1_res
        self.lut2 = lut2_all_res

        # do optional image segmentation to enhance processing speed
        self.segmentation = options["retrieval"]["segmentation"]
        self.n_pca = options["retrieval"]["n_pca"]
        self.segs = options["retrieval"]["segs"]
        if self.segmentation:
            self.logger.info("Segmenting L1B spectra to enhance processing speed...")
            self.X, self.segs, self.labels = SLIC_segmentation(data_rad_all=self.data, n_pca=self.n_pca, segs=self.segs)

            # prepare segmented L1B data cube
            self.logger.info("Preparing segmented L1B data cube...")
            self.rdn_subset = np.zeros((1, self.segs, self.data.shape[2]))
            self.dem_subset = np.zeros((1, self.segs))
            self.pt_subset = np.zeros((1, self.segs, 4))
            for i in range(self.segs):
                radiance = self.X[self.labels.flat == i, :].mean(axis=0)
                hsf_mean = self.hsf.flatten()[self.labels.flat == i].mean(axis=0)
                pt_mean = self.pt.reshape(self.pt.shape[0] * self.pt.shape[1], 4)[self.labels.flat == i, :].mean(axis=0)
                self.rdn_subset[:, i, :] = radiance
                self.dem_subset[:, i] = hsf_mean
                self.pt_subset[:, i, :] = pt_mean

    def toa_rad(self, xx, pt, perturb=None):
        """
        Model TOA radiance for a given atmospheric state by interpolating in the LUT and applying the simplified
        solution of the RTE. Here, the atmospheric state contains water vapor and aot.

        :param xx:       state vector
        :param pt:       model parameter vector
        :param perturb:  perturbance factor for calculating perturbed TOA radiance; default None
        :return:         modeled TOA radiance
        """
        # LUT interpolation
        vtest = np.asarray([pt[0], pt[1], pt[2], xx[1], pt[3], xx[0]])
        f_int = interpol_lut(lut1=self.lut1, lut2=self.lut2, xnodes=self.xnodes, nm_nodes=self.nm_nodes,
                             ndim=self.ndim, x_cell=self.x_cell, vtest=vtest, intp_wvl=self.wvl)

        f_int_l0 = f_int[0, :] * 1.e+3
        f_int_edir = f_int[1, :] * 1.e+3
        f_int_edif = f_int[2, :] * 1.e+3
        f_int_ss = f_int[3, :]

        f_int_ee = f_int_edir * np.cos(np.deg2rad(pt[1])) + f_int_edif

        # surface reflectance
        rho = xx[2:-self.rho_idx]

        # modeling of TOA radiance
        if perturb:
            f_int_toa = (f_int_l0 + f_int_ee * rho / np.pi / (1 - f_int_ss * rho * perturb)) * self.fac
        else:
            f_int_toa = (f_int_l0 + f_int_ee * rho / np.pi / (1 - f_int_ss * rho)) * self.fac

        return f_int_toa

    def surf_ref(self, dt, xx, pt):
        """
        Model surface reflectance for a given atmospheric state by interpolating in the LUT and applying the
        simplified solution of the RTE.

        :param dt:   measurement vector
        :param xx:   state vector
        :param pt:   model parameter vector
        :return:     modeled surface reflectance
        """
        # LUT interpolation
        vtest = np.asarray([pt[0], pt[1], pt[2], xx[1], pt[3], xx[0]])

        f_int = interpol_lut(lut1=self.lut1, lut2=self.lut2, xnodes=self.xnodes, nm_nodes=self.nm_nodes,
                             ndim=self.ndim, x_cell=self.x_cell, vtest=vtest, intp_wvl=self.wvl)

        f_int_l0 = f_int[0, :] * 1.e+3 * self.fac
        f_int_edir = f_int[1, :] * 1.e+3 * self.fac
        f_int_edif = f_int[2, :] * 1.e+3 * self.fac
        f_int_ss = f_int[3, :]

        f_int_ee = f_int_edir * np.cos(np.deg2rad(pt[1])) + f_int_edif

        # modeling of surface reflectance
        xterm = np.pi * (dt - f_int_l0) / f_int_ee
        rho = xterm / (1. + f_int_ss * xterm)

        return rho

    def drdn_drtb(self, xx, pt, rdn):
        """
        Calculate Jacobian of radiance with respect to unknown radiative transfer model parameters.

        :param xx:  state vector
        :param pt:  model parameter vector
        :param rdn: forward modeled TOA radiance for the current state vector xx
        :return:    Jacobian of unknown radiative transfer model parameters
        """
        kb_rt = []
        eps = 1e-5
        perturb = (1.0 + eps)
        unknowns = ["skyview", "h2o_absco"]

        for unknown in unknowns:
            if unknown == "skyview":
                # perturb the sky view
                rdne = self.toa_rad(xx=xx, pt=pt, perturb=perturb)
                dx = (rdne - rdn) / eps
                kb_rt.append(dx)
            elif unknown == "h2o_absco":
                xx_perturb = xx.copy()
                xx_perturb[0] = xx[0] * perturb
                rdne = self.toa_rad(xx=xx_perturb, pt=pt)
                dx = (rdne - rdn) / eps
                kb_rt.append(dx)

        kb_rt = np.array(kb_rt).T

        return kb_rt

    def calc_kb(self, xx, pt, num_bd, sb):
        """
        Derivative of measurement with respect to unmodeled & unretrieved unknown variables, e.g. S_b. This is the
        concatenation of Jacobians with respect to parameters of the surface and the radiative transfer model.

        :param xx:     state vector
        :param pt:     model parameter vector
        :param num_bd: number of instrument bands
        :param sb:     unknown model parameter error covariance matrix
        :return:       Jacobian of unknown model parameters
        """
        kb = np.zeros((num_bd, sb.shape[0]), dtype=float)
        # calculate the radiance at the current state vector
        rdn = self.toa_rad(xx=xx, pt=pt,)
        drdn_drtb = self.drdn_drtb(xx=xx, pt=pt, rdn=rdn)
        kb[:, :] = drdn_drtb

        return kb

    def calc_se(self, xx, dt, pt, sb, num_bd, snr, unknowns):
        """
        Calculate the total uncertainty of the observation, including both the instrument noise and the uncertainty
        due to unmodeled variables. This is the S_epsilon matrix of Rodgers et al.

        :param xx:       state vector
        :param dt:       measurement vector
        :param pt:       model parameter vector
        :param sb:       unknown model parameter error covariance matrix
        :param num_bd:   number of instrument bands
        :param snr:      signal-to-noise ratio for each instrument band
        :param unknowns: if True, uncertainties due to unknown forward model parameters are added to S_epsilon;
                         default: False
        :return:         measurement error covariance matrix
        """
        if self.instrument == "AVIRIS":
            nedl = abs(snr[:, 0] * np.sqrt(snr[:, 1] + dt) + snr[:, 2])
            sy = np.identity(num_bd) * nedl**2
        elif self.instrument == "PRISMA":
            nedl = np.sqrt(dt / snr[:, 1]) * snr[:, 1] / snr[:, 0]
            sy = np.identity(num_bd) * nedl ** 2
        else:
            sy = np.identity(num_bd) * ((dt / snr)**2)

        if not unknowns:
            return sy
        else:
            kb = self.calc_kb(xx=xx, pt=pt, num_bd=num_bd, sb=sb)
            se = sy + kb.dot(sb).dot(kb.T)

            return se


class FoFunc(object):
    """
    Forward operator function function.
    """
    def __init__(self, fo):
        """
        Instance of forward operator function.

        :param fo: Forward operator
        """
        self.fo = fo

    @staticmethod
    def __norm__(aa, bb):
        """
        Calculate L2 norm between measured and modeled values.

        :param aa: measured values
        :param bb: modeled values
        :return:   L2 norm
        """
        return (aa - bb) ** 2

    @staticmethod
    def __d_bb_norm__(aa, bb):
        """
        Calculate derivative of L2 norm between measured and modeled values.

        :param aa: measured values
        :param bb: modeled values
        :return:   derivative of L2 norm
        """
        return -2 * (aa - bb)

    def __call__(self, xx, pt, dt, model_output=False):
        """
        Call forward operator function.

        :param xx:           state vector
        :param pt:           model parameter vector
        :param dt:           measurement vector
        :param model_output: if True, modeled TOA radiance is returned; else, L2 norm; default: False
        :return:             if model_output=False, L2 norm is returned; else, modeled TOA radiance
        """
        ff = self.fo.toa_rad(xx=xx, pt=pt)

        if model_output is True:
            return ff
        else:
            f = (np.sum(self.__norm__(aa=dt, bb=ff)))
            n = np.float(len(dt))

            return f / n


# noinspection PyUnresolvedReferences
def __minimize__(fo, opt_func, unknowns=False, logger=None):
    """
    Minimize value of cost function using optimal estimation.

    :param fo:       forward operator
    :param opt_func: forward operator function
    :param unknowns: if True, model unknown uncertainties are calculated and propagated into Se; default: False
    :param logger:   None or logging instance
    :return:         atmosphere and surface solution state, including optional measures of retrieval uncertainty
    """
    logger = logger or logging.getLogger(__name__)

    # set up multiprocessing
    warnings.filterwarnings("always")
    processes = fo.cpu
    if platform.system() == "Windows" and processes > 1:
        warnings.warn('Multiprocessing is currently not available on Windows.', Warning)
    if platform.system() == "Windows" or processes == 1:
        logger.info("Singleprocessing on 1 cpu")
    else:
        logger.info("Setting up multiprocessing...")
        logger.info("Multiprocessing on %s cpu's" % processes)

    globs = dict()
    globs["__instrument__"] = fo.instrument

    if fo.segmentation:
        opt_pt = np.array(fo.pt_subset)
        opt_data = fo.rdn_subset
        globs["__data__"] = opt_data
    else:
        opt_pt = np.array(fo.pt)
        opt_data = fo.data
        globs["__data__"] = opt_data

    # perform first guess water vapor retrieval based on a common band ratio
    # EnMAP wavelengths [73, 76, 81]
    # PRISMA wavelengths [52, 55, 59]
    warnings.filterwarnings("ignore")
    if fo.use_prior_mean[0]:
        cwv_fg = np.full(opt_data.shape[:2], fo.prior_mean[0])
    else:
        logger.info("Performing first guess water vapor retrieval...")
        cwv_fg = wv_band_ratio_snow(data=opt_data, fn_table=fo.fn_table, vza=opt_pt[:, :, 0].mean(),
                                    sza=opt_pt[:, :, 1].mean(), dem=opt_pt[:, :, 2].mean(), aot=fo.prior_mean[1],
                                    raa=opt_pt[:, :, 3].mean(), intp_wvl=fo.wvl, intp_fwhm=fo.fwhm, jday=fo.jday,
                                    month=fo.month, idx=[52, 55, 59])
        cwv_fg[np.isnan(cwv_fg)] = fo.prior_mean[0]

    # perform first guess surface reflectance retrieval based on first guess water vapor and prior mean aot
    logger.info("Performing first guess surface reflectance retrieval...")
    surf_fg = np.zeros(opt_data.shape)
    for ii in tqdm(range(opt_data.shape[0])):
        for jj in range(opt_data.shape[1]):
            surf_fg[ii, jj, :] = fo.surf_ref(dt=opt_data[ii, jj, :],
                                             xx=[cwv_fg[ii, jj], fo.prior_mean[1]],
                                             pt=opt_pt[ii, jj, :])

    # avoid unrealistic values in deep water absorption features
    # 1370-1394 nm, 1813-1960 nm
    surf_fg[np.isnan(surf_fg)] = 0.01

    # determine appropriate prior mean and covariance by assigning the first guess to the closest cluster
    logger.info("Determining appropriate surface prior mean and covariance...")
    mu = np.zeros((opt_data.shape[0], opt_data.shape[1], opt_data.shape[2] + fo.rho_idx))
    Cov = np.zeros((opt_data.shape[0], opt_data.shape[1], opt_data.shape[2] + fo.rho_idx,
                    opt_data.shape[2] + fo.rho_idx))
    for ii in tqdm(range(opt_data.shape[0])):
        for jj in range(opt_data.shape[1]):
            mu[ii, jj, :] = fo.mcs.xa(x_surface=surf_fg[ii, jj, :])
            Cov[ii, jj, :, :] = fo.mcs.Sa(x_surface=surf_fg[ii, jj, :])

    # increase or decrease prior covariance of surface reflectance (optional)
    Cov[:, :, :230, :230] = Cov[:, :, :230, :230] * 0.1

    # prepare arguments for optimal estimation
    logger.info("Preparing optimal estimation input...")
    globs["__par_opt__"] = fo.par_opt
    globs["__state_dim__"] = fo.state_dim
    globs["__rho_idx__"] = fo.rho_idx

    fg = np.zeros((opt_data.shape[0], opt_data.shape[1], fo.state_dim))
    xa = np.zeros((opt_data.shape[0], opt_data.shape[1], fo.state_dim))
    ll = np.zeros(fo.state_dim - fo.wvl.shape[0] - fo.rho_idx)
    ul = np.zeros(fo.state_dim - fo.wvl.shape[0] - fo.rho_idx)
    sa = np.zeros((opt_data.shape[0], opt_data.shape[1], fo.state_dim, fo.state_dim))

    for ii in range(opt_data.shape[0]):
        for jj in range(opt_data.shape[1]):
            fg[ii, jj, 0] = cwv_fg[ii, jj]
            fg[ii, jj, 1] = fo.prior_mean[1]
            fg[ii, jj, 2:-fo.rho_idx] = surf_fg[ii, jj, :]
            for kk in range(fo.rho_idx):
                fg[ii, jj, -fo.rho_idx+kk] = mu[ii, jj, -fo.rho_idx+kk]
            xa[ii, jj, 0] = fo.prior_mean[0]
            xa[ii, jj, 1] = fo.prior_mean[1]
            xa[ii, jj, 2:] = mu[ii, jj, :]

    for dd in range(fo.state_dim - fo.wvl.shape[0] - fo.rho_idx):
        ll[dd] = fo.ll[dd]
        ul[dd] = fo.ul[dd]
        sa[:, :, dd, dd] = fo.prior_sigma[dd] ** 2

    ll = np.concatenate((ll, np.full(fo.wvl.shape[0], 0.001), np.array([fo.surface_ll])[0]))
    ul = np.concatenate((ul, np.ones(fo.wvl.shape[0]), np.array([fo.surface_ul])[0]))

    sb = sp.diagflat(pow(np.array(fo.unknowns), 2))

    sa[:, :, 2:, 2:] = Cov

    globs["__fg__"] = fg
    globs["__xa__"] = xa
    globs["__ll__"] = ll
    globs["__ul__"] = ul
    globs["__sa__"] = sa
    globs["__sb__"] = sb

    globs["__pt__"] = np.array(opt_pt)
    globs["__wvl__"] = fo.wvl
    globs["__sza__"] = fo.sza
    globs["__dsol__"] = fo.dsol
    globs["__forward__"] = opt_func

    globs["__cwv__"] = SharedNdarray(dims=list(opt_data.shape[:2]))
    globs["__aot__"] = SharedNdarray(dims=list(opt_data.shape[:2]))
    globs["__grain_size__"] = SharedNdarray(dims=list(opt_data.shape[:2]))
    globs["__sld__"] = SharedNdarray(dims=list(opt_data.shape[:2]))
    globs["__liquid_water__"] = SharedNdarray(dims=list(opt_data.shape[:2]))
    globs["__snow_algae__"] = SharedNdarray(dims=list(opt_data.shape[:2]))
    globs["__glacier_algae_1__"] = SharedNdarray(dims=list(opt_data.shape[:2]))
    globs["__glacier_algae_2__"] = SharedNdarray(dims=list(opt_data.shape[:2]))
    globs["__black_carbon__"] = SharedNdarray(dims=list(opt_data.shape[:2]))
    globs["__dust__"] = SharedNdarray(dims=list(opt_data.shape[:2]))
    globs["__surf_model__"] = SharedNdarray(dims=list(opt_data.shape[:2]) + [fo.wvl.shape[0]])
    globs["__toa_model__"] = SharedNdarray(dims=list(opt_data.shape[:2]) + [fo.wvl.shape[0]])

    globs["__sx__"] = SharedNdarray(dims=list(opt_data.shape[:2]) + [fo.state_dim] + [fo.state_dim])
    globs["__scem__"] = SharedNdarray(dims=list(opt_data.shape[:2]) + [fo.state_dim] + [fo.state_dim])
    globs["__srem__"] = SharedNdarray(dims=list(opt_data.shape[:2]) + [fo.state_dim] + [fo.state_dim])

    if fo.oe_full:
        globs["__jacobian__"] = SharedNdarray(dims=list(opt_data.shape[:2]) + [fo.wvl.shape[0]] + [fo.state_dim])
        globs["__convergence__"] = SharedNdarray(dims=list(opt_data.shape[:2]))
        globs["__iterations__"] = SharedNdarray(dims=list(opt_data.shape[:2]))
        globs["__gain__"] = SharedNdarray(dims=list(opt_data.shape[:2]) + [fo.state_dim] + [fo.wvl.shape[0]])
        globs["__averaging_kernel__"] = SharedNdarray(dims=list(opt_data.shape[:2]) + [fo.state_dim] + [fo.state_dim])
        globs["__cost_function__"] = SharedNdarray(dims=list(opt_data.shape[:2]))
        globs["__dof__"] = SharedNdarray(dims=list(opt_data.shape[:2]))
        globs["__information_content__"] = SharedNdarray(dims=list(opt_data.shape[:2]))
        globs["__retrieval_noise__"] = SharedNdarray(dims=list(opt_data.shape[:2]) + [fo.state_dim] + [fo.state_dim])
        globs["__smoothing_error__"] = SharedNdarray(dims=list(opt_data.shape[:2]) + [fo.state_dim] + [fo.state_dim])

    globs["__snr__"] = fo.snr
    globs["__inv_func__"] = invert_function(fo.toa_rad)
    globs["__calc_se__"] = fo.calc_se
    globs["__unknowns__"] = unknowns
    globs["__gnform__"] = fo.oe_gnform
    globs["__full__"] = fo.oe_full
    globs["__maxiter__"] = fo.oe_maxiter
    globs["__eps__"] = fo.oe_eps

    rng = list(product(np.arange(0, opt_data.shape[0], 1), np.arange(0, opt_data.shape[1], 1)))
    mp_fun = __oe__

    # start optimization
    logger.info("Optimization...")
    t0 = time()
    # check if operating system is 'Windows'; in that case, multiprocessing is currently not working
    if platform.system() == "Windows" or processes == 1:
        initializer(globals(), globs)
        [mp_fun(ii) for ii in tqdm(rng)]
    else:
        with closing(Pool(processes=processes, initializer=initializer, initargs=(globals(), globs,))) as pl:
            results = pl.map_async(mp_fun, rng, chunksize=1)
            if not fo.disable_progressbars:
                bar = ProgressBar(prefix='\tprogress:')
            while True:
                if not fo.disable_progressbars:
                    mp_progress_bar(iter_list=rng, results=results, bar=bar)
                if results.ready():
                    results.get()
                    break
    t1 = time()

    cwv = globs["__cwv__"].np
    aot = globs["__aot__"].np
    grain_size = globs["__grain_size__"].np
    sld = globs["__sld__"].np
    liquid_water = globs["__liquid_water__"].np
    snow_algae = globs["__snow_algae__"].np
    glacier_algae_1 = globs["__glacier_algae_1__"].np
    glacier_algae_2 = globs["__glacier_algae_2__"].np
    black_carbon = globs["__black_carbon__"].np
    dust = globs["__dust__"].np
    surf_model = globs["__surf_model__"].np
    toa_model = globs["__toa_model__"].np

    sx = globs["__sx__"].np
    scem = globs["__scem__"].np
    srem = globs["__srem__"].np

    # optional optimal estimation output
    if fo.oe_full:
        jacobian = globs["__jacobian__"].np
        convergence = globs["__convergence__"].np
        iterations = globs["__iterations__"].np
        gain = globs["__gain__"].np
        averaging_kernel = globs["__averaging_kernel__"].np
        cost_function = globs["__cost_function__"].np
        dof = globs["__dof__"].np
        information_content = globs["__information_content__"].np
        retrieval_noise = globs["__retrieval_noise__"].np
        smoothing_error = globs["__smoothing_error__"].np
    else:
        jacobian = None
        convergence = None
        iterations = None
        gain = None
        averaging_kernel = None
        cost_function = None
        dof = None
        information_content = None
        retrieval_noise = None
        smoothing_error = None

    # simple validation of optimization output
    warnings.filterwarnings("always")

    cwv_check = np.sum(cwv - cwv_fg)
    aot_check = np.sum(aot - xa[:, :, 1])

    if cwv_check == 0 or aot_check == 0:
        warnings.warn("Optimization failed and returned first guess values. Please check for errors in the input data, "
                      "the options file, or the processing code.", Warning)

    logger.info("Done!")
    logger.info("Runtime: %.2f" % (t1 - t0) + " s")

    res = {"cwv": cwv, "aot": aot, "grain_size": grain_size,  "sld": sld, "liquid_water": liquid_water,
           "snow_algae": snow_algae, "glacier_algae_1": glacier_algae_1, "glacier_algae_2": glacier_algae_2,
           "black_carbon": black_carbon, "dust": dust, "surf_model": surf_model, "toa_model": toa_model, "sx": sx,
           "scem": scem, "srem": srem, "jacobian": jacobian, "convergence": convergence, "iterations": iterations,
           "gain": gain, "averaging_kernel": averaging_kernel, "cost_function": cost_function, "dof": dof,
           "information_content": information_content, "retrieval_noise": retrieval_noise,
           "smoothing_error": smoothing_error}

    return res


# noinspection PyUnresolvedReferences
def __oe__(ii):
    """
    Minimize value of cost function using optimal estimation.

    :param ii: index of data pixel
    """
    i1, i2 = ii

    se = __calc_se__(xx=__fg__[i1, i2, :], dt=__data__[i1, i2, :], pt=__pt__[i1, i2, :], sb=__sb__,
                     num_bd=len(__wvl__), snr=__snr__, unknowns=__unknowns__)

    res = __inv_func__(yy=__data__[i1, i2, :], fparam=__pt__[i1, i2, :], ll=__ll__, ul=__ul__,
                       xa=__xa__[i1, i2, :], fg=__fg__[i1, i2, :], sa=__sa__[i1, i2, :, :], se=se, gnform=__gnform__,
                       full=__full__, maxiter=__maxiter__, eps=__eps__)

    model = __forward__(xx=res[0], pt=__pt__[i1, i2, :], dt=__data__[i1, i2, :], model_output=True)

    __cwv__[i1, i2] = res[0][0]
    __aot__[i1, i2] = res[0][1]

    if "grain_size" in __par_opt__:
        __grain_size__[i1, i2] = res[0][-len(__par_opt__)+__par_opt__.index("grain_size")]
    if "sld" in __par_opt__:
        __sld__[i1, i2] = res[0][-len(__par_opt__)+__par_opt__.index("sld")]
    if "liquid_water" in __par_opt__:
        __liquid_water__[i1, i2] = res[0][-len(__par_opt__) + __par_opt__.index("liquid_water")]
    if "snow_algae" in __par_opt__:
        __snow_algae__[i1, i2] = res[0][-len(__par_opt__)+__par_opt__.index("snow_algae")]
    if "glacier_algae_1" in __par_opt__:
        __glacier_algae_1__[i1, i2] = res[0][-len(__par_opt__)+__par_opt__.index("glacier_algae_1")]
    if "glacier_algae_2" in __par_opt__:
        __glacier_algae_2__[i1, i2] = res[0][-len(__par_opt__)+__par_opt__.index("glacier_algae_2")]
    if "black_carbon" in __par_opt__:
        __black_carbon__[i1, i2] = res[0][-len(__par_opt__)+__par_opt__.index("black_carbon")]
    if "dust" in __par_opt__:
        __dust__[i1, i2] = res[0][-len(__par_opt__)+__par_opt__.index("dust")]

    __surf_model__[i1, i2] = res[0][2:-__rho_idx__]
    __toa_model__[i1, i2, :] = model

    # a posteriori covariance matrix
    __sx__[i1, i2, :, :] = res[4]

    # correlation error matrix
    cem = np.zeros((__state_dim__, __state_dim__))

    for mm in range(__state_dim__):
        for nn in range(__state_dim__):
            cem[mm, nn] = __sx__[i1, i2, :, :][mm, nn] / np.sqrt(__sx__[i1, i2, :, :][mm, mm] *
                                                                 __sx__[i1, i2, :, :][nn, nn])

    __scem__[i1, i2, :, :] = cem

    # relative error matrix
    x_ = res[0]
    rem = np.zeros((__state_dim__, __state_dim__))

    for mm in range(__state_dim__):
        for nn in range(__state_dim__):
            rem[mm, nn] = 100 * np.sqrt(__sx__[i1, i2, :, :][mm, nn] / (x_[mm] * x_[nn]))

    __srem__[i1, i2, :, :] = rem

    if __full__:
        __jacobian__[i1, i2, :, :] = res[1]
        __convergence__[i1, i2] = res[2]
        __iterations__[i1, i2] = res[3]
        __gain__[i1, i2, :, :] = res[5]
        __averaging_kernel__[i1, i2, :, :] = res[6]
        __cost_function__[i1, i2] = res[7]
        __dof__[i1, i2] = res[8]
        __information_content__[i1, i2] = res[9]
        __retrieval_noise__[i1, i2, :, :] = res[10]
        __smoothing_error__[i1, i2, :, :] = res[11]
