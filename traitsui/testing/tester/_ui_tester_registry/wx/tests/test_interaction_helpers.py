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

from traitsui.testing.tester import command
from traitsui.testing.tester.exceptions import Disabled
from traitsui.testing.tester._ui_tester_registry.wx import _interaction_helpers

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
        _interaction_helpers.mouse_click_button(control=button, delay=0)

        # then
        self.assertEqual(handler.call_count, 1)

    def test_mouse_click_disabled_button(self):
        handler = mock.Mock()
        button = wx.Button(self.frame)
        button.Bind(wx.EVT_BUTTON, handler)
        button.Enable(False)

        # when
        _interaction_helpers.mouse_click_button(control=button, delay=0)

        # then
        self.assertEqual(handler.call_count, 0)

    def test_mouse_click_None_warns(self):
        control = None
        with self.assertWarns(UserWarning):
            _interaction_helpers.mouse_click_button(control=control, delay=0)

    def test_key_sequence(self):
        # The insertion point is moved to the end
        textbox = wx.TextCtrl(self.frame)
        textbox.SetValue("123")
        handler = mock.Mock()
        textbox.Bind(wx.EVT_TEXT, handler)

        _interaction_helpers.key_sequence_text_ctrl(
            textbox, command.KeySequence("abc"), 0
        )

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
                _interaction_helpers.key_sequence_text_ctrl(
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
            _interaction_helpers.key_sequence_text_ctrl(
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
            _interaction_helpers.key_sequence_text_ctrl(
                textbox, command.KeySequence("abc"), 0
            )

    def test_key_click(self):
        textbox = wx.TextCtrl(self.frame)
        handler = mock.Mock()
        textbox.Bind(wx.EVT_TEXT, handler)

        _interaction_helpers.key_click_text_entry(
            textbox, command.KeyClick("A"), 0
        )

        self.assertEqual(textbox.Value, "A")
        self.assertEqual(handler.call_count, 1)

    def test_key_click_backspace(self):
        textbox = wx.TextCtrl(self.frame)
        textbox.SetValue("A")
        handler = mock.Mock()
        textbox.Bind(wx.EVT_TEXT, handler)

        _interaction_helpers.key_click_text_entry(
            textbox, command.KeyClick("Backspace"), 0
        )

        self.assertEqual(textbox.Value, "")
        self.assertEqual(handler.call_count, 1)

    def test_key_click_backspace_with_selection(self):
        textbox = wx.TextCtrl(self.frame)
        textbox.SetFocus()
        textbox.SetValue("ABCDE")
        textbox.SetSelection(0, 4)
        # sanity check
        self.assertEqual(textbox.GetStringSelection(), "ABCD")

        handler = mock.Mock()
        textbox.Bind(wx.EVT_TEXT, handler)

        _interaction_helpers.key_click_text_entry(
            textbox, command.KeyClick("Backspace"), 0
        )

        self.assertEqual(textbox.Value, "E")
        self.assertEqual(handler.call_count, 1)

    def test_key_click_end(self):
        textbox = wx.TextCtrl(self.frame)
        textbox.SetValue("ABCDE")
        textbox.SetInsertionPoint(0)

        # sanity check
        self.assertEqual(textbox.GetInsertionPoint(), 0)

        _interaction_helpers.key_click_text_entry(
            textbox, command.KeyClick("End"), 0
        )
        _interaction_helpers.key_click_text_entry(
            textbox, command.KeyClick("F"), 0
        )

        self.assertEqual(textbox.Value, "ABCDEF")

    def test_key_click_disabled(self):
        textbox = wx.TextCtrl(self.frame)
        textbox.SetEditable(False)

        with self.assertRaises(Disabled):
            _interaction_helpers.key_click_text_entry(
                textbox, command.KeyClick("Enter"), 0
            )

    def test_key_click_slider_helpful_err(self):
        slider = wx.Slider()
        with self.assertRaises(ValueError) as exc:
            _interaction_helpers.key_click_slider(
                slider, command.KeyClick("Enter"), 0
            )
        self.assertIn(
            "['Down', 'Left', 'Page Down', 'Page Up', 'Right', 'Up']",
            str(exc.exception),
        )
