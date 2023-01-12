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

from traits.api import HasTraits, List, Str
from traitsui.api import CheckListEditor, UItem, View
from traitsui.tests._tools import (
    BaseTestMixin,
    create_ui,
    get_all_button_status,
    is_qt,
    is_wx,
    process_cascade_events,
    requires_toolkit,
    reraise_exceptions,
    ToolkitName,
)
from traitsui.testing.api import Index, MouseClick, UITester


class ListModel(HasTraits):

    value = List()


def get_view(style):
    return View(
        UItem(
            "value",
            editor=CheckListEditor(
                values=["one", "two", "three", "four"],
            ),
            style=style,
        ),
        resizable=True,
    )


def get_view_custom_cols(cols):
    return View(
        UItem(
            "value",
            editor=CheckListEditor(
                values=["one", "two", "three", "four", "five", "six", "seven"],
                cols=cols,
            ),
            style="custom",
        ),
        resizable=True,
    )


def get_mapped_view(style):
    return View(
        UItem(
            "value",
            editor=CheckListEditor(
                values=[(1, "one"), (2, "two"), (3, "three"), (4, "four")],
            ),
            style=style,
        ),
        resizable=True,
    )


def get_combobox_text(combobox):
    """Return the text given a combobox control."""
    if is_wx():
        return combobox.GetString(combobox.GetSelection())

    elif is_qt():
        return combobox.currentText()

    else:
        raise unittest.SkipTest("Test not implemented for this toolkit")


def set_combobox_index(editor, idx):
    """Set the choice index of a combobox control given editor and index
    number."""
    if is_wx():
        import wx

        choice = editor.control
        choice.SetSelection(idx)
        event = wx.CommandEvent(wx.EVT_CHOICE.typeId, choice.GetId())
        event.SetString(choice.GetString(idx))
        wx.PostEvent(choice, event)

    elif is_qt():
        # Cannot initiate update programatically because of `activated`
        # event. At least check that it updates as expected when done
        # manually
        editor.update_object(idx)

    else:
        raise unittest.SkipTest("Test not implemented for this toolkit")


def set_text_in_line_edit(line_edit, text):
    """Set text in text widget and complete editing."""
    if is_wx():
        import wx

        line_edit.SetValue(text)
        event = wx.CommandEvent(wx.EVT_TEXT_ENTER.typeId, line_edit.GetId())
        wx.PostEvent(line_edit, event)

    elif is_qt():
        line_edit.setText(text)
        line_edit.editingFinished.emit()

    else:
        raise unittest.SkipTest("Test not implemented for this toolkit")


