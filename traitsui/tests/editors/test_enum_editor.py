import platform
import unittest

from pyface.gui import GUI

from traits.api import Enum, HasTraits
from traitsui.api import EnumEditor, UItem, View
from traitsui.tests._tools import (
    is_current_backend_qt4, is_current_backend_wx, skip_if_null,
    store_exceptions_on_all_threads)


is_windows = (platform.system() == 'Windows')


class EnumModel(HasTraits):

    value = Enum('one', 'two', 'three', 'four')


simple_view = View(
    UItem('value', style='simple'),
    resizable=True
)


simple_evaluate_view = View(
    UItem(
        'value',
        editor=EnumEditor(evaluate=True, values=['one', 'two', 'three', 'four']),
        style='simple'),
    resizable=True
)


simple_evaluate_view_popup = View(
    UItem(
        'value',
        editor=EnumEditor(evaluate=True, values=['one', 'two', 'three', 'four']),
        style='simple'),
    resizable=True
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


class TestEnumEditor(unittest.TestCase):

    def check_enum_text_update(self, view):
        gui = GUI()
        enum_edit = EnumModel()

        with store_exceptions_on_all_threads():
            ui = enum_edit.edit_traits(view=view)
            self.addCleanup(ui.dispose)

            gui.process_events()
            editor = ui.get_editors("value")[0]
            combobox = editor.control

            self.assertEqual(get_combobox_text(combobox), "one")

            enum_edit.value = "two"
            gui.process_events()

            self.assertEqual(get_combobox_text(combobox), "two")

    def check_enum_object_update(self, view):
        gui = GUI()
        enum_edit = EnumModel()

        with store_exceptions_on_all_threads():
            ui = enum_edit.edit_traits(view=view)
            self.addCleanup(ui.dispose)

            gui.process_events()
            editor = ui.get_editors("value")[0]
            combobox = editor.control

            self.assertEqual(enum_edit.value, "one")

            set_combobox_text(combobox, "two")
            gui.process_events()

            self.assertEqual(enum_edit.value, "two")

    def check_enum_index_update(self, view):
        gui = GUI()
        enum_edit = EnumModel()

        with store_exceptions_on_all_threads():
            ui = enum_edit.edit_traits(view=view)
            self.addCleanup(ui.dispose)

            gui.process_events()
            editor = ui.get_editors("value")[0]
            combobox = editor.control

            self.assertEqual(enum_edit.value, "one")

            set_combobox_index(combobox, 1)
            gui.process_events()

            self.assertEqual(enum_edit.value, "two")

    def check_enum_text_bad_update(self, view):
        gui = GUI()
        enum_edit = EnumModel()

        with store_exceptions_on_all_threads():
            ui = enum_edit.edit_traits(view=view)
            self.addCleanup(ui.dispose)

            gui.process_events()
            editor = ui.get_editors("value")[0]
            combobox = editor.control

            self.assertEqual(enum_edit.value, "one")

            set_combobox_text(combobox, "t")
            gui.process_events()

            self.assertEqual(enum_edit.value, "one")

    @skip_if_null
    def test_simple_enum_editor_text(self):
        self.check_enum_text_update(simple_view)

    @skip_if_null
    def test_simple_enum_editor_index(self):
        self.check_enum_index_update(simple_view)

    @skip_if_null
    @unittest.skipIf(is_windows, "Test needs fixing on windows")
    def test_simple_evaluate_editor_text(self):
        self.check_enum_text_update(simple_evaluate_view)

    @skip_if_null
    @unittest.skipIf(is_windows, "Test needs fixing on windows")
    def test_simple_evaluate_editor_index(self):
        self.check_enum_index_update(simple_evaluate_view)

    @skip_if_null
    def test_simple_evaluate_editor_bad_text(self):
        self.check_enum_text_bad_update(simple_evaluate_view)

    @skip_if_null
    @unittest.skipIf(is_windows, "Test needs fixing on windows")
    def test_simple_evaluate_editor_object(self):
        self.check_enum_object_update(simple_evaluate_view)

    @skip_if_null
    @unittest.skipIf(is_windows, "Test needs fixing on windows")
    def test_simple_evaluate_popup_editor_text(self):
        self.check_enum_text_update(simple_evaluate_view_popup)

    @skip_if_null
    @unittest.skipIf(is_windows, "Test needs fixing on windows")
    def test_simple_evaluate_popup_editor_index(self):
        self.check_enum_index_update(simple_evaluate_view_popup)

    @skip_if_null
    def test_simple_evaluate_popup_editor_bad_text(self):
        self.check_enum_text_bad_update(simple_evaluate_view_popup)

    @skip_if_null
    @unittest.skipIf(is_windows, "Test needs fixing on windows")
    def test_simple_evaluate_popup_editor_object(self):
        self.check_enum_object_update(simple_evaluate_view_popup)
