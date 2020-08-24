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


def mouse_click_button(wrapper, interaction):
    """ Performs a mouce click on a wx button.

    Parameters
    ----------
    wrapper : UIWrapper
        The wrapper object wrapping the wx button.
    interaction : instance of traitsui.testing.tester.command.MouseClick
        interaction is unused here, but it is included so that the function
        matches the expected format for a handler.  Note this handler is
        intended to be used with an interaction_class of a MouseClick.
    """
    control = wrapper.target
    if not control.IsEnabled():
        return
    wx.MilliSleep(wrapper.delay)
    click_event = wx.CommandEvent(
        wx.wxEVT_COMMAND_BUTTON_CLICKED, control.GetId()
    )
    control.ProcessEvent(click_event)


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

    control = wrapper.target
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


def key_press_text_ctrl(wrapper, interaction):
    control = wrapper.target
    if interaction.key == "Enter":
        if not control.HasFocus():
            control.SetFocus()
        wx.MilliSleep(wrapper.delay)
        event = wx.CommandEvent(wx.EVT_TEXT_ENTER.typeId, control.GetId())
        control.ProcessEvent(event)
    else:
        raise ValueError("Only supported Enter key.")


def key_sequence_text_ctrl(wrapper, interaction):
    control = wrapper.target
    if not control.HasFocus():
        control.SetFocus()
    for char in interaction.sequence:
        wx.MilliSleep(wrapper.delay)
        if char == "\b":
            pos = control.GetInsertionPoint()
            control.Remove(max(0, pos - 1), pos)
        else:
            control.AppendText(char)
