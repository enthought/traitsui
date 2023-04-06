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

from pyface.font import Font as PyfaceFont
from pyface.util.font_parser import simple_parser
from pyface.qt.QtGui import QFont, QFontInfo, QApplication
from traits.api import HasTraits, TraitError

from ..font_trait import (
    PyQtFont, TraitsFont, create_traitsfont, font_families, font_styles,
    font_to_str, font_weights
)


class FontExample(HasTraits):

    font = PyQtFont()


class TestPyQtFont(unittest.TestCase):

    def test_create_traitsfont(self):
        expected_outcomes = {}
        expected_outcomes[""] = TraitsFont()

        for weight, qt_weight in font_weights.items():
            expected_outcomes[weight] = TraitsFont()
            expected_outcomes[weight].setWeight(qt_weight)

        for style, qt_style in font_styles.items():
            expected_outcomes[style] = TraitsFont()
            expected_outcomes[style].setStyle(qt_style)

        expected_outcomes["underline"] = TraitsFont()
        expected_outcomes["underline"].setUnderline(True)

        expected_outcomes["18"] = TraitsFont()
        expected_outcomes["18"].setPointSize(18)
        expected_outcomes["18 pt"] = TraitsFont()
        expected_outcomes["18 pt"].setPointSize(18)
        expected_outcomes["18 point"] = TraitsFont()
        expected_outcomes["18 point"].setPointSize(18)

        for family, qt_style_hint in font_families.items():
            expected_outcomes[family] = TraitsFont()
            expected_outcomes[family].setStyleHint(qt_style_hint)

        default_size = QApplication.font().pointSize()
        expected_outcomes["Courier"] = TraitsFont("Courier", default_size)
        expected_outcomes["Comic Sans"] = TraitsFont("Comic Sans", default_size)
        expected_outcomes["18 pt Bold Oblique Underline Comic Sans script"] = TraitsFont(
            "Comic Sans", 18, QFont.Weight.Bold, False
        )
        expected_outcomes["18 pt Bold Oblique Underline Comic Sans script"].setStyleHint(QFont.StyleHint.Cursive)
        expected_outcomes["18 pt Bold Oblique Underline Comic Sans script"].setStyle(QFont.Style.StyleOblique)
        expected_outcomes["18 pt Bold Oblique Underline Comic Sans script"].setUnderline(True)

        for name, expected in expected_outcomes.items():
            with self.subTest(name=name):
                result = create_traitsfont(name)

                # test we get expected font
                self.assertIsInstance(result, TraitsFont)
                self.assert_qfont_equal(result, expected)

                # round-trip through font_to_str
                result_2 = create_traitsfont(font_to_str(result))
                self.assert_qfont_equal(result, result_2)

    def test_create_traitsfont_qfont(self):
        font = QFont("Comic Sans", 18, QFont.Weight.Bold, False)
        traits_font = create_traitsfont(font)

        self.assertIsInstance(traits_font, TraitsFont)
        self.assert_qfont_equal(traits_font, font)

    def test_create_traitsfont_pyface_font(self):
        args = simple_parser("18 pt Bold Oblique Underline Courier")
        font = PyfaceFont(**args)
        traits_font = create_traitsfont(font)

        self.assertIsInstance(traits_font, TraitsFont)
        self.assert_qfont_equal(traits_font, font.to_toolkit())

    def test_font_trait_default(self):
        obj = FontExample()

        self.assertIsInstance(obj.font, TraitsFont)
        self.assert_qfont_equal(obj.font, TraitsFont())

    def test_font_trait_str(self):
        obj = FontExample(font="18 pt Bold Oblique Underline Comic Sans script")
        qfont = TraitsFont(
            "Comic Sans", 18, QFont.Weight.Bold, False
        )
        qfont.setStyleHint(QFont.StyleHint.Cursive)
        qfont.setStyle(QFont.Style.StyleOblique)
        qfont.setUnderline(True)

        self.assertIsInstance(obj.font, TraitsFont)
        self.assert_qfont_equal(obj.font, qfont)

    def test_font_trait_qfont(self):
        qfont = TraitsFont(
            "Comic Sans", 18, QFont.Weight.Bold, False
        )
        qfont.setStyleHint(QFont.StyleHint.Cursive)
        qfont.setStyle(QFont.Style.StyleOblique)
        qfont.setUnderline(True)
        obj = FontExample(font=qfont)

        self.assertIsInstance(obj.font, TraitsFont)
        self.assert_qfont_equal(obj.font, qfont)

    def test_font_trait_pyface_font(self):
        args = simple_parser("18 pt Bold Oblique Underline Courier typewriter")
        font = PyfaceFont(**args)
        obj = FontExample(font=font)

        self.assertIsInstance(obj.font, TraitsFont)
        self.assert_qfont_equal(obj.font, font.to_toolkit())

    def test_font_trait_none(self):
        obj = FontExample(font=None)

        self.assertIsNone(obj.font)

    def test_font_trait_bad(self):
        with self.assertRaises(TraitError):
            obj = FontExample(font=1)

    def test_traits_font_reduce(self):
        traits_font = TraitsFont(
            "Comic Sans", 18, QFont.Weight.Bold, False
        )
        traits_font.setStyleHint(QFont.StyleHint.Cursive)
        traits_font.setStyle(QFont.Style.StyleOblique)
        traits_font.setUnderline(True)

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
            "Comic Sans", 18, QFont.Weight.Bold, False
        )
        traits_font.setStyleHint(QFont.StyleHint.Cursive)
        traits_font.setStyle(QFont.Style.StyleOblique)
        traits_font.setUnderline(True)

        result = str(traits_font)

        self.assertEqual(
            result,
            "18 point Comic Sans Oblique Bold underline",
        )

    def assert_qfont_equal(self, font, other):
        self.assertIsInstance(font, QFont)
        self.assertIsInstance(other, QFont)

        self.assertEqual(font.family(), other.family())
        self.assertEqual(font.styleHint(), font.styleHint())
        self.assertEqual(font.pointSize(), other.pointSize())
        self.assertEqual(font.style(), other.style())
        self.assertEqual(font.weight(), other.weight())
        self.assertEqual(font.underline(), other.underline())
