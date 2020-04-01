from nose.tools import assert_equal

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


def test_simple_override():
    editor_name, editor, ui, obj, name, description, parent = do.simple_editor(
        "ui", dummy_object, "x", "description", "parent"
    )
    assert_equal(editor_name, "simple_editor")
    assert_equal(editor.x, 15)
    assert_equal(editor.y, 25)
    assert_equal(obj, dummy_object)
    assert_equal(name, "x")
    assert_equal(description, "description")
    assert_equal(parent, "parent")


def test_text_override():
    editor_name, editor, ui, obj, name, description, parent = do.text_editor(
        "ui", dummy_object, "x", "description", "parent"
    )
    assert_equal(editor_name, "text_editor")
    assert_equal(editor.x, 15)
    assert_equal(editor.y, 25)
    assert_equal(obj, dummy_object)
    assert_equal(name, "x")
    assert_equal(description, "description")
    assert_equal(parent, "parent")


def test_custom_override():
    editor_name, editor, ui, obj, name, description, parent = do.custom_editor(
        "ui", dummy_object, "x", "description", "parent"
    )
    assert_equal(editor_name, "custom_editor")
    assert_equal(editor.x, 15)
    assert_equal(editor.y, 25)
    assert_equal(obj, dummy_object)
    assert_equal(name, "x")
    assert_equal(description, "description")
    assert_equal(parent, "parent")


def test_readonly_override():
    editor_name, editor, ui, obj, name, description, parent = do.readonly_editor(
        "ui", dummy_object, "x", "description", "parent"
    )
    assert_equal(editor_name, "readonly_editor")
    assert_equal(editor.x, 15)
    assert_equal(editor.y, 25)
    assert_equal(obj, dummy_object)
    assert_equal(name, "x")
    assert_equal(description, "description")
    assert_equal(parent, "parent")
