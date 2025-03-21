#!/usr/bin/env python
# coding: utf-8

# SICOR is a freely available, platform-independent software designed to process hyperspectral remote sensing data,
# and particularly developed to handle data from the EnMAP sensor.

# This file contains the Sensor Independent Atmospheric CORrection (SICOR) AC module - EnMAP specific parts.

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
from scipy.ndimage import gaussian_filter
import warnings

from sicor.AC.RtFo_3_phases import Fo, FoFunc, __minimize__


def make_ac_enmap(data, enmap_l1b, fo: Fo, cwv, pt, surf_res, logger=None):
    """
    Perform atmospheric correction for enmap_l1b product, based on given and retrieved parameters. Instead of returning
    an object, the function adds a 'data_l2a' attribute to each detector. This numpy array holds the retrieved surface
    reflectance map.

    :param data:      array containing measured TOA radiance of VNIR and SWIR
    :param enmap_l1b: EnMAP Level-1B object
    :param fo:        forward operator object
    :param cwv:       CWV retrieval maps for VNIR and SWIR
    :param pt:        forward model parameter vector for VNIR and SWIR
    :param surf_res:  dictionary of retrieved surface parameters ('intercept', 'slope', 'liquid water', 'ice')
    :param logger:    None or logging instance
    :return:          None
    """
    logger = logger or logging.getLogger(__name__)

    for detector_name in enmap_l1b.detector_attrNames:
        logger.info("Calculating surface reflectance for %s detector..." % detector_name)
        detector = getattr(enmap_l1b, detector_name)

        detector.data_l2a = fo.compute_boa_ref_for_image(
            data[detector_name],
            cwv[detector_name],
            pt[detector_name],
            detector_name
        )

        if detector_name == 'swir' and not fo.segmentation:
            detector.data_l2a = fo.apply_surface_model(detector.data_l2a, surf_res)


