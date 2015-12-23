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
import sys

class Filter(BaseFilter):

    phase = PHASE_AFTER_LOAD

    def _find_profile(self, profile=None):
        if not profile:
            profile = self.context.config.ICC_DEFAULT_PROFILE

        iccfile = profile + '.icc'

        for path in self.context.config.ICC_PATH:
            filepath = os.path.join(path, iccfile)
            logger.debug('ICC: Checking for profile in {:s}'.format(filepath))
            if os.path.exists(filepath):
                return filepath


    @filter_method(BaseFilter.String)
    def icc_profile_apply(self, profile=None):
        # Check whether input image has color management.
        if not self.engine.icc_profile:
            logger.info('ICC: Image has no embedded profile. Skipping this image.')
            return

        # Sanitize profile parameter.
        if profile != None:
            profile = os.path.basename(profile).lstrip('.')
            if len(profile) == 0:
                logger.warning('ICC: Invalid profile name.')
                return

        # Find output profile.
        outprofile = self._find_profile(profile)
        if not outprofile:
            logger.warning('ICC: Failed to load profile: {:s}'.format(profile))
            return


        inmode = self.engine.get_image_mode()
        insize = self.engine.size
        inimg = Image.frombytes(inmode, insize, self.engine.get_image_data())
        inprofile = StringIO(self.engine.icc_profile)
        outmode = 'RGBA' if 'A' in inmode else 'RGB'

        logger.debug('ICC: Attempting to apply profile: {:s}'.format(profile))
        try:
            outimg = ImageCms.profileToProfile(inimg, inprofile, outprofile, outputMode=outmode)
            self.engine.set_image_data(outimg.tostring())
        except:
            logger.error('ICC: Failed to apply profile: {:s}'.format(profile))
