import unittest
from unittest import mock

from pyface.gui import GUI
from traitsui.tests._tools import (
    is_qt,
    requires_toolkit,
    ToolkitName,
)
from traitsui.testing import command, locator, query
from traitsui.testing.exceptions import Disabled
from traitsui.testing.tests._tools import (
    create_interactor,
)
from traitsui.testing.ui_tester import UIWrapper

try:
    from pyface.qt import QtCore, QtGui
    from traitsui.testing.qt4 import default_registry
    from traitsui.testing.qt4 import helpers
except ImportError:
    if is_qt():
        raise


@requires_toolkit([ToolkitName.qt])
class TestInteractorAction(unittest.TestCase):

    def test_mouse_click(self):
        button = QtGui.QPushButton()
        click_slot = mock.Mock()
        button.clicked.connect(click_slot)

        wrapper = wrapper = UIWrapper(
            editor=button,
            registries=[default_registry.get_default_registry()],
        )

        wrapper.perform(command.MouseClick())

        self.assertEqual(click_slot.call_count, 1)

    def test_mouse_click_disabled(self):
        button = QtGui.QPushButton()
        button.setEnabled(False)

        click_slot = mock.Mock()
        button.clicked.connect(click_slot)

        wrapper = wrapper = UIWrapper(
            editor=button,
            registries=[default_registry.get_default_registry()],
        )

        # when
        # clicking won't fail, it just does not do anything.
        # This is consistent with the actual UI.
        wrapper.perform(command.MouseClick())

        # then
        self.assertEqual(click_slot.call_count, 0)

    def test_key_sequence(self):
        textbox = QtGui.QLineEdit()
        change_slot = mock.Mock()
        textbox.textEdited.connect(change_slot)
        wrapper = create_interactor(editor=textbox)

        # when
        default_registry.key_sequence_qwidget(
            wrapper, command.KeySequence("abc"))

        # then
        self.assertEqual(textbox.text(), "abc")
        # each keystroke fires a signal
        self.assertEqual(change_slot.call_count, 3)

    def test_key_sequence_disabled(self):
        textbox = QtGui.QLineEdit()
        textbox.setEnabled(False)
        wrapper = create_interactor(editor=textbox)

        # then
        # this will fail, because one should not be allowed to set
        # cursor on the widget to type anything
        with self.assertRaises(Disabled):
            default_registry.key_sequence_qwidget(
                wrapper, command.KeySequence("abc"))

    def test_key_press(self):
        textbox = QtGui.QLineEdit()
        change_slot = mock.Mock()
        textbox.editingFinished.connect(change_slot)
        wrapper = create_interactor(editor=textbox)

        # sanity check
        default_registry.key_sequence_qwidget(
            wrapper, command.KeySequence("abc"))
        self.assertEqual(change_slot.call_count, 0)

        default_registry.key_press_qwidget(
            wrapper, command.KeyClick("Enter"))
        self.assertEqual(change_slot.call_count, 1)

    def test_key_press_disabled(self):
        textbox = QtGui.QLineEdit()
        textbox.setEnabled(False)
        change_slot = mock.Mock()
        textbox.editingFinished.connect(change_slot)
        wrapper = create_interactor(editor=textbox)

        with self.assertRaises(Disabled):
            default_registry.key_press_qwidget(
                wrapper, command.KeyClick("Enter"))
        self.assertEqual(change_slot.call_count, 0)

    def test_mouse_click_combobox(self):
        combobox = QtGui.QComboBox()
        combobox.addItems(["a", "b", "c"])
        change_slot = mock.Mock()
        combobox.currentIndexChanged.connect(change_slot)

        # when
        helpers.mouse_click_combobox(combobox=combobox, index=1)

        # then
        self.assertEqual(change_slot.call_count, 1)
        (index, ), _ = change_slot.call_args_list[0]
        self.assertEqual(index, 1)

    def test_mouse_click_combobox_index_out_of_range(self):
        combobox = QtGui.QComboBox()
        combobox.addItems(["a", "b", "c"])
        change_slot = mock.Mock()
        combobox.currentIndexChanged.connect(change_slot)

        # when
        with self.assertRaises(LookupError):
            helpers.mouse_click_combobox(combobox=combobox, index=10)

        # then
        self.assertEqual(change_slot.call_count, 0)

    def test_mouse_click_combobox_different_model(self):
        # Test with a different item model
        item_model = QtGui.QStringListModel()
        combobox = QtGui.QComboBox()
        combobox.setModel(item_model)
        combobox.addItems(["a", "b", "c"])
        change_slot = mock.Mock()
        combobox.currentIndexChanged.connect(change_slot)

        # when
        helpers.mouse_click_combobox(combobox=combobox, index=1)

        # then
        self.assertEqual(change_slot.call_count, 1)
        self.assertEqual(combobox.currentIndex(), 1)


