""" This module defines action objects that can be passed to
``UITester.perform`` where the actions represent 'commands'.

Implementations for these actions are expected to produce the
documented side effects without returning any values.
"""


class MouseClick:
    """ An object representing the user clicking a mouse button.
    Currently the left mouse button is assumed.

    In most circumstances, a widget can still be clicked on even if it is
    disabled. Therefore unlike key events, if the widget is disabled,
    implementations should not raise an exception.
    """
    pass


class MouseDClick:
    """ An object representing the user double clicking a mouse button.
    Currently the left mouse button is assumed.
    """
    pass


class KeySequence:
    """ An object representing the user typing a sequence of keys.

    Implementations should raise ``Disabled`` if the widget is disabled.

    Attribute
    ---------
    sequence : str
        A string that represents a sequence of key inputs.
        e.g. "Hello World"
    """

    def __init__(self, sequence):
        self.sequence = sequence


class KeyClick:
    """ An object representing the user clicking a key on the keyboard.

    Implementations should raise ``Disabled`` if the widget is disabled.

    Attribute
    ---------
    key : str
        Standardized (pyface) name for a keyboard event.
        e.g. "Enter", "Tab", "Space", "0", "1", "A", ...
    """

    def __init__(self, key):
        self.key = key
