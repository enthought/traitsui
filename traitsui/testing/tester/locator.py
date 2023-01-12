# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" This module defines objects for locating nested UI targets, to be
used with ``UIWrapper.locate``.

Implementations for these actions are expected to return a value which is
a UI target where further location resolution or user interaction can be
applied.
"""


class Cell:
    """ A locator for locating a target uniquely specified by a row index and a
    column index.

    Attributes
    ----------
    row : int
        0-based index
    column : int
        0-based index
    """

    def __init__(self, row, column):
        self.row = row
        self.column = column


class Index:
    """A locator for locating a target that is uniquely specified by a single
    0-based index.

    Attributes
    ----------
    index : int
        0-based index
    """

    def __init__(self, index):
        self.index = index


class TargetByName:
    """A locator for locating the next UI target using a name.

    Attributes
    ----------
    name : str
    """

    def __init__(self, name):
        self.name = name


class TargetById:
    """A locator for locating the next UI target using an id.

    Attributes
    ----------
    id : str
    """

    def __init__(self, id):
        self.id = id


class Slider:
    """A locator for locating a nested slider widget within a UI."""

    pass


class Textbox:
    """A locator for locating a nested textbox widget within a UI."""

    pass
