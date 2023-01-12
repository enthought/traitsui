# (C) Copyright 2008-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

# ------------------------------------------------------------------------------
# Copyright (c) 2007, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD license.
# However, when used with the GPL version of PyQt the additional terms
# described in the PyQt GPL exception also apply

#
# Author: Riverbank Computing Limited
# ------------------------------------------------------------------------------

""" Converts a QKeyEvent to a standardized "name".
"""


from pyface.qt import QtCore


# Mapping from PyQt keypad key names to Pyface key names.
keypad_map = {
    QtCore.Qt.Key.Key_Enter: "Enter",
    QtCore.Qt.Key.Key_0: "Numpad 0",
    QtCore.Qt.Key.Key_1: "Numpad 1",
    QtCore.Qt.Key.Key_2: "Numpad 2",
    QtCore.Qt.Key.Key_3: "Numpad 3",
    QtCore.Qt.Key.Key_4: "Numpad 4",
    QtCore.Qt.Key.Key_5: "Numpad 5",
    QtCore.Qt.Key.Key_6: "Numpad 6",
    QtCore.Qt.Key.Key_7: "Numpad 7",
    QtCore.Qt.Key.Key_8: "Numpad 8",
    QtCore.Qt.Key.Key_9: "Numpad 9",
    QtCore.Qt.Key.Key_Asterisk: "Multiply",
    QtCore.Qt.Key.Key_Plus: "Add",
    QtCore.Qt.Key.Key_Comma: "Separator",
    QtCore.Qt.Key.Key_Minus: "Subtract",
    QtCore.Qt.Key.Key_Period: "Decimal",
    QtCore.Qt.Key.Key_Slash: "Divide",
}

