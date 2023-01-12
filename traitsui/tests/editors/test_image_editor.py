# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Tests pertaining to the ImageEditor
"""

import unittest

import pkg_resources

from pyface.api import Image, ImageResource
from traits.api import File, HasTraits
from traitsui.api import ImageEditor, Item, View
from traitsui.tests._tools import (
    BaseTestMixin,
    create_ui,
    is_qt,
    is_mac_os,
    requires_toolkit,
    ToolkitName,
)


filename1 = pkg_resources.resource_filename(
    "traitsui", "examples/demo/Extras/images/python-logo.png"
)
filename2 = pkg_resources.resource_filename(
    "traitsui", "examples/demo/Extras/images/info.png"
)


class ImageDisplay(HasTraits):

    image = Image()


@requires_toolkit([ToolkitName.wx, ToolkitName.qt])
class TestImageEditor(BaseTestMixin, unittest.TestCase):

    def test_image_editor_static(self):
        obj1 = ImageDisplay()
        view = View(
            Item(
                'image',
                editor=ImageEditor(
                    image=ImageResource(filename1),
                ),
            )
        )

        # This should not fail.
        with create_ui(obj1, dict(view=view)) as ui:
            pass

    def test_image_editor_resource(self):
        obj1 = ImageDisplay(
            image=ImageResource(filename1)
        )
        view = View(
            Item(
                'image',
                editor=ImageEditor()
            )
        )

        # This should not fail.
        with create_ui(obj1, dict(view=view)) as ui:
            obj1.image = ImageResource(filename2)

    def test_image_editor_array(self):
        try:
            import numpy as np
            from pyface.api import ArrayImage
        except ImportError:
            self.skipTest("NumPy is not available")

        gradient1 = np.empty(shape=(256, 256, 3), dtype='uint8')
        gradient1[:, :, 0] = np.arange(256).reshape(256, 1)
        gradient1[:, :, 1] = np.arange(256).reshape(1, 256)
        gradient1[:, :, 2] = np.arange(255, -1, -1).reshape(1, 256)

        gradient2 = np.empty(shape=(256, 256, 3), dtype='uint8')
        gradient2[:, :, 0] = np.arange(255, -1, -1).reshape(256, 1)
        gradient2[:, :, 1] = np.arange(256).reshape(1, 256)
        gradient2[:, :, 2] = np.arange(255, -1, -1).reshape(1, 256)

        obj1 = ImageDisplay(
            image=ArrayImage(data=gradient1)
        )
        view = View(
            Item(
                'image',
                editor=ImageEditor()
            )
        )

        # This should not fail.
        with create_ui(obj1, dict(view=view)) as ui:
            obj1.image = ArrayImage(data=gradient2)

    @unittest.skipIf(is_mac_os, "Segfault on MacOS, see issue #1979")
    def test_image_editor_pillow(self):
        try:
            import PIL.Image
            from pyface.api import PILImage
        except ImportError:
            self.skipTest("Pillow is not available")
        if is_qt:
            try:
                # is ImageQt available as well
                from PIL.ImageQt import ImageQt
            except ImportError:
                self.skipTest("ImageQt is not available")

        pil_image_1 = PIL.Image.open(filename1)
        pil_image_2 = PIL.Image.open(filename2)

        obj1 = ImageDisplay(
            image=PILImage(image=pil_image_1)
        )
        view = View(
            Item(
                'image',
                editor=ImageEditor()
            )
        )

        # This should not fail.
        with create_ui(obj1, dict(view=view)) as ui:
            obj1.image = PILImage(image=pil_image_2)

    def test_image_editor_none(self):

        obj1 = ImageDisplay(image=None)
        view = View(
            Item(
                'image',
                editor=ImageEditor()
            )
        )

        # This should not fail.
        with create_ui(obj1, dict(view=view)) as ui:
            pass
