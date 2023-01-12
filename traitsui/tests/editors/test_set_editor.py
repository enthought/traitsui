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

from traits.api import HasTraits, List
from traitsui.api import SetEditor, UItem, View
from traitsui.tests._tools import (
    BaseTestMixin,
    create_ui,
    click_button,
    is_control_enabled,
    is_qt,
    is_wx,
    process_cascade_events,
    requires_toolkit,
    reraise_exceptions,
    ToolkitName,
)


class ListModel(HasTraits):

    value = List(["one", "two"])


def get_view(can_move_all=True, ordered=False):
    return View(
        UItem(
            "value",
            editor=SetEditor(
                values=["one", "two", "three", "four"],
                ordered=ordered,
                can_move_all=can_move_all,
            ),
            style="simple",
        )
    )


def get_list_items(list_widget):
    """Return a list of strings from the list widget."""
    items = []

    if is_wx():
        for i in range(list_widget.GetCount()):
            items.append(list_widget.GetString(i))

    elif is_qt():
        for i in range(list_widget.count()):
            items.append(list_widget.item(i).text())

    else:
        raise unittest.SkipTest("Test not implemented for this toolkit")

    return items


def click_on_item(editor, item_idx, in_used=False):
    """Simulate a click on an item in a specified list.

    The function deselects all items in both used and unused lists, then
    selects an item at index item_idx either in the used list (if
    in_used=True) or in the unused list. Finally the function simulates a
    click on the selected item.
    """
    unused_list = editor._unused
    used_list = editor._used

    if is_wx():
        import wx

        # First deselect all items
        for i in range(unused_list.GetCount()):
            unused_list.Deselect(i)
        for i in range(used_list.GetCount()):
            used_list.Deselect(i)
        # Select the item in the correct list
        list_with_selection = used_list if in_used else unused_list
        list_with_selection.SetSelection(item_idx)

        event = wx.CommandEvent(
            wx.EVT_LISTBOX.typeId, list_with_selection.GetId()
        )
        wx.PostEvent(editor.control, event)

    elif is_qt():
        for i in range(unused_list.count()):
            status = (not in_used) and (item_idx == i)
            unused_list.item(i).setSelected(status)

        for i in range(used_list.count()):
            status = (in_used) and (item_idx == i)
            used_list.item(i).setSelected(status)

        if in_used:
            used_list.itemClicked.emit(used_list.item(item_idx))
        else:
            unused_list.itemClicked.emit(unused_list.item(item_idx))

    else:
        raise unittest.SkipTest("Test not implemented for this toolkit")


def double_click_on_item(editor, item_idx, in_used=False):
    """Simulate a double click on an item in a specified list.

    The function deselects all items in both used and unused lists, then
    selects an item at index item_idx either in the used list (if
    in_used=True) or in the unused list. Finally the function simulates a
    double click on the selected item.
    """
    unused_list = editor._unused
    used_list = editor._used

    if is_wx():
        import wx

        # First deselect all items
        for i in range(unused_list.GetCount()):
            unused_list.Deselect(i)
        for i in range(used_list.GetCount()):
            used_list.Deselect(i)
        # Select the item in the correct list
        list_with_selection = used_list if in_used else unused_list
        list_with_selection.SetSelection(item_idx)

        event = wx.CommandEvent(
            wx.EVT_LISTBOX_DCLICK.typeId, list_with_selection.GetId()
        )
        wx.PostEvent(editor.control, event)

    elif is_qt():
        for i in range(unused_list.count()):
            status = (not in_used) and (item_idx == i)
            unused_list.item(i).setSelected(status)

        for i in range(used_list.count()):
            status = (in_used) and (item_idx == i)
            used_list.item(i).setSelected(status)

        if in_used:
            used_list.itemDoubleClicked.emit(used_list.item(item_idx))
        else:
            unused_list.itemDoubleClicked.emit(unused_list.item(item_idx))

    else:
        raise unittest.SkipTest("Test not implemented for this toolkit")


