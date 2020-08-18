""" This module defines action objects that can be passed to
``UITester.perform`` where the actions represent 'queries'.

Implementations for these actions are expected to return value(s), ideally
without incurring side-effects (though in some situation side effects might
also be expected in the GUI context.)
"""


class DisplayedText:
    """ An object representing an action to obtain the displayed (echoed)
    plain text.

    E.g. For a textbox using a password styling, the displayed text should
    be a string of platform-dependent password mask characters.

    Implementations should return a str.
    """
    pass