# Mapping from PyQt non-keypad key names to Pyface key names.
key_map = {
    QtCore.Qt.Key.Key_0: "0",
    QtCore.Qt.Key.Key_1: "1",
    QtCore.Qt.Key.Key_2: "2",
    QtCore.Qt.Key.Key_3: "3",
    QtCore.Qt.Key.Key_4: "4",
    QtCore.Qt.Key.Key_5: "5",
    QtCore.Qt.Key.Key_6: "6",
    QtCore.Qt.Key.Key_7: "7",
    QtCore.Qt.Key.Key_8: "8",
    QtCore.Qt.Key.Key_9: "9",
    QtCore.Qt.Key.Key_A: "A",
    QtCore.Qt.Key.Key_B: "B",
    QtCore.Qt.Key.Key_C: "C",
    QtCore.Qt.Key.Key_D: "D",
    QtCore.Qt.Key.Key_E: "E",
    QtCore.Qt.Key.Key_F: "F",
    QtCore.Qt.Key.Key_G: "G",
    QtCore.Qt.Key.Key_H: "H",
    QtCore.Qt.Key.Key_I: "I",
    QtCore.Qt.Key.Key_J: "J",
    QtCore.Qt.Key.Key_K: "K",
    QtCore.Qt.Key.Key_L: "L",
    QtCore.Qt.Key.Key_M: "M",
    QtCore.Qt.Key.Key_N: "N",
    QtCore.Qt.Key.Key_O: "O",
    QtCore.Qt.Key.Key_P: "P",
    QtCore.Qt.Key.Key_Q: "Q",
    QtCore.Qt.Key.Key_R: "R",
    QtCore.Qt.Key.Key_S: "S",
    QtCore.Qt.Key.Key_T: "T",
    QtCore.Qt.Key.Key_U: "U",
    QtCore.Qt.Key.Key_V: "V",
    QtCore.Qt.Key.Key_W: "W",
    QtCore.Qt.Key.Key_X: "X",
    QtCore.Qt.Key.Key_Y: "Y",
    QtCore.Qt.Key.Key_Z: "Z",
    QtCore.Qt.Key.Key_Space: "Space",
    QtCore.Qt.Key.Key_Backspace: "Backspace",
    QtCore.Qt.Key.Key_Tab: "Tab",
    QtCore.Qt.Key.Key_Enter: "Enter",
    QtCore.Qt.Key.Key_Return: "Return",
    QtCore.Qt.Key.Key_Escape: "Esc",
    QtCore.Qt.Key.Key_Delete: "Delete",
    QtCore.Qt.Key.Key_Cancel: "Cancel",
    QtCore.Qt.Key.Key_Clear: "Clear",
    QtCore.Qt.Key.Key_Shift: "Shift",
    QtCore.Qt.Key.Key_Menu: "Menu",
    QtCore.Qt.Key.Key_Pause: "Pause",
    QtCore.Qt.Key.Key_PageUp: "Page Up",
    QtCore.Qt.Key.Key_PageDown: "Page Down",
    QtCore.Qt.Key.Key_End: "End",
    QtCore.Qt.Key.Key_Home: "Home",
    QtCore.Qt.Key.Key_Left: "Left",
    QtCore.Qt.Key.Key_Up: "Up",
    QtCore.Qt.Key.Key_Right: "Right",
    QtCore.Qt.Key.Key_Down: "Down",
    QtCore.Qt.Key.Key_Select: "Select",
    QtCore.Qt.Key.Key_Print: "Print",
    QtCore.Qt.Key.Key_Execute: "Execute",
    QtCore.Qt.Key.Key_Insert: "Insert",
    QtCore.Qt.Key.Key_Help: "Help",
    QtCore.Qt.Key.Key_F1: "F1",
    QtCore.Qt.Key.Key_F2: "F2",
    QtCore.Qt.Key.Key_F3: "F3",
    QtCore.Qt.Key.Key_F4: "F4",
    QtCore.Qt.Key.Key_F5: "F5",
    QtCore.Qt.Key.Key_F6: "F6",
    QtCore.Qt.Key.Key_F7: "F7",
    QtCore.Qt.Key.Key_F8: "F8",
    QtCore.Qt.Key.Key_F9: "F9",
    QtCore.Qt.Key.Key_F10: "F10",
    QtCore.Qt.Key.Key_F11: "F11",
    QtCore.Qt.Key.Key_F12: "F12",
    QtCore.Qt.Key.Key_F13: "F13",
    QtCore.Qt.Key.Key_F14: "F14",
    QtCore.Qt.Key.Key_F15: "F15",
    QtCore.Qt.Key.Key_F16: "F16",
    QtCore.Qt.Key.Key_F17: "F17",
    QtCore.Qt.Key.Key_F18: "F18",
    QtCore.Qt.Key.Key_F19: "F19",
    QtCore.Qt.Key.Key_F20: "F20",
    QtCore.Qt.Key.Key_F21: "F21",
    QtCore.Qt.Key.Key_F22: "F22",
    QtCore.Qt.Key.Key_F23: "F23",
    QtCore.Qt.Key.Key_F24: "F24",
    QtCore.Qt.Key.Key_NumLock: "Num Lock",
    QtCore.Qt.Key.Key_ScrollLock: "Scroll Lock",
}

# -------------------------------------------------------------------------
#  Converts a keystroke event into a corresponding key name:
# -------------------------------------------------------------------------


def key_event_to_name(event):
    """Converts a keystroke event into a corresponding key name."""
    key_code = event.key()
    modifiers = event.modifiers()
    if modifiers & QtCore.Qt.KeyboardModifier.KeypadModifier:
        key = keypad_map.get(key_code)
    else:
        key = None
    if key is None:
        key = key_map.get(key_code, "Unknown-Key")

    name = ""
    if modifiers & QtCore.Qt.KeyboardModifier.ControlModifier:
        name += "Ctrl"

    if modifiers & QtCore.Qt.KeyboardModifier.AltModifier:
        name += "-Alt" if name else "Alt"

    if modifiers & QtCore.Qt.KeyboardModifier.MetaModifier:
        name += "-Meta" if name else "Meta"

    if modifiers & QtCore.Qt.KeyboardModifier.ShiftModifier and (
        (name != "") or (len(key) > 1)
    ):
        name += "-Shift" if name else "Shift"

    if key:
        if name:
            name += "-"
        name += key
    return name
