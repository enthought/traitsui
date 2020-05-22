import platform
import unittest

from pyface.gui import GUI

from traits.api import Enum, HasTraits, Int, List
from traitsui.api import EnumEditor, UItem, View
from traitsui.tests._tools import (
    is_current_backend_qt4,
    is_current_backend_wx,
    skip_if_null,
    store_exceptions_on_all_threads,
)


is_windows = platform.system() == "Windows"


class EnumModel(HasTraits):

    value = Enum("one", "two", "three", "four")


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


def get_combobox_text(combobox):
    """ Return the text given a combobox control """
    if is_current_backend_wx():
        import wx

        if isinstance(combobox, wx.Choice):
            return combobox.GetString(combobox.GetSelection())
        else:
            return combobox.GetValue()
    elif is_current_backend_qt4():
        return combobox.currentText()


def set_combobox_text(combobox, text):
    """ Set the text given a combobox control """
    if is_current_backend_wx():
        import wx

        if isinstance(combobox, wx.Choice):
            event_type = wx.EVT_CHOICE.typeId
            event = wx.CommandEvent(event_type, combobox.GetId())
            event.SetString(text)
            wx.PostEvent(combobox, event)
        else:
            combobox.SetValue(text)
            event_type = wx.EVT_COMBOBOX.typeId
            event = wx.CommandEvent(event_type, combobox.GetId())
            event.SetString(text)
            wx.PostEvent(combobox, event)

    elif is_current_backend_qt4():
        combobox.setEditText(text)


def set_combobox_index(combobox, idx):
    """ Set the choice index given a combobox control and index number """
    if is_current_backend_wx():
        import wx

        if isinstance(combobox, wx.Choice):
            event_type = wx.EVT_CHOICE.typeId
        else:
            event_type = wx.EVT_COMBOBOX.typeId
        event = wx.CommandEvent(event_type, combobox.GetId())
        text = combobox.GetString(idx)
        event.SetString(text)
        event.SetInt(idx)
        wx.PostEvent(combobox, event)

    elif is_current_backend_qt4():
        combobox.setCurrentIndex(idx)


def finish_combobox_text_entry(combobox):
    """ Finish text entry given combobox. """
    if is_current_backend_wx():
        import wx

        event = wx.CommandEvent(wx.EVT_TEXT_ENTER.typeId, combobox.GetId())
        wx.PostEvent(combobox, event)

    elif is_current_backend_qt4():
        combobox.lineEdit().editingFinished.emit()


def get_all_button_status(widget):
    """ Gets status of all radio buttons in the layout of a given widget."""
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


def click_radio_button(widget, button_idx):
    """ Simulate a radio button click given widget and button number."""
    if is_current_backend_wx():
        import wx

        sizer_items = widget.GetSizer().GetChildren()
        button = sizer_items[button_idx].GetWindow()
        event = wx.CommandEvent(wx.EVT_RADIOBUTTON.typeId, button.GetId())
        event.SetEventObject(button)
        wx.PostEvent(widget, event)

    elif is_current_backend_qt4():
        widget.layout().itemAt(button_idx).widget().click()


def get_list_widget_text(list_widget):
    """ Return the text of currently selected item in given list widget. """
    if is_current_backend_wx():
        selected_item_idx = list_widget.GetSelection()
        return list_widget.GetString(selected_item_idx)

    elif is_current_backend_qt4():
        return list_widget.currentItem().text()


def set_list_widget_selected_index(list_widget, idx):
    """ Set the choice index given a list widget control and index number. """
    if is_current_backend_wx():
        import wx

        list_widget.SetSelection(idx)
        event = wx.CommandEvent(wx.EVT_LISTBOX.typeId, list_widget.GetId())
        wx.PostEvent(list_widget, event)

    elif is_current_backend_qt4():
        list_widget.setCurrentRow(idx)


