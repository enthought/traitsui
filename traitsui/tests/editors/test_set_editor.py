import unittest

from pyface.gui import GUI

from traits.api import HasTraits, List
from traitsui.api import SetEditor, UItem, View
from traitsui.tests._tools import (
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


def get_unused_items(editor):
    """ Return a list of unused items (left column) as shown in ui. """
    if is_current_backend_wx():
        raise unittest.SkipTest("Test not implemented for wx")

    elif is_current_backend_qt4():
        list_widget = editor.root_layout.itemAtPosition(1, 0).widget()
        items = []
        for i in range(list_widget.count()):
            items.append(list_widget.item(i).text())
        return items


def get_used_items(editor):
    """ Return a list of used items (left column) as shown in ui. """
    if is_current_backend_wx():
        raise unittest.SkipTest("Test not implemented for wx")

    elif is_current_backend_qt4():
        list_widget = editor.root_layout.itemAtPosition(1, 2).widget()
        items = []
        for i in range(list_widget.count()):
            items.append(list_widget.item(i).text())
        return items


def click_on_item(editor, item_no, in_used=False):
    """ Simulate a click on an item in a specified list. """
    if is_current_backend_wx():
        raise unittest.SkipTest("Test not implemented for wx")

    elif is_current_backend_qt4():
        layout = editor.root_layout

        unused_list = layout.itemAtPosition(1, 0).widget()
        for i in range(unused_list.count()):
            status = (not in_used) and (item_no == i)
            unused_list.item(i).setSelected(status)

        used_list = layout.itemAtPosition(1, 2).widget()
        for i in range(used_list.count()):
            status = (in_used) and (item_no == i)
            used_list.item(i).setSelected(status)

        if in_used:
            used_list.itemClicked.emit(used_list.item(item_no))
        else:
            unused_list.itemClicked.emit(unused_list.item(item_no))


def double_click_on_item(editor, item_no, in_used=False):
    """ Simulate a double click on an item in a specified list. """
    if is_current_backend_wx():
        raise unittest.SkipTest("Test not implemented for wx")

    elif is_current_backend_qt4():
        layout = editor.root_layout

        unused_list = layout.itemAtPosition(1, 0).widget()
        for i in range(unused_list.count()):
            status = (not in_used) and (item_no == i)
            unused_list.item(i).setSelected(status)

        used_list = layout.itemAtPosition(1, 2).widget()
        for i in range(used_list.count()):
            status = (in_used) and (item_no == i)
            used_list.item(i).setSelected(status)

        if in_used:
            used_list.itemDoubleClicked.emit(used_list.item(item_no))
        else:
            unused_list.itemDoubleClicked.emit(unused_list.item(item_no))


def get_button_enabled(button):
    """ Return if the button is enabled or not."""
    if is_current_backend_wx():
        raise unittest.SkipTest("Test not implemented for wx")

    elif is_current_backend_qt4():
        return button.isEnabled()


def click_button(button):
    """ Click the provided button. """
    if is_current_backend_wx():
        raise unittest.SkipTest("Test not implemented for wx")

    elif is_current_backend_qt4():
        button.click()


class TestSetEditorMapping(unittest.TestCase):

    def setup_ui(self, model, view):
        ui = model.edit_traits(view=view)
        self.addCleanup(ui.dispose)
        return ui.get_editors("value")[0]

    @skip_if_null
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

            with self.assertRaises(AssertionError):  # FIXME issue #782
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

    @skip_if_null
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

            self.assertEqual(editor.names, ["FALSE", "TRUE"])
            self.assertEqual(editor.mapping, {"FALSE": 0, "TRUE": 1})
            self.assertEqual(
                editor.inverse_mapping, {0: "FALSE", 1: "TRUE"}
            )

            model.possible_values = [1, 0]

            self.assertEqual(editor.names, ["TRUE", "FALSE"])
            self.assertEqual(editor.mapping, {"TRUE": 1, "FALSE": 0})
            self.assertEqual(
                editor.inverse_mapping, {1: "TRUE", 0: "FALSE"}
            )


class TestSimpleSetEditor(unittest.TestCase):

    def setup_gui(self, model, view):
        gui = GUI()
        ui = model.edit_traits(view=view)
        self.addCleanup(ui.dispose)

        gui.process_events()
        editor = ui.get_editors("value")[0]

        return gui, editor

    @skip_if_null
    def test_simple_set_editor_use_button(self):
        with store_exceptions_on_all_threads():
            gui, editor = self.setup_gui(ListModel(), get_view())

            self.assertEqual(get_unused_items(editor), ["four", "three"])
            self.assertEqual(get_used_items(editor), ["one", "two"])

            click_on_item(editor, 1, in_used=False)
            gui.process_events()

            self.assertTrue(get_button_enabled(editor._use))
            self.assertFalse(get_button_enabled(editor._unuse))

            click_button(editor._use)
            gui.process_events()

            self.assertEqual(get_unused_items(editor), ["four"])
            # Button inserts at the top
            self.assertEqual(get_used_items(editor), ["three", "one", "two"])
            self.assertEqual(editor._get_selected_strings(editor._used), [])

    @skip_if_null
    def test_simple_set_editor_unuse_button(self):
        with store_exceptions_on_all_threads():
            gui, editor = self.setup_gui(ListModel(), get_view())

            self.assertEqual(get_unused_items(editor), ["four", "three"])
            self.assertEqual(get_used_items(editor), ["one", "two"])

            click_on_item(editor, 0, in_used=True)
            gui.process_events()

            self.assertFalse(get_button_enabled(editor._use))
            self.assertTrue(get_button_enabled(editor._unuse))

            click_button(editor._unuse)
            gui.process_events()

            # Button inserts at the top
            self.assertEqual(
                get_unused_items(editor), ["one", "four", "three"]
            )
            self.assertEqual(get_used_items(editor), ["two"])

    @skip_if_null
    def test_simple_set_editor_use_dclick(self):
        with store_exceptions_on_all_threads():
            gui, editor = self.setup_gui(ListModel(), get_view())

            self.assertEqual(get_unused_items(editor), ["four", "three"])
            self.assertEqual(get_used_items(editor), ["one", "two"])

            double_click_on_item(editor, 1, in_used=False)
            gui.process_events()

            self.assertEqual(get_unused_items(editor), ["four"])
            # Inserts at the top
            self.assertEqual(get_used_items(editor), ["three", "one", "two"])
            self.assertEqual(editor._get_selected_strings(editor._used), [])

    @skip_if_null
    def test_simple_set_editor_unuse_dclick(self):
        with store_exceptions_on_all_threads():
            gui, editor = self.setup_gui(ListModel(), get_view())

            self.assertEqual(get_unused_items(editor), ["four", "three"])
            self.assertEqual(get_used_items(editor), ["one", "two"])

            double_click_on_item(editor, 0, in_used=True)
            gui.process_events()

            # Inserts at the top
            self.assertEqual(
                get_unused_items(editor), ["one", "four", "three"]
            )
            self.assertEqual(get_used_items(editor), ["two"])

    @skip_if_null
    def test_simple_set_editor_use_all(self):
        with store_exceptions_on_all_threads():
            gui, editor = self.setup_gui(ListModel(), get_view())

            self.assertEqual(get_unused_items(editor), ["four", "three"])
            self.assertEqual(get_used_items(editor), ["one", "two"])

            click_on_item(editor, 1, in_used=False)
            gui.process_events()

            self.assertTrue(get_button_enabled(editor._use_all))
            self.assertFalse(get_button_enabled(editor._unuse_all))

            click_button(editor._use_all)
            gui.process_events()

            self.assertEqual(get_unused_items(editor), [])
            # Button inserts at the end
            self.assertEqual(
                get_used_items(editor), ["one", "two", "four", "three"]
            )

    @skip_if_null
    def test_simple_set_editor_unuse_all(self):
        with store_exceptions_on_all_threads():
            gui, editor = self.setup_gui(ListModel(), get_view())

            self.assertEqual(get_unused_items(editor), ["four", "three"])
            self.assertEqual(get_used_items(editor), ["one", "two"])

            click_on_item(editor, 0, in_used=True)
            gui.process_events()

            self.assertFalse(get_button_enabled(editor._use_all))
            self.assertTrue(get_button_enabled(editor._unuse_all))

            click_button(editor._unuse_all)
            gui.process_events()

            # Button inserts at the end
            self.assertEqual(
                get_unused_items(editor), ["four", "three", "one", "two"]
            )
            self.assertEqual(get_used_items(editor), [])

    @skip_if_null
    def test_simple_set_editor_move_up(self):
        with store_exceptions_on_all_threads():
            gui, editor = self.setup_gui(
                ListModel(), get_view(ordered=True)
            )

            self.assertEqual(get_unused_items(editor), ["four", "three"])
            self.assertEqual(get_used_items(editor), ["one", "two"])

            click_on_item(editor, 1, in_used=True)
            gui.process_events()

            self.assertTrue(get_button_enabled(editor._up))
            self.assertFalse(get_button_enabled(editor._down))

            click_button(editor._up)
            gui.process_events()

            self.assertEqual(get_unused_items(editor), ["four", "three"])
            self.assertEqual(get_used_items(editor), ["two", "one"])

    @skip_if_null
    def test_simple_set_editor_move_down(self):
        with store_exceptions_on_all_threads():
            gui, editor = self.setup_gui(
                ListModel(), get_view(ordered=True)
            )

            self.assertEqual(get_unused_items(editor), ["four", "three"])
            self.assertEqual(get_used_items(editor), ["one", "two"])

            click_on_item(editor, 0, in_used=True)
            gui.process_events()

            self.assertFalse(get_button_enabled(editor._up))
            self.assertTrue(get_button_enabled(editor._down))

            click_button(editor._down)
            gui.process_events()

            self.assertEqual(get_unused_items(editor), ["four", "three"])
            self.assertEqual(get_used_items(editor), ["two", "one"])

    @skip_if_null
    def test_simple_set_editor_use_all_button(self):
        with store_exceptions_on_all_threads():
            gui, editor = self.setup_gui(ListModel(), get_view())

            self.assertEqual(get_unused_items(editor), ["four", "three"])
            self.assertEqual(get_used_items(editor), ["one", "two"])

            click_on_item(editor, 1, in_used=False)
            gui.process_events()

            self.assertTrue(get_button_enabled(editor._use_all))
            self.assertFalse(get_button_enabled(editor._unuse_all))

            click_button(editor._use_all)
            gui.process_events()

            self.assertEqual(get_unused_items(editor), [])
            # Button inserts at the end
            self.assertEqual(
                get_used_items(editor), ["one", "two", "four", "three"]
            )

    @skip_if_null
    def test_simple_set_editor_unuse_all_button(self):
        with store_exceptions_on_all_threads():
            gui, editor = self.setup_gui(ListModel(), get_view())

            self.assertEqual(get_unused_items(editor), ["four", "three"])
            self.assertEqual(get_used_items(editor), ["one", "two"])

            click_on_item(editor, 0, in_used=True)
            gui.process_events()

            self.assertFalse(get_button_enabled(editor._use_all))
            self.assertTrue(get_button_enabled(editor._unuse_all))

            click_button(editor._unuse_all)
            gui.process_events()

            # Button inserts at the end
            self.assertEqual(
                get_unused_items(editor), ["four", "three", "one", "two"]
            )
            self.assertEqual(get_used_items(editor), [])

    @skip_if_null
    def test_simple_set_editor_default_selection_unused(self):
        with store_exceptions_on_all_threads():
            gui, editor = self.setup_gui(ListModel(), get_view())

            self.assertEqual(get_unused_items(editor), ["four", "three"])
            self.assertEqual(get_used_items(editor), ["one", "two"])

            click_button(editor._use)
            gui.process_events()

            # Button inserts at the top
            self.assertEqual(
                get_unused_items(editor), ["three"]
            )
            self.assertEqual(get_used_items(editor), ["four", "one", "two"])

    @skip_if_null
    def test_simple_set_editor_default_selection_used(self):
        # When all items are used, top used item is selected by default
        list_edit = ListModel(value=["one", "two", "three", "four"])

        with store_exceptions_on_all_threads():
            gui, editor = self.setup_gui(list_edit, get_view())

            self.assertEqual(get_unused_items(editor), [])
            self.assertEqual(
                get_used_items(editor), ["four", "one", "three", "two"])

            click_button(editor._unuse)
            gui.process_events()

            # Button inserts at the top
            self.assertEqual(get_unused_items(editor), ["four"])
            self.assertEqual(get_used_items(editor), ["one", "three", "two"])

    @skip_if_null
    def test_simple_set_editor_deleted_valid_values(self):
        editor_factory = SetEditor(values=["one", "two", "three", "four"])
        view = View(UItem("value", editor=editor_factory, style="simple",))
        list_edit = ListModel()

        with store_exceptions_on_all_threads():
            gui, editor = self.setup_gui(list_edit, view)

            self.assertEqual(get_unused_items(editor), ["four", "three"])
            self.assertEqual(get_used_items(editor), ["one", "two"])

            editor_factory.values = ["two", "three", "four"]
            gui.process_events()

            self.assertEqual(get_unused_items(editor), ["four", "three"])
            self.assertEqual(get_used_items(editor), ["two"])
            self.assertEqual(list_edit.value, ["two"])

    @skip_if_null
    def test_simple_set_editor_use_ordered_selected(self):
        with store_exceptions_on_all_threads():
            gui, editor = self.setup_gui(
                ListModel(), get_view(ordered=True)
            )

            self.assertEqual(get_unused_items(editor), ["four", "three"])
            self.assertEqual(get_used_items(editor), ["one", "two"])

            click_on_item(editor, 1, in_used=False)
            gui.process_events()

            self.assertTrue(get_button_enabled(editor._use))
            self.assertFalse(get_button_enabled(editor._unuse))

            click_button(editor._use)
            gui.process_events()

            self.assertEqual(get_unused_items(editor), ["four"])
            # Button inserts at the top
            self.assertEqual(get_used_items(editor), ["three", "one", "two"])
            self.assertEqual(
                editor._get_selected_strings(editor._used), ["three"]
            )

    @skip_if_null
    def test_simple_set_editor_unordeder_button_existence(self):
        with store_exceptions_on_all_threads():
            _, editor = self.setup_gui(ListModel(), get_view())

            self.assertIsNone(editor._up)
            self.assertIsNone(editor._down)

    @skip_if_null
    def test_simple_set_editor_cant_move_all_button_existence(self):
        with store_exceptions_on_all_threads():
            _, editor = self.setup_gui(
                ListModel(), get_view(can_move_all=False)
            )

            self.assertIsNone(editor._use_all)
            self.assertIsNone(editor._unuse_all)
