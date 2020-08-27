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


def apply_modifiers(key_event, modifiers):
    possible_modifiers = ["Alt", "Ctrl", "Meta", "Shift"]
    modifier_map = {mod: (mod in modifiers) for mod in possible_modifiers}
    key_event.SetAltDown(modifier_map["Alt"])
    key_event.SetControlDown(modifier_map["Ctrl"])
    key_event.SetMetaDown(modifier_map["Meta"])
    key_event.SetShiftDown(modifier_map["Shift"])


def key_click(widget, key, delay=0):
    """ Performs a key click of the given key on the given widget after
    a delay.

    Parameters
    ----------
    widget : wxObject
        The wx Object to be clicked. Should be wx.TextCtrl instance
    key : str
        Standardized (pyface) name for a keyboard event.
        e.g. "Enter", "Tab", "Space", "0", "1", "A", ...
    delay : int
        Time delay (in ms) in which the key click will be performed.
    """
    if "-" in key:
        *modifiers, key = key.split("-")
    else:
        modifiers = []

    mapping = {name: event for event, name in _KEY_MAP.items()}
    if key not in mapping:
        if len(key) == 1:
            try:
                KEY = ord(key)
            except:
                raise ValueError(
                    "Unknown key {!r}. Expected one of these: {!r}, or a unicode character".format(  # noqa
                        key, sorted(mapping)
                    ))
            else:
                wx.MilliSleep(delay)
                key_event = wx.KeyEvent(wx.wxEVT_CHAR)
                apply_modifiers(key_event, modifiers)
                key_event.SetUnicodeKey(KEY)
                widget.EmulateKeyPress(key_event)
        else:
            raise ValueError(
                    "Unknown key {!r}. Expected one of these: {!r}, or a unicode character".format(  # noqa
                        key, sorted(mapping)
                    ))

    else:
        wx.MilliSleep(delay)
        KEY = mapping[key]
        key_event = wx.KeyEvent(wx.wxEVT_CHAR)
        apply_modifiers(key_event, modifiers)
        key_event.SetKeyCode(mapping[key])
        widget.EmulateKeyPress(key_event)


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

def mouse_click_text_ctrl(control, delay):
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
    control : wxObject
        The wx Object to be acted on. Should be wx.TextCtrl instance. If it is
        a wx.StaticText (i.e. from a ReadonlyEditor) nothing occurs.
    interaction : instance of command.KeyClick
        The interaction object holding the key input
        to be simulated being typed
    delay : int
        Time delay (in ms) in which the key click will be performed.
    """
    if isinstance(control, wx.StaticText):
        return
    if not control.IsEditable():
        raise Disabled("{!r} is disabled.".format(control))
    if not control.HasFocus():
        control.SetFocus()
    key_click(control, interaction.key, delay)


def key_sequence_text_ctrl(control, interaction, delay):
    """ Performs simulated typing of a sequence of keys on the given wxObject
    after a delay.

    Parameters
    ----------
    control : wxObject
        The wx Object to be acted on. Should be wx.TextCtrl instance. If it is
        a wx.StaticText (i.e. from a ReadonlyEditor) nothing occurs.
    interaction : instance of command.KeySequence
        The interaction object holding the sequence of key inputs
        to be simulated being typed
    delay : int
        Time delay (in ms) in which each key click in the sequence will be
        performed.
    """
    if isinstance(control, wx.StaticText):
        return
    if not control.IsEditable():
        raise Disabled("{!r} is disabled.".format(control))
    if not control.HasFocus():
        control.SetFocus()
    for char in interaction.sequence:
        key_click(control, char, delay)
