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
    pop_exception_handler,
    push_exception_handler,
)
from traits.testing.api import UnittestTools
from traitsui.api import TextEditor, View, Item
from traitsui.testing.tester.ui_tester import UITester
from traitsui.testing.tester import command, query
from traitsui.tests._tools import (
    GuiTestAssistant,
    no_gui_test_assistant,
    requires_toolkit,
    ToolkitName,
)


class Foo(HasTraits):

    name = Str()

    nickname = Str()


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


# Skips tests if the backend is not either qt4 or qt5
@requires_toolkit([ToolkitName.qt])
@unittest.skipIf(no_gui_test_assistant, "No GuiTestAssistant")
class TestTextEditorQt(GuiTestAssistant, UnittestTools, unittest.TestCase):
    """ Test on TextEditor with Qt backend."""

    def test_text_editor_placeholder_text(self):
        foo = Foo()
        editor = TextEditor(
            placeholder="Enter name",
        )
        view = View(Item(name="name", editor=editor))

        tester = UITester()
        with tester.create_ui(foo, dict(view=view)) as ui:
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
        tester = UITester()
        with tester.create_ui(foo, dict(view=view)) as ui:
            name_editor, = ui.get_editors("name")
            self.assertEqual(
                name_editor.control.placeholderText(),
                "Enter name",
            )

    def test_text_editor_default_view(self):
        foo = Foo()
        tester = UITester()
        with tester.create_ui(foo) as ui:
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
        tester = UITester()
        with tester.create_ui(foo, dict(view=view)) as ui:
            name_editor, = ui.get_editors("name")
            try:
                placeholder = name_editor.control.placeholderText()
            except AttributeError:
                # placeholderText is introduced to QTextEdit since Qt 5.2
                pass
            else:
                self.assertEqual(placeholder, "Enter name")


# We should be able to run this test case against wx.
# Not running them now to avoid test interaction. See enthought/traitsui#752
@requires_toolkit([ToolkitName.qt])
class TestTextEditor(unittest.TestCase, UnittestTools):
    """ Tests that can be run with any toolkit as long as there is an
    implementation for simulating user interactions.
    """

    def setUp(self):
        push_exception_handler(reraise_exceptions=True)
        self.addCleanup(pop_exception_handler)

    def check_editor_init_and_dispose(self, style, auto_set):
        # Smoke test to test setup and tear down of an editor.
        foo = Foo()
        view = get_view(style=style, auto_set=auto_set)
        with UITester().create_ui(foo, dict(view=view)) as ui:
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
        tester = UITester()
        with tester.create_ui(foo, dict(view=view)) as ui:
            with self.assertTraitChanges(foo, "name", count=3):
                tester.find_by_name(ui, "name").perform(command.KeySequence("NEW"))
            self.assertEqual(foo.name, "NEW")


    def test_simple_auto_set_false_do_not_update(self):
        foo = Foo(name="")
        view = get_view(style="simple", auto_set=False)
        tester = UITester()
        with tester.create_ui(foo, dict(view=view)) as ui:
            tester.find_by_name(ui, "name").perform(command.KeySequence("NEW"))
            self.assertEqual(foo.name, "")
            tester.find_by_name(ui, "name").perform(command.KeyClick("Enter"))
            self.assertEqual(foo.name, "NEW")


    def test_custom_auto_set_true_update_text(self):
        # the auto_set flag is disregard for custom editor.
        foo = Foo()
        view = get_view(auto_set=True, style="custom")
        tester = UITester()
        with tester.create_ui(foo, dict(view=view)) as ui:
            with self.assertTraitChanges(foo, "name", count=3):
                tester.find_by_name(ui, "name").perform(command.KeySequence("NEW"))
            self.assertEqual(foo.name, "NEW")


    def test_custom_auto_set_false_update_text(self):
        # the auto_set flag is disregard for custom editor.
        foo = Foo()
        view = get_view(auto_set=False, style="custom")
        tester = UITester()
        with tester.create_ui(foo, dict(view=view)) as ui:
            tester.find_by_name(ui, "name").perform(command.KeySequence("NEW"))
            tester.find_by_name(ui, "name").perform(command.KeyClick("Enter"))
            self.assertEqual(foo.name, "NEW\n")


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
        tester = UITester()
        with tester.create_ui(foo, dict(view=view)) as ui:
            display_name = (
                tester.find_by_name(ui, "name").inspect(query.DisplayedText())
            )
            display_nickname = (
                tester.find_by_name(ui, "nickname").inspect(query.DisplayedText())
            )
            self.assertEqual(display_name, "WILLIAM")
            self.assertEqual(display_nickname, "bill")
