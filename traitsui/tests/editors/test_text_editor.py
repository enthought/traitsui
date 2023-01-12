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

from packaging.version import Version

from traits import __version__ as TRAITS_VERSION
from traits.api import (
    HasTraits,
    Str,
)
from traits.testing.api import UnittestTools
from traitsui.api import TextEditor, View, Item
from traitsui.testing.api import (
    DisplayedText,
    KeyClick,
    KeySequence,
    MouseClick,
    InteractionNotSupported,
    UITester,
)
from traitsui.tests._tools import (
    BaseTestMixin,
    GuiTestAssistant,
    no_gui_test_assistant,
    requires_toolkit,
    ToolkitName,
)


class Foo(HasTraits):

    name = Str()

    nickname = Str()


def get_view(style, auto_set):
    """Return the default view for the Foo object.

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
class TestTextEditorQt(
    BaseTestMixin, GuiTestAssistant, UnittestTools, unittest.TestCase
):
    """Test on TextEditor with Qt backend."""

    def setUp(self):
        BaseTestMixin.setUp(self)
        GuiTestAssistant.setUp(self)

    def tearDown(self):
        GuiTestAssistant.tearDown(self)
        BaseTestMixin.tearDown(self)

    def test_text_editor_placeholder_text(self):
        foo = Foo()
        editor = TextEditor(
            placeholder="Enter name",
        )
        view = View(Item(name="name", editor=editor))

        tester = UITester()
        with tester.create_ui(foo, dict(view=view)) as ui:
            (name_editor,) = ui.get_editors("name")
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
            (name_editor,) = ui.get_editors("name")
            self.assertEqual(
                name_editor.control.placeholderText(),
                "Enter name",
            )

    def test_text_editor_default_view(self):
        foo = Foo()
        tester = UITester()
        with tester.create_ui(foo) as ui:
            (name_editor,) = ui.get_editors("name")
            self.assertEqual(
                name_editor.control.placeholderText(),
                "",
            )

    def test_text_editor_custom_style_placeholder(self):
        # Test against CustomEditor using QTextEdit
        foo = Foo()
        view = View(
            Item(
                name="name",
                style="custom",
                editor=TextEditor(placeholder="Enter name"),
            )
        )
        tester = UITester()
        with tester.create_ui(foo, dict(view=view)) as ui:
            (name_editor,) = ui.get_editors("name")
            try:
                placeholder = name_editor.control.placeholderText()
            except AttributeError:
                # placeholderText is introduced to QTextEdit since Qt 5.2
                pass
            else:
                self.assertEqual(placeholder, "Enter name")

    def test_cancel_button(self):
        foo = Foo()
        view = View(
            Item(
                name="name",
                style="simple",
                editor=TextEditor(cancel_button=True),
            )
        )
        tester = UITester()
        with tester.create_ui(foo, dict(view=view)) as ui:
            (name_editor,) = ui.get_editors("name")
            # isClearButtonEnabled is introduced to QLineEdit since Qt 5.2
            if hasattr(name_editor.control, 'isClearButtonEnabled'):
                self.assertTrue(name_editor.control.isClearButtonEnabled())


# We should be able to run this test case against wx.
# Not running them now to avoid test interaction. See enthought/traitsui#752
@requires_toolkit([ToolkitName.qt, ToolkitName.wx])
class TestTextEditor(BaseTestMixin, unittest.TestCase, UnittestTools):
    """Tests that can be run with any toolkit as long as there is an
    implementation for simulating user interactions.
    """

    def setUp(self):
        BaseTestMixin.setUp(self)

    def tearDown(self):
        BaseTestMixin.tearDown(self)

    def check_editor_init_and_dispose(self, style, auto_set):
        # Smoke test to test setup and tear down of an editor.
        foo = Foo()
        view = get_view(style=style, auto_set=auto_set)
        with UITester().create_ui(foo, dict(view=view)):
            pass

    def test_simple_editor_init_and_dispose(self):
        # Smoke test to test setup and tear down of an editor.
        self.check_editor_init_and_dispose(style="simple", auto_set=True)

    def test_custom_editor_init_and_dispose(self):
        # Smoke test to test setup and tear down of an editor.
        self.check_editor_init_and_dispose(style="custom", auto_set=True)

    def test_readonly_editor_init_and_dispose(self):
        # Smoke test to test setup and tear down of an editor.
        self.check_editor_init_and_dispose(style="readonly", auto_set=True)

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
                name_field = tester.find_by_name(ui, "name")
                name_field.perform(KeySequence("NEW"))
                # with auto-set the displayed name should match the name trait
            display_name = name_field.inspect(DisplayedText())
            self.assertEqual(foo.name, "NEW")
            self.assertEqual(display_name, foo.name)

    # Currently if auto_set is false, and enter_set is false (the default
    # behavior), on Qt to ensure the text is actually set, Enter will set
    # the value
    @requires_toolkit([ToolkitName.qt])
    def test_simple_auto_set_false_do_not_update_qt(self):
        foo = Foo(name="")
        view = get_view(style="simple", auto_set=False)
        tester = UITester()
        with tester.create_ui(foo, dict(view=view)) as ui:
            name_field = tester.find_by_name(ui, "name")
            name_field.perform(KeySequence("NEW"))
            # with auto-set as False the displayed name should match what has
            # been typed not the trait itself, After "Enter" is pressed it
            # should match the name trait
            display_name = name_field.inspect(DisplayedText())
            self.assertEqual(foo.name, "")
            self.assertEqual(display_name, "NEW")
            name_field.perform(KeyClick("Enter"))
            display_name = name_field.inspect(DisplayedText())
            self.assertEqual(foo.name, "NEW")
            self.assertEqual(display_name, foo.name)

    # If auto_set is false, the value can be set by killing the focus. This
    # can be done by simply moving to another textbox.
    @requires_toolkit([ToolkitName.wx])
    def test_simple_auto_set_false_do_not_update_wx(self):
        foo = Foo(name="")
        view = View(
            Item("name", editor=TextEditor(auto_set=False), style="simple"),
            Item(
                "nickname", editor=TextEditor(auto_set=False), style="simple"
            ),
        )
        tester = UITester()
        with tester.create_ui(foo, dict(view=view)) as ui:
            name_field = tester.find_by_name(ui, "name")
            name_field.perform(KeySequence("NEW"))
            # with auto-set as False the displayed name should match what has
            # been typed not the trait itself, After moving to another textbox
            # it should match the name trait
            display_name = name_field.inspect(DisplayedText())
            self.assertEqual(foo.name, "")
            self.assertEqual(display_name, "NEW")
            tester.find_by_name(ui, "nickname").perform(MouseClick())
            display_name = name_field.inspect(DisplayedText())
            self.assertEqual(foo.name, "NEW")
            self.assertEqual(display_name, foo.name)

    def test_custom_auto_set_true_update_text(self):
        # the auto_set flag is disregard for custom editor.  (not true on WX)
        foo = Foo()
        view = get_view(auto_set=True, style="custom")
        tester = UITester()
        with tester.create_ui(foo, dict(view=view)) as ui:
            with self.assertTraitChanges(foo, "name", count=3):
                name_field = tester.find_by_name(ui, "name")
                name_field.perform(KeySequence("NEW"))
            # with auto-set the displayed name should match the name trait
            display_name = name_field.inspect(DisplayedText())
            self.assertEqual(foo.name, "NEW")
            self.assertEqual(display_name, foo.name)

    @requires_toolkit([ToolkitName.qt])
    def test_custom_auto_set_false_update_text(self):
        # the auto_set flag is disregard for custom editor. (not true on WX)
        foo = Foo()
        view = get_view(auto_set=False, style="custom")
        tester = UITester()
        with tester.create_ui(foo, dict(view=view)) as ui:
            name_field = tester.find_by_name(ui, "name")
            name_field.perform(KeySequence("NEW"))
            name_field.perform(KeyClick("Enter"))
            display_name = name_field.inspect(DisplayedText())
            self.assertEqual(foo.name, "NEW\n")
            self.assertEqual(display_name, foo.name)

    # If auto_set is false, the value can be set by killing the focus. This
    # can be done by simply moving to another textbox.
    @requires_toolkit([ToolkitName.wx])
    def test_custom_auto_set_false_do_not_update_wx(self):
        foo = Foo(name="")
        view = View(
            Item("name", editor=TextEditor(auto_set=False), style="custom"),
            Item(
                "nickname", editor=TextEditor(auto_set=False), style="custom"
            ),
        )
        tester = UITester()
        with tester.create_ui(foo, dict(view=view)) as ui:
            name_field = tester.find_by_name(ui, "name")
            name_field.perform(KeySequence("NEW"))
            # with auto-set as False the displayed name should match what has
            # been typed not the trait itself, After moving to another textbox
            # it should match the name trait
            display_name = name_field.inspect(DisplayedText())
            self.assertEqual(foo.name, "")
            self.assertEqual(display_name, "NEW")
            tester.find_by_name(ui, "nickname").perform(MouseClick())
            display_name = name_field.inspect(DisplayedText())
            self.assertEqual(foo.name, "NEW")
            self.assertEqual(display_name, foo.name)

    def test_readonly_editor(self):
        foo = Foo(name="A name")
        view = get_view(style="readonly", auto_set=True)
        tester = UITester()
        with tester.create_ui(foo, dict(view=view)) as ui:
            name_field = tester.find_by_name(ui, "name")
            with self.assertRaises(InteractionNotSupported):
                name_field.perform(KeySequence("NEW"))
            # Trying to type should do nothing
            with self.assertRaises(InteractionNotSupported):
                name_field.perform(KeyClick("Space"))
            display_name = name_field.inspect(DisplayedText())
            self.assertEqual(display_name, "A name")

    def check_format_func_used(self, style):
        # Regression test for enthought/traitsui#790
        # The test will fail with traits < 6.1.0 because the bug
        # is fixed in traits, see enthought/traitsui#980 for moving those
        # relevant code to traitsui.
        foo = Foo(name="william", nickname="bill")
        view = View(
            Item("name", format_func=lambda s: s.upper(), style=style),
            Item("nickname", style=style),
        )
        tester = UITester()
        with tester.create_ui(foo, dict(view=view)) as ui:
            display_name = tester.find_by_name(ui, "name").inspect(
                DisplayedText()
            )
            display_nickname = tester.find_by_name(ui, "nickname").inspect(
                DisplayedText()
            )
            self.assertEqual(display_name, "WILLIAM")
            self.assertEqual(display_nickname, "bill")

    @unittest.skipUnless(
        Version(TRAITS_VERSION) >= Version("6.1.0"),
        "This test requires traits >= 6.1.0",
    )
    def test_format_func_used_simple(self):
        self.check_format_func_used(style='simple')

    @unittest.skipUnless(
        Version(TRAITS_VERSION) >= Version("6.1.0"),
        "This test requires traits >= 6.1.0",
    )
    def test_format_func_used_custom(self):
        self.check_format_func_used(style='custom')

    @unittest.skipUnless(
        Version(TRAITS_VERSION) >= Version("6.1.0"),
        "This test requires traits >= 6.1.0",
    )
    def test_format_func_used_readonly(self):
        self.check_format_func_used(style='readonly')
