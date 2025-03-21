#!/usr/bin/env python
# coding: utf-8

# SICOR is a freely available, platform-independent software designed to process hyperspectral remote sensing data,
# and particularly developed to handle data from the EnMAP sensor.

# This file contains LUT tools.

# Copyright (C) 2018  Niklas Bohn (GFZ, <nbohn@gfz-potsdam.de>),
# Maximilian Brell (GFZ, <maximilian.brell@gfz-potsdam.de>),
# Daniel Scheffler (GFZ, <daniel.scheffler@gfz-potsdam.de>)
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


from pkg_resources import resource_filename, Requirement, DistributionNotFound
import os
from os.path import isfile, join, dirname
import inspect
import sys
import numpy as np
import urllib.request


def get_data_file(module_name, file_basename):
    """
    Load data file.

    :param module_name:   name of python module where data file is located
    :param file_basename: name of data file
    :return:              path to data file
    """
    try:
        fn = resource_filename(Requirement.parse(module_name), os.path.join("data", file_basename))
        if isfile(fn) is False:
            raise FileNotFoundError(fn, os.listdir(os.path.dirname(fn)))

    except (FileNotFoundError, DistributionNotFound):
        # noinspection PyProtectedMember
        fn = join(dirname(inspect.getfile(sys._getframe(1))), "data", file_basename)
        if isfile(fn) is False:
            raise FileNotFoundError((module_name, file_basename, fn))

    if isfile(fn) is False:
        raise FileNotFoundError(fn, file_basename)
    else:
        return fn


def download_LUT(path_LUT_default):
    """
    Download LUT file from remote GIT repository.

    :param path_LUT_default: directory where to store the LUT file
    :return:                 directory of downloaded LUT file
    """
    fname = "https://git.gfz-potsdam.de/EnMAP/sicor/-/raw/main/sicor/AC/data/EnMAP_LUT_MOD5_formatted_1nm"
    urllib.request.urlretrieve(fname, path_LUT_default)
    if os.path.isfile(path_LUT_default):
        fn_table = path_LUT_default
    else:
        raise FileNotFoundError("Download of LUT file failed. Please download it manually from "
                                "https://git.gfz-potsdam.de/EnMAP/sicor and store it at /sicor/AC/data/ directory. "
                                "Otherwise, the AC will not work.")

    return fn_table


def read_lut_enmap_formatted(file_lut):
    """
    Read MODTRAN® LUT.

    :param file_lut: path to LUT
    :return:         LUT of atmospheric functions, x and y axes grid points, LUT wavelengths
    """
    def read_int16(data: np.ndarray, count: int):
        val = np.array(data[self._offset:self._offset + count * 2].view('int16'))
        self._offset += count * 2
        return val

    def read_float32(data: np.ndarray, count: int):
        val = np.array(data[self._offset:self._offset + count * 4].view('f4'))
        self._offset += count * 4
        return val

    with open(self.p_lut_bin, 'rb') as fd:
        data = np.frombuffer(fd.read(), dtype=np.uint8)  # Read all data as bytes

    wvl, vza, sza, alt, aot, raa, cwv = [read_float32(data, count=read_int16(data, count=1)[0]) for _ in range(7)]
    npar1, npar2 = [read_int16(data, count=1)[0] for _ in range(2)]

    # LUT1 containing path radiance
    # NOTE: The rhoatm values do not vary much with changing CVW contents,
    #       therefore the LUT was created with a single CWV value.
    lut1_axnames = ['VZA', 'SZA', 'ALT', 'AOT', 'RAA', 'CWV', 'WVL', 'NPAR1']
    lut1 = read_float32(data, count=10584000).reshape(
        (len(vza), len(sza), len(alt), len(aot), len(raa), 1, len(wvl), npar1))
    # LUT2 containing downwelling direct and diffuse surface solar irradiance, spherical albedo and transmittance
    # NOTE: The values in LUT2 do not vary much with changing RAAs,
    #       therefore the LUT was created with a single RAA value.
    lut2_axnames = lut1_axnames
    lut2 = read_float32(data, count=42336000).reshape(
        (len(vza), len(sza), len(alt), len(aot), 1, len(cwv), len(wvl), npar2))

    # Build xnodes for LUT dimensions
    ndim = 6

    def create_xnodes(dim_arr, values, ndim):
        xnodes = np.zeros((max(dim_arr), ndim))
        for i, val in enumerate(values):
            xnodes[:dim_arr[i], i] = val
        return xnodes

    dim_arr1 = [len(vza), len(sza), len(raa), len(alt), len(aot), 1]
    dim_arr2 = [len(vza), len(sza), 1, len(alt), len(aot), len(cwv)]
    xnodes1 = create_xnodes(dim_arr1, [vza, sza, raa, alt, aot, [1]], ndim)
    xnodes2 = create_xnodes(dim_arr2, [vza, sza, [1], alt, aot, cwv], ndim)

    # Combine xnodes
    dim_arr = [len(vza), len(sza), len(alt), len(aot), len(raa), len(cwv)]
    xnodes = np.zeros((max(dim_arr), ndim))
    xnodes[:, :4] = xnodes1[:, [0, 1, 3, 4]]
    xnodes[:, 4] = xnodes1[:, 2]
    xnodes[:, 5] = xnodes2[:, 5]

    # Create cell coordinates
    x_cell = np.array([[i, j, k, ii, jj, kk]
                       for i in [0, 1] for j in [0, 1] for k in [0, 1]
                       for ii in [0, 1] for jj in [0, 1] for kk in [0, 1]])

    # Adjust boundaries
    for arr, dim in zip([vza, sza, alt, aot, raa, cwv], dim_arr):
        arr[0] += 0.0001
        arr[dim - 1] -= 0.0001

    # Extract LUTs
    luts = l0_lut, edir_lut, edif_lut, sab_lut = [
        np.squeeze(lut1[..., 0], axis=5),  # l0 LUT
        np.squeeze(lut2[..., 0], axis=4),  # edir LUT
        np.squeeze(lut2[..., 1], axis=4),  # edif LUT
        np.squeeze(lut2[..., 2], axis=4)  # sab LUT
    ]

    # Define axes
    axes_x = [
        [vza, sza, alt, aot, raa],  # axes x l0
        [vza, sza, alt, aot, cwv]  # axes x e s
    ]
    axes_y = [
        [np.arange(i) for i in luts[0].shape[:-1]],  # axes y l0
        [np.arange(i) for i in luts[0].shape[:-1]]  # axes y e s
    ]

    return luts, axes_x, axes_y, wvl, lut1, lut2, xnodes, 2 ** ndim, ndim, x_cell


