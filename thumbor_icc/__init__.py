#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

_well_known_paths = [
    "/usr/share/color/icc"
]

_default_paths = [path for path in _well_known_paths if os.path.exists(path)]

# ICC options
from thumbor.config import Config
Config.define('ICC_PATH', _default_paths, 'An array of path to directories containing ICC profiles.', 'Color management')
Config.define('ICC_DEFAULT_PROFILE', 'sRGB', 'Name of the default ICC profile applied of none is specified.', 'Color management')
