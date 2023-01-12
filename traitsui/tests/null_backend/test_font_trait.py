# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import unittest

from traits.api import HasTraits

from traitsui.toolkit_traits import Font
from traitsui.tests._tools import BaseTestMixin, requires_toolkit, ToolkitName


class TestFontTrait(BaseTestMixin, unittest.TestCase):
    def setUp(self):
        BaseTestMixin.setUp(self)

    def tearDown(self):
        BaseTestMixin.tearDown(self)

    @requires_toolkit([ToolkitName.null])
    def test_font_trait_default(self):
        class Foo(HasTraits):
            font = Font()

        f = Foo()
        self.assertEqual(f.font, "10 pt Arial")

    @requires_toolkit([ToolkitName.null])
    def test_font_trait_examples(self):
        """
        An assigned font string is parsed, and the substrings are put
        in the order: point size, family, style, weight, underline, facename

        The words 'pt, 'point' and 'family' are ignored.

        """

        class Foo(HasTraits):
            font = Font

        f = Foo(font="Qwerty 10")
        self.assertEqual(f.font, "10 pt Qwerty")

        f = Foo(font="nothing")
        self.assertEqual(f.font, "nothing")

        f = Foo(font="swiss family arial")
        self.assertEqual(f.font, "swiss arial")

        f = Foo(font="12 pt bold italic")
        self.assertEqual(f.font, "12 pt italic bold")

        f = Foo(font="123 Foo bar slant")
        self.assertEqual(f.font, "123 pt slant Foo bar")

        f = Foo(font="123 point Foo family bar slant")
        self.assertEqual(f.font, "123 pt slant Foo bar")

        f = Foo(font="16 xyzzy underline slant")
        self.assertEqual(f.font, "16 pt slant underline xyzzy")
