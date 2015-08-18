#------------------------------------------------------------------------------
#
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Author: Pietro Berkes
#  Date:   Feb 2012
#
#------------------------------------------------------------------------------

"""
Test that menu and toolbar actions are triggered.
"""
import pyface

from traits.has_traits import HasTraits
from traits.trait_types import Bool
from traitsui.menu import Action, ActionGroup, Menu, MenuBar, ToolBar
from traitsui.item import Item
from traitsui.view import View

from traitsui.tests._tools import *
from traitsui.tests._tools import _is_current_backend

if _is_current_backend('null'):
    import nose
    raise nose.SkipTest("Not supported using the null backend")


TestAction = Action(
    name        = 'Test',
    action      = 'test_clicked',
    tooltip     = 'Click to test'
)


class DialogWithToolbar(HasTraits):
    """Test dialog with toolbar and menu."""

    action_successful = Bool(False)

    def test_clicked(self):
        self.action_successful = True

    menubar = MenuBar(
        Menu(
            ActionGroup(TestAction),
            name='&Test menu'
        ),
    )

    toolbar = ToolBar(
        ActionGroup(TestAction),
    )

    traits_view = View(
        Item(label="Click the button on the toolbar or the menu item.\n"
                   "The 'Action successful' element should turn to True."),
        Item('action_successful', style='readonly'),
        menubar = menubar,
        toolbar = toolbar,
        buttons = ['OK']
    )


def _test_actions(trigger_action_func):
    """Template test for wx, qt4, menu, and toolbar testing.
    """
    # Behavior: when clicking on a menu or toolbar action,
    # the corresponding function should be executed

    with store_exceptions_on_all_threads():
        # create dialog with toolbar adn menu
        dialog = DialogWithToolbar()
        ui = dialog.edit_traits()

        # press toolbar or menu button
        trigger_action_func(ui)

        # verify that the action was triggered
        nose.tools.assert_true(dialog.action_successful)


# ----- Qt4 tests

def _qt_trigger_action(container_class, ui):
    toolbar = ui.control.findChild(container_class)
    action = toolbar.actions()[0]
    action.trigger()


@skip_if_not_qt4
def test_qt_toolbar_action():
    # Behavior: when clicking on a toolbar action, the corresponding function
    # should be executed

    # Bug: in the Qt4 backend, a
    # TypeError: perform() takes exactly 2 arguments (1 given) was raised
    # instead

    qt_trigger_toolbar_action = partial(
        _qt_trigger_action, pyface.ui.qt4.action.tool_bar_manager._ToolBar)

    _test_actions(qt_trigger_toolbar_action)


@skip_if_not_qt4
def test_qt_menu_action():
    # Behavior: when clicking on a menu action, the corresponding function
    # should be executed

    # Bug: in the Qt4 backend, a
    # TypeError: perform() takes exactly 2 arguments (1 given) was raised
    # instead

    qt_trigger_menu_action = partial(
        _qt_trigger_action, pyface.ui.qt4.action.menu_manager._Menu)

    _test_actions(qt_trigger_menu_action)


# ----- wx tests

@skip_if_not_wx
def test_wx_toolbar_action():
    # Behavior: when clicking on a toolbar action, the corresponding function
    # should be executed

    import wx

    def _wx_trigger_toolbar_action(ui):
        # long road to get at the Id of the toolbar button
        toolbar_item = ui.view.toolbar.groups[0].items[0]
        toolbar_item_wrapper = toolbar_item._wrappers[0]
        control_id = toolbar_item_wrapper.control_id

        # build event that clicks the button
        click_event = wx.CommandEvent(wx.wxEVT_COMMAND_TOOL_CLICKED,
                                      control_id)

        # send the event to the toolbar
        toolbar = ui.control.FindWindowByName('toolbar')
        toolbar.ProcessEvent(click_event)

    _test_actions(_wx_trigger_toolbar_action)


# TODO: I couldn't find a way to press menu items programmatically for wx


if __name__ == '__main__':
    # Execute from command line for manual testing
    vw = DialogWithToolbar()
    vw.configure_traits()
