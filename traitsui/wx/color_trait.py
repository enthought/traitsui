#------------------------------------------------------------------------------
#
#  Copyright (c) 2005, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
#  Author: David C. Morrill
#  Date:   12/22/2004
#
#------------------------------------------------------------------------------

""" Trait definition for a wxPython-based color.
"""

#-------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------
from __future__ import absolute_import
import wx

from traits.api \
    import Trait, TraitError

# Version dependent imports (ColourPtr not defined in wxPython 2.5):
try:
    ColourPtr = wx.ColourPtr
except:
    class ColourPtr(object):
        pass


#-------------------------------------------------------------------------
#  W3CColourDatabase
#-------------------------------------------------------------------------

class W3CColourDatabase(object):
    """ Proxy for the ColourDatabase which allows for finding W3C colors.

        This class is necessary because the wx 'green' is the W3C 'lime',
        and we need some means to lookup the color names since wx has
        only a few hardcoded.

        This class is a proxy because AddColour expects a wx.ColourDatabase
        instance, not an instance of a subclass
    """

    _database = wx.ColourDatabase()

    def __init__(self):
        self._color_names = ['aqua', 'black', 'blue', 'fuchsia', 'gray',
                             'green', 'lime', 'maroon', 'navy', 'olive',
                             'purple', 'red', 'silver', 'teal', 'white',
                             'yellow']

        self.AddColour('aqua', wx.Colour(0, 0xff, 0xff, 255))
        self.AddColour('fuchsia', wx.Colour(0xff, 0, 0xff, 255))
        self.AddColour('green', wx.Colour(0, 0x80, 0, 255))
        self.AddColour('lime', wx.Colour(0, 0xff, 0, 255))
        self.AddColour('maroon', wx.Colour(0x80, 0x0, 0, 255))
        self.AddColour('navy', wx.Colour(0x00, 0x0, 0x80, 255))
        self.AddColour('olive', wx.Colour(0x80, 0x80, 0, 255))
        self.AddColour('purple', wx.Colour(0x80, 0x00, 0x80, 255))
        self.AddColour('silver', wx.Colour(0xc0, 0xc0, 0xc0, 255))
        self.AddColour('teal', wx.Colour(0, 0x80, 0x80, 255))

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

        return ''

w3c_color_database = W3CColourDatabase()

#-------------------------------------------------------------------------
#  Convert a number into a wxColour object:
#-------------------------------------------------------------------------


def tuple_to_wxcolor(tup):
    if 3 <= len(tup) <= 4:
        for c in tup:
            if not isinstance(c, int):
                raise TraitError

        return wx.Colour(*tup)
    else:
        raise TraitError


def convert_to_color(object, name, value):
    """ Converts a number into a wxColour object.
    """
    if isinstance(value, tuple):
        return tuple_to_wxcolor(value)

    elif isinstance(value, ColourPtr):
        return wx.Colour(value.Red(), value.Green(), value.Blue())

    elif isinstance(value, wx.Colour):
        return value

    elif isinstance(value, str):

        if value in standard_colors:
            return standard_colors[value]

        # Check for tuple-ness
        tmp = value.strip()
        if tmp.startswith("(") and tmp.endswith(
                ")") and tmp.count(",") in (2, 3):
            tup = eval(tmp)
            return tuple_to_wxcolor(tup)

    elif isinstance(value, int):
        num = int(value)
        return wx.Colour(num / 0x10000, (num / 0x100) & 0xFF, num & 0xFF)

    raise TraitError

convert_to_color.info = ('a string of the form (r,g,b) or (r,g,b,a) where r, '
                         'g, b, and a are integers from 0 to 255, a wx.Colour '
                         'instance, an integer which in hex is of the form '
                         '0xRRGGBB, where RR is red, GG is green, and BB is '
                         'blue')

#-------------------------------------------------------------------------
#  Standard colors:
#-------------------------------------------------------------------------

standard_colors = {}
for name in ['aquamarine', 'black', 'blue', 'blue violet', 'brown',
             'cadet blue', 'coral', 'cornflower blue', 'cyan', 'dark grey',
             'dark green', 'dark olive green', 'dark orchid',
             'dark slate blue', 'dark slate grey', 'dark turquoise',
             'dim grey', 'firebrick', 'forest green', 'gold', 'goldenrod',
             'grey', 'green', 'green yellow', 'indian red', 'khaki',
             'light blue', 'light grey', 'light steel blue', 'lime green',
             'magenta', 'maroon', 'medium aquamarine', 'medium blue',
             'medium forest green', 'medium goldenrod', 'medium orchid',
             'medium sea green', 'medium slate blue', 'medium spring green',
             'medium turquoise', 'medium violet red', 'midnight blue', 'navy',
             'orange', 'orange red', 'orchid', 'pale green', 'pink', 'plum',
             'purple', 'red', 'salmon', 'sea green', 'sienna', 'sky blue',
             'slate blue', 'spring green', 'steel blue', 'tan', 'thistle',
             'turquoise', 'violet', 'violet red', 'wheat', 'white', 'yellow',
             'yellow green']:
    try:
        wx_color = w3c_color_database.Find(name)
        standard_colors[name] = convert_to_color(None, None,
                                                 wx_color)
    except:
        pass

#-------------------------------------------------------------------------
#  Define wxPython specific color traits:
#-------------------------------------------------------------------------

### Note: Declare the editor to be a function which returns the ColorEditor
# class from traits ui to avoid circular import issues. For backwards
# compatibility with previous Traits versions, the 'editors' folder in Traits
# project declares 'from api import *' in its __init__.py. The 'api' in turn
# can contain classes that have a Color trait which lead to this file getting
# imported. This leads to a circular import when declaring a Color trait.


def get_color_editor(*args, **traits):
    from .color_editor import ToolkitEditorFactory
    return ToolkitEditorFactory(*args, **traits)


def WxColor(default='white', allow_none=False, **metadata):
    """ Defines wxPython-specific color traits.
    """

    if allow_none:
        return Trait(default, None, standard_colors, convert_to_color,
                     editor=get_color_editor, **metadata)

    return Trait(default, standard_colors, convert_to_color,
                 editor=get_color_editor, **metadata)
