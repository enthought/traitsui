# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import contextlib
import unittest

from traits.api import Enum, HasTraits, Int, List
from traitsui.api import EnumEditor, UItem, View
from traitsui.tests._tools import (
    BaseTestMixin,
    create_ui,
    is_qt,
    is_wx,
    requires_toolkit,
    reraise_exceptions,
    ToolkitName,
)
from traitsui.testing.api import (
    Disabled,
    DisplayedText,
    Index,
    IsEnabled,
    KeyClick,
    KeySequence,
    MouseClick,
    SelectedText,
    UITester,
)


class EnumModel(HasTraits):

    value = Enum("one", "two", "three", "four")


class EnumModelWithNone(HasTraits):

    value = Enum(None, "one", "two", "three", "four")


def get_view(style):
    return View(UItem("value", style=style), resizable=True)


def get_evaluate_view(style, auto_set=True, mode="radio"):
    return View(
        UItem(
            "value",
            editor=EnumEditor(
                evaluate=True,
                values=["one", "two", "three", "four"],
                auto_set=auto_set,
                mode=mode,
            ),
            style=style,
        ),
        resizable=True,
    )


def get_radio_view(cols=1):
    return View(
        UItem(
            "value",
            editor=EnumEditor(
                values=["one", "two", "three", "four"],
                cols=cols,
                mode="radio",
            ),
            style="custom",
        ),
        resizable=True,
    )


@requires_toolkit([ToolkitName.qt, ToolkitName.wx])
class TestEnumEditorMapping(BaseTestMixin, unittest.TestCase):
    def setUp(self):
        BaseTestMixin.setUp(self)

    def tearDown(self):
        BaseTestMixin.tearDown(self)

    @contextlib.contextmanager
    def setup_ui(self, model, view):
        with create_ui(model, dict(view=view)) as ui:
            yield ui.get_editors("value")[0]

    def check_enum_mappings_value_change(self, style, mode):
        class IntEnumModel(HasTraits):
            value = Int()

        enum_editor_factory = EnumEditor(
            values=[0, 1],
            format_func=lambda v: str(bool(v)).upper(),
            mode=mode,
        )
        formatted_view = View(
            UItem(
                "value",
                editor=enum_editor_factory,
                style=style,
            )
        )

        with reraise_exceptions(), self.setup_ui(
            IntEnumModel(), formatted_view
        ) as editor:

            self.assertEqual(editor.names, ["FALSE", "TRUE"])
            self.assertEqual(editor.mapping, {"FALSE": 0, "TRUE": 1})
            self.assertEqual(editor.inverse_mapping, {0: "FALSE", 1: "TRUE"})

            enum_editor_factory.values = [1, 0]

            self.assertEqual(editor.names, ["TRUE", "FALSE"])
            self.assertEqual(editor.mapping, {"TRUE": 1, "FALSE": 0})
            self.assertEqual(editor.inverse_mapping, {1: "TRUE", 0: "FALSE"})

    def check_enum_mappings_name_change(self, style, mode):
        class IntEnumModel(HasTraits):
            value = Int()
            possible_values = List([0, 1])

        formatted_view = View(
            UItem(
                'value',
                editor=EnumEditor(
                    name="object.possible_values",
                    format_func=lambda v: str(bool(v)).upper(),
                    mode=mode,
                ),
                style=style,
            )
        )
        model = IntEnumModel()

        with reraise_exceptions(), self.setup_ui(
            model, formatted_view
        ) as editor:

            self.assertEqual(editor.names, ["FALSE", "TRUE"])
            self.assertEqual(editor.mapping, {"FALSE": 0, "TRUE": 1})
            self.assertEqual(editor.inverse_mapping, {0: "FALSE", 1: "TRUE"})

            model.possible_values = [1, 0]

            self.assertEqual(editor.names, ["TRUE", "FALSE"])
            self.assertEqual(editor.mapping, {"TRUE": 1, "FALSE": 0})
            self.assertEqual(editor.inverse_mapping, {1: "TRUE", 0: "FALSE"})

    def test_simple_editor_mapping_values(self):
        self.check_enum_mappings_value_change("simple", "radio")

    def test_simple_editor_mapping_name(self):
        self.check_enum_mappings_name_change("simple", "radio")

    def test_radio_editor_mapping_values(self):
        # FIXME issue enthought/traitsui#842
        if is_wx():
            import wx

            with self.assertRaises(wx._core.wxAssertionError):
                self.check_enum_mappings_value_change("custom", "radio")
        else:
            self.check_enum_mappings_value_change("custom", "radio")

    def test_radio_editor_mapping_name(self):
        # FIXME issue enthought/traitsui#842
        if is_wx():
            import wx

            with self.assertRaises(wx._core.wxAssertionError):
                self.check_enum_mappings_name_change("custom", "radio")
        else:
            self.check_enum_mappings_name_change("custom", "radio")

    def test_list_editor_mapping_values(self):
        self.check_enum_mappings_value_change("custom", "list")

    def test_list_editor_mapping_name(self):
        self.check_enum_mappings_name_change("custom", "list")


