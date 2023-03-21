# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Tests pertaining to the AnimatedGIFEditor
"""

import unittest

import pkg_resources

from traits.api import File, HasTraits
from traitsui.api import Item, View
from traitsui.tests._tools import (
    BaseTestMixin,
    create_ui,
    requires_toolkit,
    ToolkitName,
)

filename = pkg_resources.resource_filename(
    "traitsui", "examples/demo/Extras/images/logo_32x32.gif"
)


class AnimatedGIF(HasTraits):

    gif_file = File(filename)


@requires_toolkit([ToolkitName.wx])
class TestAnimatedGIFEditor(BaseTestMixin, unittest.TestCase):
    def setUp(self):
        BaseTestMixin.setUp(self)

    def tearDown(self):
        BaseTestMixin.tearDown(self)

    def test_animated_gif_editor(self):
        from traitsui.wx.animated_gif_editor import AnimatedGIFEditor

        # Regression test for enthought/traitsui#1071
        obj1 = AnimatedGIF()
        view = View(
            Item('gif_file', editor=AnimatedGIFEditor(playing='playing')),
        )

        # This should not fail.
        with create_ui(obj1, dict(view=view)):
            pass
