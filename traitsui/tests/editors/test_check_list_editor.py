import unittest

from pyface.gui import GUI

from traits.api import HasTraits, List, Str
from traitsui.api import CheckListEditor, UItem, View
from traitsui.tests._tools import (
    is_current_backend_qt4,
    is_current_backend_wx,
    skip_if_null,
    store_exceptions_on_all_threads,
)


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
        resizable=True
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
        resizable=True
    )


def get_combobox_text(combobox):
    """ Return the text given a combobox control """
    if is_current_backend_wx():
        return combobox.GetString(combobox.GetSelection())

    elif is_current_backend_qt4():
        return combobox.currentText()


def set_combobox_index(editor, idx):
    """ Set combobox index to given index value. """
    if is_current_backend_wx():
        import wx

        choice = editor.control
        choice.SetSelection(idx)
        event = wx.CommandEvent(wx.EVT_CHOICE.typeId, choice.GetId())
        event.SetString(choice.GetString(idx))
        wx.PostEvent(choice, event)

    elif is_current_backend_qt4():
        # Cannot initiate update programatically because of `activated`
        # event. At least check that it updates as expected when done
        # manually
        editor.update_object(idx)


def get_all_button_status(widget):
    """ Gets status of all check buttons in the layout of a given widget."""
    if is_current_backend_wx():
        button_status = []
        for item in widget.GetSizer().GetChildren():
            button = item.GetWindow()
            if button.value != "":  # There are empty invisible buttons
                button_status.append(button.GetValue())
        return button_status

    elif is_current_backend_qt4():
        layout = widget.layout()
        button_status = []
        for i in range(layout.count()):
            button_status.append(layout.itemAt(i).widget().isChecked())
        return button_status


def click_checkbox_button(widget, button_idx):
    """ Simulate a checkbox click given widget and button number."""
    if is_current_backend_wx():
        import wx

        sizer_items = widget.GetSizer().GetChildren()
        button = sizer_items[button_idx].GetWindow()
        button.SetValue(not button.GetValue())
        event = wx.CommandEvent(wx.EVT_CHECKBOX.typeId, button.GetId())
        event.SetEventObject(button)
        wx.PostEvent(widget, event)

    elif is_current_backend_qt4():
        layout = widget.layout()
        layout.itemAt(button_idx).widget().click()


def set_text_in_line_edit(line_edit, text):
    """ Set text in text widget and complete editing. """
    if is_current_backend_wx():
        import wx

        line_edit.SetValue(text)
        event = wx.CommandEvent(wx.EVT_TEXT_ENTER.typeId, line_edit.GetId())
        wx.PostEvent(line_edit, event)

    elif is_current_backend_qt4():
        line_edit.setText(text)
        line_edit.editingFinished.emit()