@requires_toolkit([ToolkitName.qt, ToolkitName.wx])
class TestSimpleEnumEditor(BaseTestMixin, unittest.TestCase):
    def setUp(self):
        BaseTestMixin.setUp(self)

    def tearDown(self):
        BaseTestMixin.tearDown(self)

    def check_enum_text_update(self, view):
        enum_edit = EnumModel()

        tester = UITester()
        with tester.create_ui(enum_edit, dict(view=view)) as ui:
            combobox = tester.find_by_name(ui, "value")
            displayed = combobox.inspect(DisplayedText())
            self.assertEqual(displayed, "one")

            combobox.locate(Index(1)).perform(MouseClick())
            displayed = combobox.inspect(DisplayedText())
            self.assertEqual(displayed, "two")

    def check_enum_object_update(self, view):
        enum_edit = EnumModel()

        tester = UITester()
        with tester.create_ui(enum_edit, dict(view=view)) as ui:

            self.assertEqual(enum_edit.value, "one")

            combobox = tester.find_by_name(ui, "value")
            for _ in range(3):
                combobox.perform(KeyClick("Backspace"))
            combobox.perform(KeySequence("two"))
            combobox.perform(KeyClick("Enter"))

            self.assertEqual(enum_edit.value, "two")

    def check_enum_index_update(self, view):
        enum_edit = EnumModel()
        tester = UITester()
        with tester.create_ui(enum_edit, dict(view=view)) as ui:

            self.assertEqual(enum_edit.value, "one")

            combobox = tester.find_by_name(ui, "value")
            combobox.locate(Index(1)).perform(MouseClick())

            self.assertEqual(enum_edit.value, "two")

    def check_enum_text_bad_update(self, view):
        enum_edit = EnumModel()

        tester = UITester()
        with tester.create_ui(enum_edit, dict(view=view)) as ui:

            self.assertEqual(enum_edit.value, "one")

            combobox = tester.find_by_name(ui, "value")
            for _ in range(3):
                combobox.perform(KeyClick("Backspace"))
            combobox.perform(KeyClick("H"))
            combobox.perform(KeyClick("Enter"))

            self.assertEqual(enum_edit.value, "one")

    def test_simple_enum_editor_text(self):
        self.check_enum_text_update(get_view("simple"))

    def test_simple_enum_editor_index(self):
        self.check_enum_index_update(get_view("simple"))

    def test_simple_evaluate_editor_text(self):
        self.check_enum_text_update(get_evaluate_view("simple"))

    def test_simple_evaluate_editor_index(self):
        self.check_enum_index_update(get_evaluate_view("simple"))

    def test_simple_evaluate_editor_bad_text(self):
        self.check_enum_text_bad_update(get_evaluate_view("simple"))

    def test_simple_evaluate_editor_object(self):
        self.check_enum_object_update(get_evaluate_view("simple"))

    def test_simple_evaluate_editor_object_no_auto_set(self):
        view = get_evaluate_view("simple", auto_set=False)
        enum_edit = EnumModel()

        tester = UITester()
        with tester.create_ui(enum_edit, dict(view=view)) as ui:
            self.assertEqual(enum_edit.value, "one")

            combobox = tester.find_by_name(ui, "value")
            for _ in range(3):
                combobox.perform(KeyClick("Backspace"))
            combobox.perform(KeySequence("two"))

            self.assertEqual(enum_edit.value, "one")
            combobox.perform(KeyClick("Enter"))
            self.assertEqual(enum_edit.value, "two")

    def test_simple_editor_resizable(self):
        # Smoke test for `qt.enum_editor.SimpleEditor.set_size_policy`
        enum_edit = EnumModel()
        resizable_view = View(UItem("value", style="simple", resizable=True))

        tester = UITester()
        with tester.create_ui(enum_edit, dict(view=resizable_view)):
            pass

    def test_simple_editor_rebuild_editor_evaluate(self):
        # Smoke test for `wx.enum_editor.SimpleEditor.rebuild_editor`
        enum_editor_factory = EnumEditor(
            evaluate=True,
            values=["one", "two", "three", "four"],
        )
        view = View(UItem("value", editor=enum_editor_factory, style="simple"))

        tester = UITester()
        with tester.create_ui(EnumModel(), dict(view=view)):
            enum_editor_factory.values = ["one", "two", "three"]

    def test_simple_editor_disabled(self):
        enum_edit = EnumModel(value="two")
        view = View(
            UItem(
                "value",
                style="simple",
                enabled_when="value == 'one'",
                editor=EnumEditor(evaluate=True, values=["one", "two"]),
            ),
        )
        tester = UITester()
        with tester.create_ui(enum_edit, dict(view=view)) as ui:
            combobox = tester.find_by_name(ui, "value")
            with self.assertRaises(Disabled):
                combobox.perform(KeyClick("Enter"))
            with self.assertRaises(Disabled):
                combobox.perform(KeySequence("two"))
            self.assertFalse(combobox.inspect(IsEnabled()))


