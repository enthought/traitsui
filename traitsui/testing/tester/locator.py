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

import enum


class Index:
    """ A locator for locating a target that is uniquely specified by a single
    0-based index.

    Attributes
    ----------
    index : int
        0-based index
    """

    def __init__(self, index):
        self.index = index


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


class TargetById:
    """ A locator for locating the next UI target using an id.

    Attributes
    ----------
    id : str
    """
    def __init__(self, id):
        self.id = id


class WidgetType(enum.Enum):
    """ A locator for locating nested widgets within a UI. Many editors will
    contain many sub-widgets (e.g. a textbox, slider, tabs, buttons, etc.).

    For example when working with a range editor, one could call
    ``tester.find_by_name(ui, "number").locate(locator.WidgetType.textbox)``
    where number utilizes a Range Editor.
    """

    # A textbox within a UI
    textbox = "textbox"
