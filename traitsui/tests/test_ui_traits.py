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

from traits.api import HasStrictTraits
from traitsui import ui_traits
from traitsui.tests._tools import BaseTestMixin


class ObjectWithUITraits(HasStrictTraits):

    orientation = ui_traits.Orientation
    style = ui_traits.EditorStyle
    layout = ui_traits.Layout
    an_object = ui_traits.AnObject
    dock_style = ui_traits.DockStyle
    view_status = ui_traits.ViewStatus()


class TestUITraits(BaseTestMixin, unittest.TestCase):
    def setUp(self):
        BaseTestMixin.setUp(self)

    def tearDown(self):
        BaseTestMixin.tearDown(self)

    def test_orientation(self):
        obj = ObjectWithUITraits()
        self.assertEqual(obj.orientation, "vertical")

        obj.orientation = "h"
        self.assertEqual(obj.orientation, "horizontal")

    def test_editor_style(self):
        obj = ObjectWithUITraits()
        self.assertEqual(obj.style, "simple")

        obj.style = "r"
        self.assertEqual(obj.style, "readonly")

    def test_layout(self):
        obj = ObjectWithUITraits()
        self.assertEqual(obj.layout, "normal")

    def test_an_object(self):
        obj = ObjectWithUITraits()
        obj.an_object = "[1,2,3][0]"
        self.assertEqual(obj.an_object, "[1,2,3][0]")
        actual = eval(obj.an_object_, {}, {})
        self.assertEqual(actual, 1)


class TestStatusItem(BaseTestMixin, unittest.TestCase):
    def setUp(self):
        BaseTestMixin.setUp(self)

    def tearDown(self):
        BaseTestMixin.tearDown(self)

    def test_init(self):
        item = ui_traits.StatusItem(
            name="some_trait_name",
            width=10.0,
        )
        self.assertEqual(item.name, "some_trait_name")

    def test_init_with_name_and_value(self):
        # value trumps name. Not sure why but this is the way it is.
        item = ui_traits.StatusItem(
            name="some_trait_name",
            width=10.0,
            value="some_other_name",
        )
        self.assertEqual(item.name, "some_other_name")


class TestViewStatus(BaseTestMixin, unittest.TestCase):
    def setUp(self):
        BaseTestMixin.setUp(self)

    def tearDown(self):
        BaseTestMixin.tearDown(self)

    def test_init(self):
        obj = ObjectWithUITraits()

        obj.view_status = "some_name"
        self.assertEqual(len(obj.view_status), 1)
        (status,) = obj.view_status
        self.assertIsInstance(status, ui_traits.StatusItem)
        self.assertEqual(status.name, "some_name")