def sicor_ac_enmap(enmap_l1b, options, unknowns=False, logger=None):
    """
    Atmospheric correction for EnMAP Level-1B products, including a three-phases-of-water retrieval.

    :param enmap_l1b: EnMAP Level-1B object
    :param options:   dictionary with EnMAP specific options
    :param unknowns:  if True, uncertainties due to unknown forward model parameters are added to S_epsilon;
                      default: False
    :param logger:    None or logging instance
    :return:          surface reflectance for EnMAP VNIR and SWIR detectors as well as dictionary containing estimated
                      three phases of water maps and several-retrieval uncertainty measures
    """
    logger = logger or logging.getLogger(__name__)

    logger.info("Setting up forward operator...")
    fo_enmap = Fo(enmap_l1b=enmap_l1b, options=options, logger=logger)
    fo_func_enmap = FoFunc(fo=fo_enmap)

    logger.info("Performing 3 phases of water retrieval...")
    res = __minimize__(fo=fo_enmap, opt_func=fo_func_enmap, logger=logger, unknowns=unknowns)

    if fo_enmap.segmentation:
        logger.info("Smoothing segmented CWV retrieval map...")
        cwv_seg = np.zeros(fo_enmap.data_swir.shape[:2])

        if fo_enmap.land_only:
            for ii, lbl in enumerate(fo_enmap.lbl):
                cwv_seg[fo_enmap.labels == lbl] = res["cwv_model"][:, ii]
        else:
            for i in range(fo_enmap.segs):
                cwv_seg[fo_enmap.labels == i] = res["cwv_model"][:, i]

        # smoothing segmented CWV map
        cwv_smoothed = gaussian_filter(cwv_seg, sigma=fo_enmap.smoothing_sigma)

        logger.info("Transforming smoothed CWV retrieval map to VNIR sensor geometry to enable AC of VNIR data...")
        cwv_trans = enmap_l1b.transform_swir_to_vnir_raster(array_swirsensorgeo=cwv_smoothed,
                                                            resamp_alg=fo_enmap.resamp_alg,
                                                            respect_keystone=False,
                                                            src_nodata=0,  # just for clearance (same effect like None)
                                                            tgt_nodata=0  # just for clearance (same effect like None)
                                                            )

        data_ac = {"vnir": fo_enmap.data_vnir, "swir": fo_enmap.data_swir}
        cwv_ac = {"vnir": cwv_trans, "swir": cwv_smoothed}
        pt_ac = {"vnir": fo_enmap.pt_vnir, "swir": fo_enmap.pt}

        logger.info("Starting surface reflectance retrieval...")
        warnings.filterwarnings("ignore")
        make_ac_enmap(data=data_ac, enmap_l1b=enmap_l1b, fo=fo_enmap, cwv=cwv_ac, pt=pt_ac, surf_res=None,
                      logger=logger)

        enmap_l2a_vnir = enmap_l1b.vnir.data_l2a
        enmap_l2a_swir = enmap_l1b.swir.data_l2a

        logger.info("Smoothing segmented liquid water and ice maps...")
        liq_seg = np.zeros(fo_enmap.data_swir.shape[:2])
        ice_seg = np.zeros(fo_enmap.data_swir.shape[:2])

        if fo_enmap.land_only:
            for ii, lbl in enumerate(fo_enmap.lbl):
                liq_seg[fo_enmap.labels == lbl] = res["liq_model"][:, ii]
                ice_seg[fo_enmap.labels == lbl] = res["ice_model"][:, ii]
        else:
            for i in range(fo_enmap.segs):
                liq_seg[fo_enmap.labels == i] = res["liq_model"][:, i]
                ice_seg[fo_enmap.labels == i] = res["ice_model"][:, i]

        liq_smoothed = gaussian_filter(liq_seg, sigma=fo_enmap.smoothing_sigma)
        ice_smoothed = gaussian_filter(ice_seg, sigma=fo_enmap.smoothing_sigma)

        if fo_enmap.land_only:
            enmap_l2a_vnir[fo_enmap.water_mask_vnir != 1] = np.nan
            enmap_l2a_swir[fo_enmap.water_mask_swir != 1] = np.nan

            cwv_smoothed[fo_enmap.water_mask_swir != 1] = np.nan
            liq_smoothed[fo_enmap.water_mask_swir != 1] = np.nan
            ice_smoothed[fo_enmap.water_mask_swir != 1] = np.nan

        res["cwv_model"] = cwv_smoothed
        res["liq_model"] = liq_smoothed
        res["ice_model"] = ice_smoothed
    else:
        logger.info("Transforming CWV retrieval map to VNIR sensor geometry to enable AC of VNIR data...")
        cwv_trans = enmap_l1b.transform_swir_to_vnir_raster(array_swirsensorgeo=res["cwv_model"],
                                                            resamp_alg=fo_enmap.resamp_alg,
                                                            respect_keystone=False,
                                                            src_nodata=0,  # just for clearance (same effect like None)
                                                            tgt_nodata=0  # just for clearance (same effect like None)
                                                            )

        data_ac = {"vnir": fo_enmap.data_vnir, "swir": fo_enmap.data_swir}
        cwv_ac = {"vnir": cwv_trans, "swir": res["cwv_model"]}
        pt_ac = {"vnir": fo_enmap.pt_vnir, "swir": fo_enmap.pt}
        surf_ac = {"intercept": res["intercept_model"], "slope": res["slope_model"], "liquid": res["liq_model"],
                   "ice": res["ice_model"]}

        logger.info("Starting surface reflectance retrieval...")
        warnings.filterwarnings("ignore")
        make_ac_enmap(data=data_ac, enmap_l1b=enmap_l1b, fo=fo_enmap, cwv=cwv_ac, pt=pt_ac, surf_res=surf_ac,
                      logger=logger)

        enmap_l2a_vnir = enmap_l1b.vnir.data_l2a
        enmap_l2a_swir = enmap_l1b.swir.data_l2a

    # simple validation of L2A data
    if fo_enmap.land_only:
        val_vnir = enmap_l2a_vnir[fo_enmap.water_mask_vnir == 1]
        val_swir = enmap_l2a_swir[fo_enmap.water_mask_swir == 1]
        if np.isnan(val_vnir).any() or np.isnan(val_swir).any():
            logger.warning("The surface reflectance for land only generated by SICOR contains NaN values. Please check "
                           "for errors in the input data, the options file, or the processing code.")
    else:
        if np.isnan(enmap_l2a_vnir).any() or np.isnan(enmap_l2a_swir).any():
            logger.warning("The surface reflectance for land + water generated by SICOR contains NaN values. Please "
                           "check for errors in the input data, the options file, or the processing code.")

    for ii, dl2a in zip(range(2), [enmap_l2a_vnir, enmap_l2a_swir]):
        if dl2a[np.isfinite(dl2a)].shape[0] > 0:
            if ii == 0:
                d_name = "VNIR L2A"
            else:
                d_name = "SWIR L2A"
            if np.min(dl2a[np.isfinite(dl2a)]) < 0:
                logger.warning("%s data contain negative values indicating an overcorrection. Please check for "
                               "errors in the input data, the options file, or the processing code." % d_name)
            if np.max(dl2a[np.isfinite(dl2a)]) > 1:
                logger.warning("%s data contain values exceeding 1 indicating a saturation. Please check for errors "
                               "in the input data, the options file, or the processing code." % d_name)

    del enmap_l1b.vnir.data_l2a
    del enmap_l1b.swir.data_l2a

    if fo_enmap.land_only:
        mode = "combined"
    else:
        mode = "land"

    logger.info("SICOR atmospheric correction for %s in %s mode successfully finished!" % (options["sensor"]["name"],
                                                                                           mode))

    return enmap_l2a_vnir, enmap_l2a_swir, res
