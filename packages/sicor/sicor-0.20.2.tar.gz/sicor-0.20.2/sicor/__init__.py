# -*- coding: utf-8 -*-
"""Sensor Independent  Atmospheric CORrection (SICOR)"""

import os
from .version import __version__
from .sicor_ac import ac, ac_gms
from .sicor_enmap import sicor_ac_enmap
from .options.options import get_options

if 'MPLBACKEND' not in os.environ:
    os.environ['MPLBACKEND'] = 'Agg'

__authors__ = """Niklas Bohn, André Hollstein, René Preusker"""
__email__ = 'nbohn@gfz-potsdam.de'
__all__ = ["__version__", "ac", "ac_gms", "sicor_ac_enmap", "get_options"]


# $PROJ_LIB was renamed to $PROJ_DATA in proj=9.1.1, which leads to issues with fiona>=1.8.20,<1.9
# https://github.com/conda-forge/pyproj-feedstock/issues/130
# -> fix it by setting PROJ_DATA
if 'GDAL_DATA' in os.environ and 'PROJ_DATA' not in os.environ and 'PROJ_LIB' not in os.environ:
    os.environ['PROJ_DATA'] = os.path.join(os.path.dirname(os.environ['GDAL_DATA']), 'proj')
