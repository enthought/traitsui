# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

"""
Test that menu and toolbar actions are triggered.
"""

from functools import partial
import unittest

import pyface
from pyface.action.schema.api import ActionSchema, SGroup, SMenu, SMenuBar, SToolBar
from traits.has_traits import HasTraits
from traits.trait_types import Bool
from traitsui.menu import Action, ActionGroup, Menu, MenuBar, ToolBar
from traitsui.item import Item
from traitsui.view import View

from traitsui.tests._tools import (
    BaseTestMixin,
    create_ui,
    is_mac_os,
    is_null,
    requires_toolkit,
    reraise_exceptions,
    ToolkitName,
)

if is_null():
    raise unittest.SkipTest("Not supported using the null backend")


TestAction = Action(
    name="Test", action="test_clicked", tooltip="Click to test"
)


class DialogWithToolbar(HasTraits):
    """Test dialog with toolbar and menu."""

    action_successful = Bool(False)

    def test_clicked(self):
        self.action_successful = True

    menubar = MenuBar(Menu(ActionGroup(TestAction), name="&Test menu"))

    toolbar = ToolBar(ActionGroup(TestAction))

    traits_view = View(
        Item(
            label="Click the button on the toolbar or the menu item.\n"
            "The 'Action successful' element should turn to True."
        ),
        Item("action_successful", style="readonly"),
        menubar=menubar,
        toolbar=toolbar,
        buttons=[TestAction, "OK"],
    )


class DialogWithSchema(HasTraits):
    """Test dialog with toolbar and menu schemas."""

    action_successful = Bool(False)

    def test_clicked(self):
        self.action_successful = True

    menubar = SMenuBar(
        SMenu(
            SGroup(
                ActionSchema(
                    action_factory=lambda **traits: TestAction,
                ),
            ),
            name="&Test menu",
        ),
    )

    toolbar = SToolBar(
        SGroup(
            ActionSchema(
                action_factory=lambda **traits: TestAction,
            ),
        ),
    )

    traits_view = View(
        Item(
            label="Click the button on the toolbar or the menu item.\n"
            "The 'Action successful' element should turn to True."
        ),
        Item("action_successful", style="readonly"),
        menubar=menubar,
        toolbar=toolbar,
        buttons=[TestAction, "OK"],
    )


# ----- qt helper functions


def _qt_trigger_action(container_class, ui):
    toolbar = ui.control.findChild(container_class)
    action = toolbar.actions()[0]
    action.trigger()


def _qt_click_button(ui):
    from pyface.qt.QtGui import QDialogButtonBox

    bbox = ui.control.findChild(QDialogButtonBox)
    button = bbox.buttons()[1]
    button.click()


class TestActions(BaseTestMixin, unittest.TestCase):

    def _test_actions(self, trigger_action_func):
        """Template test for wx, qt, menu, and toolbar testing."""
        # Behavior: when clicking on a menu or toolbar action,
        # the corresponding function should be executed

        # create dialog with toolbar adn menu
        dialog = DialogWithToolbar()
        with reraise_exceptions(), create_ui(dialog) as ui:

            # press toolbar or menu button
            trigger_action_func(ui)

            # verify that the action was triggered
            self.assertTrue(dialog.action_successful)

    # ----- Qt tests

    @requires_toolkit([ToolkitName.qt])
    def test_qt_toolbar_action(self):
        # Behavior: when clicking on a toolbar action, the corresponding
        # function should be executed

        # Bug: in the Qt4 backend, a
        # TypeError: perform() takes exactly 2 arguments (1 given) was raised
        # instead
        from pyface.ui.qt.action.tool_bar_manager import _ToolBar

        qt_trigger_toolbar_action = partial(_qt_trigger_action, _ToolBar)

        self._test_actions(qt_trigger_toolbar_action)

    @requires_toolkit([ToolkitName.qt])
    def test_qt_menu_action(self):
        # Behavior: when clicking on a menu action, the corresponding function
        # should be executed

        # Bug: in the Qt4 backend, a
        # TypeError: perform() takes exactly 2 arguments (1 given) was raised
        # instead
        from pyface.ui.qt.action.menu_manager import _Menu

        qt_trigger_menu_action = partial(
            _qt_trigger_action, _Menu
        )

        self._test_actions(qt_trigger_menu_action)

    @requires_toolkit([ToolkitName.qt])
    def test_qt_button_action(self):
        # Behavior: when clicking on a button action, the corresponding
        # function should be executed

        # Bug: in the Qt4 backend, a
        # TypeError: perform() takes exactly 2 arguments (1 given) was raised
        # instead

        self._test_actions(_qt_click_button)

    # ----- wx tests

    @unittest.skip(
        "Problem with triggering toolbar actions. Issue #428 and #1843."
    )
    @requires_toolkit([ToolkitName.wx])
    def test_wx_toolbar_action(self):
        # Behavior: when clicking on a toolbar action, the corresponding
        # function should be executed

        import wx

        def _wx_trigger_toolbar_action(ui):
            # long road to get at the Id of the toolbar button
            toolbar_control = ui.control.GetToolBar()
            toolbar_item = toolbar_control.tool_bar_manager.groups[0].items[0]
            toolbar_item_wrapper = toolbar_item._wrappers[0]
            control_id = toolbar_item_wrapper.control_id

            # build event that clicks the button
            click_event = wx.CommandEvent(
                wx.wxEVT_COMMAND_TOOL_CLICKED, control_id
            )

            # send the event to the toolbar
            toolbar_control.ProcessEvent(click_event)

        self._test_actions(_wx_trigger_toolbar_action)

    @requires_toolkit([ToolkitName.wx])
    def test_wx_button_action(self):
        # Behavior: when clicking on a button action, the corresponding
        # function should be executed

        import wx

        def _wx_trigger_button_action(ui):
            # long road to get at the Id of the toolbar button
            button_sizer = ui.control.GetSizer().GetChildren()[2].GetSizer()
            button = button_sizer.GetChildren()[0].GetWindow()

            control_id = button.GetId()

            # build event that clicks the button
            click_event = wx.CommandEvent(
                wx.wxEVT_COMMAND_BUTTON_CLICKED, control_id
            )

            # send the event to the toolbar
            ui.control.ProcessEvent(click_event)

        self._test_actions(_wx_trigger_button_action)

    # TODO: I couldn't find a way to press menu items programmatically for wx


