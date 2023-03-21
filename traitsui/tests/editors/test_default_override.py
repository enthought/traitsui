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

from traitsui.api import DefaultOverride, EditorFactory
from traits.api import HasTraits, Int
from traitsui.tests._tools import BaseTestMixin


class DummyEditor(EditorFactory):

    x = Int(10)
    y = Int(20)

    def simple_editor(self, ui, object, name, description, parent):
        return ("simple_editor", self, ui, object, name, description, parent)

    def custom_editor(self, ui, object, name, description, parent):
        return ("custom_editor", self, ui, object, name, description, parent)

    def text_editor(self, ui, object, name, description, parent):
        return ("text_editor", self, ui, object, name, description, parent)

    def readonly_editor(self, ui, object, name, description, parent):
        return ("readonly_editor", self, ui, object, name, description, parent)


class NewInt(Int):
    def create_editor(self):
        return DummyEditor()


class Dummy(HasTraits):
    x = NewInt()


dummy_object = Dummy()
do = DefaultOverride(x=15, y=25, format_str="%r")


class TestDefaultOverride(BaseTestMixin, unittest.TestCase):
    def setUp(self):
        BaseTestMixin.setUp(self)

    def tearDown(self):
        BaseTestMixin.tearDown(self)

    def test_simple_override(self):
        (
            editor_name,
            editor,
            ui,
            obj,
            name,
            description,
            parent,
        ) = do.simple_editor("ui", dummy_object, "x", "description", "parent")
        self.assertEqual(editor_name, "simple_editor")
        self.assertEqual(editor.x, 15)
        self.assertEqual(editor.y, 25)
        self.assertEqual(obj, dummy_object)
        self.assertEqual(name, "x")
        self.assertEqual(description, "description")
        self.assertEqual(parent, "parent")

    def test_text_override(self):
        (
            editor_name,
            editor,
            ui,
            obj,
            name,
            description,
            parent,
        ) = do.text_editor("ui", dummy_object, "x", "description", "parent")
        self.assertEqual(editor_name, "text_editor")
        self.assertEqual(editor.x, 15)
        self.assertEqual(editor.y, 25)
        self.assertEqual(obj, dummy_object)
        self.assertEqual(name, "x")
        self.assertEqual(description, "description")
        self.assertEqual(parent, "parent")

    def test_custom_override(self):
        (
            editor_name,
            editor,
            ui,
            obj,
            name,
            description,
            parent,
        ) = do.custom_editor("ui", dummy_object, "x", "description", "parent")
        self.assertEqual(editor_name, "custom_editor")
        self.assertEqual(editor.x, 15)
        self.assertEqual(editor.y, 25)
        self.assertEqual(obj, dummy_object)
        self.assertEqual(name, "x")
        self.assertEqual(description, "description")
        self.assertEqual(parent, "parent")

    def test_readonly_override(self):
        (
            editor_name,
            editor,
            ui,
            obj,
            name,
            description,
            parent,
        ) = do.readonly_editor(
            "ui", dummy_object, "x", "description", "parent"
        )
        self.assertEqual(editor_name, "readonly_editor")
        self.assertEqual(editor.x, 15)
        self.assertEqual(editor.y, 25)
        self.assertEqual(obj, dummy_object)
        self.assertEqual(name, "x")
        self.assertEqual(description, "description")
        self.assertEqual(parent, "parent")
