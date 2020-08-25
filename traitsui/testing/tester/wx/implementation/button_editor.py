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

from traitsui.wx.button_editor import SimpleEditor, CustomEditor
from traitsui.testing.tester import command, query
from traitsui.testing.tester.wx import helpers


def mouse_click_ImageButton(wrapper, interaction):
    """ Performs a mouce click on an pyface.ui.wx.ImageButton object.

    Parameters
    ----------
    wrapper : UIWrapper
        The wrapper object wrapping the Custom Button Editor which utilizes
        an ImageButton.
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

    registry.register_handler(
        target_class=SimpleEditor,
        interaction_class=command.MouseClick,
        handler=(lambda wrapper, _: helpers.mouse_click_button(
                 wrapper.target.control, wrapper.delay))
    )

    registry.register_handler(
        target_class=SimpleEditor,
        interaction_class=query.DisplayedText,
        handler=lambda wrapper, _: wrapper.target.control.GetLabel()
    )

    registry.register_handler(
        target_class=CustomEditor,
        interaction_class=command.MouseClick,
        handler=mouse_click_ImageButton
    )

    registry.register_handler(
        target_class=CustomEditor,
        interaction_class=query.DisplayedText,
        handler=lambda wrapper, _: wrapper.target.control.GetLabel()
    )
