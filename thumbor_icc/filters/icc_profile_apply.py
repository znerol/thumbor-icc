#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
A collection of thumbor filters providing better support for color managed
images.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import os

from cStringIO import StringIO

from PIL import Image, ImageCms
from thumbor.filters import BaseFilter, filter_method, PHASE_AFTER_LOAD
from thumbor.utils import logger


# pylint: disable=R0903
class Filter(BaseFilter):
    """
    A collection of thumbor filters providing better support for color managed
    images.
    """

    phase = PHASE_AFTER_LOAD

    def _find_profile(self, profile=None):
        result = ""

        if not profile:
            profile = self.context.config.ICC_DEFAULT_PROFILE

        iccfile = profile + ".icc"

        for path in self.context.config.ICC_PATH:
            filepath = os.path.join(path, iccfile)
            logger.debug("ICC: Checking for profile in {:s}".format(filepath))
            if os.path.exists(filepath):
                result = filepath
                break

        return result

    # pylint: disable=R0911
    # pylint: disable=W0703
    @filter_method(BaseFilter.String)
    def icc_profile_apply(self, profile=None):
        """
        Optain an RGB(A) image by applying the given profile.
        """
        # Check whether input image has color management.
        if not self.engine.icc_profile:
            logger.info("ICC: Image has no embedded profile. "
                        "Skipping this image.")
            return

        # Sanitize profile parameter.
        if profile is not None:
            profile = os.path.basename(profile).lstrip(".")
            if not profile:
                logger.warning("ICC: Invalid profile name.")
                return

        # Find output profile.
        outprofile = self._find_profile(profile)
        if not outprofile:
            logger.warning("ICC: Failed to load profile: {:s}".format(profile))
            return

        try:
            ext = self.engine.extension
            fmt = Image.EXTENSION[ext.lower()]
        except Exception:
            logger.exception("ICC: Failed to determine image format and "
                             "extension before attempting to apply "
                             "profile: {:s}".format(profile))
            return

        try:
            inmode = self.engine.get_image_mode()
            insize = self.engine.size
            indata = self.engine.get_image_data()
            inimg = Image.frombytes(inmode, insize, indata)

            # In PIL>=3.0.0 / Thumbor 6, icc_profile is sometimes a tuple :/
            # https://github.com/python-pillow/Pillow/issues/1462
            profile_data = self.engine.icc_profile
            # pylint: disable=C0123
            if type(profile_data) == tuple:
                profile_data = profile_data[0]
            inprofile = StringIO(profile_data)

            outmode = "RGBA" if "A" in inmode else "RGB"
        except Exception:
            logger.exception("ICC: Failed to determine image "
                             "properties before attempting to apply "
                             "profile: {:s}".format(profile))
            return

        logger.info("ICC: Attempting to apply profile: {:s}, inmode: {:s}, "
                    "outmode: {:s}".format(profile, inmode, outmode))
        try:
            outimg = ImageCms.profileToProfile(inimg, inprofile, outprofile,
                                               outputMode=outmode)
        except Exception:
            logger.exception("ICC: Failed to apply profile: {:s}, "
                             "inmode: {:s}, "
                             "outmode: {:s}".format(profile, inmode, outmode))
            return

        # Reload the image into the engine.
        outbuf = StringIO()
        try:
            outimg.save(outbuf, fmt)
            self.engine.load(outbuf.getvalue(), ext)
        except Exception:
            logger.exception("ICC: Failed load the image with an applied "
                             "profile: {:s}, inmode: {:s}, "
                             "outmode: {:s}".format(profile, inmode, outmode))
            return
        finally:
            outbuf.close()
