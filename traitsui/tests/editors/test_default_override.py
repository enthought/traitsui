import unittest

from traitsui.api import DefaultOverride, EditorFactory
from traits.api import HasTraits, Int


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


class TestDefaultOverride(unittest.TestCase):

    def test_simple_override(self):
        editor_name, editor, ui, obj, name, description, parent = \
            do.simple_editor("ui", dummy_object, "x", "description", "parent")
        self.assertEqual(editor_name, "simple_editor")
        self.assertEqual(editor.x, 15)
        self.assertEqual(editor.y, 25)
        self.assertEqual(obj, dummy_object)
        self.assertEqual(name, "x")
        self.assertEqual(description, "description")
        self.assertEqual(parent, "parent")

    def test_text_override(self):
        editor_name, editor, ui, obj, name, description, parent = \
            do.text_editor("ui", dummy_object, "x", "description", "parent")
        self.assertEqual(editor_name, "text_editor")
        self.assertEqual(editor.x, 15)
        self.assertEqual(editor.y, 25)
        self.assertEqual(obj, dummy_object)
        self.assertEqual(name, "x")
        self.assertEqual(description, "description")
        self.assertEqual(parent, "parent")

    def test_custom_override(self):
        editor_name, editor, ui, obj, name, description, parent = \
            do.custom_editor("ui", dummy_object, "x", "description", "parent")
        self.assertEqual(editor_name, "custom_editor")
        self.assertEqual(editor.x, 15)
        self.assertEqual(editor.y, 25)
        self.assertEqual(obj, dummy_object)
        self.assertEqual(name, "x")
        self.assertEqual(description, "description")
        self.assertEqual(parent, "parent")

    def test_readonly_override(self):
        editor_name, editor, ui, obj, name, description, parent = \
            do.readonly_editor(
                "ui", dummy_object, "x", "description", "parent"
            )
        self.assertEqual(editor_name, "readonly_editor")
        self.assertEqual(editor.x, 15)
        self.assertEqual(editor.y, 25)
        self.assertEqual(obj, dummy_object)
        self.assertEqual(name, "x")
        self.assertEqual(description, "description")
        self.assertEqual(parent, "parent")