class TestCheckListEditorMapping(unittest.TestCase):

    def setup_ui(self, model, view):
        ui = model.edit_traits(view=view)
        self.addCleanup(ui.dispose)
        return ui.get_editors("value")[0]

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

        with store_exceptions_on_all_threads():
            editor = self.setup_ui(model, formatted_view)

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

        with store_exceptions_on_all_threads():
            editor = self.setup_ui(model, formatted_view)

            with self.assertRaises(AssertionError):  # FIXME issue #841
                self.assertEqual(editor.names, ["ONE", "TWO"])
            self.assertEqual(editor.names, ["one", "two"])

            check_list_editor_factory.values = [(2, "two"), (1, "one")]

            with self.assertRaises(AssertionError):  # FIXME issue #841
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
        model = ListModel(possible_values=["one", "two"])

        with store_exceptions_on_all_threads():
            editor = self.setup_ui(model, formatted_view)

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

        with store_exceptions_on_all_threads():
            editor = self.setup_ui(model, formatted_view)

            with self.assertRaises(AssertionError):  # FIXME issue #841
                self.assertEqual(editor.names, ["ONE", "TWO"])
            self.assertEqual(editor.names, ["one", "two"])

            model.possible_values = [(2, "two"), (1, "one")]

            with self.assertRaises(AssertionError):  # FIXME issue #841
                self.assertEqual(editor.names, ["TWO", "ONE"])
            self.assertEqual(editor.names, ["two", "one"])

    @skip_if_null
    def test_simple_editor_mapping_values(self):
        self.check_checklist_mappings_value_change("simple")

    @skip_if_null
    def test_simple_editor_mapping_values_tuple(self):
        self.check_checklist_mappings_tuple_value_change("simple")

    @skip_if_null
    def test_simple_editor_mapping_name(self):
        self.check_checklist_mappings_name_change("simple")

    @skip_if_null
    def test_simple_editor_mapping_name_tuple(self):
        self.check_checklist_mappings_tuple_name_change("simple")

    @skip_if_null
    def test_custom_editor_mapping_values(self):
        if is_current_backend_wx():  # FIXME issue #842
            import wx

            with self.assertRaises(wx._core.wxAssertionError):
                self.check_checklist_mappings_value_change("custom")
        else:
            self.check_checklist_mappings_value_change("custom")

    @skip_if_null
    def test_custom_editor_mapping_values_tuple(self):
        if is_current_backend_wx():  # FIXME issue #842
            import wx

            with self.assertRaises(wx._core.wxAssertionError):
                self.check_checklist_mappings_tuple_value_change("custom")
        else:
            self.check_checklist_mappings_tuple_value_change("custom")

    @skip_if_null
    def test_custom_editor_mapping_name(self):
        if is_current_backend_wx():  # FIXME issue #842
            import wx

            with self.assertRaises(wx._core.wxAssertionError):
                self.check_checklist_mappings_name_change("custom")
        else:
            self.check_checklist_mappings_name_change("custom")

    @skip_if_null
    def test_custom_editor_mapping_name_tuple(self):
        if is_current_backend_wx():  # FIXME issue #842
            import wx

            with self.assertRaises(wx._core.wxAssertionError):
                self.check_checklist_mappings_tuple_name_change("custom")
        else:
            self.check_checklist_mappings_tuple_name_change("custom")


class TestSimpleCheckListEditor(unittest.TestCase):

    def setup_gui(self, model, view):
        gui = GUI()
        ui = model.edit_traits(view=view)
        self.addCleanup(ui.dispose)

        gui.process_events()
        editor = ui.get_editors("value")[0]
        combobox = editor.control

        return gui, editor, combobox

    @skip_if_null
    def test_simple_check_list_editor_text(self):
        list_edit = ListModel()

        with store_exceptions_on_all_threads():
            gui, _, combobox = self.setup_gui(list_edit, get_view("simple"))

            self.assertEqual(get_combobox_text(combobox), "One")

            list_edit.value = ["two"]
            gui.process_events()

            self.assertEqual(get_combobox_text(combobox), "Two")

    @skip_if_null
    def test_simple_check_list_editor_text_mapped(self):
        view = get_mapped_view("simple")
        list_edit = ListModel()

        with store_exceptions_on_all_threads():
            gui, _, combobox = self.setup_gui(list_edit, view)

            with self.assertRaises(AssertionError):  # FIXME issue #841
                self.assertEqual(get_combobox_text(combobox), "One")
            self.assertEqual(get_combobox_text(combobox), "one")

            list_edit.value = [2]
            gui.process_events()

            with self.assertRaises(AssertionError):  # FIXME issue #841
                self.assertEqual(get_combobox_text(combobox), "Two")
            self.assertEqual(get_combobox_text(combobox), "two")

    @skip_if_null
    def test_simple_check_list_editor_index(self):
        list_edit = ListModel()

        with store_exceptions_on_all_threads():
            gui, editor, _ = self.setup_gui(list_edit, get_view("simple"))

            self.assertEqual(list_edit.value, [])

            set_combobox_index(editor, 1)
            gui.process_events()

            self.assertEqual(list_edit.value, ["two"])

            set_combobox_index(editor, 0)
            gui.process_events()

            self.assertEqual(list_edit.value, ["one"])

    @skip_if_null
    def test_simple_check_list_editor_invalid_current_values(self):
        list_edit = ListModel(value=[1, "two", "a", object(), "one"])

        with store_exceptions_on_all_threads():
            gui, _, _ = self.setup_gui(list_edit, get_view("simple"))

            self.assertEqual(list_edit.value, ["two", "one"])

    @skip_if_null
    def test_simple_check_list_editor_invalid_current_values_str(self):
        class StrModel(HasTraits):
            value = Str()

        str_edit = StrModel(value="alpha, \ttwo, beta,\n lambda, one")

        with store_exceptions_on_all_threads():
            gui, _, _ = self.setup_gui(str_edit, get_view("simple"))

            self.assertEqual(str_edit.value, "two,one")


