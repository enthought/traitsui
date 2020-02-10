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

from pyface.ui.qt4.util.gui_test_assistant import GuiTestAssistant
from traits.api import (
    HasTraits,
    Str,
    pop_exception_handler,
    push_exception_handler,
)
from traitsui.api import TextEditor, View, Item
from traitsui.tests._tools import (
    skip_if_not_qt4,
)


class Foo(HasTraits):

    name = Str()


def default_view():
    return View(
        Item(
            name="name",
        )
    )


def view_with_placeholder():
    return View(
        Item(
            name="name",
            editor=TextEditor(text="Enter name"),
        )
    )


def view_with_readonly_and_placeholder():
    return View(
        Item(
            name="name",
            editor=TextEditor(
                text="Enter name",
                read_only=True,
            )
        )
    )


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
class TestTextEditorQt(GuiTestAssistant, unittest.TestCase):
    """ Test on TextEditor with Qt backend."""

    def test_text_editor_placeholder_text(self):
        foo = Foo()
        view = view_with_placeholder()
        with launch_ui(self, object=foo, view=view) as ui:
            name_editor, = ui.get_editors("name")
            self.assertEqual(
                name_editor.control.placeholderText(),
                "Enter name",
            )

    def test_text_editor_placeholder_text_and_readonly(self):
        # Placeholder can be set independently of read_only flag
        foo = Foo()
        view = view_with_readonly_and_placeholder()
        with launch_ui(self, object=foo, view=view) as ui:
            name_editor, = ui.get_editors("name")
            self.assertEqual(
                name_editor.control.placeholderText(),
                "Enter name",
            )

    def test_text_editor_default_view(self):
        foo = Foo()
        view = default_view()
        with launch_ui(self, object=foo, view=view) as ui:
            name_editor, = ui.get_editors("name")
            self.assertEqual(
                name_editor.control.placeholderText(),
                "",
            )
