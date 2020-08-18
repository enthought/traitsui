""" This module defines objects for locating nested UI targets, to be
used with ``UIWrapper.locate``.

Implementations for these actions are expected to return a value which is
a UI target where further location resolution or user interaction can be
applied.
"""


class NestedUI:
    """ A locator for locating a nested ``traitsui.ui.UI`` object assuming
    there is only one. If there are multiple, more location information
    needs to have been provided already.
    """
    pass


class TargetByName:
    """ A locator for locating the next UI target using a name.

    Attributes
    ----------
    name : str
    """
    def __init__(self, name):
        self.name = name
