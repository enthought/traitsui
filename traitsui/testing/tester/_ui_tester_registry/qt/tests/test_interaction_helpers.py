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
from unittest import mock

from traitsui.tests._tools import (
    is_qt,
    requires_toolkit,
    ToolkitName,
)
from traitsui.testing.tester import command
from traitsui.testing.tester.exceptions import Disabled
from traitsui.testing.tester._ui_tester_registry.qt import (
    _interaction_helpers,
)

try:
    from pyface.qt import QtGui
except ImportError:
    if is_qt():
        raise


@requires_toolkit([ToolkitName.qt])
class TestInteractions(unittest.TestCase):
    def test_mouse_click(self):
        button = QtGui.QPushButton()
        click_slot = mock.Mock()
        button.clicked.connect(lambda checked: click_slot(checked))

        _interaction_helpers.mouse_click_qwidget(button, 0)

        self.assertEqual(click_slot.call_count, 1)

    def test_mouse_click_disabled(self):
        button = QtGui.QPushButton()
        button.setEnabled(False)

        click_slot = mock.Mock()
        # pyside6 can't connect to a mock
        button.clicked.connect(lambda checked: click_slot(checked))

        # when
        # clicking won't fail, it just does not do anything.
        # This is consistent with the actual UI.
        _interaction_helpers.mouse_click_qwidget(button, 0)

        # then
        self.assertEqual(click_slot.call_count, 0)

    def test_mouse_click_combobox_warns(self):
        combo = None
        with self.assertWarns(UserWarning):
            _interaction_helpers.mouse_click_combobox(combo, 0, 0)

    def test_key_sequence(self):
        # test on different Qwidget objects
        textboxes = [QtGui.QLineEdit(), QtGui.QTextEdit()]
        for i, textbox in enumerate(textboxes):
            with self.subTest(widget=textbox.__class__.__name__):
                change_slot = mock.Mock()
                textbox.textChanged.connect(lambda *args: change_slot(*args))

                # when
                _interaction_helpers.key_sequence_qwidget(
                    textbox, command.KeySequence("abc"), 0
                )

                # then
                if i == 0:
                    self.assertEqual(textbox.text(), "abc")
                else:
                    self.assertEqual(textbox.toPlainText(), "abc")
                # each keystroke fires a signal
                self.assertEqual(change_slot.call_count, 3)

        # for a QLabel, one can try a key sequence and nothing will happen
        textbox = QtGui.QLabel()
        _interaction_helpers.key_sequence_qwidget(
            textbox, command.KeySequence("abc"), 0
        )
        self.assertEqual(textbox.text(), "")

    def test_key_sequence_textbox_with_unicode(self):
        for code in range(32, 127):
            with self.subTest(code=code, word=chr(code)):
                textbox = QtGui.QLineEdit()
                change_slot = mock.Mock()
                textbox.textChanged.connect(lambda text: change_slot(text))

                # when
                _interaction_helpers.key_sequence_textbox(
                    textbox,
                    command.KeySequence(chr(code) * 3),
                    delay=0,
                )

                # then
                self.assertEqual(textbox.text(), chr(code) * 3)
                self.assertEqual(change_slot.call_count, 3)

    def test_key_sequence_unsupported_key(self):
        textbox = QtGui.QLineEdit()

        with self.assertRaises(ValueError) as exception_context:
            # QTest does not support this character.
            _interaction_helpers.key_sequence_textbox(
                textbox,
                command.KeySequence(chr(31)),
                delay=0,
            )

        self.assertIn(
            "is currently not supported.",
            str(exception_context.exception),
        )

    def test_key_sequence_backspace_character(self):
        # Qt does convert backspace character to the backspace key
        # But we disallow it for now to be consistent with wx.
        textbox = QtGui.QLineEdit()

        with self.assertRaises(ValueError) as exception_context:
            _interaction_helpers.key_sequence_textbox(
                textbox,
                command.KeySequence("\b"),
                delay=0,
            )

        self.assertIn(
            "is currently not supported.",
            str(exception_context.exception),
        )

    def test_key_sequence_insert_point_qlineedit(self):
        textbox = QtGui.QLineEdit()
        textbox.setText("123")

        # when
        _interaction_helpers.key_sequence_textbox(
            textbox,
            command.KeySequence("abc"),
            delay=0,
        )

        # then
        self.assertEqual(textbox.text(), "123abc")

    def test_key_sequence_insert_point_qtextedit(self):
        # The default insertion point moved to the end to be consistent
        # with QLineEdit
        textbox = QtGui.QTextEdit()
        textbox.setText("123")

        # when
        _interaction_helpers.key_sequence_textbox(
            textbox,
            command.KeySequence("abc"),
            delay=0,
        )

        # then
        self.assertEqual(textbox.toPlainText(), "123abc")

    def test_key_sequence_disabled(self):
        textbox = QtGui.QLineEdit()
        textbox.setEnabled(False)

        # this will fail, because one should not be allowed to set
        # cursor on the widget to type anything
        with self.assertRaises(Disabled):
            _interaction_helpers.key_sequence_qwidget(
                textbox, command.KeySequence("abc"), 0
            )

    def test_key_click(self):
        textbox = QtGui.QLineEdit()
        change_slot = mock.Mock()
        textbox.editingFinished.connect(lambda: change_slot())

        # sanity check on editingFinished signal
        _interaction_helpers.key_sequence_qwidget(
            textbox, command.KeySequence("abc"), 0
        )
        self.assertEqual(change_slot.call_count, 0)

        _interaction_helpers.key_click_qwidget(
            textbox, command.KeyClick("Enter"), 0
        )
        self.assertEqual(change_slot.call_count, 1)

        # test on a different Qwidget object - QtGui.QTextEdit()
        textbox = QtGui.QTextEdit()
        change_slot = mock.Mock()
        # Now "Enter" should not finish editing, but instead go to next line
        textbox.textChanged.connect(lambda: change_slot())
        _interaction_helpers.key_click_qwidget(
            textbox, command.KeyClick("Enter"), 0
        )
        # The textChanged event appears to be fired twice instead of once
        # on Windows/PySide6, for reasons as yet undetermined. But for our
        # purposes it's good enough that it's fired at all.
        # xref: enthought/traitsui#1895
        change_slot.assert_called()
        self.assertEqual(textbox.toPlainText(), "\n")

        # for a QLabel, one can try a key click and nothing will happen
        textbox = QtGui.QLabel()
        _interaction_helpers.key_click_qwidget(
            textbox, command.KeyClick("A"), 0
        )
        self.assertEqual(textbox.text(), "")

    def test_key_click_disabled(self):
        textbox = QtGui.QLineEdit()
        textbox.setEnabled(False)
        change_slot = mock.Mock()
        textbox.editingFinished.connect(lambda text: change_slot(text))

        with self.assertRaises(Disabled):
            _interaction_helpers.key_click_qwidget(
                textbox, command.KeyClick("Enter"), 0
            )
        self.assertEqual(change_slot.call_count, 0)

    def test_check_q_model_index_valid(self):
        self.widget = QtGui.QListWidget()
        self.items = ["a", "b", "c"]
        self.widget.addItems(self.items)
        self.good_q_index = self.widget.model().index(1, 0)
        self.bad_q_index = self.widget.model().index(10, 0)

        self.model = self.widget.model()
        _interaction_helpers.check_q_model_index_valid(self.good_q_index)
        with self.assertRaises(LookupError):
            _interaction_helpers.check_q_model_index_valid(self.bad_q_index)

    def test_key_click_q_slider_helpful_err(self):
        slider = QtGui.QSlider()
        with self.assertRaises(ValueError) as exc:
            _interaction_helpers.key_click_qslider(
                slider, command.KeyClick("Enter"), 0
            )
        self.assertIn(
            "['Down', 'Left', 'Page Down', 'Page Up', 'Right', 'Up']",
            str(exc.exception),
        )
