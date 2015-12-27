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

        try:
            ext = self.engine.extension
            fmt = Image.EXTENSION[ext.lower()]
        except:
            logger.exception('ICC: Failed to determine image format and extension before attempting to apply profile: {:s}'.format(profile))
            return

        try:
            inmode = self.engine.get_image_mode()
            insize = self.engine.size
            inimg = Image.frombytes(inmode, insize, self.engine.get_image_data())
            inprofile = StringIO(self.engine.icc_profile)
            outmode = 'RGBA' if 'A' in inmode else 'RGB'
        except:
            logger.exception('ICC: Failed to determine image properties before attempting to apply profile: {:s}'.format(profile))
            return

        logger.info('ICC: Attempting to apply profile: {:s}, inmode: {:s}, outmode: {:s}'.format(profile, inmode, outmode))
        try:
            outimg = ImageCms.profileToProfile(inimg, inprofile, outprofile, outputMode=outmode)
        except:
            logger.exception('ICC: Failed to apply profile: {:s}, inmode: {:s}, outmode: {:s}'.format(profile, inmode, outmode))
            return

        # Reload the image into the engine.
        outbuf = StringIO()
        try:
            outimg.save(outbuf, fmt)
            self.engine.load(outbuf.getvalue(), ext)
        except:
            logger.exception('ICC: Failed load the image with an applied profile: {:s}, inmode: {:s}, outmode: {:s}'.format(profile, inmode, outmode))
            return
        finally:
            outbuf.close()