class TestActionSchemas(BaseTestMixin, unittest.TestCase):
    def setUp(self):
        BaseTestMixin.setUp(self)

    def tearDown(self):
        BaseTestMixin.tearDown(self)

    def _test_actions(self, trigger_action_func):
        """Template test for wx, qt, menu, and toolbar testing."""
        # Behavior: when clicking on a menu or toolbar action,
        # the corresponding function should be executed

        # create dialog with toolbar adn menu
        dialog = DialogWithSchema()
        with reraise_exceptions(), create_ui(dialog) as ui:

            # press toolbar or menu button
            trigger_action_func(ui)

            # verify that the action was triggered
            self.assertTrue(dialog.action_successful)

    # ----- Qt tests

    @requires_toolkit([ToolkitName.qt])
    def test_qt_toolbar_action(self):
        # Behavior: when clicking on a toolbar action, the corresponding
        # function should be executed

        # Bug: in the Qt4 backend, a
        # TypeError: perform() takes exactly 2 arguments (1 given) was raised
        # instead
        from pyface.ui.qt.action.tool_bar_manager import _ToolBar

        qt_trigger_toolbar_action = partial(_qt_trigger_action, _ToolBar)

        self._test_actions(qt_trigger_toolbar_action)

    @requires_toolkit([ToolkitName.qt])
    def test_qt_menu_action(self):
        # Behavior: when clicking on a menu action, the corresponding function
        # should be executed

        # Bug: in the Qt4 backend, a
        # TypeError: perform() takes exactly 2 arguments (1 given) was raised
        # instead
        from pyface.ui.qt.action.menu_manager import _Menu

        qt_trigger_menu_action = partial(_qt_trigger_action, _Menu)

        self._test_actions(qt_trigger_menu_action)

    # ----- wx tests

    @unittest.skipIf(
        not is_mac_os,
        "Problem with triggering toolbar actions on Linux and Windows. Issue #428.",  # noqa: E501
    )
    @requires_toolkit([ToolkitName.wx])
    def test_wx_toolbar_action(self):
        # Behavior: when clicking on a toolbar action, the corresponding
        # function should be executed

        import wx

        def _wx_trigger_toolbar_action(ui):
            # long road to get at the Id of the toolbar button
            toolbar_control = ui.control.GetToolBar()
            toolbar_item = toolbar_control.tool_bar_manager.groups[0].items[0]
            toolbar_item_wrapper = toolbar_item._wrappers[0]
            control_id = toolbar_item_wrapper.control_id

            # build event that clicks the button
            click_event = wx.CommandEvent(
                wx.wxEVT_COMMAND_TOOL_CLICKED, control_id
            )

            # send the event to the toolbar
            toolbar_control.ProcessEvent(click_event)

        self._test_actions(_wx_trigger_toolbar_action)

    # TODO: I couldn't find a way to press menu items programmatically for wx


if __name__ == "__main__":
    # Execute from command line for manual testing
    vw = DialogWithToolbar()
    vw.configure_traits()
