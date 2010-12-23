#------------------------------------------------------------------------------
# Copyright (c) 2007, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD license.
# However, when used with the GPL version of PyQt the additional terms described in the PyQt GPL exception also apply

#
# Author: Riverbank Computing Limited
#------------------------------------------------------------------------------

""" Converts a QKeyEvent to a standardized "name".
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from enthought.qt.api import Qt
    
#-------------------------------------------------------------------------------
#  Constants:  
#-------------------------------------------------------------------------------

# Mapping from PyQt keypad key names to Enable key names.
keypad_map = {
    Qt.Key_Enter:     'Enter',
    Qt.Key_0:         'Numpad 0',
    Qt.Key_1:         'Numpad 1',
    Qt.Key_2:         'Numpad 2',
    Qt.Key_3:         'Numpad 3',
    Qt.Key_4:         'Numpad 4',
    Qt.Key_5:         'Numpad 5',
    Qt.Key_6:         'Numpad 6',
    Qt.Key_7:         'Numpad 7',
    Qt.Key_8:         'Numpad 8',
    Qt.Key_9:         'Numpad 9',
    Qt.Key_Asterisk:  'Multiply',
    Qt.Key_Plus:      'Add',
    Qt.Key_Comma:     'Separator',
    Qt.Key_Minus:     'Subtract',
    Qt.Key_Period:    'Decimal',
    Qt.Key_Slash:     'Divide'
}

# Mapping from PyQt non-keypad key names to Enable key names.
key_map = {
    Qt.Key_Backspace: 'Backspace',
    Qt.Key_Tab:       'Tab',
    Qt.Key_Return:    'Enter',
    Qt.Key_Escape:    'Esc',
    Qt.Key_Delete:    'Delete',
    #Qt.Key_START:     'Start',
    #Qt.Key_LBUTTON:   'Left Button',
    #Qt.Key_RBUTTON:   'Right Button',
    Qt.Key_Cancel:    'Cancel',
    #Qt.Key_MBUTTON:   'Middle Button',
    Qt.Key_Clear:     'Clear',
    Qt.Key_Shift:     'Shift',
    Qt.Key_Control:   'Control',
    Qt.Key_Menu:      'Menu',
    Qt.Key_Pause:     'Pause',
    #Qt.Key_CAPITAL:   'Capital',
    Qt.Key_PageUp:    'Page Up',
    Qt.Key_PageDown:  'Page Down',
    Qt.Key_End:       'End',
    Qt.Key_Home:      'Home',
    Qt.Key_Left:      'Left',
    Qt.Key_Up:        'Up',
    Qt.Key_Right:     'Right',
    Qt.Key_Down:      'Down',
    Qt.Key_Select:    'Select',
    Qt.Key_Print:     'Print',
    Qt.Key_Execute:   'Execute',
    #Qt.Key_SNAPSHOT:  'Snapshot',
    Qt.Key_Insert:    'Insert',
    Qt.Key_Help:      'Help',
    Qt.Key_F1:        'F1',
    Qt.Key_F2:        'F2',
    Qt.Key_F3:        'F3',
    Qt.Key_F4:        'F4',
    Qt.Key_F5:        'F5',
    Qt.Key_F6:        'F6',
    Qt.Key_F7:        'F7',
    Qt.Key_F8:        'F8',
    Qt.Key_F9:        'F9',
    Qt.Key_F10:       'F10',
    Qt.Key_F11:       'F11',
    Qt.Key_F12:       'F12',
    Qt.Key_F13:       'F13',
    Qt.Key_F14:       'F14',
    Qt.Key_F15:       'F15',
    Qt.Key_F16:       'F16',
    Qt.Key_F17:       'F17',
    Qt.Key_F18:       'F18',
    Qt.Key_F19:       'F19',
    Qt.Key_F20:       'F20',
    Qt.Key_F21:       'F21',
    Qt.Key_F22:       'F22',
    Qt.Key_F23:       'F23',
    Qt.Key_F24:       'F24',
    Qt.Key_NumLock:   'Num Lock',
    Qt.Key_ScrollLock:'Scroll Lock'
}
        
#-------------------------------------------------------------------------------
#  Converts a keystroke event into a corresponding key name:  
#-------------------------------------------------------------------------------
                
def key_event_to_name(event):
    """ Converts a keystroke event into a corresponding key name.
    """
    key_code = event.key()
    modifiers = event.modifiers()

    if modifiers & Qt.KeypadModifier:
        key = keypad_map.get(key_code)
    else:
        key = None

    if key is None:
        key = key_map.get(key_code)

    if key is None:
        key = unicode(event.text())

        if len(key) == 1 and 1 <= ord(key[0]) <= 26:
            key = chr(ord(key[0]) + ord('a') - 1)
    
    name = ''
    if modifiers & Qt.AltModifier:
        name = 'Alt'

    if modifiers & Qt.ControlModifier:
        name += '-Ctrl'
            
    if (modifiers & Qt.ShiftModifier) and ((name != '') or (len(key) > 1)):
        name += '-Shift'
        
    if key == ' ':
        key = 'Space'
    
    name += ('-' + key)

    if name[:1] == '-':
        return name[1:]

    return name
