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

from traitsui.toolkit_traits import RGBColor


class HasRGBColor(HasTraits):
    color = RGBColor()


class TestRGBColor(unittest.TestCase):

    # regression test for enthought/traitsui#1531
    def test_hex_converion(self):
        has_rgb_color = HasRGBColor()
        has_rgb_color.color = 0x000000
        self.assertEqual(has_rgb_color.color, (0.0, 0.0, 0.0))