@requires_toolkit([ToolkitName.qt])
class TestHelperIndexedLayout(unittest.TestCase):

    def test_mouse_click_list_layout(self):
        widget = QtGui.QWidget()
        layout = QtGui.QGridLayout(widget)
        button0 = QtGui.QPushButton()
        button0_clicked = mock.Mock()
        button0.clicked.connect(button0_clicked)
        button1 = QtGui.QPushButton()
        button1_clicked = mock.Mock()
        button1.clicked.connect(button1_clicked)
        layout.addWidget(button0, 0, 0)
        layout.addWidget(button1, 1, 0)

        # when
        helpers.mouse_click_qlayout(layout, 1)

        # then
        self.assertEqual(button0_clicked.call_count, 0)
        self.assertEqual(button1_clicked.call_count, 1)


@requires_toolkit([ToolkitName.qt])
class TestHelperIndexedItemView(unittest.TestCase):

    def setUp(self):
        self.widget = QtGui.QListWidget()
        self.items = ["a", "b", "c"]
        self.widget.addItems(self.items)

        self.good_q_index = self.widget.model().index(1, 0)
        self.bad_q_index = self.widget.model().index(10, 0)

        self.model = self.widget.model()

    def test_mouse_click_list_widget_item_view(self):
        change_slot = mock.Mock()
        self.widget.currentTextChanged.connect(change_slot)

        # when
        helpers.mouse_click_item_view(
            model=self.model,
            view=self.widget,
            index=self.good_q_index,
        )

        # then
        self.assertEqual(change_slot.call_count, 1)
        (text, ), _ = change_slot.call_args_list[0]
        self.assertEqual(text, "b")

    def test_mouse_click_list_widget_item_view_out_of_range(self):
        change_slot = mock.Mock()
        self.widget.currentTextChanged.connect(change_slot)

        # when
        with self.assertRaises(LookupError):
            helpers.mouse_click_item_view(
                model=self.model,
                view=self.widget,
                index=self.bad_q_index,
            )

        # then
        self.assertEqual(change_slot.call_count, 0)

    def test_key_sequence_list_widget_item_view_disabled(self):

        # by default the item is not editable
        with self.assertRaises(Disabled) as exception_context:
            helpers.key_sequence_item_view(
                model=self.model,
                view=self.widget,
                index=self.good_q_index,
                sequence="a",
            )
        self.assertEqual(
            str(exception_context.exception),
            "No editable widget for item at row 1 and column 0",
        )

    def test_key_press_list_widget_item_view_disabled(self):

        # by default the item is not editable
        with self.assertRaises(Disabled) as exception_context:
            helpers.key_press_item_view(
                model=self.model,
                view=self.widget,
                index=self.good_q_index,
                key="Enter",
            )
        self.assertEqual(
            str(exception_context.exception),
            "No editable widget for item at row 1 and column 0",
        )

    def test_key_sequence_and_press_list_widget_item_view(self):
        for index in range(self.widget.count()):
            item = self.widget.item(index)
            item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)

        target_item = self.widget.item(1)
        self.widget.setCurrentItem(target_item)
        self.widget.editItem(target_item)

        # when
        helpers.key_sequence_item_view(
            model=self.model,
            view=self.widget,
            index=self.good_q_index,
            sequence="\bd",
        )
        helpers.key_press_item_view(
            model=self.model,
            view=self.widget,
            index=self.good_q_index,
            key="Enter",
        )
        # this needs an extra kick. The tester will do this too.
        GUI.process_events()

        # then
        self.assertEqual(self.widget.item(1).text(), "d")

    def test_get_displayed_text_list_widget_item_view(self):
        # when
        actual = helpers.get_display_text_item_view(
            model=self.model,
            view=self.widget,
            index=self.good_q_index,
        )
        # then
        self.assertEqual(actual, "b")
