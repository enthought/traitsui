# (C) Copyright 2008-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

# ------------------------------------------------------------------------------
# Copyright (c) 2007, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD license.
# However, when used with the GPL version of PyQt the additional terms
# described in the PyQt GPL exception also apply

#
# Author: Riverbank Computing Limited
# ------------------------------------------------------------------------------

""" Trait definition for a PyQt-based color.
"""

from ast import literal_eval

from pyface.qt import QtGui
from pyface.color import Color as PyfaceColor
from pyface.util.color_helpers import channels_to_ints
from pyface.util.color_parser import color_table
from traits.api import Trait, TraitError


def convert_to_color(object, name, value):
    """Converts a number into a QColor object."""
    # Try the toolkit agnostic format.
    try:
        tup = literal_eval(value)
    except Exception:
        tup = value

    if isinstance(value, str):
        # Allow for spaces in the string value.
        value = value.replace(" ", "")

        # is it in the color table?
        if value in color_table:
            tup = channels_to_ints(color_table[value])

    if isinstance(tup, tuple):
        if 3 <= len(tup) <= 4 and all(isinstance(x, int) for x in tup):
            try:
                color = QtGui.QColor(*tup)
            except Exception:
                raise TraitError
        else:
            raise TraitError
    elif isinstance(value, PyfaceColor):
        color = value.to_toolkit()
    else:
        # Let the standard ctors handle the value.
        try:
            color = QtGui.QColor(value)
        except TypeError:
            raise TraitError

    if not color.isValid():
        raise TraitError

    return color


convert_to_color.info = (
    "a string of the form (r,g,b) or (r,g,b,a) where r, "
    "g, b, and a are integers from 0 to 255, a QColor "
    "instance, a Qt.GlobalColor, an integer which in hex "
    "is of the form 0xRRGGBB, a string of the form #RGB, "
    "#RRGGBB, #RRRGGGBBB or #RRRRGGGGBBBB"
)

# -------------------------------------------------------------------------
#  Standard colors:
# -------------------------------------------------------------------------

standard_colors = {}
for name, rgba in color_table.items():
    rgba_bytes = channels_to_ints(rgba)
    standard_colors[str(name)] = QtGui.QColor(*rgba_bytes)

# -------------------------------------------------------------------------
#  Callable that returns an instance of the PyQtToolkitEditorFactory for color
#  editors.
# -------------------------------------------------------------------------

### FIXME: We have declared the 'editor' to be a function instead of  the
# traitsui.qt.color_editor.ToolkitEditorFactory class, since the
# latter is leading to too many circular imports. In the future, try to see if
# there is a better way to do this.


def get_color_editor(*args, **traits):
    from traitsui.qt.color_editor import ToolkitEditorFactory

    return ToolkitEditorFactory(*args, **traits)


def PyQtColor(default="white", allow_none=False, **metadata):
    """Defines PyQt-specific color traits."""
    if default is None:
        allow_none = True

    if allow_none:
        return Trait(
            default,
            None,
            standard_colors,
            convert_to_color,
            editor=get_color_editor,
            **metadata,
        )

    return Trait(
        default,
        standard_colors,
        convert_to_color,
        editor=get_color_editor,
        **metadata,
    )
