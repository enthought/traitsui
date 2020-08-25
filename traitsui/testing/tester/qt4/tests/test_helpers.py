#  Copyright (c) 2005-2020, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#

import unittest
from unittest import mock

from traitsui.tests._tools import (
    is_qt,
    requires_toolkit,
    ToolkitName,
)
from traitsui.testing.tester import command
from traitsui.testing.tester.exceptions import Disabled
from traitsui.testing.tester.qt4 import helpers


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
        button.clicked.connect(click_slot)

        helpers.mouse_click_qwidget(button, 0)

        self.assertEqual(click_slot.call_count, 1)

    def test_mouse_click_disabled(self):
        button = QtGui.QPushButton()
        button.setEnabled(False)

        click_slot = mock.Mock()
        button.clicked.connect(click_slot)

        # when
        # clicking won't fail, it just does not do anything.
        # This is consistent with the actual UI.
        helpers.mouse_click_qwidget(button, 0)

        # then
        self.assertEqual(click_slot.call_count, 0)

    def test_key_sequence(self):
        textbox = QtGui.QLineEdit()
        change_slot = mock.Mock()
        textbox.textEdited.connect(change_slot)

        # when
        helpers.key_sequence_qwidget(textbox, command.KeySequence("abc"), 0)

        # then
        self.assertEqual(textbox.text(), "abc")
        # each keystroke fires a signal
        self.assertEqual(change_slot.call_count, 3)


    def test_key_sequence_disabled(self):
        textbox = QtGui.QLineEdit()
        textbox.setEnabled(False)
        
        # this will fail, because one should not be allowed to set
        # cursor on the widget to type anything
        with self.assertRaises(Disabled):
            helpers.key_sequence_qwidget(textbox, command.KeySequence("abc"), 0)


    def test_key_click(self):
        textbox = QtGui.QLineEdit()
        change_slot = mock.Mock()
        textbox.editingFinished.connect(change_slot)
        
        # sanity check
        helpers.key_sequence_qwidget(textbox, command.KeySequence("abc"), 0)
        self.assertEqual(change_slot.call_count, 0)

        helpers.key_click_qwidget(textbox, command.KeyClick("Enter"), 0)
        self.assertEqual(change_slot.call_count, 1)


    def test_key_click_disabled(self):
        textbox = QtGui.QLineEdit()
        textbox.setEnabled(False)
        change_slot = mock.Mock()
        textbox.editingFinished.connect(change_slot)


        with self.assertRaises(Disabled):
            helpers.key_click_qwidget(textbox, command.KeyClick("Enter"), 0)
        self.assertEqual(change_slot.call_count, 0)

