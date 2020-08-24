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


class DefaultTarget:
    """ A locator for locating a default target.  In some cases, handlers may
    not be registered for certain interactions on a given target.  Instead
    there may be a solver registered a locator_class of DefaultTarget and a
    target_class of the original target.  The registered solver will then
    return some generic (toolkit specific) object, for which frequently used
    handlers will be registered.  If user tries to perform the intetractions
    of these handlers on the original object, machinery is in place for the
    UIWrapper to try and locate a DefaultTarget and then look for the needed
    handler automatically, if it can not find a handler directly for the
    original target and interaction.

    Note: This object will likely be used by developers implementing solvers/
    handlers.  For those just using UITester, this object should work its magic
    under-the-hood, and not be needed directly. 
    """
    pass
