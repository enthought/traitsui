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
from traitsui.testing.tester.exceptions import Disabled
from traitsui.testing.tester.wx import helpers

from traitsui.tests._tools import (
    is_wx,
    requires_toolkit,
    ToolkitName,
)

try:
    import wx
except ImportError:
    if is_wx():
        raise


@requires_toolkit([ToolkitName.wx])
class TestInteractions(unittest.TestCase):

    def setUp(self):
        self.frame = wx.Frame(None)
        self.frame.Show()

    def tearDown(self):
        self.frame.Close()
        self.frame.Destroy()

    def test_mouse_click(self):
        handler = mock.Mock()
        button = wx.Button(self.frame)
        button.Bind(wx.EVT_BUTTON, handler)

        # when
        helpers.mouse_click_button(button, 0)

        # then
        self.assertEqual(handler.call_count, 1)

    def test_mouse_click_disabled_button(self):
        handler = mock.Mock()
        button = wx.Button(self.frame)
        button.Bind(wx.EVT_BUTTON, handler)
        button.Enable(False)

        # when
        helpers.mouse_click_button(button, 0)

        # then
        self.assertEqual(handler.call_count, 0)

    def test_key_sequence(self):
        textbox = wx.TextCtrl(self.frame)

        helpers.key_sequence_text_ctrl(textbox, command.KeySequence("abc"), 0)

        self.assertEqual(textbox.Value, "abc")

    def test_key_sequence_disabled(self):
        textbox = wx.TextCtrl(self.frame)
        textbox.SetEditable(False)

        with self.assertRaises(Disabled):
            helpers.key_sequence_text_ctrl(textbox,
                                           command.KeySequence("abc"),
                                           0)

    def test_key_click(self):
        textbox = wx.TextCtrl(self.frame)

        helpers.key_click_text_ctrl(textbox, command.KeyClick("A"), 0)
        self.assertEqual(textbox.Value, "A")
        helpers.key_click_text_ctrl(textbox, command.KeyClick("Backspace"), 0)
        self.assertEqual(textbox.Value, "")

    def test_key_click_disabled(self):
        textbox = wx.TextCtrl(self.frame)
        textbox.SetEditable(False)

        with self.assertRaises(Disabled):
            helpers.key_click_text_ctrl(textbox, command.KeyClick("Enter"), 0)
