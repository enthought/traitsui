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
    pass
