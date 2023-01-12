# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Trait definition for a wxPython-based color.
"""

from ast import literal_eval

import wx

from pyface.color import Color as PyfaceColor
from pyface.util.color_helpers import channels_to_ints
from pyface.util.color_parser import color_table
from traits.api import Trait, TraitError


# -------------------------------------------------------------------------
#  W3CColourDatabase
# -------------------------------------------------------------------------


class W3CColourDatabase(object):
    """Proxy for the ColourDatabase which allows for finding W3C colors.

    This class is necessary because the wx 'green' is the W3C 'lime',
    and we need some means to lookup the color names since wx has
    only a few hardcoded.

    This class is a proxy because AddColour expects a wx.ColourDatabase
    instance, not an instance of a subclass
    """

    _database = wx.ColourDatabase()

    def __init__(self):
        # correct for differences in definitions
        self._color_names = [
            "aqua",
            "black",
            "blue",
            "fuchsia",
            "gray",
            "green",
            "lime",
            "maroon",
            "navy",
            "olive",
            "purple",
            "red",
            "silver",
            "teal",
            "white",
            "yellow",
        ]

        self.AddColour("aqua", wx.Colour(0, 0xFF, 0xFF, 255))
        self.AddColour("fuchsia", wx.Colour(0xFF, 0, 0xFF, 255))
        self.AddColour("green", wx.Colour(0, 0x80, 0, 255))
        self.AddColour("lime", wx.Colour(0, 0xFF, 0, 255))
        self.AddColour("maroon", wx.Colour(0x80, 0x0, 0, 255))
        self.AddColour("navy", wx.Colour(0x00, 0x0, 0x80, 255))
        self.AddColour("olive", wx.Colour(0x80, 0x80, 0, 255))
        self.AddColour("purple", wx.Colour(0x80, 0x00, 0x80, 255))
        self.AddColour("silver", wx.Colour(0xC0, 0xC0, 0xC0, 255))
        self.AddColour("teal", wx.Colour(0, 0x80, 0x80, 255))

        # add all the standard colours
        for name, rgba in color_table.items():
            rgba_bytes = channels_to_ints(rgba)
            self.AddColour(name, wx.Colour(*rgba_bytes))

    def AddColour(self, name, color):
        if name not in self._color_names:
            self._color_names.append(name)
        return self._database.AddColour(name, color)

    def Find(self, color_name):
        return self._database.Find(color_name)

    def FindName(self, color):
        for color_name in self._color_names:
            if self.Find(color_name) == color:
                return color_name

        return ""


w3c_color_database = W3CColourDatabase()

# -------------------------------------------------------------------------
#  Convert a number into a wxColour object:
# -------------------------------------------------------------------------


def tuple_to_wxcolor(tup):
    if 3 <= len(tup) <= 4:
        for c in tup:
            if not isinstance(c, int):
                raise TraitError

        return wx.Colour(*tup)
    else:
        raise TraitError


def convert_to_color(object, name, value):
    """Converts a number into a wxColour object."""
    if isinstance(value, tuple):
        return tuple_to_wxcolor(value)

    elif isinstance(value, PyfaceColor):
        return value.to_toolkit()

    elif isinstance(value, wx.Colour):
        return value

    elif isinstance(value, str):
        # Allow for spaces in the string value.
        value = value.replace(" ", "")

        if value in standard_colors:
            return standard_colors[value]

        # Check for tuple string
        try:
            tup = literal_eval(value)
        except Exception:
            raise TraitError
        return tuple_to_wxcolor(tup)

    else:
        try:
            num = int(value)
        except Exception:
            raise TraitError
        return wx.Colour(num // 0x10000, (num // 0x100) & 0xFF, num & 0xFF)

    raise TraitError


convert_to_color.info = (
    "a string of the form (r,g,b) or (r,g,b,a) where r, "
    "g, b, and a are integers from 0 to 255, a wx.Colour "
    "instance, an integer which in hex is of the form "
    "0xRRGGBB, where RR is red, GG is green, and BB is "
    "blue"
)

# -------------------------------------------------------------------------
#  Standard colors:
# -------------------------------------------------------------------------

standard_colors = {}
for name in color_table:
    try:
        wx_color = w3c_color_database.Find(name)
        standard_colors[name] = convert_to_color(None, None, wx_color)
    except:
        pass

# -------------------------------------------------------------------------
#  Define wxPython specific color traits:
# -------------------------------------------------------------------------

### Note: Declare the editor to be a function which returns the ColorEditor
# class from traits ui to avoid circular import issues. For backwards
# compatibility with previous Traits versions, the 'editors' folder in Traits
# project declares 'from api import *' in its __init__.py. The 'api' in turn
# can contain classes that have a Color trait which lead to this file getting
# imported. This leads to a circular import when declaring a Color trait.


def get_color_editor(*args, **traits):
    from .color_editor import ToolkitEditorFactory

    return ToolkitEditorFactory(*args, **traits)


def WxColor(default="white", allow_none=False, **metadata):
    """Defines wxPython-specific color traits."""
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
