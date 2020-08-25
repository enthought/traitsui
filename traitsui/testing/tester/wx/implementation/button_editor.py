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
import wx

from pyface.ui.wx.image_button import ImageButton

from traitsui.wx.button_editor import SimpleEditor, CustomEditor
from traitsui.testing.tester import command, locator, query


def mouse_click_ImageButton(wrapper, interaction):
    """ Performs a mouce click on an pyface.ui.wx.ImageButton object.

    Parameters
    ----------
    wrapper : UIWrapper
        The wrapper object wrapping the ImageButton.
    interaction : instance of traitsui.testing.tester.command.MouseClick
        interaction is unused here, but it is included so that the function
        matches the expected format for a handler.  Note this handler is
        intended to be used with an interaction_class of a MouseClick.
    """

    control = wrapper.target.control
    if not control.IsEnabled():
        return
    wx.MilliSleep(wrapper.delay)

    left_down_event = wx.MouseEvent(
        wx.wxEVT_LEFT_DOWN
    )
    left_up_event = wx.MouseEvent(
        wx.wxEVT_LEFT_UP
    )
    control.ProcessEvent(left_down_event)
    control.ProcessEvent(left_up_event)


def register(registry):
    """ Register solvers/handlers specific to wx Button Editors
    for the given registry.

    If there are any conflicts, an error will occur.

    Parameters
    ----------
    registry : TargetRegistry
    """
    registry.register_solver(
        target_class=SimpleEditor,
        locator_class=locator.DefaultTarget,
        solver=lambda wrapper, _: wrapper.target.control,
    )
    registry.register_solver(
        target_class=CustomEditor,
        locator_class=locator.DefaultTarget,
        solver=lambda wrapper, _: wrapper.target._control,
    )

    registry.register_handler(
        target_class=ImageButton,
        interaction_class=command.MouseClick,
        handler=lambda wrapper, _: mouse_click_ImageButton(wrapper, command.MouseClick())
    )

    registry.register_handler(
        target_class=ImageButton,
        interaction_class=query.DisplayedText,
        handler=lambda wrapper, _: wrapper.target.control.GetLabel()
    )
