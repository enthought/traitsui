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

from packaging.version import Version

from traits import __version__ as TRAITS_VERSION
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
    store_exceptions_on_all_threads,
    no_gui_test_assistant,
)


class Foo(HasTraits):

    name = Str()

    nickname = Str()


@contextlib.contextmanager
def launch_ui(gui_test_case, object, view):
    ui = object.edit_traits(view=view)
    try:
        yield ui
    finally:
        with gui_test_case.delete_widget(ui.control):
            ui.dispose()


def get_text(editor):
    """ Return the text from the widget for checking.
    """
    if is_current_backend_qt4():
        return editor.control.text()
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

    @unittest.skipUnless(
        Version(TRAITS_VERSION) >= Version("6.1.0"),
        "This test requires traits >= 6.1.0"
    )
    def test_format_func_used(self):
        # Regression test for enthought/traitsui#790
        # The test will fail with traits < 6.1.0 because the bug
        # is fixed in traits, see enthought/traitsui#980 for moving those
        # relevant code to traitsui.
        foo = Foo(name="william", nickname="bill")
        view = View(
            Item("name", format_func=lambda s: s.upper()),
            Item("nickname"),
        )
        with store_exceptions_on_all_threads(), \
                create_ui(foo, dict(view=view)) as ui:
            name_editor, = ui.get_editors("name")
            nickname_editor, = ui.get_editors("nickname")
            self.assertEqual(get_text(name_editor), "WILLIAM")
            self.assertEqual(get_text(nickname_editor), "bill")
