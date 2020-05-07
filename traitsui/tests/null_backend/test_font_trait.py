import unittest

from traits.api import HasTraits

from traitsui.toolkit_traits import Font
from traitsui.tests._tools import skip_if_not_null


class TestFontTrait(unittest.TestCase):

    @skip_if_not_null
    def test_font_trait_default(self):
        class Foo(HasTraits):
            font = Font()

        f = Foo()
        self.assertEquals(f.font, "10 pt Arial")

    @skip_if_not_null
    def test_font_trait_examples(self):
        """
        An assigned font string is parsed, and the substrings are put
        in the order: point size, family, style, weight, underline, facename

        The words 'pt, 'point' and 'family' are ignored.

        """

        class Foo(HasTraits):
            font = Font

        f = Foo(font="Qwerty 10")
        self.assertEquals(f.font, "10 pt Qwerty")

        f = Foo(font="nothing")
        self.assertEquals(f.font, "nothing")

        f = Foo(font="swiss family arial")
        self.assertEquals(f.font, "swiss arial")

        f = Foo(font="12 pt bold italic")
        self.assertEquals(f.font, "12 pt italic bold")

        f = Foo(font="123 Foo bar slant")
        self.assertEquals(f.font, "123 pt slant Foo bar")

        f = Foo(font="123 point Foo family bar slant")
        self.assertEquals(f.font, "123 pt slant Foo bar")

        f = Foo(font="16 xyzzy underline slant")
        self.assertEquals(f.font, "16 pt slant underline xyzzy")
