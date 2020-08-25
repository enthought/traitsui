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

from traitsui.testing.tester import command
from traitsui.testing.tester.ui_wrapper import UIWrapper

from traitsui.tests._tools import (
    is_wx,
    requires_toolkit,
    ToolkitName,
)

try:
    import wx
    from traitsui.testing.tester.wx import default_registry
except ImportError:
    if is_wx():
        raise


@requires_toolkit([ToolkitName.wx])
class TestInteractions(unittest.TestCase):

    def setUp(self):
        self.app = wx.App()
        self.frame = wx.Frame(None)
        self.frame.Show()

    def tearDown(self):
        wx.CallAfter(self.app.ExitMainLoop)
        self.app.MainLoop()

    def test_mouse_click(self):
        handler = mock.Mock()
        button = wx.Button(self.frame)
        button.Bind(wx.EVT_BUTTON, handler)
        wrapper = UIWrapper(
            target=button,
            registries=[default_registry.get_default_registry()],
        )

        # when
        wrapper.perform(command.MouseClick())

        # then
        self.assertEqual(handler.call_count, 1)

    def test_mouse_click_disabled_button(self):
        handler = mock.Mock()
        button = wx.Button(self.frame)
        button.Bind(wx.EVT_BUTTON, handler)
        button.Enable(False)
        wrapper = UIWrapper(
            target=button,
            registries=[default_registry.get_default_registry()],
        )

        # when
        wrapper.perform(command.MouseClick())

        # then
        self.assertEqual(handler.call_count, 0)

    def test_key_sequence(self):
        textbox = wx.TextCtrl()

        wrapper = UIWrapper(
            target=textbox,
            registries=[default_registry.get_default_registry()],
        )

        wrapper.perform(command.KeySequence("abc"))

        self.assertEqual(textbox.value, "abc")



"""def test_key_sequence(self):
        textbox = QtGui.QLineEdit()
        change_slot = mock.Mock()
        textbox.textEdited.connect(change_slot)

        wrapper = UIWrapper(
            target=textbox,
            registries=[default_registry.get_default_registry()],
        )

        # when
        wrapper.perform(command.KeySequence("abc"))
        # then
        self.assertEqual(textbox.text(), "abc")
        # each keystroke fires a signal
        self.assertEqual(change_slot.call_count, 3)


    def test_key_sequence_disabled(self):
        textbox = QtGui.QLineEdit()
        textbox.setEnabled(False)

        wrapper = UIWrapper(
            target=textbox,
            registries=[default_registry.get_default_registry()],
        )
        
        # then
        # this will fail, because one should not be allowed to set
        # cursor on the widget to type anything
        with self.assertRaises(Disabled):
            wrapper.perform(command.KeySequence("abc"))


    def test_key_click(self):
        textbox = QtGui.QLineEdit()
        change_slot = mock.Mock()
        textbox.editingFinished.connect(change_slot)
        wrapper = UIWrapper(
            target=textbox,
            registries=[default_registry.get_default_registry()],
        )
        # sanity check
        wrapper.perform(command.KeySequence("abc"))
        self.assertEqual(change_slot.call_count, 0)

        wrapper.perform(command.KeyClick("Enter"))
        self.assertEqual(change_slot.call_count, 1)


    def test_key_click_disabled(self):
        textbox = QtGui.QLineEdit()
        textbox.setEnabled(False)
        change_slot = mock.Mock()
        textbox.editingFinished.connect(change_slot)
        wrapper = UIWrapper(
            target=textbox,
            registries=[default_registry.get_default_registry()],
        )

        with self.assertRaises(Disabled):
            wrapper.perform(command.KeyClick("Enter"))
        self.assertEqual(change_slot.call_count, 0)"""