@requires_toolkit([ToolkitName.qt, ToolkitName.wx])
class TestCheckListEditorMapping(BaseTestMixin, unittest.TestCase):
    def setUp(self):
        BaseTestMixin.setUp(self)

    def tearDown(self):
        BaseTestMixin.tearDown(self)

    @contextlib.contextmanager
    def setup_ui(self, model, view):
        with create_ui(model, dict(view=view)) as ui:
            yield ui.get_editors("value")[0]

    def check_checklist_mappings_value_change(self, style):
        check_list_editor_factory = CheckListEditor(
            values=["one", "two"],
            format_func=lambda v: v.upper(),
        )
        formatted_view = View(
            UItem(
                "value",
                editor=check_list_editor_factory,
                style=style,
            )
        )
        model = ListModel()

        with reraise_exceptions(), self.setup_ui(
            model, formatted_view
        ) as editor:

            self.assertEqual(editor.names, ["ONE", "TWO"])

            check_list_editor_factory.values = ["two", "one"]

            self.assertEqual(editor.names, ["TWO", "ONE"])

    def check_checklist_mappings_tuple_value_change(self, style):
        check_list_editor_factory = CheckListEditor(
            values=[(1, "one"), (2, "two")],
            format_func=lambda t: t[1].upper(),
        )
        formatted_view = View(
            UItem(
                "value",
                editor=check_list_editor_factory,
                style=style,
            )
        )
        model = ListModel()

        with reraise_exceptions(), self.setup_ui(
            model, formatted_view
        ) as editor:

            # FIXME issue enthought/traitsui#841
            with self.assertRaises(AssertionError):
                self.assertEqual(editor.names, ["ONE", "TWO"])
            self.assertEqual(editor.names, ["one", "two"])

            check_list_editor_factory.values = [(2, "two"), (1, "one")]

            # FIXME issue enthought/traitsui#841
            with self.assertRaises(AssertionError):
                self.assertEqual(editor.names, ["TWO", "ONE"])
            self.assertEqual(editor.names, ["two", "one"])

    def check_checklist_mappings_name_change(self, style):
        class ListModel(HasTraits):
            value = List()
            possible_values = List(["one", "two"])

        check_list_editor_factory = CheckListEditor(
            name="object.possible_values",
            format_func=lambda v: v.upper(),
        )
        formatted_view = View(
            UItem(
                "value",
                editor=check_list_editor_factory,
                style=style,
            )
        )
        model = ListModel()

        with reraise_exceptions(), self.setup_ui(
            model, formatted_view
        ) as editor:

            self.assertEqual(editor.names, ["ONE", "TWO"])

            model.possible_values = ["two", "one"]

            self.assertEqual(editor.names, ["TWO", "ONE"])

    def check_checklist_mappings_tuple_name_change(self, style):
        class ListModel(HasTraits):
            value = List()
            possible_values = List([(1, "one"), (2, "two")])

        check_list_editor_factory = CheckListEditor(
            name="object.possible_values",
            format_func=lambda t: t[1].upper(),
        )
        formatted_view = View(
            UItem(
                "value",
                editor=check_list_editor_factory,
                style=style,
            )
        )
        model = ListModel()

        with reraise_exceptions(), self.setup_ui(
            model, formatted_view
        ) as editor:

            # FIXME issue enthought/traitsui#841
            with self.assertRaises(AssertionError):
                self.assertEqual(editor.names, ["ONE", "TWO"])
            self.assertEqual(editor.names, ["one", "two"])

            model.possible_values = [(2, "two"), (1, "one")]

            # FIXME issue enthought/traitsui#841
            with self.assertRaises(AssertionError):
                self.assertEqual(editor.names, ["TWO", "ONE"])
            self.assertEqual(editor.names, ["two", "one"])

    def check_checklist_values_change_after_ui_dispose(self, style):
        # Check the available values can change after the ui is closed

        class ListModel(HasTraits):
            value = List()
            possible_values = List(["one", "two"])

        check_list_editor_factory = CheckListEditor(
            name="object.possible_values",
        )
        view = View(
            UItem(
                "value",
                editor=check_list_editor_factory,
                style=style,
            )
        )
        model = ListModel()

        with reraise_exceptions():
            with create_ui(model, dict(view=view)):
                pass

            model.possible_values = ["two", "one"]

    def test_simple_editor_mapping_values(self):
        self.check_checklist_mappings_value_change("simple")

    def test_simple_editor_mapping_values_tuple(self):
        self.check_checklist_mappings_tuple_value_change("simple")

    def test_simple_editor_mapping_name(self):
        self.check_checklist_mappings_name_change("simple")

    def test_simple_editor_mapping_name_tuple(self):
        self.check_checklist_mappings_tuple_name_change("simple")

    def test_custom_editor_mapping_values(self):
        # FIXME issue enthought/traitsui#842
        if is_wx():
            import wx

            with self.assertRaises(wx._core.wxAssertionError):
                self.check_checklist_mappings_value_change("custom")
        else:
            self.check_checklist_mappings_value_change("custom")

    def test_custom_editor_mapping_values_tuple(self):
        # FIXME issue enthought/traitsui#842
        if is_wx():
            import wx

            with self.assertRaises(wx._core.wxAssertionError):
                self.check_checklist_mappings_tuple_value_change("custom")
        else:
            self.check_checklist_mappings_tuple_value_change("custom")

    def test_custom_editor_mapping_name(self):
        # FIXME issue enthought/traitsui#842
        if is_wx():
            import wx

            with self.assertRaises(wx._core.wxAssertionError):
                self.check_checklist_mappings_name_change("custom")
        else:
            self.check_checklist_mappings_name_change("custom")

    def test_custom_editor_mapping_name_tuple(self):
        # FIXME issue enthought/traitsui#842
        if is_wx():
            import wx

            with self.assertRaises(wx._core.wxAssertionError):
                self.check_checklist_mappings_tuple_name_change("custom")
        else:
            self.check_checklist_mappings_tuple_name_change("custom")

    def test_simple_editor_checklist_values_change_dispose(self):
        self.check_checklist_values_change_after_ui_dispose("simple")

    def test_custom_editor_checklist_values_change_dispose(self):
        self.check_checklist_values_change_after_ui_dispose("custom")


