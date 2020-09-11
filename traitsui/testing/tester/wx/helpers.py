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

from traitsui.testing.tester.compat import check_key_compat
from traitsui.testing.tester.exceptions import Disabled


def mouse_click_button(control, delay):
    """ Performs a mouce click on a wx button.

    Parameters
    ----------
    control : wxButton
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


def mouse_click_checkbox(control, delay):
    """ Performs a mouce click on a wx check box.

    Parameters
    ----------
    control : wxCheckBox
        The wx Object to be clicked.
    delay: int
        Time delay (in ms) in which click will be performed.
    """
    if not control.IsEnabled():
        return
    wx.MilliSleep(delay)
    click_event = wx.CommandEvent(
        wx.wxEVT_COMMAND_CHECKBOX_CLICKED, control.GetId()
    )
    click_event.SetEventObject(control)
    control.SetValue(not control.GetValue())
    control.ProcessWindowEvent(click_event)


def mouse_click_object(control, delay):
    """ Performs a mouce click on a wxTextCtrl.

    Parameters
    ----------
    control : wxObject
        The wx Object to be clicked.
    delay: int
        Time delay (in ms) in which click will be performed.
    """
    if not control.IsEnabled():
        return
    if not control.HasFocus():
        control.SetFocus()
    wx.MilliSleep(delay)
    click_event = wx.CommandEvent(
        wx.wxEVT_COMMAND_LEFT_CLICK, control.GetId()
    )
    control.ProcessEvent(click_event)


def mouse_click_child_in_panel(control, index, delay):
    """ Performs a mouce click on a child of a Wx Panel.
    Parameters
    ----------
    control : wx.Panel
        The Panel containing child objects, one of which will be clicked.
    index : int
        The index of the child object in the Panel to be clicked
    delay : int
        Time delay (in ms) in which click will be performed.
    """
    children_list = control.GetSizer().GetChildren()
    if not 0 <= index <= len(children_list) - 1:
        raise IndexError(index)
    obj = children_list[index].GetWindow()
    if isinstance(obj, wx.CheckBox):
        mouse_click_checkbox(obj, delay)
    else:
        raise NotImplementedError(
            "The only currently supported child object type is wx.CheckBox"
        )


def key_click_text_ctrl(control, interaction, delay):
    """ Performs simulated typing of a key on the given wxObject
    after a delay.

    Parameters
    ----------
    control : wxTextCtrl
        The wx Object to be acted on.
    interaction : instance of command.KeyClick
        The interaction object holding the key input
        to be simulated being typed
    delay : int
        Time delay (in ms) in which the key click will be performed.
    """
    if not control.IsEditable():
        raise Disabled("{!r} is disabled.".format(control))
    if not control.HasFocus():
        control.SetFocus()
        control.SetInsertionPointEnd()
    if interaction.key == "Enter":
        wx.MilliSleep(delay)
        event = wx.CommandEvent(wx.EVT_TEXT_ENTER.typeId, control.GetId())
        control.ProcessEvent(event)
    elif interaction.key == "Backspace":
        wx.MilliSleep(delay)
        if control.GetStringSelection():
            control.Remove(*control.GetSelection())
        else:
            pos = control.GetInsertionPoint()
            control.Remove(max(0, pos - 1), pos)
    else:
        check_key_compat(interaction.key)
        wx.MilliSleep(delay)
        control.WriteText(interaction.key)


def key_sequence_text_ctrl(control, interaction, delay):
    """ Performs simulated typing of a sequence of keys on the given wxObject
    after a delay.

    Parameters
    ----------
    control : wxTextCtrl
        The wx Object to be acted on.
    interaction : instance of command.KeySequence
        The interaction object holding the sequence of key inputs
        to be simulated being typed
    delay : int
        Time delay (in ms) in which each key click in the sequence will be
        performed.
    """
    # fail early
    for char in interaction.sequence:
        check_key_compat(char)

    if not control.IsEditable():
        raise Disabled("{!r} is disabled.".format(control))
    if not control.HasFocus():
        control.SetFocus()
        control.SetInsertionPointEnd()
    for char in interaction.sequence:
        wx.MilliSleep(delay)
        control.WriteText(char)


def key_click_slider(control, interaction, delay):
    valid_keys = {"Left", "Right", "Up", "Down", "Page Up", "Page Down"}
    if interaction.key not in valid_keys:
        raise ValueError("Unexpected Key.")
    if not control.HasFocus():
        control.SetFocus()
    value = control.GetValue()
    wx.MilliSleep(delay)
    if interaction.key in {"Up", "Right"}:
        position = min(control.GetMax(), value + control.GetLineSize())
    elif interaction.key == "Page Up":
        position = min(control.GetMax(), value + control.GetPageSize())
    elif interaction.key == "Page Down":
        position = max(control.GetMin(), value - control.GetPageSize())
    else:
        position = max(control.GetMin(), value - control.GetLineSize())
    control.SetValue(position)
    event = wx.ScrollEvent(
        wx.wxEVT_SCROLL_CHANGED, control.GetId(), position
    )
    wx.PostEvent(control, event)