def interpol_lut(lut1, lut2, xnodes, nm_nodes, ndim, x_cell, vtest, intp_wvl):
    """
    Multidimensional LUT interpolation.

    :param lut1:     LUT containing path radiance
    :param lut2:     LUT containing downwelling direct and diffuse surface solar irradiance, spherical albedo and
                     transmittance
    :param xnodes:   gridpoints for each LUT dimension
    :param nm_nodes: overall number of LUT gridpoints (2**ndim)
    :param ndim:     dimension of LUT
    :param x_cell:   interpolation grid (nm_nodes x n_dim)
    :param vtest:    atmospheric state vector (interpolation point); contains VZA, SZA, HSF, AOT, RAA, CWV
    :param intp_wvl: wavelengths for which interpolation should be conducted
    :return:         path radiance, downwelling direct and diffuse surface solar irradiance, spherical albedo and
                     transmittance interpolated at vtest
    """
    lim = np.zeros((2, ndim), np.int8)

    for ii in range(ndim):
        if vtest[ii] >= xnodes[:, ii].max():
            vtest[ii] = 0.99 * xnodes[-1, ii]
        if vtest[ii] < xnodes[:, ii].min():
            vtest[ii] = 1.01 * xnodes[0, ii]

        wh = np.where(vtest[ii] < xnodes[:, ii])[0]
        lim[0, ii] = wh[0] - 1
        lim[1, ii] = wh[0]

    lut_cell = np.zeros((5, nm_nodes, len(intp_wvl)))

    cont = 0
    for i in range(2):
        iv = lim[i, 0]

        for j in range(2):
            jv = lim[j, 1]

            for k in range(2):
                kv = lim[k, 2]

                for ii in range(2):
                    iiv = lim[ii, 3]

                    for jj in range(2):
                        jjv = lim[jj, 4]

                        for kk in range(2):
                            kkv = lim[kk, 5]

                            lut_cell[0, cont, :] = \
                                lut1[iv, jv, kv, iiv, jjv, 0, :]

                            for ind in range(1, 5):
                                lut_cell[ind, cont, :] = \
                                    lut2[iv, jv, kv, iiv, 0, kkv, :, ind - 1]

                            cont += 1

    for i in range(ndim):
        vtest[i] = (vtest[i] - xnodes[lim[0, i], i]) / (xnodes[lim[1, i], i] - xnodes[lim[0, i], i])

    diffs = vtest - x_cell[::-1, :]
    weights = np.abs(np.array([np.prod(diffs[i]) for i in range(nm_nodes)])).reshape(1, nm_nodes, 1)
    f_int = np.sum(weights * lut_cell, axis=1)

    return f_int