class TestEnumEditorMapping(unittest.TestCase):

    def setup_ui(self, model, view):
        ui = model.edit_traits(view=view)
        self.addCleanup(ui.dispose)
        return ui.get_editors("value")[0]

    def check_enum_mappings_value_change(self, style, mode):
        class IntEnumModel(HasTraits):
            value = Int()

        enum_editor_factory = EnumEditor(
            values=[0, 1],
            format_func=lambda v: str(bool(v)).upper(),
            mode=mode
        )
        formatted_view = View(
            UItem(
                "value",
                editor=enum_editor_factory,
                style=style,
            )
        )

        with store_exceptions_on_all_threads():
            editor = self.setup_ui(IntEnumModel(), formatted_view)

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

            enum_editor_factory.values = [1, 0]

            self.assertEqual(editor.names, ["TRUE", "FALSE"])
            self.assertEqual(editor.mapping, {"TRUE": 1, "FALSE": 0})
            self.assertEqual(
                editor.inverse_mapping, {1: "TRUE", 0: "FALSE"}
            )

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
                    mode=mode
                ),
                style=style,
            )
        )
        model = IntEnumModel()

        with store_exceptions_on_all_threads():
            editor = self.setup_ui(model, formatted_view)

            if is_current_backend_wx():  # FIXME issue #835
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

            if is_current_backend_wx():  # FIXME issue #835
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
    def test_simple_editor_mapping_values(self):
        self.check_enum_mappings_value_change("simple", "radio")

    @skip_if_null
    def test_simple_editor_mapping_name(self):
        self.check_enum_mappings_name_change("simple", "radio")

    @skip_if_null
    def test_radio_editor_mapping_values(self):
        if is_current_backend_wx():  # FIXME
            import wx

            with self.assertRaises(wx._core.wxAssertionError):
                self.check_enum_mappings_value_change("custom", "radio")
        else:
            self.check_enum_mappings_value_change("custom", "radio")

    @skip_if_null
    def test_radio_editor_mapping_name(self):
        if is_current_backend_wx():  # FIXME
            import wx

            with self.assertRaises(wx._core.wxAssertionError):
                self.check_enum_mappings_name_change("custom", "radio")
        else:
            self.check_enum_mappings_name_change("custom", "radio")

    @skip_if_null
    def test_list_editor_mapping_values(self):
        self.check_enum_mappings_value_change("custom", "list")

    @skip_if_null
    def test_list_editor_mapping_name(self):
        self.check_enum_mappings_name_change("custom", "list")


class TestSimpleEnumEditor(unittest.TestCase):

    def setup_gui(self, model, view):
        gui = GUI()
        ui = model.edit_traits(view=view)
        self.addCleanup(ui.dispose)

        gui.process_events()
        editor = ui.get_editors("value")[0]
        combobox = editor.control

        return gui, combobox

    def check_enum_text_update(self, view):
        enum_edit = EnumModel()

        with store_exceptions_on_all_threads():
            gui, combobox = self.setup_gui(enum_edit, view)

            self.assertEqual(get_combobox_text(combobox), "one")

            enum_edit.value = "two"
            gui.process_events()

            self.assertEqual(get_combobox_text(combobox), "two")

    def check_enum_object_update(self, view):
        enum_edit = EnumModel()

        with store_exceptions_on_all_threads():
            gui, combobox = self.setup_gui(enum_edit, view)

            self.assertEqual(enum_edit.value, "one")

            set_combobox_text(combobox, "two")
            gui.process_events()

            self.assertEqual(enum_edit.value, "two")

    def check_enum_index_update(self, view):
        enum_edit = EnumModel()

        with store_exceptions_on_all_threads():
            gui, combobox = self.setup_gui(enum_edit, view)

            self.assertEqual(enum_edit.value, "one")

            set_combobox_index(combobox, 1)
            gui.process_events()

            self.assertEqual(enum_edit.value, "two")

    def check_enum_text_bad_update(self, view):
        enum_edit = EnumModel()

        with store_exceptions_on_all_threads():
            gui, combobox = self.setup_gui(enum_edit, view)

            self.assertEqual(enum_edit.value, "one")

            set_combobox_text(combobox, "t")
            gui.process_events()

            self.assertEqual(enum_edit.value, "one")

    @skip_if_null
    def test_simple_enum_editor_text(self):
        self.check_enum_text_update(get_view("simple"))

    @skip_if_null
    def test_simple_enum_editor_index(self):
        self.check_enum_index_update(get_view("simple"))

    @skip_if_null
    @unittest.skipIf(is_windows, "Test needs fixing on windows")
    def test_simple_evaluate_editor_text(self):
        self.check_enum_text_update(get_evaluate_view("simple"))

    @skip_if_null
    @unittest.skipIf(is_windows, "Test needs fixing on windows")
    def test_simple_evaluate_editor_index(self):
        self.check_enum_index_update(get_evaluate_view("simple"))

    @skip_if_null
    def test_simple_evaluate_editor_bad_text(self):
        self.check_enum_text_bad_update(get_evaluate_view("simple"))

    @skip_if_null
    @unittest.skipIf(is_windows, "Test needs fixing on windows")
    def test_simple_evaluate_editor_object(self):
        self.check_enum_object_update(get_evaluate_view("simple"))

    @skip_if_null
    def test_simple_evaluate_editor_object_no_auto_set(self):
        view = get_evaluate_view("simple", auto_set=False)
        enum_edit = EnumModel()

        with store_exceptions_on_all_threads():
            gui, combobox = self.setup_gui(enum_edit, view)

            self.assertEqual(enum_edit.value, "one")

            set_combobox_text(combobox, "two")
            gui.process_events()

            # wx modifies the value without the need to finish entry
            if is_current_backend_qt4():
                self.assertEqual(enum_edit.value, "one")

                finish_combobox_text_entry(combobox)
                gui.process_events()

            self.assertEqual(enum_edit.value, "two")

    @skip_if_null
    def test_simple_editor_resizable(self):
        # Smoke test for `qt4.enum_editor.SimpleEditor.set_size_policy`
        enum_edit = EnumModel()
        resizable_view = View(UItem("value", style="simple", resizable=True))

        with store_exceptions_on_all_threads():
            ui = enum_edit.edit_traits(view=resizable_view)
            self.addCleanup(ui.dispose)

    def test_simple_editor_rebuild_editor_evaluate(self):
        # Smoke test for `wx.enum_editor.SimpleEditor.rebuild_editor`
        enum_editor_factory = EnumEditor(
            evaluate=True,
            values=["one", "two", "three", "four"],
        )
        view = View(UItem("value", editor=enum_editor_factory, style="simple"))

        with store_exceptions_on_all_threads():
            gui, combobox = self.setup_gui(EnumModel(), view)

            enum_editor_factory.values = ["one", "two", "three"]


