#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
A collection of thumbor filters providing better support for color managed
images.
"""

import os

from thumbor.config import Config

# ICC options
_WELL_KNOWN_PATHS = [
    "/usr/share/color/icc"
]

_DEFAULT_PATHS = [path for path in _WELL_KNOWN_PATHS if os.path.exists(path)]

Config.define('ICC_PATH', _DEFAULT_PATHS,
              'An array of path to directories containing ICC profiles.',
              'Color management')
Config.define('ICC_DEFAULT_PROFILE', 'sRGB',
              'Name of the default ICC profile applied of none is specified.',
              'Color management')