@requires_toolkit([ToolkitName.qt, ToolkitName.wx])
class TestSetEditorMapping(BaseTestMixin, unittest.TestCase):
    def setUp(self):
        BaseTestMixin.setUp(self)

    def tearDown(self):
        BaseTestMixin.tearDown(self)

    @contextlib.contextmanager
    def setup_ui(self, model, view):
        with create_ui(model, dict(view=view)) as ui:
            yield ui.get_editors("value")[0]

    def test_simple_editor_mapping_values(self):
        class IntListModel(HasTraits):
            value = List()

        set_editor_factory = SetEditor(
            values=[0, 1], format_func=lambda v: str(bool(v)).upper()
        )
        formatted_view = View(
            UItem(
                "value",
                editor=set_editor_factory,
                style="simple",
            )
        )

        with reraise_exceptions(), self.setup_ui(
            IntListModel(), formatted_view
        ) as editor:

            self.assertEqual(editor.names, ["FALSE", "TRUE"])
            self.assertEqual(editor.mapping, {"FALSE": 0, "TRUE": 1})
            self.assertEqual(editor.inverse_mapping, {0: "FALSE", 1: "TRUE"})

            set_editor_factory.values = [1, 0]

            self.assertEqual(editor.names, ["TRUE", "FALSE"])
            self.assertEqual(editor.mapping, {"TRUE": 1, "FALSE": 0})
            self.assertEqual(editor.inverse_mapping, {1: "TRUE", 0: "FALSE"})

    def test_simple_editor_mapping_name(self):
        class IntListModel(HasTraits):
            value = List()
            possible_values = List([0, 1])

        formatted_view = View(
            UItem(
                'value',
                editor=SetEditor(
                    name="object.possible_values",
                    format_func=lambda v: str(bool(v)).upper(),
                ),
                style="simple",
            )
        )
        model = IntListModel()

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


