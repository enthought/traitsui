# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" This module defines interaction objects that can be passed to
``UIWrapper.perform`` where the actions represent 'commands'.

Implementations for these actions are expected to produce the
documented side effects without returning any values.
"""


class MouseClick:
    """An object representing the user clicking a mouse button.
    Currently the left mouse button is assumed.

    In most circumstances, a widget can still be clicked on even if it is
    disabled. Therefore unlike key events, if the widget is disabled,
    implementations should not raise an exception.
    """

    pass


class MouseDClick:
    """ An object representing the user double clicking a mouse button.
    Currently the left mouse button is assumed.

    In most circumstances, a widget can still be clicked on even if it is
    disabled. Therefore unlike key events, if the widget is disabled,
    implementations should not raise an exception.
    """
    pass


class KeySequence:
    """An object representing the user typing a sequence of keys.

    Implementations should raise ``Disabled`` if the widget is disabled.

    Attributes
    ----------
    sequence : str
        A string that represents a sequence of key inputs.
        e.g. "Hello World"
    """

    def __init__(self, sequence):
        self.sequence = sequence


class KeyClick:
    """An object representing the user clicking a key on the keyboard.

    Implementations should raise ``Disabled`` if the widget is disabled.

    Attributes
    ----------
    key : str
        Standardized (pyface) name for a keyboard event.
        e.g. "Enter", "Tab", "Space", "0", "1", "A", ...
    """

    def __init__(self, key):
        self.key = key