def interpol_lut_red(lut1, lut2, xnodes, nm_nodes, ndim, x_cell, vtest, intp_wvl):
    """
    LUT interpolation based in a reduced grid.

    :param lut1:     LUT containing path radiance
    :param lut2:     LUT containing downwelling direct and diffuse surface solar irradiance, spherical albedo and
                     transmittance
    :param xnodes:   gridpoints for each LUT dimension
    :param nm_nodes: overall number of LUT gridpoints (2**ndim)
    :param ndim:     dimension of LUT
    :param x_cell:   interpolation grid (nm_nodes x n_dim)
    :param vtest:    atmospheric state vector (interpolation point); only surface elevation and CWV
    :param intp_wvl: wavelengths for which interpolation should be conducted
    :return:         path radiance, downwelling direct and diffuse surface solar irradiance, spherical albedo and
                     transmittance interpolated at vtest
    """
    # TODO: vectorization of this function would speed up large parts of SICOR
    #       (see https://git.gfz-potsdam.de/EnMAP/sicor/-/commit/1dbacaa8c65f207665578dc356a147a10d10019e and
    #       https://git.gfz-potsdam.de/EnMAP/sicor/-/commit/b5f0006d0281d8f8f1aceaebebebb2b842025e4f)
    lim = np.zeros((2, ndim), np.int8)

    for ii in range(ndim):
        if vtest[ii] >= xnodes[:, ii].max():
            vtest[ii] = 0.99 * xnodes[-1, ii]

        wh = np.where(vtest[ii] < xnodes[:, ii])[0]
        lim[0, ii] = wh[0] - 1
        lim[1, ii] = wh[0]

    lut_cell = np.zeros((5, nm_nodes, len(intp_wvl)))

    cont = 0
    for i in range(2):
        iv = lim[i, 0]

        for j in range(2):
            jv = lim[j, 1]

            lut_cell[0, cont, :] = \
                lut1[iv, jv, :]

            for ind in range(1, 5):
                lut_cell[ind, cont, :] = \
                    lut2[iv, jv, :, ind - 1]

            cont += 1

    for i in range(ndim):
        vtest[i] = (vtest[i] - xnodes[lim[0, i], i]) / (xnodes[lim[1, i], i] - xnodes[lim[0, i], i])

    diffs = vtest - x_cell[::-1, :]
    weights = np.abs(np.array([np.prod(diffs[i]) for i in range(nm_nodes)])).reshape(1, nm_nodes, 1)
    f_int = np.sum(weights * lut_cell, axis=1)

    return f_int


def reduce_lut(lut1, lut2, xnodes, nm_nodes, ndim, x_cell, gp, intp_wvl):
    """
    Reduce grid dimensionality of LUT based on fixed solar and view geometry as well as one single scene value of AOT.

    :param lut1:     LUT containing path radiance
    :param lut2:     LUT containing downwelling direct and diffuse surface solar irradiance, spherical albedo and
                     transmittance
    :param xnodes:   gridpoints for each LUT dimension
    :param nm_nodes: overall number of LUT gridpoints (2**ndim)
    :param ndim:     dimension of LUT
    :param x_cell:   interpolation grid (nm_nodes x n_dim)
    :param gp:       state vector of fixed scene parameters (VZA, SZA, AOT, RAA)
    :param intp_wvl: wavelengths for which interpolation should be conducted
    :return:         2D LUT including path radiance, downwelling direct and diffuse surface solar irradiance, spherical
                     albedo and transmittance interpolated at gp for varying surface elevation and CWV; reduced
                     gridpoints for each LUT dimension; reduced overall number of LUT gridpoints; reduced dimension of
                     LUT; reduced interpolation grid
    """
    red_lut = np.zeros((len(xnodes[:4, 2]), len(xnodes[:, 5]), len(intp_wvl), lut2.shape[-1] + 1))

    for ii, hsf in enumerate(xnodes[:4, 2]):
        for jj, cwv in enumerate(xnodes[:, 5]):
            vtest = np.array([gp[0], gp[1], hsf, gp[2], gp[3], cwv])

            pp = interpol_lut(lut1=lut1, lut2=lut2, xnodes=xnodes, nm_nodes=nm_nodes, ndim=ndim, x_cell=x_cell,
                              vtest=vtest, intp_wvl=intp_wvl)

            red_lut[ii, jj, :, 0] = pp[0, :]
            red_lut[ii, jj, :, 1] = pp[1, :]
            red_lut[ii, jj, :, 2] = pp[2, :]
            red_lut[ii, jj, :, 3] = pp[3, :]
            red_lut[ii, jj, :, 4] = pp[4, :]

    new_xnodes = np.zeros((xnodes.shape[0], 2))
    new_xnodes[:, 0] = xnodes[:, 2]
    new_xnodes[:, 1] = xnodes[:, 5]

    new_nm_nodes = new_xnodes.shape[1] ** 2
    new_ndim = new_xnodes.shape[1]
    new_x_cell = np.zeros((new_nm_nodes, new_ndim))

    for ii in range(new_nm_nodes):
        new_x_cell[ii, :] = x_cell[ii][-2:]

    return red_lut, new_xnodes, new_nm_nodes, new_ndim, new_x_cell
