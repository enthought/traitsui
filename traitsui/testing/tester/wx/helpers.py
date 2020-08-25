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

from traitsui.testing.tester.exceptions import Disabled


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


def key_click_text_ctrl(control, interaction, delay):
    if not control.IsEditable():
        raise Disabled("{!r} is disabled.".format(control))
    if interaction.key == "Enter":
        if not control.HasFocus():
            control.SetFocus()
        wx.MilliSleep(delay)
        event = wx.CommandEvent(wx.EVT_TEXT_ENTER.typeId, control.GetId())
        control.ProcessEvent(event)
    else:
        raise ValueError("Only supported Enter key.")


"""def key_sequence_text_ctrl(control, interaction, delay):
    if not control.IsEditable():
        raise Disabled("{!r} is disabled.".format(control))
    if not control.HasFocus():
        control.SetFocus()
    for char in interaction.sequence:
        wx.MilliSleep(delay)
        if char == "\b":
            pos = control.GetInsertionPoint()
            control.Remove(max(0, pos - 1), pos)
        else:
            control.AppendText(char)"""

def key_sequence_text_ctrl(control, interaction, delay):
    if not control.IsEditable():
        raise Disabled("{!r} is disabled.".format(control))
    if not control.HasFocus():
        control.SetFocus()
    for char in interaction.sequence:
        wx.MilliSleep(delay)
        if char == "\b":
            pos = control.GetInsertionPoint()
            control.Remove(max(0, pos - 1), pos)
        else:
            char_key_event = wx.KeyEvent(wx.wxEVT_CHAR)
            char_key_event.SetUnicodeKey(ord(char))
            control.EmulateKeyPress(char_key_event)

