#------------------------------------------------------------------------------
#
#  Copyright (c) 2009, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
#------------------------------------------------------------------------------

""" Trait definition for an RGB-based color, which is a tuple of the form
    (*red*, *green*, *blue*), where *red*, *green* and *blue* are floats in the
    range from 0.0 to 1.0.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from traits.api import Trait, TraitError
from traits.trait_base import SequenceTypes

from traitsui.qt4.color_trait import standard_colors

#-------------------------------------------------------------------------------
#  Convert a number into an RGB tuple:
#-------------------------------------------------------------------------------

def range_check(value):
    """ Checks that *value* can be converted to a value in the range 0.0 to 1.0.

        If so, it returns the floating point value; otherwise, it raises a
        TraitError.
    """
    value = float(value)
    if 0.0 <= value <= 1.0:
        return value
    raise TraitError

def convert_to_color(object, name, value):
    """ Converts a tuple or an integer to an RGB color value, or raises a
        TraitError if that is not possible.
    """
    if isinstance(value, SequenceTypes) and len(value) == 3:
        return (range_check(value[0]),
                range_check(value[1]),
                range_check(value[2]))
    if isinstance(value, int):
        return ((value / 0x10000)        / 255.0,
                ((value / 0x100) & 0xFF) / 255.0,
                (value & 0xFF)           / 255.0)
    raise TraitError

convert_to_color.info = ('a tuple of the form (r,g,b), where r, g, and b '
    'are floats in the range from 0.0 to 1.0, or an integer which in hex is of '
    'the form 0xRRGGBB, where RR is red, GG is green, and BB is blue')

#-------------------------------------------------------------------------------
#  Standard colors:
#-------------------------------------------------------------------------------

# RGB versions of standard colors:
rgb_standard_colors = {}
for name, color in standard_colors.items():
    rgb_standard_colors[name] = (color.redF(),
                                 color.greenF(),
                                 color.blueF())

#-------------------------------------------------------------------------------
#  Define wxPython specific color traits:
#-------------------------------------------------------------------------------

### Note: Declare the editor to be a function which returns the RGBColorEditor
# class from traits ui to avoid circular import issues. For backwards
# compatibility with previous Traits versions, the 'editors' folder in Traits
# project declares 'from api import *' in its __init__.py. The 'api' in turn
# can contain classes that have a RGBColor trait which lead to this file getting
# imported. This will lead to a circular import when declaring a RGBColor trait.
def get_rgb_color_editor(*args, **traits):
    from rgb_color_editor import ToolkitEditorFactory
    return ToolkitEditorFactory(*args, **traits)

# Trait whose value must be an RGB color:
RGBColor = Trait('white', convert_to_color, rgb_standard_colors,
                 editor=get_rgb_color_editor)