class TestCustomCheckListEditor(unittest.TestCase):

    def setup_gui(self, model, view):
        gui = GUI()
        ui = model.edit_traits(view=view)
        self.addCleanup(ui.dispose)

        gui.process_events()
        editor = ui.get_editors("value")[0]
        widget = editor.control

        return gui, editor, widget

    @skip_if_null
    def test_custom_check_list_editor_button_update(self):
        list_edit = ListModel()

        with store_exceptions_on_all_threads():
            gui, _, widget = self.setup_gui(list_edit, get_view("custom"))

            self.assertEqual(
                get_all_button_status(widget), [False, False, False, False]
            )

            list_edit.value = ["two", "four"]
            gui.process_events()

            self.assertEqual(
                get_all_button_status(widget), [False, True, False, True]
            )

            list_edit.value = ["one", "four"]
            gui.process_events()

            self.assertEqual(
                get_all_button_status(widget), [True, False, False, True]
            )

    @skip_if_null
    def test_custom_check_list_editor_click(self):
        list_edit = ListModel()

        with store_exceptions_on_all_threads():
            gui, _, widget = self.setup_gui(list_edit, get_view("custom"))

            self.assertEqual(list_edit.value, [])

            click_checkbox_button(widget, 1)
            gui.process_events()

            self.assertEqual(list_edit.value, ["two"])

            click_checkbox_button(widget, 1)
            gui.process_events()

            self.assertEqual(list_edit.value, [])

    @skip_if_null
    def test_custom_check_list_editor_click_initial_value(self):
        list_edit = ListModel(value=["two"])

        with store_exceptions_on_all_threads():
            gui, _, widget = self.setup_gui(list_edit, get_view("custom"))

            self.assertEqual(list_edit.value, ["two"])

            click_checkbox_button(widget, 1)
            gui.process_events()

            self.assertEqual(list_edit.value, [])

    @skip_if_null
    def test_custom_check_list_editor_invalid_current_values_str(self):
        class StrModel(HasTraits):
            value = Str()

        str_edit = StrModel(value="alpha, \ttwo, three,\n lambda, one")

        with store_exceptions_on_all_threads():
            gui, _, widget = self.setup_gui(str_edit, get_view("custom"))

            self.assertEqual(str_edit.value, "two,three,one")

            click_checkbox_button(widget, 1)
            gui.process_events()

            self.assertEqual(str_edit.value, "three,one")


class TestTextCheckListEditor(unittest.TestCase):

    def setup_gui(self, model, view):
        gui = GUI()
        ui = model.edit_traits(view=view)
        self.addCleanup(ui.dispose)

        gui.process_events()
        editor = ui.get_editors("value")[0]
        line_edit = editor.control

        return gui, editor, line_edit

    @skip_if_null
    def test_text_check_list_object_list(self):
        list_edit = ListModel()

        with store_exceptions_on_all_threads():
            gui, _, line_edit = self.setup_gui(list_edit, get_view("text"))

            self.assertEqual(list_edit.value, [])

            set_text_in_line_edit(line_edit, "['one', 'two']")
            gui.process_events()

            self.assertEqual(list_edit.value, ["one", "two"])

    @skip_if_null
    def test_text_check_list_object_str(self):
        class StrModel(HasTraits):
            value = Str()

        str_edit = StrModel(value="three, four")

        with store_exceptions_on_all_threads():
            gui, _, line_edit = self.setup_gui(str_edit, get_view("text"))

            self.assertEqual(str_edit.value, "three, four")

            set_text_in_line_edit(line_edit, "one, two")
            gui.process_events()

            self.assertEqual(str_edit.value, "one, two")
