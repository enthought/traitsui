# (C) Copyright 2008-2022 Enthought, Inc., Austin, TX
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

from pyface.color import Color as PyfaceColor
from traits.api import HasStrictTraits, TraitError

from traitsui.wx.color_trait import WxColor


class ObjectWithColor(HasStrictTraits):

    color = WxColor()


class ObjectWithColorAllowsNone(HasStrictTraits):

    color = WxColor(allow_none=True)


class TestWxColor(unittest.TestCase):

    def test_default(self):
        obj = ObjectWithColor()

        self.assertIsInstance(obj.color, wx.Colour)
        self.assertEqual(obj.color.Get(), (255, 255, 255, 255))

    def test_tuple_rgb(self):
        obj = ObjectWithColor(color=(0, 128, 255))

        self.assertIsInstance(obj.color, wx.Colour)
        self.assertEqual(obj.color.Get(), (0, 128, 255, 255))

    def test_tuple_rgba(self):
        obj = ObjectWithColor(color=(0, 128, 255, 64))

        self.assertIsInstance(obj.color, wx.Colour)
        self.assertEqual(obj.color.Get(), (0, 128, 255, 64))

    def test_name_string(self):
        obj = ObjectWithColor(color="maroon")

        self.assertIsInstance(obj.color, wx.Colour)
        self.assertEqual(obj.color.Get(), (128, 0, 0, 255))

    def test_rgb_string(self):
        obj = ObjectWithColor(color="(0, 128, 255)")

        self.assertIsInstance(obj.color, wx.Colour)
        self.assertEqual(obj.color.Get(), (0, 128, 255, 255))

    def test_rgba_string(self):
        obj = ObjectWithColor(color="(0, 128, 255, 64)")

        self.assertIsInstance(obj.color, wx.Colour)
        self.assertEqual(obj.color.Get(), (0, 128, 255, 64))

    def test_rgb_int_string(self):
        obj = ObjectWithColor(color="0x0088ff")

        self.assertIsInstance(obj.color, wx.Colour)
        self.assertEqual(obj.color.Get(), (0x00, 0x88, 0xff, 0xff))

    def test_rgb_int(self):
        obj = ObjectWithColor(color=0x0088ff)

        self.assertIsInstance(obj.color, wx.Colour)
        self.assertEqual(obj.color.Get(), (0x00, 0x88, 0xff, 0xff))

    def test_pyface_color(self):
        obj = ObjectWithColor(color=PyfaceColor(rgba=(0.0, 0.5, 1.0, 0.25)))

        self.assertIsInstance(obj.color, wx.Colour)
        self.assertEqual(obj.color.Get(), (0, 128, 255, 64))

    def test_default_none(self):
        obj = ObjectWithColorAllowsNone()

        self.assertIsInstance(obj.color, wx.Colour)
        self.assertEqual(obj.color.Get(), (255, 255, 255, 255))

    def test_bad_color(self):
        with self.assertRaises(TraitError):
            ObjectWithColor(color="not a color")
