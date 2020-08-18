import unittest
from unittest import mock

from pyface.api import GUI
from traitsui.tests._tools import (
    is_wx,
    requires_toolkit,
    ToolkitName,
)
from traitsui.testing import command
from traitsui.testing.ui_tester import UIWrapper
from traitsui.testing.tests._tools import (
    create_interactor,
)

try:
    import wx
    from traitsui.testing.wx import default_registry
except ImportError:
    if is_wx():
        raise


@requires_toolkit([ToolkitName.wx])
class TestInteractorAction(unittest.TestCase):

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
        interactor = UIWrapper(
            editor=button,
            registries=[default_registry.get_default_registry()],
        )

        # when
        interactor.perform(command.MouseClick())

        # then
        self.assertEqual(handler.call_count, 1)

    def test_mouse_click_disabled_button(self):
        handler = mock.Mock()
        button = wx.Button(self.frame)
        button.Bind(wx.EVT_BUTTON, handler)
        button.Enable(False)
        interactor = UIWrapper(
            editor=button,
            registries=[default_registry.get_default_registry()],
        )

        # when
        interactor.perform(command.MouseClick())

        # then
        self.assertEqual(handler.call_count, 0)
