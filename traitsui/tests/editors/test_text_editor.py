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

from traits.api import (
    HasTraits,
    Str,
)
from traitsui.api import TextEditor, View, Item
from traitsui.tests._tools import (
    GuiTestAssistant,
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
