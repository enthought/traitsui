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
from traitsui.wx.key_event_to_name import key_map as _KEY_MAP


def key_click(widget, key, delay=0):
    """ Performs a key click of the given key on the given widget after
    a delay.

    Parameters
    ----------
    widget : wx.TextCtrl
        The wx Object to be key cliecked to.
    key : str
        Standardized (pyface) name for a keyboard event.
        e.g. "Enter", "Tab", "Space", "0", "1", "A", ...
        Note: modifiers (e.g. Shift, Alt, etc. are not currently supported)
    delay : int
        Time delay (in ms) in which the key click will be performed.
    """

    mapping = {name: event for event, name in _KEY_MAP.items()}
    if key not in mapping:
        try:
            KEY = ord(key)
        except [TypeError, ValueError]:
            raise ValueError(
                "Unknown key {!r}. Expected one of these: {!r}, or a unicode character".format(  # noqa
                    key, sorted(mapping)
                ))
        else:
            wx.MilliSleep(delay)
            key_event = wx.KeyEvent(wx.wxEVT_CHAR)
            key_event.SetKeyCode(KEY)
            widget.EmulateKeyPress(key_event)
    else:
        wx.MilliSleep(delay)
        key_event = wx.KeyEvent(wx.wxEVT_CHAR)
        key_event.SetKeyCode(mapping[key])
        widget.EmulateKeyPress(key_event)


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
    # EmulateKeyPress in key_click seems to not be handling "Enter"
    # correctly.
    if interaction.key == "Enter":
        wx.MilliSleep(delay)
        event = wx.CommandEvent(wx.EVT_TEXT_ENTER.typeId, control.GetId())
        control.ProcessEvent(event)
    else:
        key_click(control, interaction.key, delay)


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
    if not control.IsEditable():
        raise Disabled("{!r} is disabled.".format(control))
    if not control.HasFocus():
        control.SetFocus()
    for char in interaction.sequence:
        key_click(control, char, delay)
