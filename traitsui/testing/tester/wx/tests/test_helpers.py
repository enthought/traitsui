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