class TestRadioEnumEditor(unittest.TestCase):

    def setup_gui(self, model, view):
        gui = GUI()
        ui = model.edit_traits(view=view)
        self.addCleanup(ui.dispose)

        gui.process_events()
        editor = ui.get_editors("value")[0]
        widget = editor.control

        return gui, widget

    @skip_if_null
    def test_radio_enum_editor_button_update(self):
        enum_edit = EnumModel()

        with store_exceptions_on_all_threads():
            gui, widget = self.setup_gui(enum_edit, get_view("custom"))

            # The layout is: one, three, four \n two
            self.assertEqual(
                get_all_button_status(widget), [True, False, False, False]
            )

            enum_edit.value = "two"
            gui.process_events()

            self.assertEqual(
                get_all_button_status(widget), [False, False, False, True]
            )

    @skip_if_null
    def test_radio_enum_editor_pick(self):
        enum_edit = EnumModel()

        with store_exceptions_on_all_threads():
            gui, widget = self.setup_gui(enum_edit, get_view("custom"))

            self.assertEqual(enum_edit.value, "one")

            # The layout is: one, three, four \n two
            click_radio_button(widget, 3)
            gui.process_events()

            self.assertEqual(enum_edit.value, "two")


class TestListEnumEditor(unittest.TestCase):

    def setup_gui(self, model, view):
        gui = GUI()
        ui = model.edit_traits(view=view)
        self.addCleanup(ui.dispose)

        gui.process_events()
        editor = ui.get_editors("value")[0]
        list_widget = editor.control

        return gui, list_widget

    def check_enum_text_update(self, view):
        enum_edit = EnumModel()

        with store_exceptions_on_all_threads():
            gui, list_widget = self.setup_gui(enum_edit, view)

            self.assertEqual(get_list_widget_text(list_widget), "one")

            enum_edit.value = "two"
            gui.process_events()

            self.assertEqual(get_list_widget_text(list_widget), "two")

    def check_enum_index_update(self, view):
        enum_edit = EnumModel()

        with store_exceptions_on_all_threads():
            gui, list_widget = self.setup_gui(enum_edit, view)

            self.assertEqual(enum_edit.value, "one")

            set_list_widget_selected_index(list_widget, 1)
            gui.process_events()

            self.assertEqual(enum_edit.value, "two")

    @skip_if_null
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

    @skip_if_null
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

    @skip_if_null
    def test_list_evaluate_editor_text(self):
        self.check_enum_text_update(get_evaluate_view("custom", mode="list"))

    @skip_if_null
    def test_list_evaluate_editor_index(self):
        self.check_enum_index_update(get_evaluate_view("custom", mode="list"))
