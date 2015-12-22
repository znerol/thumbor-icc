#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from PIL import Image, ImageCms
from cStringIO import StringIO
from thumbor.filters import BaseFilter, filter_method, PHASE_AFTER_LOAD
from thumbor.utils import logger

import os

class Filter(BaseFilter):

    phase = PHASE_AFTER_LOAD

    def _find_profile(self, profile=None):
        if not profile:
            profile = self.context.config.ICC_DEFAULT_PROFILE

        iccfile = profile + '.icc'

        for path in self.context.config.ICC_PATH:
            filepath = os.path.join(path, iccfile)
            logger.debug('Checking for ICC profile in {:s}'.format(filepath))
            if os.path.exists(filepath):
                return filepath


    @filter_method(BaseFilter.String)
    def icc_profile_apply(self, profile=None):
        if not self.engine.icc_profile:
            logger.info('Input image has no embedded profile. Cannot convert.')
            return

        inmode = self.engine.get_image_mode()
        insize = self.engine.size
        inimg = Image.frombytes(inmode, insize, self.engine.get_image_data())

        inprofile = StringIO(self.engine.icc_profile)

        outmode = 'RGBA' if 'A' in inmode else 'RGB'
        outprofile = self._find_profile(profile)

        if not outprofile:
            logger.warning('Failed to load ICC profile: {:s}'.format(profile))
            return

        logger.debug('Attempting to convert to ICC profile: {:s}'.format(profile))
        try:
            outimg = ImageCms.profileToProfile(inimg, inprofile, outprofile, outputMode=outmode)
            self.engine.set_image_data(outimg.tostring())
        except:
            logger.error('Failed to convert to ICC profile: {:s}'.format(profile))