@requires_toolkit([ToolkitName.qt, ToolkitName.wx])
class TestSimpleCheckListEditor(BaseTestMixin, unittest.TestCase):
    def setUp(self):
        BaseTestMixin.setUp(self)

    def tearDown(self):
        BaseTestMixin.tearDown(self)

    @contextlib.contextmanager
    def setup_gui(self, model, view):
        with create_ui(model, dict(view=view)) as ui:
            process_cascade_events()
            editor = ui.get_editors("value")[0]
            yield editor

    def test_simple_check_list_editor_text(self):
        list_edit = ListModel(value=["one"])

        with reraise_exceptions(), self.setup_gui(
            list_edit, get_view("simple")
        ) as editor:

            self.assertEqual(get_combobox_text(editor.control), "One")

            list_edit.value = ["two"]
            process_cascade_events()

            self.assertEqual(get_combobox_text(editor.control), "Two")

    def test_simple_check_list_editor_text_mapped(self):
        view = get_mapped_view("simple")
        list_edit = ListModel(value=[1])

        with reraise_exceptions(), self.setup_gui(list_edit, view) as editor:

            # FIXME issue enthought/traitsui#841
            with self.assertRaises(AssertionError):
                self.assertEqual(get_combobox_text(editor.control), "One")
            self.assertEqual(get_combobox_text(editor.control), "one")

            list_edit.value = [2]
            process_cascade_events()

            # FIXME issue enthought/traitsui#841
            with self.assertRaises(AssertionError):
                self.assertEqual(get_combobox_text(editor.control), "Two")
            self.assertEqual(get_combobox_text(editor.control), "two")

    def test_simple_check_list_editor_index(self):
        list_edit = ListModel(value=["one"])

        with reraise_exceptions(), self.setup_gui(
            list_edit, get_view("simple")
        ) as editor:

            self.assertEqual(list_edit.value, ["one"])

            set_combobox_index(editor, 1)
            process_cascade_events()

            self.assertEqual(list_edit.value, ["two"])

            set_combobox_index(editor, 0)
            process_cascade_events()

            self.assertEqual(list_edit.value, ["one"])

    def test_simple_check_list_editor_invalid_current_values(self):
        list_edit = ListModel(value=[1, "two", "a", object(), "one"])

        with reraise_exceptions(), self.setup_gui(
            list_edit, get_view("simple")
        ):

            self.assertEqual(list_edit.value, ["two", "one"])

    def test_simple_check_list_editor_invalid_current_values_str(self):
        class StrModel(HasTraits):
            value = Str()

        str_edit = StrModel(value="alpha, \ttwo, beta,\n lambda, one")

        with reraise_exceptions(), self.setup_gui(
            str_edit, get_view("simple")
        ):

            self.assertEqual(str_edit.value, "two,one")


