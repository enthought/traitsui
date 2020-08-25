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


def mouse_click_button(control, delay):
    """ Performs a mouce click on a wx button.

    Parameters
    ----------
    control : wxObject
        The wx Object to be clicked.  
    delay: int
        Time delay (in ms) in which click will be performed. 
    """
    if not control.IsEnabled():
        return
    wx.MilliSleep(delay)
    click_event = wx.CommandEvent(
        wx.wxEVT_COMMAND_BUTTON_CLICKED, control.GetId()
    )
    control.ProcessEvent(click_event)


def key_click_text_ctrl(wrapper, interaction):
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
