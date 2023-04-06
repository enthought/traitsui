# (C) Copyright 2008-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import unittest

import wx

from pyface.font import Font as PyfaceFont
from pyface.util.font_parser import simple_parser
from traits.api import HasTraits, TraitError

from ..font_trait import (
    WxFont, TraitsFont, create_traitsfont, font_families, font_styles,
    font_to_str, font_weights
)


class FontExample(HasTraits):

    font = WxFont()


class TestWxFont(unittest.TestCase):

    def test_create_traitsfont(self):
        expected_outcomes = {}
        expected_outcomes[""] = TraitsFont(
            10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL
        )

        for weight, wx_weight in font_weights.items():
            expected_outcomes[weight] = TraitsFont(
                10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx_weight
            )

        for style, wx_style in font_styles.items():
            expected_outcomes[style] = TraitsFont(
                10, wx.FONTFAMILY_DEFAULT, wx_style, wx.FONTWEIGHT_NORMAL
            )

        expected_outcomes["underline"] = TraitsFont(
            10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, True
        )

        for size in ["18", "18 pt", "18 point"]:
            expected_outcomes[size] = TraitsFont(
                18, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL
            )

        for family, wx_family in font_families.items():
            expected_outcomes[family] = TraitsFont(
                10, wx_family, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL
            )

        expected_outcomes["Courier"] = TraitsFont(
            10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "Courier",
        )
        expected_outcomes["Comic Sans"] = TraitsFont(
            10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "Comic Sans",
        )
        expected_outcomes["18 pt Bold Oblique Underline Comic Sans script"] = TraitsFont(
            18, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_SLANT, wx.FONTWEIGHT_BOLD, True, "Comic Sans",
        )

        for name, expected in expected_outcomes.items():
            with self.subTest(name=name):
                result = create_traitsfont(name)

                # test we get expected font
                self.assertIsInstance(result, TraitsFont)
                self.assert_wxfont_equal(result, expected)

                # round-trip trhough font_to_str
                result_2 = create_traitsfont(font_to_str(result))
                self.assert_wxfont_equal(result, result_2)

    def test_create_traitsfont_wx_font(self):
        font = wx.Font(
            18, wx.FONTFAMILY_SCRIPT, wx.FONTSTYLE_SLANT, wx.FONTWEIGHT_BOLD, True, "Comic Sans",
        )
        traits_font = create_traitsfont(font)

        self.assertIsInstance(traits_font, TraitsFont)
        self.assert_wxfont_equal(traits_font, font)

    def test_create_traitsfont_system_default(self):
        font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        traits_font = create_traitsfont(font)

        self.assertIsInstance(traits_font, TraitsFont)
        self.assert_wxfont_equal(traits_font, font)

    def test_create_traitsfont_pyface_font(self):
        args = simple_parser("18 pt Bold Oblique Underline Courier")
        font = PyfaceFont(**args)
        traits_font = create_traitsfont(font)

        self.assertIsInstance(traits_font, TraitsFont)
        self.assert_wxfont_equal(traits_font, font.to_toolkit())

    def test_font_trait_default(self):
        obj = FontExample()

        self.assertIsInstance(obj.font, TraitsFont)
        self.assert_wxfont_equal(obj.font, wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT))

    def test_font_trait_str(self):
        obj = FontExample(font="18 pt Bold Oblique Underline Comic Sans script")
        wx_font = TraitsFont(
            18, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_SLANT, wx.FONTWEIGHT_BOLD, True, "Comic Sans",
        )

        self.assertIsInstance(obj.font, TraitsFont)
        self.assert_wxfont_equal(obj.font, wx_font)

    def test_font_trait_wx_font(self):
        wx_font = TraitsFont(
            18, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_SLANT, wx.FONTWEIGHT_BOLD, True, "Comic Sans",
        )
        obj = FontExample(font=wx_font)

        self.assertIsInstance(obj.font, TraitsFont)
        self.assert_wxfont_equal(obj.font, wx_font)

    def test_font_trait_pyface_font(self):
        args = simple_parser("18 pt Bold Oblique Underline Courier typewriter")
        font = PyfaceFont(**args)
        obj = FontExample(font=font)

        self.assertIsInstance(obj.font, TraitsFont)
        self.assert_wxfont_equal(obj.font, font.to_toolkit())

    def test_font_trait_none(self):
        obj = FontExample(font=None)

        self.assertIsNone(obj.font)

    def test_font_trait_bad(self):
        with self.assertRaises(TraitError):
            obj = FontExample(font=1)

    def test_traits_font_reduce(self):
        traits_font = TraitsFont(
            18, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_SLANT, wx.FONTWEIGHT_BOLD, True, "Comic Sans",
        )

        result = traits_font.__reduce_ex__(None)

        self.assertEqual(
            result,
            (
                create_traitsfont,
                ("18 point Comic Sans Oblique Bold underline",),
            ),
        )

    def test_traits_font_str(self):
        traits_font = TraitsFont(
            18, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_SLANT, wx.FONTWEIGHT_BOLD, True, "Comic Sans",
        )

        result = str(traits_font)

        self.assertEqual(
            result,
            "18 point Comic Sans Oblique Bold underline",
        )

    def assert_wxfont_equal(self, font, other):
        self.assertIsInstance(font, wx.Font)
        self.assertIsInstance(other, wx.Font)

        self.assertEqual(font.FaceName, font.FaceName)
        self.assertEqual(font.Family, other.Family)
        self.assertEqual(font.PointSize, other.PointSize)
        self.assertEqual(font.Style, other.Style)
        self.assertEqual(font.Weight, other.Weight)
        self.assertEqual(font.GetUnderlined(), other.GetUnderlined())
