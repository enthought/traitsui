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

from pyface.qt import QtGui
from pyface.color import Color as PyfaceColor
from traits.api import HasStrictTraits, TraitError

from traitsui.qt.color_trait import PyQtColor


class ObjectWithColor(HasStrictTraits):

    color = PyQtColor()


class ObjectWithColorAllowsNone(HasStrictTraits):

    color = PyQtColor(allow_none=True)


class TestPyQtColor(unittest.TestCase):

    def test_default(self):
        obj = ObjectWithColor()

        self.assertIsInstance(obj.color, QtGui.QColor)
        self.assertEqual(obj.color.getRgb(), (255, 255, 255, 255))
        self.assertIsInstance(obj.color_, QtGui.QColor)
        self.assertEqual(obj.color_.getRgb(), (255, 255, 255, 255))

    def test_tuple_rgb(self):
        obj = ObjectWithColor(color=(0, 128, 255))

        self.assertIsInstance(obj.color, QtGui.QColor)
        self.assertEqual(obj.color.getRgb(), (0, 128, 255, 255))
        self.assertIsInstance(obj.color_, QtGui.QColor)
        self.assertEqual(obj.color_.getRgb(), (0, 128, 255, 255))

    def test_tuple_rgba(self):
        obj = ObjectWithColor(color=(0, 128, 255, 64))

        self.assertIsInstance(obj.color, QtGui.QColor)
        self.assertEqual(obj.color.getRgb(), (0, 128, 255, 64))
        self.assertIsInstance(obj.color_, QtGui.QColor)
        self.assertEqual(obj.color_.getRgb(), (0, 128, 255, 64))

    def test_name_string(self):
        obj = ObjectWithColor(color="rebeccapurple")

        self.assertIsInstance(obj.color, QtGui.QColor)
        self.assertEqual(obj.color.getRgb(), (0x66, 0x33, 0x99, 0xff))
        self.assertIsInstance(obj.color_, QtGui.QColor)
        self.assertEqual(obj.color_.getRgb(), (0x66, 0x33, 0x99, 0xff))

    def test_name_string_with_space(self):
        obj = ObjectWithColor(color="rebecca purple")

        self.assertIsInstance(obj.color, QtGui.QColor)
        self.assertEqual(obj.color.getRgb(), (0x66, 0x33, 0x99, 0xff))
        self.assertIsInstance(obj.color_, QtGui.QColor)
        self.assertEqual(obj.color_.getRgb(), (0x66, 0x33, 0x99, 0xff))

    def test_rgb_string(self):
        obj = ObjectWithColor(color="(0, 128, 255)")

        self.assertIsInstance(obj.color, QtGui.QColor)
        self.assertEqual(obj.color.getRgb(), (0, 128, 255, 255))
        self.assertIsInstance(obj.color_, QtGui.QColor)
        self.assertEqual(obj.color_.getRgb(), (0, 128, 255, 255))

    def test_rgba_string(self):
        obj = ObjectWithColor(color="(0, 128, 255, 64)")

        self.assertIsInstance(obj.color, QtGui.QColor)
        self.assertEqual(obj.color.getRgb(), (0, 128, 255, 64))
        self.assertIsInstance(obj.color_, QtGui.QColor)
        self.assertEqual(obj.color_.getRgb(), (0, 128, 255, 64))

    def test_rgb_int_string_3(self):
        obj = ObjectWithColor(color="#08f")

        self.assertIsInstance(obj.color, QtGui.QColor)
        self.assertEqual(obj.color.getRgb(), (0x00, 0x88, 0xff, 0xff))
        self.assertIsInstance(obj.color_, QtGui.QColor)
        self.assertEqual(obj.color_.getRgb(), (0x00, 0x88, 0xff, 0xff))

    def test_rgb_int_string_6(self):
        obj = ObjectWithColor(color="#0088ff")

        self.assertIsInstance(obj.color, QtGui.QColor)
        self.assertEqual(obj.color.getRgb(), (0x00, 0x88, 0xff, 0xff))
        self.assertIsInstance(obj.color_, QtGui.QColor)
        self.assertEqual(obj.color_.getRgb(), (0x00, 0x88, 0xff, 0xff))

    def test_rgb_int_string_12(self):
        obj = ObjectWithColor(color="#00008888ffff")

        self.assertIsInstance(obj.color, QtGui.QColor)
        self.assertEqual(obj.color.getRgb(), (0x00, 0x88, 0xff, 0xff))
        self.assertIsInstance(obj.color_, QtGui.QColor)
        self.assertEqual(obj.color_.getRgb(), (0x00, 0x88, 0xff, 0xff))

    def test_rgb_int(self):
        obj = ObjectWithColor(color=0x0088ff)

        self.assertIsInstance(obj.color, QtGui.QColor)
        self.assertEqual(obj.color.getRgb(), (0x00, 0x88, 0xff, 0xff))
        self.assertIsInstance(obj.color_, QtGui.QColor)
        self.assertEqual(obj.color_.getRgb(), (0x00, 0x88, 0xff, 0xff))

    def test_qcolor(self):
        obj = ObjectWithColor(color=QtGui.QColor(0, 128, 255, 64))

        self.assertIsInstance(obj.color, QtGui.QColor)
        self.assertEqual(obj.color.getRgb(), (0, 128, 255, 64))
        self.assertIsInstance(obj.color_, QtGui.QColor)
        self.assertEqual(obj.color_.getRgb(), (0, 128, 255, 64))

    def test_pyface_color(self):
        obj = ObjectWithColor(color=PyfaceColor(rgba=(0.0, 0.5, 1.0, 0.25)))

        self.assertIsInstance(obj.color, QtGui.QColor)
        self.assertEqual(obj.color.getRgb(), (0, 128, 255, 64))
        self.assertIsInstance(obj.color_, QtGui.QColor)
        self.assertEqual(obj.color_.getRgb(), (0, 128, 255, 64))

    def test_default_none(self):
        obj = ObjectWithColorAllowsNone(color=None)

        self.assertIsNone(obj.color)
        self.assertIsNone(obj.color_)

    def test_bad_color(self):
        with self.assertRaises(TraitError):
            ObjectWithColor(color="not a color")

    def test_bad_tuple(self):
        with self.assertRaises(TraitError):
            ObjectWithColor(color=(0xff, 0xff))

    def test_bad_tuple_not_int(self):
        with self.assertRaises(TraitError):
            ObjectWithColor(color=("not an int", 0xff, 0xff))

    def test_bad_tuple_string(self):
        with self.assertRaises(TraitError):
            ObjectWithColor(color="(0xff, 0xff)")