@requires_toolkit([ToolkitName.qt, ToolkitName.wx])
class TestRadioEnumEditor(BaseTestMixin, unittest.TestCase):
    def setUp(self):
        BaseTestMixin.setUp(self)

    def tearDown(self):
        BaseTestMixin.tearDown(self)

    def test_radio_enum_editor_update(self):
        enum_edit = EnumModel()
        tester = UITester()

        with tester.create_ui(enum_edit, dict(view=get_view("custom"))) as ui:
            # sanity check
            self.assertEqual(enum_edit.value, "one")
            radio_editor = tester.find_by_name(ui, "value")
            self.assertEqual(
                radio_editor.inspect(SelectedText()),
                "One",
            )

            enum_edit.value = "two"

            self.assertEqual(
                radio_editor.inspect(SelectedText()),
                "Two",
            )

    def test_radio_enum_editor_pick(self):
        for cols in range(1, 4):
            for row_major in [True, False]:
                enum_edit = EnumModel()
                tester = UITester()
                view = get_radio_view(cols=cols)
                with tester.create_ui(enum_edit, dict(view=view)) as ui:
                    # sanity check
                    self.assertEqual(enum_edit.value, "one")
                    radio_editor = tester.find_by_name(ui, "value")
                    if is_qt():
                        radio_editor._target.row_major = row_major
                        radio_editor._target.rebuild_editor()
                    item = radio_editor.locate(Index(3))
                    item.perform(MouseClick())
                    self.assertEqual(enum_edit.value, "four")

    def test_radio_enum_none_selected(self):
        enum_edit = EnumModelWithNone()
        tester = UITester()
        with tester.create_ui(enum_edit, dict(view=get_radio_view())) as ui:
            self.assertEqual(enum_edit.value, None)
            radio_editor = tester.find_by_name(ui, "value")
            displayed = radio_editor.inspect(SelectedText())
            self.assertEqual(displayed, None)


@requires_toolkit([ToolkitName.qt, ToolkitName.wx])
class TestListEnumEditor(BaseTestMixin, unittest.TestCase):
    def setUp(self):
        BaseTestMixin.setUp(self)

    def tearDown(self):
        BaseTestMixin.tearDown(self)

    def check_enum_text_update(self, view):
        enum_edit = EnumModel()

        tester = UITester()
        with tester.create_ui(enum_edit, dict(view=view)) as ui:

            list_editor = tester.find_by_name(ui, "value")
            displayed = list_editor.inspect(SelectedText())

            self.assertEqual(displayed, "one")

            list_editor.locate(Index(1)).perform(MouseClick())
            displayed = list_editor.inspect(SelectedText())
            self.assertEqual(displayed, "two")

    def check_enum_index_update(self, view):
        enum_edit = EnumModel()
        tester = UITester()
        with tester.create_ui(enum_edit, dict(view=view)) as ui:

            self.assertEqual(enum_edit.value, "one")

            list_editor = tester.find_by_name(ui, "value")
            list_editor.locate(Index(1)).perform(MouseClick())

            self.assertEqual(enum_edit.value, "two")

    def test_list_enum_editor_text(self):
        view = View(
            UItem(
                "value",
                editor=EnumEditor(
                    values=["one", "two", "three", "four"],
                    mode="list",
                ),
                style="custom",
            ),
            resizable=True,
        )
        self.check_enum_text_update(view)

    def test_list_enum_editor_index(self):
        view = View(
            UItem(
                "value",
                editor=EnumEditor(
                    values=["one", "two", "three", "four"],
                    mode="list",
                ),
                style="custom",
            ),
            resizable=True,
        )
        self.check_enum_index_update(view)

    def test_list_evaluate_editor_text(self):
        self.check_enum_text_update(get_evaluate_view("custom", mode="list"))

    def test_list_evaluate_editor_index(self):
        self.check_enum_index_update(get_evaluate_view("custom", mode="list"))

    def test_list_enum_none_selected(self):
        enum_edit = EnumModelWithNone()
        view = View(
            UItem(
                "value",
                editor=EnumEditor(
                    # Note that for the list style editor, in order to select
                    # None, it must be one of the displayed options
                    values=[None, "one", "two", "three", "four"],
                    mode="list",
                ),
                style="custom",
            ),
            resizable=True,
        )
        tester = UITester()
        with tester.create_ui(enum_edit, dict(view=view)) as ui:
            self.assertEqual(enum_edit.value, None)
            list_editor = tester.find_by_name(ui, "value")
            # As a result the displayed text is actually the string 'None'
            displayed = list_editor.inspect(SelectedText())
            self.assertEqual(displayed, 'None')
