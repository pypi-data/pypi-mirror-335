#!/usr/bin/env python
# coding: utf-8

# SICOR is a freely available, platform-independent software designed to process hyperspectral remote sensing data,
# and particularly developed to handle data from the EnMAP sensor.

# This file contains a wrapper for the 'lazy Gaussian inversion', a Bayesian snow and ice surface property retrieval
# based on a simultaneous optimal estimation of atmosphere and surface state.

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

from sicor.AC.RtFo_snow import FoSnow, FoFunc, __minimize__
from sicor.Tools.EnMAP.segmentation import empirical_line_solution_snow


def sicor_ac_snow(data_l1b, options, dem=None, unknowns=False, logger=None):
    """
    Wrapper function for a simultaneous optimal estimation of atmosphere and surface state
    focusing on snow and glacier ice properties.

    :param data_l1b: Level-1B data object in units of TOA radiance
    :param options:  dictionary with pre-defined specific instrument options
    :param dem:      digital elevation model to be optionally provided; default: None
    :param unknowns: if True, uncertainties due to unknown forward model parameters are added to S_epsilon;
                     default: False
    :param logger:   None or logging instance
    :return:         atmosphere and surface solution state including water vapor, aot, surface reflectance,
                     as well as estimated snow and glacier ice surface properties; optional output: several measures of
                     retrieval uncertainties
    """
    logger = logger or logging.getLogger(__name__)

    logger.info("Setting up forward operator...")
    fo_snow = FoSnow(data=data_l1b, options=options, dem=dem, logger=logger)
    fo_func_snow = FoFunc(fo=fo_snow)

    logger.info("Starting combined atmospheric and surface retrieval...")
    res = __minimize__(fo=fo_snow, opt_func=fo_func_snow,  unknowns=unknowns, logger=logger)

    # apply empirical line solution to extrapolate L2A data for each pixel
    if fo_snow.segmentation:
        logger.info("Applying empirical line solution to extrapolate L2A data pixelwise...")
        data_l2a_seg = res["surf_model"]
        reflectance = empirical_line_solution_snow(X=fo_snow.X, rdn_subset=fo_snow.rdn_subset,
                                                   data_l2a_seg=data_l2a_seg, rows=fo_snow.data.shape[0],
                                                   cols=fo_snow.data.shape[1], bands=fo_snow.data.shape[2],
                                                   segs=fo_snow.segs, labels=fo_snow.labels, processes=fo_snow.cpu)

        data_l2a_el = reflectance.reshape(fo_snow.data.shape)

        logger.info("Extrapolating atmospheric and surface parameters maps...")
        cwv_seg = np.zeros(fo_snow.data.shape[:2])
        aot_seg = np.zeros(fo_snow.data.shape[:2])
        grain_size_seg = np.zeros(fo_snow.data.shape[:2])
        sld_seg = np.zeros(fo_snow.data.shape[:2])
        liquid_water_seg = np.zeros(fo_snow.data.shape[:2])
        snow_algae_seg = np.zeros(fo_snow.data.shape[:2])
        glacier_algae_1_seg = np.zeros(fo_snow.data.shape[:2])
        glacier_algae_2_seg = np.zeros(fo_snow.data.shape[:2])
        black_carbon_seg = np.zeros(fo_snow.data.shape[:2])
        dust_seg = np.zeros(fo_snow.data.shape[:2])

        for i in range(fo_snow.segs):
            cwv_seg[fo_snow.labels == i] = res["cwv"][:, i]
            aot_seg[fo_snow.labels == i] = res["aot"][:, i]
            grain_size_seg[fo_snow.labels == i] = res["grain_size"][:, i]
            sld_seg[fo_snow.labels == i] = res["sld"][:, i]
            liquid_water_seg[fo_snow.labels == i] = res["liquid_water"][:, i]
            snow_algae_seg[fo_snow.labels == i] = res["snow_algae"][:, i]
            glacier_algae_1_seg[fo_snow.labels == i] = res["glacier_algae_1"][:, i]
            glacier_algae_2_seg[fo_snow.labels == i] = res["glacier_algae_2"][:, i]
            black_carbon_seg[fo_snow.labels == i] = res["black_carbon"][:, i]
            dust_seg[fo_snow.labels == i] = res["dust"][:, i]

        res_seg = {"cwv": cwv_seg, "aot": aot_seg, "grain_size": grain_size_seg, "sld": sld_seg,
                   "liquid_water": liquid_water_seg, "snow_algae": snow_algae_seg,
                   "glacier_algae_1": glacier_algae_1_seg, "glacier_algae_2": glacier_algae_2_seg,
                   "black_carbon": black_carbon_seg, "dust": dust_seg, "surf_model": data_l2a_el,
                   "toa_model": res["toa_model"], "sx": res["sx"], "scem": res["scem"], "srem": res["srem"],
                   "jacobian": res["jacobian"], "convergence": res["convergence"], "iterations": res["iterations"],
                   "gain": res["gain"], "averaging_kernel": res["averaging_kernel"],
                   "cost_function": res["cost_function"], "dof": res["dof"],
                   "information_content": res["information_content"], "retrieval_noise": res["retrieval_noise"],
                   "smoothing_error": res["smoothing_error"]}

    else:
        res_seg = res

    logger.info("%s atmospheric correction successfully finished!" % options["sensor"]["name"])

    return res_seg
