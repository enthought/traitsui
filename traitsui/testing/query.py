""" This module defines action objects that can be passed to
``UITester.perform`` where the actions represent 'queries'.

Implementations for these actions are expected to return value(s), ideally
without incurring side-effects (though in some situation side effects might
also be expected in the GUI context.)
"""


class CustomAction:
    """ This is a special action for tests to wrap any arbitrary function
    to be used with UITester.

    The wrapped function will be called with an instance of ``UIWrapper``
    which contains a toolkit specific editor. With that, the wrapped function
    is likely toolkit specific.

    Instead of using ``CustomAction``, consider using ``InteractionRegistry``
    to register custom actions for custom editor and action types to allow test
    code to be toolkit agnostic.

    Attributes
    ----------
    func : callable(UIWrapper) -> any
    """
    def __init__(self, func):
        self.func = func


class DisplayedText:
    """ An object representing an action to obtain the displayed (echoed)
    plain text.

    E.g. For a textbox using a password styling, the displayed text should
    be a string of platform-dependent password mask characters.

    Implementations should return a str.
    """
    pass
