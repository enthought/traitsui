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


def _create_event(event_type, control):
    click_event = wx.CommandEvent(
        event_type, control.GetId()
    )
    click_event.SetEventObject(control)
    return click_event


def mouse_click(func):
    def mouse_click_handler(control, delay, *args, **kwargs):
        if not control.IsEnabled():
            return
        wx.MilliSleep(delay)
        func(control, *args, **kwargs)
    return mouse_click_handler


@mouse_click
def mouse_click_button(control):
    """ Performs a mouce click on a wx button.

    Parameters
    ----------
    control : wxButton
        The wx Object to be clicked.
    delay: int
        Time delay (in ms) in which click will be performed.
    """
    click_event = _create_event(wx.wxEVT_COMMAND_BUTTON_CLICKED, control)
    control.ProcessWindowEvent(click_event)


@mouse_click
def mouse_click_checkbox(control):
    """ Performs a mouce click on a wx check box.

    Parameters
    ----------
    control : wxCheckBox
        The wx Object to be clicked.
    delay: int
        Time delay (in ms) in which click will be performed.
    """
    click_event = _create_event(wx.wxEVT_COMMAND_CHECKBOX_CLICKED, control)
    control.SetValue(not control.GetValue())
    control.ProcessWindowEvent(click_event)


@mouse_click
def mouse_click_combobox_or_choice(control, index):
    """ Performs a mouce click on either a wx combo box or a wx choice on the
    entry at the given index.

    Parameters
    ----------
    control : wxComboBox or wxChoice
        The wx Object to be clicked.
    index : int
        The index of the item in the combobox/choice to be clicked
    delay: int
        Time delay (in ms) in which click will be performed.
    """
    if isinstance(control, wx.ComboBox):
        click_event = _create_event(wx.wxEVT_COMMAND_COMBOBOX_SELECTED, control)
    elif isinstance(control, wx.Choice):
        click_event = _create_event(wx.wxEVT_COMMAND_CHOICE_SELECTED, control)
    else:
        raise TypeError("Only supported controls are wxComboBox or wxChoice")
    click_event.SetString(control.GetString(index))
    control.SetSelection(index)
    control.ProcessWindowEvent(click_event)

@mouse_click
def mouse_click_listbox(control, index):
    """Performs a mouce click on a wx list box on the entry at
    the given index.

    Parameters
    ----------
    control : wxListBox
        The wx Object to be clicked.
    index : int
        The index of the item in the list box to be clicked
    delay: int
        Time delay (in ms) in which click will be performed.
    """
    click_event = _create_event(wx.wxEVT_COMMAND_LISTBOX_SELECTED, control)
    control.SetSelection(index)
    control.ProcessWindowEvent(click_event)


@mouse_click
def mouse_click_radiobutton(control):
    """ Performs a mouce click on a wx radio button.

    Parameters
    ----------
    control : wxRadioButton
        The wx Object to be clicked.
    delay: int
        Time delay (in ms) in which click will be performed.
    """
    click_event = _create_event(wx.wxEVT_COMMAND_RADIOBUTTON_SELECTED, control)
    control.SetValue(not control.GetValue())
    control.ProcessWindowEvent(click_event)


@mouse_click
def mouse_click_object(control):
    """ Performs a mouce click on a wxTextCtrl.

    Parameters
    ----------
    control : wxObject
        The wx Object to be clicked.
    delay: int
        Time delay (in ms) in which click will be performed.
    """
    if not control.HasFocus():
        control.SetFocus()
    click_event = _create_event(wx.wxEVT_COMMAND_LEFT_CLICK, control)
    control.ProcessWindowEvent(click_event)


###############################################################################


def mouse_click_notebook_tab_index(control, index, delay=0):
    """ Performs a mouseclick on a Noteboook List Editor on the tab specified
    by index.

    Parameters
    ----------
    control : wx.Window
        The control of the DockWindow
    index : int
        The index of the child object in the Panel to be clicked
    delay : int
        Time delay (in ms) in which click will be performed.
    """
    controls_list = control.GetSizer().GetContents().get_controls()
    wx.MilliSleep(delay)

    # find the boundaries of the tab to be clicked
    bx, by, bdx, bdy = controls_list[index].drag_bounds
    # find the center
    tab_center = wx.Point(bx + bdx//2, by + bdy//2)

    click_down_event = wx.MouseEvent(
        wx.wxEVT_LEFT_DOWN
    )
    click_down_event.SetPosition(tab_center)
    click_up_event = wx.MouseEvent(
        wx.wxEVT_LEFT_UP
    )
    click_up_event.SetPosition(tab_center)
    control.ProcessEvent(click_down_event)
    control.ProcessEvent(click_up_event)


def mouse_click_checkbox_child_in_panel(control, index, delay):
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
    mouse_click_checkbox(obj, delay)


def mouse_click_radiobutton_child_in_panel(control, index, delay):
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
    mouse_click_radiobutton(obj, delay)


def key_click_text_entry(
    control, interaction, delay,
    get_selection=lambda control: control.GetSelection()
):
    """ Performs simulated typing of a key on the given wxObject
    after a delay.

    Parameters
    ----------
    control : wxTextEntry
        The wx Object to be acted on.
    interaction : instance of command.KeyClick
        The interaction object holding the key input
        to be simulated being typed
    delay : int
        Time delay (in ms) in which the key click will be performed.
    get_selection: callable(wx.TextEntry) -> tuple(int, int)
        Callable that takes an instance of wx.TextEntry and return the
        current selection span. Default is to call `GetSelection` method.
        Useful for when the TextEntry.GetSelection is overridden by a subclass
        that does not conform to the common API.
    """
    if not (control.IsEnabled() and control.IsEditable()):
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
        start, end = get_selection(control)
        if end > start:
            control.Remove(start, end)
        else:
            pos = control.GetInsertionPoint()
            control.Remove(max(0, pos - 1), pos)
    else:
        check_key_compat(interaction.key)
        wx.MilliSleep(delay)
        control.WriteText(interaction.key)


def key_click_combobox(control, interaction, delay):
    """ Performs simulated typing of a key on the given wxComboBox
    after a delay.

    Parameters
    ----------
    control : wxComboBox
        The wx Object to be acted on.
    interaction : instance of command.KeyClick
        The interaction object holding the key input
        to be simulated being typed
    delay : int
        Time delay (in ms) in which the key click will be performed.
    """
    key_click_text_entry(
        control, interaction, delay,
        get_selection=lambda control: control.GetTextSelection(),
    )


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

    if not (control.IsEnabled() and control.IsEditable()):
        raise Disabled("{!r} is disabled.".format(control))
    if not control.HasFocus():
        control.SetFocus()
        control.SetInsertionPointEnd()
    for char in interaction.sequence:
        wx.MilliSleep(delay)
        control.WriteText(char)
