import unittest

from pyface.gui import GUI

from traits.api import HasTraits, List
from traitsui.api import SetEditor, UItem, View
from traitsui.tests._tools import (
    click_button,
    is_control_enabled,
    is_current_backend_qt4,
    is_current_backend_wx,
    skip_if_null,
    store_exceptions_on_all_threads,
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
    """ Return a list of strings from the list widget. """
    items = []

    if is_current_backend_wx():
        for i in range(list_widget.GetCount()):
            items.append(list_widget.GetString(i))

    elif is_current_backend_qt4():
        for i in range(list_widget.count()):
            items.append(list_widget.item(i).text())

    else:
        raise unittest.SkipTest("Test not implemented for this toolkit")

    return items


def click_on_item(editor, item_idx, in_used=False):
    """ Simulate a click on an item in a specified list.

    The function deselects all items in both used and unused lists, then
    selects an item at index item_idx either in the used list (if
    in_used=True) or in the unused list. Finally the function simulates a
    click on the selected item.
    """
    unused_list = editor._unused
    used_list = editor._used

    if is_current_backend_wx():
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

    elif is_current_backend_qt4():
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
    """ Simulate a double click on an item in a specified list.

    The function deselects all items in both used and unused lists, then
    selects an item at index item_idx either in the used list (if
    in_used=True) or in the unused list. Finally the function simulates a
    double click on the selected item.
    """
    unused_list = editor._unused
    used_list = editor._used

    if is_current_backend_wx():
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

    elif is_current_backend_qt4():
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


@skip_if_null
class TestSetEditorMapping(unittest.TestCase):

    def setup_ui(self, model, view):
        ui = model.edit_traits(view=view)
        self.addCleanup(ui.dispose)
        return ui.get_editors("value")[0]

    def test_simple_editor_mapping_values(self):
        class IntListModel(HasTraits):
            value = List()

        set_editor_factory = SetEditor(
            values=[0, 1],
            format_func=lambda v: str(bool(v)).upper()
        )
        formatted_view = View(
            UItem(
                "value",
                editor=set_editor_factory,
                style="simple",
            )
        )

        with store_exceptions_on_all_threads():
            editor = self.setup_ui(IntListModel(), formatted_view)

            # FIXME issue enthought/traitsui#782
            with self.assertRaises(AssertionError):
                self.assertEqual(editor.names, ["FALSE", "TRUE"])
                self.assertEqual(editor.mapping, {"FALSE": 0, "TRUE": 1})
                self.assertEqual(
                    editor.inverse_mapping, {0: "FALSE", 1: "TRUE"}
                )
            self.assertEqual(editor.names, ["0", "1"])
            self.assertEqual(editor.mapping, {"0": 0, "1": 1})
            self.assertEqual(
                editor.inverse_mapping, {0: "0", 1: "1"}
            )

            set_editor_factory.values = [1, 0]

            self.assertEqual(editor.names, ["TRUE", "FALSE"])
            self.assertEqual(editor.mapping, {"TRUE": 1, "FALSE": 0})
            self.assertEqual(
                editor.inverse_mapping, {1: "TRUE", 0: "FALSE"}
            )

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

        with store_exceptions_on_all_threads():
            editor = self.setup_ui(model, formatted_view)

            # FIXME issue enthought/traitsui#835
            if is_current_backend_wx():
                with self.assertRaises(AssertionError):
                    self.assertEqual(editor.names, ["FALSE", "TRUE"])
                    self.assertEqual(editor.mapping, {"FALSE": 0, "TRUE": 1})
                    self.assertEqual(
                        editor.inverse_mapping, {0: "FALSE", 1: "TRUE"}
                    )
                self.assertEqual(editor.names, ["0", "1"])
                self.assertEqual(editor.mapping, {"0": 0, "1": 1})
                self.assertEqual(
                    editor.inverse_mapping, {0: "0", 1: "1"}
                )
            else:
                self.assertEqual(editor.names, ["FALSE", "TRUE"])
                self.assertEqual(editor.mapping, {"FALSE": 0, "TRUE": 1})
                self.assertEqual(
                    editor.inverse_mapping, {0: "FALSE", 1: "TRUE"}
                )

            model.possible_values = [1, 0]

            # FIXME issue enthought/traitsui#835
            if is_current_backend_wx():
                with self.assertRaises(AssertionError):
                    self.assertEqual(editor.names, ["TRUE", "FALSE"])
                    self.assertEqual(editor.mapping, {"TRUE": 1, "FALSE": 0})
                    self.assertEqual(
                        editor.inverse_mapping, {1: "TRUE", 0: "FALSE"}
                    )
                self.assertEqual(editor.names, ["1", "0"])
                self.assertEqual(editor.mapping, {"1": 1, "0": 0})
                self.assertEqual(
                    editor.inverse_mapping, {1: "1", 0: "0"}
                )
            else:
                self.assertEqual(editor.names, ["TRUE", "FALSE"])
                self.assertEqual(editor.mapping, {"TRUE": 1, "FALSE": 0})
                self.assertEqual(
                    editor.inverse_mapping, {1: "TRUE", 0: "FALSE"}
                )


@skip_if_null
class TestSimpleSetEditor(unittest.TestCase):

    def setup_gui(self, model, view):
        gui = GUI()
        ui = model.edit_traits(view=view)
        self.addCleanup(ui.dispose)

        gui.process_events()
        editor = ui.get_editors("value")[0]

        return gui, editor

    def test_simple_set_editor_use_button(self):
        with store_exceptions_on_all_threads():
            gui, editor = self.setup_gui(ListModel(), get_view())

            self.assertEqual(get_list_items(editor._unused), ["four", "three"])
            self.assertEqual(get_list_items(editor._used), ["one", "two"])

            click_on_item(editor, 1, in_used=False)
            gui.process_events()

            self.assertTrue(is_control_enabled(editor._use))
            self.assertFalse(is_control_enabled(editor._unuse))

            click_button(editor._use)
            gui.process_events()

            self.assertEqual(get_list_items(editor._unused), ["four"])
            # Button inserts at the top
            self.assertEqual(
                get_list_items(editor._used), ["three", "one", "two"]
            )
            self.assertEqual(editor._get_selected_strings(editor._used), [])

    def test_simple_set_editor_unuse_button(self):
        with store_exceptions_on_all_threads():
            gui, editor = self.setup_gui(ListModel(), get_view())

            self.assertEqual(get_list_items(editor._unused), ["four", "three"])
            self.assertEqual(get_list_items(editor._used), ["one", "two"])

            click_on_item(editor, 0, in_used=True)
            gui.process_events()

            self.assertFalse(is_control_enabled(editor._use))
            self.assertTrue(is_control_enabled(editor._unuse))

            click_button(editor._unuse)
            gui.process_events()

            # Button inserts at the top
            self.assertEqual(
                get_list_items(editor._unused), ["one", "four", "three"]
            )
            self.assertEqual(get_list_items(editor._used), ["two"])

    def test_simple_set_editor_use_dclick(self):
        with store_exceptions_on_all_threads():
            gui, editor = self.setup_gui(ListModel(), get_view())

            self.assertEqual(get_list_items(editor._unused), ["four", "three"])
            self.assertEqual(get_list_items(editor._used), ["one", "two"])

            double_click_on_item(editor, 1, in_used=False)
            gui.process_events()

            self.assertEqual(get_list_items(editor._unused), ["four"])
            # Inserts at the top
            self.assertEqual(
                get_list_items(editor._used), ["three", "one", "two"]
            )
            self.assertEqual(editor._get_selected_strings(editor._used), [])

    def test_simple_set_editor_unuse_dclick(self):
        with store_exceptions_on_all_threads():
            gui, editor = self.setup_gui(ListModel(), get_view())

            self.assertEqual(get_list_items(editor._unused), ["four", "three"])
            self.assertEqual(get_list_items(editor._used), ["one", "two"])

            double_click_on_item(editor, 0, in_used=True)
            gui.process_events()

            # Inserts at the top
            self.assertEqual(
                get_list_items(editor._unused), ["one", "four", "three"]
            )
            self.assertEqual(get_list_items(editor._used), ["two"])

    def test_simple_set_editor_use_all(self):
        with store_exceptions_on_all_threads():
            gui, editor = self.setup_gui(ListModel(), get_view())

            self.assertEqual(get_list_items(editor._unused), ["four", "three"])
            self.assertEqual(get_list_items(editor._used), ["one", "two"])

            click_on_item(editor, 1, in_used=False)
            gui.process_events()

            self.assertTrue(is_control_enabled(editor._use_all))
            self.assertFalse(is_control_enabled(editor._unuse_all))

            click_button(editor._use_all)
            gui.process_events()

            self.assertEqual(get_list_items(editor._unused), [])
            # Button inserts at the end
            self.assertEqual(
                get_list_items(editor._used), ["one", "two", "four", "three"]
            )

    def test_simple_set_editor_unuse_all(self):
        with store_exceptions_on_all_threads():
            gui, editor = self.setup_gui(ListModel(), get_view())

            self.assertEqual(get_list_items(editor._unused), ["four", "three"])
            self.assertEqual(get_list_items(editor._used), ["one", "two"])

            click_on_item(editor, 0, in_used=True)
            gui.process_events()

            self.assertFalse(is_control_enabled(editor._use_all))
            self.assertTrue(is_control_enabled(editor._unuse_all))

            click_button(editor._unuse_all)
            gui.process_events()

            # Button inserts at the end
            self.assertEqual(
                get_list_items(editor._unused), ["four", "three", "one", "two"]
            )
            self.assertEqual(get_list_items(editor._used), [])

    def test_simple_set_editor_move_up(self):
        with store_exceptions_on_all_threads():
            gui, editor = self.setup_gui(
                ListModel(), get_view(ordered=True)
            )

            self.assertEqual(get_list_items(editor._unused), ["four", "three"])
            self.assertEqual(get_list_items(editor._used), ["one", "two"])

            click_on_item(editor, 1, in_used=True)
            gui.process_events()

            self.assertTrue(is_control_enabled(editor._up))
            self.assertFalse(is_control_enabled(editor._down))

            click_button(editor._up)
            gui.process_events()

            self.assertEqual(get_list_items(editor._unused), ["four", "three"])
            self.assertEqual(get_list_items(editor._used), ["two", "one"])

    def test_simple_set_editor_move_down(self):
        with store_exceptions_on_all_threads():
            gui, editor = self.setup_gui(
                ListModel(), get_view(ordered=True)
            )

            self.assertEqual(get_list_items(editor._unused), ["four", "three"])
            self.assertEqual(get_list_items(editor._used), ["one", "two"])

            click_on_item(editor, 0, in_used=True)
            gui.process_events()

            self.assertFalse(is_control_enabled(editor._up))
            self.assertTrue(is_control_enabled(editor._down))

            click_button(editor._down)
            gui.process_events()

            self.assertEqual(get_list_items(editor._unused), ["four", "three"])
            self.assertEqual(get_list_items(editor._used), ["two", "one"])

    def test_simple_set_editor_use_all_button(self):
        with store_exceptions_on_all_threads():
            gui, editor = self.setup_gui(ListModel(), get_view())

            self.assertEqual(get_list_items(editor._unused), ["four", "three"])
            self.assertEqual(get_list_items(editor._used), ["one", "two"])

            click_on_item(editor, 1, in_used=False)
            gui.process_events()

            self.assertTrue(is_control_enabled(editor._use_all))
            self.assertFalse(is_control_enabled(editor._unuse_all))

            click_button(editor._use_all)
            gui.process_events()

            self.assertEqual(get_list_items(editor._unused), [])
            # Button inserts at the end
            self.assertEqual(
                get_list_items(editor._used), ["one", "two", "four", "three"]
            )

    def test_simple_set_editor_unuse_all_button(self):
        with store_exceptions_on_all_threads():
            gui, editor = self.setup_gui(ListModel(), get_view())

            self.assertEqual(get_list_items(editor._unused), ["four", "three"])
            self.assertEqual(get_list_items(editor._used), ["one", "two"])

            click_on_item(editor, 0, in_used=True)
            gui.process_events()

            self.assertFalse(is_control_enabled(editor._use_all))
            self.assertTrue(is_control_enabled(editor._unuse_all))

            click_button(editor._unuse_all)
            gui.process_events()

            # Button inserts at the end
            self.assertEqual(
                get_list_items(editor._unused), ["four", "three", "one", "two"]
            )
            self.assertEqual(get_list_items(editor._used), [])

    def test_simple_set_editor_default_selection_unused(self):
        with store_exceptions_on_all_threads():
            gui, editor = self.setup_gui(ListModel(), get_view())

            self.assertEqual(get_list_items(editor._unused), ["four", "three"])
            self.assertEqual(get_list_items(editor._used), ["one", "two"])

            click_button(editor._use)
            gui.process_events()

            # Button inserts at the top
            self.assertEqual(
                get_list_items(editor._unused), ["three"]
            )
            self.assertEqual(
                get_list_items(editor._used), ["four", "one", "two"]
            )

    def test_simple_set_editor_default_selection_used(self):
        # When all items are used, top used item is selected by default
        list_edit = ListModel(value=["one", "two", "three", "four"])

        with store_exceptions_on_all_threads():
            gui, editor = self.setup_gui(list_edit, get_view())

            self.assertEqual(get_list_items(editor._unused), [])
            self.assertEqual(
                get_list_items(editor._used), ["four", "one", "three", "two"])

            click_button(editor._unuse)
            gui.process_events()

            # Button inserts at the top
            self.assertEqual(get_list_items(editor._unused), ["four"])
            self.assertEqual(
                get_list_items(editor._used), ["one", "three", "two"]
            )

    def test_simple_set_editor_deleted_valid_values(self):
        editor_factory = SetEditor(values=["one", "two", "three", "four"])
        view = View(UItem("value", editor=editor_factory, style="simple",))
        list_edit = ListModel()

        with store_exceptions_on_all_threads():
            gui, editor = self.setup_gui(list_edit, view)

            self.assertEqual(get_list_items(editor._unused), ["four", "three"])
            self.assertEqual(get_list_items(editor._used), ["one", "two"])

            editor_factory.values = ["two", "three", "four"]
            gui.process_events()

            self.assertEqual(get_list_items(editor._unused), ["four", "three"])
            # FIXME issue enthought/traitsui#840
            if is_current_backend_wx():
                with self.assertRaises(AssertionError):
                    self.assertEqual(get_list_items(editor._used), ["two"])
                self.assertEqual(get_list_items(editor._used), ["one", "two"])
            else:
                self.assertEqual(get_list_items(editor._used), ["two"])
            self.assertEqual(list_edit.value, ["two"])

    def test_simple_set_editor_use_ordered_selected(self):
        with store_exceptions_on_all_threads():
            gui, editor = self.setup_gui(
                ListModel(), get_view(ordered=True)
            )

            self.assertEqual(get_list_items(editor._unused), ["four", "three"])
            self.assertEqual(get_list_items(editor._used), ["one", "two"])

            click_on_item(editor, 1, in_used=False)
            gui.process_events()

            self.assertTrue(is_control_enabled(editor._use))
            self.assertFalse(is_control_enabled(editor._unuse))

            click_button(editor._use)
            gui.process_events()

            self.assertEqual(get_list_items(editor._unused), ["four"])
            # Button inserts at the top
            self.assertEqual(
                get_list_items(editor._used), ["three", "one", "two"]
            )
            self.assertEqual(
                editor._get_selected_strings(editor._used), ["three"]
            )

    def test_simple_set_editor_unordeder_button_existence(self):
        with store_exceptions_on_all_threads():
            _, editor = self.setup_gui(ListModel(), get_view())

            self.assertIsNone(editor._up)
            self.assertIsNone(editor._down)

    def test_simple_set_editor_cant_move_all_button_existence(self):
        with store_exceptions_on_all_threads():
            _, editor = self.setup_gui(
                ListModel(), get_view(can_move_all=False)
            )

            self.assertIsNone(editor._use_all)
            self.assertIsNone(editor._unuse_all)
