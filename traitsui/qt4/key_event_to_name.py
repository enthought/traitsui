#------------------------------------------------------------------------------
# Copyright (c) 2007, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD license.
# However, when used with the GPL version of PyQt the additional terms
# described in the PyQt GPL exception also apply

#
# Author: Riverbank Computing Limited
#------------------------------------------------------------------------------

""" Converts a QKeyEvent to a standardized "name".
"""

#-------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------

from __future__ import absolute_import
from pyface.qt import QtCore

#-------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------

# Mapping from PyQt keypad key names to Pyface key names.
keypad_map = {
    QtCore.Qt.Key_Enter: 'Enter',
    QtCore.Qt.Key_0: 'Numpad 0',
    QtCore.Qt.Key_1: 'Numpad 1',
    QtCore.Qt.Key_2: 'Numpad 2',
    QtCore.Qt.Key_3: 'Numpad 3',
    QtCore.Qt.Key_4: 'Numpad 4',
    QtCore.Qt.Key_5: 'Numpad 5',
    QtCore.Qt.Key_6: 'Numpad 6',
    QtCore.Qt.Key_7: 'Numpad 7',
    QtCore.Qt.Key_8: 'Numpad 8',
    QtCore.Qt.Key_9: 'Numpad 9',
    QtCore.Qt.Key_Asterisk: 'Multiply',
    QtCore.Qt.Key_Plus: 'Add',
    QtCore.Qt.Key_Comma: 'Separator',
    QtCore.Qt.Key_Minus: 'Subtract',
    QtCore.Qt.Key_Period: 'Decimal',
    QtCore.Qt.Key_Slash: 'Divide'
}

# Mapping from PyQt non-keypad key names to Pyface key names.
key_map = {
    QtCore.Qt.Key_0: '0',
    QtCore.Qt.Key_1: '1',
    QtCore.Qt.Key_2: '2',
    QtCore.Qt.Key_3: '3',
    QtCore.Qt.Key_4: '4',
    QtCore.Qt.Key_5: '5',
    QtCore.Qt.Key_6: '6',
    QtCore.Qt.Key_7: '7',
    QtCore.Qt.Key_8: '8',
    QtCore.Qt.Key_9: '9',
    QtCore.Qt.Key_A: 'A',
    QtCore.Qt.Key_B: 'B',
    QtCore.Qt.Key_C: 'C',
    QtCore.Qt.Key_D: 'D',
    QtCore.Qt.Key_E: 'E',
    QtCore.Qt.Key_F: 'F',
    QtCore.Qt.Key_G: 'G',
    QtCore.Qt.Key_H: 'H',
    QtCore.Qt.Key_I: 'I',
    QtCore.Qt.Key_J: 'J',
    QtCore.Qt.Key_K: 'K',
    QtCore.Qt.Key_L: 'L',
    QtCore.Qt.Key_M: 'M',
    QtCore.Qt.Key_N: 'N',
    QtCore.Qt.Key_O: 'O',
    QtCore.Qt.Key_P: 'P',
    QtCore.Qt.Key_Q: 'Q',
    QtCore.Qt.Key_R: 'R',
    QtCore.Qt.Key_S: 'S',
    QtCore.Qt.Key_T: 'T',
    QtCore.Qt.Key_U: 'U',
    QtCore.Qt.Key_V: 'V',
    QtCore.Qt.Key_W: 'W',
    QtCore.Qt.Key_X: 'X',
    QtCore.Qt.Key_Y: 'Y',
    QtCore.Qt.Key_Z: 'Z',
    QtCore.Qt.Key_Space: 'Space',
    QtCore.Qt.Key_Backspace: 'Backspace',
    QtCore.Qt.Key_Tab: 'Tab',
    QtCore.Qt.Key_Enter: 'Enter',
    QtCore.Qt.Key_Return: 'Return',
    QtCore.Qt.Key_Escape: 'Esc',
    QtCore.Qt.Key_Delete: 'Delete',
    QtCore.Qt.Key_Cancel: 'Cancel',
    QtCore.Qt.Key_Clear: 'Clear',
    QtCore.Qt.Key_Shift: 'Shift',
    QtCore.Qt.Key_Menu: 'Menu',
    QtCore.Qt.Key_Pause: 'Pause',
    QtCore.Qt.Key_PageUp: 'Page Up',
    QtCore.Qt.Key_PageDown: 'Page Down',
    QtCore.Qt.Key_End: 'End',
    QtCore.Qt.Key_Home: 'Home',
    QtCore.Qt.Key_Left: 'Left',
    QtCore.Qt.Key_Up: 'Up',
    QtCore.Qt.Key_Right: 'Right',
    QtCore.Qt.Key_Down: 'Down',
    QtCore.Qt.Key_Select: 'Select',
    QtCore.Qt.Key_Print: 'Print',
    QtCore.Qt.Key_Execute: 'Execute',
    QtCore.Qt.Key_Insert: 'Insert',
    QtCore.Qt.Key_Help: 'Help',
    QtCore.Qt.Key_F1: 'F1',
    QtCore.Qt.Key_F2: 'F2',
    QtCore.Qt.Key_F3: 'F3',
    QtCore.Qt.Key_F4: 'F4',
    QtCore.Qt.Key_F5: 'F5',
    QtCore.Qt.Key_F6: 'F6',
    QtCore.Qt.Key_F7: 'F7',
    QtCore.Qt.Key_F8: 'F8',
    QtCore.Qt.Key_F9: 'F9',
    QtCore.Qt.Key_F10: 'F10',
    QtCore.Qt.Key_F11: 'F11',
    QtCore.Qt.Key_F12: 'F12',
    QtCore.Qt.Key_F13: 'F13',
    QtCore.Qt.Key_F14: 'F14',
    QtCore.Qt.Key_F15: 'F15',
    QtCore.Qt.Key_F16: 'F16',
    QtCore.Qt.Key_F17: 'F17',
    QtCore.Qt.Key_F18: 'F18',
    QtCore.Qt.Key_F19: 'F19',
    QtCore.Qt.Key_F20: 'F20',
    QtCore.Qt.Key_F21: 'F21',
    QtCore.Qt.Key_F22: 'F22',
    QtCore.Qt.Key_F23: 'F23',
    QtCore.Qt.Key_F24: 'F24',
    QtCore.Qt.Key_NumLock: 'Num Lock',
    QtCore.Qt.Key_ScrollLock: 'Scroll Lock'
}

#-------------------------------------------------------------------------
#  Converts a keystroke event into a corresponding key name:
#-------------------------------------------------------------------------


def key_event_to_name(event):
    """ Converts a keystroke event into a corresponding key name.
    """
    key_code = event.key()
    modifiers = event.modifiers()
    if modifiers & QtCore.Qt.KeypadModifier:
        key = keypad_map.get(key_code)
    else:
        key = None
    if key is None:
        key = key_map.get(key_code, 'Unknown-Key')

    name = ''
    if modifiers & QtCore.Qt.ControlModifier:
        name += 'Ctrl'

    if modifiers & QtCore.Qt.AltModifier:
        name += '-Alt' if name else 'Alt'

    if modifiers & QtCore.Qt.MetaModifier:
        name += '-Meta' if name else 'Meta'

    if modifiers & QtCore.Qt.ShiftModifier and (
            (name != '') or (len(key) > 1)):
        name += '-Shift' if name else 'Shift'

    if key:
        if name:
            name += '-'
        name += key
    return name