@requires_toolkit([ToolkitName.qt, ToolkitName.wx])
class TestCustomCheckListEditor(BaseTestMixin, unittest.TestCase):
    def setUp(self):
        BaseTestMixin.setUp(self)

    def tearDown(self):
        BaseTestMixin.tearDown(self)

    @contextlib.contextmanager
    def setup_gui(self, model, view):
        with create_ui(model, dict(view=view)) as ui:
            process_cascade_events()
            editor = ui.get_editors("value")[0]
            yield editor

    def test_custom_check_list_editor_button_update(self):
        list_edit = ListModel()

        with reraise_exceptions(), self.setup_gui(
            list_edit, get_view("custom")
        ) as editor:

            self.assertEqual(
                get_all_button_status(editor.control),
                [False, False, False, False],
            )

            list_edit.value = ["two", "four"]
            process_cascade_events()

            self.assertEqual(
                get_all_button_status(editor.control),
                [False, True, False, True],
            )

            list_edit.value = ["one", "four"]
            process_cascade_events()

            self.assertEqual(
                get_all_button_status(editor.control),
                [True, False, False, True],
            )

    def test_custom_check_list_editor_click(self):
        list_edit = ListModel()

        tester = UITester()
        with tester.create_ui(list_edit, dict(view=get_view("custom"))) as ui:
            self.assertEqual(list_edit.value, [])
            check_list = tester.find_by_name(ui, "value")
            item_1 = check_list.locate(Index(1))
            item_1.perform(MouseClick())
            self.assertEqual(list_edit.value, ["two"])
            item_1.perform(MouseClick())
            self.assertEqual(list_edit.value, [])

    def test_custom_check_list_editor_click_initial_value(self):
        list_edit = ListModel(value=["two"])

        tester = UITester()
        with tester.create_ui(list_edit, dict(view=get_view("custom"))) as ui:
            self.assertEqual(list_edit.value, ["two"])

            check_list = tester.find_by_name(ui, "value")
            item_1 = check_list.locate(Index(1))
            item_1.perform(MouseClick())

            self.assertEqual(list_edit.value, [])

    def test_custom_check_list_editor_invalid_current_values_str(self):
        class StrModel(HasTraits):
            value = Str()

        str_edit = StrModel(value="alpha, \ttwo, three,\n lambda, one")

        tester = UITester()
        with tester.create_ui(str_edit, dict(view=get_view("custom"))) as ui:

            self.assertEqual(str_edit.value, "two,three,one")

            check_list = tester.find_by_name(ui, "value")
            item_1 = check_list.locate(Index(1))
            item_1.perform(MouseClick())

            self.assertEqual(str_edit.value, "three,one")

    def test_custom_check_list_editor_grid_layout(self):
        for cols in range(1, 8):
            list_edit = ListModel()
            tester = UITester()
            view = get_view_custom_cols(cols=cols)
            with tester.create_ui(list_edit, dict(view=view)) as ui:
                self.assertEqual(list_edit.value, [])
                check_list = tester.find_by_name(ui, "value")
                item = check_list.locate(Index(6))
                item.perform(MouseClick())
                self.assertEqual(list_edit.value, ["seven"])
                item.perform(MouseClick())
                self.assertEqual(list_edit.value, [])


@requires_toolkit([ToolkitName.qt, ToolkitName.wx])
class TestTextCheckListEditor(BaseTestMixin, unittest.TestCase):
    def setUp(self):
        BaseTestMixin.setUp(self)

    def tearDown(self):
        BaseTestMixin.tearDown(self)

    @contextlib.contextmanager
    def setup_gui(self, model, view):
        with create_ui(model, dict(view=view)) as ui:

            process_cascade_events()
            editor = ui.get_editors("value")[0]
            yield editor

    def test_text_check_list_object_list(self):
        list_edit = ListModel()

        with reraise_exceptions(), self.setup_gui(
            list_edit, get_view("text")
        ) as editor:

            self.assertEqual(list_edit.value, [])

            set_text_in_line_edit(editor.control, "['one', 'two']")
            process_cascade_events()

            self.assertEqual(list_edit.value, ["one", "two"])

    def test_text_check_list_object_str(self):
        class StrModel(HasTraits):
            value = Str()

        str_edit = StrModel(value="three, four")

        with reraise_exceptions(), self.setup_gui(
            str_edit, get_view("text")
        ) as editor:

            self.assertEqual(str_edit.value, "three, four")

            set_text_in_line_edit(editor.control, "one, two")
            process_cascade_events()

            self.assertEqual(str_edit.value, "one, two")
