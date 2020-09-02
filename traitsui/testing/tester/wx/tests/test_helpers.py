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
        # The insertion point is moved to the end
        textbox = wx.TextCtrl(self.frame)
        textbox.SetValue("123")
        handler = mock.Mock()
        textbox.Bind(wx.EVT_TEXT, handler)

        helpers.key_sequence_text_ctrl(textbox, command.KeySequence("abc"), 0)

        self.assertEqual(textbox.GetValue(), "123abc")
        self.assertEqual(handler.call_count, 3)

    def test_key_sequence_with_unicode(self):
        handler = mock.Mock()
        textbox = wx.TextCtrl(self.frame)
        textbox.Bind(wx.EVT_TEXT, handler)
        # This range is supported by Qt
        for code in range(32, 127):
            with self.subTest(code=code, word=chr(code)):
                textbox.Clear()
                handler.reset_mock()

                # when
                helpers.key_sequence_text_ctrl(
                    textbox,
                    command.KeySequence(chr(code) * 3),
                    delay=0,
                )

                # then
                self.assertEqual(textbox.Value, chr(code) * 3)
                self.assertEqual(handler.call_count, 3)

    def test_key_sequence_with_backspace_unsupported(self):
        textbox = wx.TextCtrl(self.frame)

        with self.assertRaises(ValueError) as exception_context:
            helpers.key_sequence_text_ctrl(
                textbox, command.KeySequence("\b"), 0
            )

        self.assertIn(
            "is currently not supported.",
            str(exception_context.exception),
        )

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