@requires_toolkit([ToolkitName.qt, ToolkitName.wx])
class TestSimpleSetEditor(BaseTestMixin, unittest.TestCase):
    def setUp(self):
        BaseTestMixin.setUp(self)

    def tearDown(self):
        BaseTestMixin.tearDown(self)

    @contextlib.contextmanager
    def setup_gui(self, model, view):
        with create_ui(model, dict(view=view)) as ui:
            yield ui.get_editors("value")[0]

    def test_simple_set_editor_use_button(self):
        # Initiate with non-alphabetical list
        model = ListModel(value=["two", "one"])
        with reraise_exceptions(), self.setup_gui(model, get_view()) as editor:

            self.assertEqual(get_list_items(editor._unused), ["four", "three"])
            # Used list is sorted alphabetically
            self.assertEqual(get_list_items(editor._used), ["one", "two"])

            click_on_item(editor, 1, in_used=False)
            process_cascade_events()

            self.assertTrue(is_control_enabled(editor._use))
            self.assertFalse(is_control_enabled(editor._unuse))

            click_button(editor._use)
            process_cascade_events()

            self.assertEqual(get_list_items(editor._unused), ["four"])
            # Button inserts at the top
            self.assertEqual(
                get_list_items(editor._used), ["three", "one", "two"]
            )
            self.assertEqual(editor._get_selected_strings(editor._used), [])

    def test_simple_set_editor_unuse_button(self):
        with reraise_exceptions(), self.setup_gui(
            ListModel(), get_view()
        ) as editor:

            self.assertEqual(get_list_items(editor._unused), ["four", "three"])
            self.assertEqual(get_list_items(editor._used), ["one", "two"])

            click_on_item(editor, 0, in_used=True)
            process_cascade_events()

            self.assertFalse(is_control_enabled(editor._use))
            self.assertTrue(is_control_enabled(editor._unuse))

            click_button(editor._unuse)
            process_cascade_events()

            # Button inserts at the top
            self.assertEqual(
                get_list_items(editor._unused), ["one", "four", "three"]
            )
            self.assertEqual(get_list_items(editor._used), ["two"])

    def test_simple_set_editor_use_dclick(self):
        with reraise_exceptions(), self.setup_gui(
            ListModel(), get_view()
        ) as editor:

            self.assertEqual(get_list_items(editor._unused), ["four", "three"])
            self.assertEqual(get_list_items(editor._used), ["one", "two"])

            double_click_on_item(editor, 1, in_used=False)
            process_cascade_events()

            self.assertEqual(get_list_items(editor._unused), ["four"])
            # Inserts at the top
            self.assertEqual(
                get_list_items(editor._used), ["three", "one", "two"]
            )
            self.assertEqual(editor._get_selected_strings(editor._used), [])

    def test_simple_set_editor_unuse_dclick(self):
        with reraise_exceptions(), self.setup_gui(
            ListModel(), get_view()
        ) as editor:

            self.assertEqual(get_list_items(editor._unused), ["four", "three"])
            self.assertEqual(get_list_items(editor._used), ["one", "two"])

            double_click_on_item(editor, 0, in_used=True)
            process_cascade_events()

            # Inserts at the top
            self.assertEqual(
                get_list_items(editor._unused), ["one", "four", "three"]
            )
            self.assertEqual(get_list_items(editor._used), ["two"])

    def test_simple_set_editor_use_all(self):
        with reraise_exceptions(), self.setup_gui(
            ListModel(), get_view()
        ) as editor:

            self.assertEqual(get_list_items(editor._unused), ["four", "three"])
            self.assertEqual(get_list_items(editor._used), ["one", "two"])

            click_on_item(editor, 1, in_used=False)
            process_cascade_events()

            self.assertTrue(is_control_enabled(editor._use_all))
            self.assertFalse(is_control_enabled(editor._unuse_all))

            click_button(editor._use_all)
            process_cascade_events()

            self.assertEqual(get_list_items(editor._unused), [])
            # Button inserts at the end
            self.assertEqual(
                get_list_items(editor._used), ["one", "two", "four", "three"]
            )

    def test_simple_set_editor_unuse_all(self):
        with reraise_exceptions(), self.setup_gui(
            ListModel(), get_view()
        ) as editor:

            self.assertEqual(get_list_items(editor._unused), ["four", "three"])
            self.assertEqual(get_list_items(editor._used), ["one", "two"])

            click_on_item(editor, 0, in_used=True)
            process_cascade_events()

            self.assertFalse(is_control_enabled(editor._use_all))
            self.assertTrue(is_control_enabled(editor._unuse_all))

            click_button(editor._unuse_all)
            process_cascade_events()

            # Button inserts at the end
            self.assertEqual(
                get_list_items(editor._unused), ["four", "three", "one", "two"]
            )
            self.assertEqual(get_list_items(editor._used), [])

    def test_simple_set_editor_move_up(self):
        with reraise_exceptions(), self.setup_gui(
            ListModel(), get_view(ordered=True)
        ) as editor:

            self.assertEqual(get_list_items(editor._unused), ["four", "three"])
            self.assertEqual(get_list_items(editor._used), ["one", "two"])

            click_on_item(editor, 1, in_used=True)
            process_cascade_events()

            self.assertTrue(is_control_enabled(editor._up))
            self.assertFalse(is_control_enabled(editor._down))

            click_button(editor._up)
            process_cascade_events()

            self.assertEqual(get_list_items(editor._unused), ["four", "three"])
            self.assertEqual(get_list_items(editor._used), ["two", "one"])

    def test_simple_set_editor_move_down(self):
        with reraise_exceptions(), self.setup_gui(
            ListModel(), get_view(ordered=True)
        ) as editor:

            self.assertEqual(get_list_items(editor._unused), ["four", "three"])
            self.assertEqual(get_list_items(editor._used), ["one", "two"])

            click_on_item(editor, 0, in_used=True)
            process_cascade_events()

            self.assertFalse(is_control_enabled(editor._up))
            self.assertTrue(is_control_enabled(editor._down))

            click_button(editor._down)
            process_cascade_events()

            self.assertEqual(get_list_items(editor._unused), ["four", "three"])
            self.assertEqual(get_list_items(editor._used), ["two", "one"])

    def test_simple_set_editor_use_all_button(self):
        with reraise_exceptions(), self.setup_gui(
            ListModel(), get_view()
        ) as editor:

            self.assertEqual(get_list_items(editor._unused), ["four", "three"])
            self.assertEqual(get_list_items(editor._used), ["one", "two"])

            click_on_item(editor, 1, in_used=False)
            process_cascade_events()

            self.assertTrue(is_control_enabled(editor._use_all))
            self.assertFalse(is_control_enabled(editor._unuse_all))

            click_button(editor._use_all)
            process_cascade_events()

            self.assertEqual(get_list_items(editor._unused), [])
            # Button inserts at the end
            self.assertEqual(
                get_list_items(editor._used), ["one", "two", "four", "three"]
            )

    def test_simple_set_editor_unuse_all_button(self):
        with reraise_exceptions(), self.setup_gui(
            ListModel(), get_view()
        ) as editor:

            self.assertEqual(get_list_items(editor._unused), ["four", "three"])
            self.assertEqual(get_list_items(editor._used), ["one", "two"])

            click_on_item(editor, 0, in_used=True)
            process_cascade_events()

            self.assertFalse(is_control_enabled(editor._use_all))
            self.assertTrue(is_control_enabled(editor._unuse_all))

            click_button(editor._unuse_all)
            process_cascade_events()

            # Button inserts at the end
            self.assertEqual(
                get_list_items(editor._unused), ["four", "three", "one", "two"]
            )
            self.assertEqual(get_list_items(editor._used), [])

    def test_simple_set_editor_default_selection_unused(self):
        with reraise_exceptions(), self.setup_gui(
            ListModel(), get_view()
        ) as editor:

            self.assertEqual(get_list_items(editor._unused), ["four", "three"])
            self.assertEqual(get_list_items(editor._used), ["one", "two"])

            click_button(editor._use)
            process_cascade_events()

            # Button inserts at the top
            self.assertEqual(get_list_items(editor._unused), ["three"])
            self.assertEqual(
                get_list_items(editor._used), ["four", "one", "two"]
            )

    def test_simple_set_editor_default_selection_used(self):
        # When all items are used, top used item is selected by default
        list_edit = ListModel(value=["one", "two", "three", "four"])

        with reraise_exceptions(), self.setup_gui(
            list_edit, get_view()
        ) as editor:

            self.assertEqual(get_list_items(editor._unused), [])
            self.assertEqual(
                get_list_items(editor._used), ["four", "one", "three", "two"]
            )

            click_button(editor._unuse)
            process_cascade_events()

            # Button inserts at the top
            self.assertEqual(get_list_items(editor._unused), ["four"])
            self.assertEqual(
                get_list_items(editor._used), ["one", "three", "two"]
            )

    def test_simple_set_editor_deleted_valid_values(self):
        editor_factory = SetEditor(values=["one", "two", "three", "four"])
        view = View(
            UItem(
                "value",
                editor=editor_factory,
                style="simple",
            )
        )
        list_edit = ListModel()

        with reraise_exceptions(), self.setup_gui(list_edit, view) as editor:

            self.assertEqual(get_list_items(editor._unused), ["four", "three"])
            self.assertEqual(get_list_items(editor._used), ["one", "two"])

            editor_factory.values = ["two", "three", "four"]
            process_cascade_events()

            self.assertEqual(get_list_items(editor._unused), ["four", "three"])
            # FIXME issue enthought/traitsui#840
            if is_wx():
                with self.assertRaises(AssertionError):
                    self.assertEqual(get_list_items(editor._used), ["two"])
                self.assertEqual(get_list_items(editor._used), ["one", "two"])
            else:
                self.assertEqual(get_list_items(editor._used), ["two"])
            self.assertEqual(list_edit.value, ["two"])

    def test_simple_set_editor_use_ordered_selected(self):
        # Initiate with non-alphabetical list
        model = ListModel(value=["two", "one"])
        with reraise_exceptions(), self.setup_gui(
            model, get_view(ordered=True)
        ) as editor:

            self.assertEqual(get_list_items(editor._unused), ["four", "three"])
            # Used list maintains the order
            self.assertEqual(get_list_items(editor._used), ["two", "one"])

            click_on_item(editor, 1, in_used=False)
            process_cascade_events()

            self.assertTrue(is_control_enabled(editor._use))
            self.assertFalse(is_control_enabled(editor._unuse))

            click_button(editor._use)
            process_cascade_events()

            self.assertEqual(get_list_items(editor._unused), ["four"])
            # Button inserts at the top
            self.assertEqual(
                get_list_items(editor._used), ["three", "two", "one"]
            )
            self.assertEqual(
                editor._get_selected_strings(editor._used), ["three"]
            )

    def test_simple_set_editor_unordeder_button_existence(self):
        with reraise_exceptions(), self.setup_gui(
            ListModel(), get_view()
        ) as editor:

            self.assertIsNone(editor._up)
            self.assertIsNone(editor._down)

    def test_simple_set_editor_cant_move_all_button_existence(self):
        view = get_view(can_move_all=False)
        with reraise_exceptions(), self.setup_gui(ListModel(), view) as editor:

            self.assertIsNone(editor._use_all)
            self.assertIsNone(editor._unuse_all)
