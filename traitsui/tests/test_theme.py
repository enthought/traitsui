# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import pickle
import unittest
from unittest.mock import patch

from traitsui.tests._tools import BaseTestMixin, requires_toolkit, ToolkitName
from traitsui.theme import Theme


class TestTheme(BaseTestMixin, unittest.TestCase):
    def setUp(self):
        BaseTestMixin.setUp(self)
        self.theme = Theme()

    def tearDown(self):
        BaseTestMixin.tearDown(self)

    def test_theme_pickling(self):
        # A regression test for issue enthought/traitsui#825
        pickle.dumps(self.theme)

    @requires_toolkit([ToolkitName.wx])
    def test_theme_content_color_default(self):
        import wx

        self.assertEqual(self.theme.content_color, wx.BLACK)

    def test_theme_content_color_setter_getter(self):
        self.theme.content_color = "red"
        self.assertEqual(self.theme.content_color, "red")

    @requires_toolkit([ToolkitName.wx])
    def test_theme_label_color_default(self):
        import wx

        self.assertEqual(self.theme.label_color, wx.BLACK)

    def test_theme_label_color_setter_getter(self):
        self.theme.label_color = "red"
        self.assertEqual(self.theme.label_color, "red")

    @requires_toolkit([ToolkitName.wx])
    def test_theme_get_image_slice(self):
        self.theme.image = "mock_image"
        with patch("traitsui.wx.image_slice.image_slice_for") as slice_func:
            self.theme.image_slice
            slice_func.assert_called_once()

    def test_theme_get_image_slice_none(self):
        self.theme.image = None
        self.assertIsNone(self.theme.image_slice)
