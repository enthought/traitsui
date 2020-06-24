import pickle
import unittest
from unittest.mock import patch

from traitsui.tests._tools import skip_if_not_wx
from traitsui.theme import Theme


class TestTheme(unittest.TestCase):

    def setUp(self):
        self.theme = Theme()

    def test_theme_pickling(self):
        # A regression test for issue enthought/traitsui#825
        pickle.dumps(self.theme)

    @skip_if_not_wx
    def test_theme_content_color_default(self):
        import wx
        self.assertEqual(self.theme.content_color, wx.BLACK)

    @skip_if_not_wx
    def test_theme_label_color_default(self):
        import wx
        self.assertEqual(self.theme.label_color, wx.BLACK)

    @skip_if_not_wx
    def test_theme_get_image_slice(self):
        self.theme.image = "mock_image"
        with patch("traitsui.wx.image_slice.image_slice_for") as slice_func:
            self.theme.image_slice
            slice_func.assert_called_once()
