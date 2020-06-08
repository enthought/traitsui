# ------------------------------------------------------------------------------
#
#  Copyright (c) 2020, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
# ------------------------------------------------------------------------------
import contextlib
import unittest

from pyface.api import GUI

from traits.api import (
    HasTraits,
    Str,
)
from traitsui.api import TextEditor, View, Item
from traitsui.tests._tools import (
    create_ui,
    GuiTestAssistant,
    is_current_backend_qt4,
    skip_if_not_qt4,
    no_gui_test_assistant,
)


class Foo(HasTraits):

    name = Str()


@contextlib.contextmanager
def launch_ui(gui_test_case, object, view):
    ui = object.edit_traits(view=view)
    try:
        yield ui
    finally:
        with gui_test_case.delete_widget(ui.control):
            ui.dispose()


def get_view(style, auto_set):
    """ Return the default view for the Foo object.

    Parameters
    ----------
    style : str
        e.g. 'simple', or 'custom'
    auto_set : bool
        To be passed directly to the editor factory.
    """
    return View(
        Item("name", editor=TextEditor(auto_set=auto_set), style=style)
    )


def set_text(editor, text):
    """ Imitate user changing the text on the text box to a new value. Note
    that this is equivalent to "clear and insert", which excludes confirmation
    via pressing a return key or causing the widget to lose focus.
    """

    if is_current_backend_qt4():
        from pyface.qt import QtGui
        control = editor.control
        if editor.base_style == QtGui.QLineEdit:
            editor.control.clear()
            editor.control.insert(text)
            editor.control.textEdited.emit(text)
        else:
            editor.control.setText(text)
            editor.control.textChanged.emit()
    else:
        raise unittest.SkipTest("Not implemented for the current toolkit.")


def key_press_return(editor):
    """ Imitate user confirming the text by pressing the return key.
    """
    if is_current_backend_qt4():
        from pyface.qt import QtGui
        control = editor.control

        # ideally we should fire keyPressEvent, but the editor does not
        # bind to this event. Pressing return key will fire editingFinished
        # event on a QLineEdit
        if editor.base_style == QtGui.QLineEdit:
            control.editingFinished.emit()
        else:
            editor.control.append("")
    else:
        raise unittest.SkipTest("Not implemented for the current toolkit.")


# Skips tests if the backend is not either qt4 or qt5
@skip_if_not_qt4
@unittest.skipIf(no_gui_test_assistant, "No GuiTestAssistant")
class TestTextEditorQt(GuiTestAssistant, unittest.TestCase):
    """ Test on TextEditor with Qt backend."""

    def test_text_editor_placeholder_text(self):
        foo = Foo()
        editor = TextEditor(
            placeholder="Enter name",
        )
        view = View(Item(name="name", editor=editor))
        with launch_ui(self, object=foo, view=view) as ui:
            name_editor, = ui.get_editors("name")
            self.assertEqual(
                name_editor.control.placeholderText(),
                "Enter name",
            )

    def test_text_editor_placeholder_text_and_readonly(self):
        # Placeholder can be set independently of read_only flag
        foo = Foo()
        editor = TextEditor(
            placeholder="Enter name",
            read_only=True,
        )
        view = View(Item(name="name", editor=editor))
        with launch_ui(self, object=foo, view=view) as ui:
            name_editor, = ui.get_editors("name")
            self.assertEqual(
                name_editor.control.placeholderText(),
                "Enter name",
            )

    def test_text_editor_default_view(self):
        foo = Foo()
        with launch_ui(self, object=foo, view=None) as ui:
            name_editor, = ui.get_editors("name")
            self.assertEqual(
                name_editor.control.placeholderText(),
                "",
            )

    def test_text_editor_custom_style_placeholder(self):
        # Test against CustomEditor using QTextEdit
        foo = Foo()
        view = View(Item(
            name="name",
            style="custom",
            editor=TextEditor(placeholder="Enter name"),
        ))
        with launch_ui(self, object=foo, view=view) as ui:
            name_editor, = ui.get_editors("name")
            try:
                placeholder = name_editor.control.placeholderText()
            except AttributeError:
                # placeholderText is introduced to QTextEdit since Qt 5.2
                pass
            else:
                self.assertEqual(placeholder, "Enter name")

    def check_editor_init_and_dispose(self, style, auto_set):
        # Smoke test to test setup and tear down of an editor.
        # This test can be pull out to become toolkit-agnostic once
        # wx TextEditor also implements dispose.
        foo = Foo()
        view = get_view(style=style, auto_set=auto_set)
        with create_ui(foo, dict(view=view)):
            pass

    def test_simple_editor_init_and_dispose(self):
        # Smoke test to test setup and tear down of an editor.
        self.check_editor_init_and_dispose(style="simple", auto_set=True)

    def test_custom_editor_init_and_dispose(self):
        # Smoke test to test setup and tear down of an editor.
        self.check_editor_init_and_dispose(style="custom", auto_set=True)

    def test_simple_editor_init_and_dispose_no_auto_set(self):
        # Smoke test to test setup and tear down of an editor.
        self.check_editor_init_and_dispose(style="simple", auto_set=False)

    def test_custom_editor_init_and_dispose_no_auto_set(self):
        # Smoke test to test setup and tear down of an editor.
        self.check_editor_init_and_dispose(style="custom", auto_set=False)

    def test_simple_auto_set_update_text(self):
        foo = Foo()
        view = get_view(style="simple", auto_set=True)
        gui = GUI()
        with create_ui(foo, dict(view=view)) as ui:
            editor, = ui.get_editors("name")
            set_text(editor, "NEW")
            gui.process_events()

            self.assertEqual(foo.name, "NEW")

    def test_simple_auto_set_false_do_not_update(self):
        foo = Foo(name="")
        view = get_view(style="simple", auto_set=False)
        gui = GUI()
        with create_ui(foo, dict(view=view)) as ui:
            editor, = ui.get_editors("name")

            set_text(editor, "NEW")
            gui.process_events()

            self.assertEqual(foo.name, "")

            key_press_return(editor)
            gui.process_events()

            self.assertEqual(foo.name, "NEW")

    def test_custom_auto_set_true_update_text(self):
        # the auto_set flag is disregard for custom editor.
        foo = Foo()
        view = get_view(auto_set=True, style="custom")
        gui = GUI()
        with create_ui(foo, dict(view=view)) as ui:
            editor, = ui.get_editors("name")

            set_text(editor, "NEW")
            gui.process_events()

            self.assertEqual(foo.name, "NEW")

    def test_custom_auto_set_false_update_text(self):
        # the auto_set flag is disregard for custom editor.
        foo = Foo()
        view = get_view(auto_set=False, style="custom")
        gui = GUI()
        with create_ui(foo, dict(view=view)) as ui:
            editor, = ui.get_editors("name")

            set_text(editor, "NEW")
            gui.process_events()

            key_press_return(editor)
            gui.process_events()

            self.assertEqual(foo.name, "NEW\n")
