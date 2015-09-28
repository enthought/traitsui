#------------------------------------------------------------------------------
# Copyright (c) 2007, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD license.
# However, when used with the GPL version of PyQt the additional terms described in the PyQt GPL exception also apply

#
# Author: Riverbank Computing Limited
#------------------------------------------------------------------------------

""" Trait definition for a PyQt-based color.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from pyface.qt import QtGui

from traits.api \
    import Trait, TraitError

#-------------------------------------------------------------------------------
#  Convert a number into a QColor object:
#-------------------------------------------------------------------------------

def convert_to_color ( object, name, value ):
    """ Converts a number into a QColor object.
    """
    # Try the toolkit agnostic format.
    try:
        tup = eval(value)
    except:
        tup = value

    if isinstance(tup, tuple):
        if 3 <= len(tup) <= 4:
            try:
                color = QtGui.QColor(*tup)
            except TypeError:
                raise TraitError
        else:
            raise TraitError
    else:
        if isinstance(value, basestring):
            # Allow for spaces in the string value.
            value = value.replace(' ', '')

        # Let the standard ctors handle the value.
        try:
            color = QtGui.QColor(value)
        except TypeError:
            raise TraitError

    if not color.isValid():
        raise TraitError

    return color

convert_to_color.info = ('a string of the form (r,g,b) or (r,g,b,a) where r, '
                         'g, b, and a are integers from 0 to 255, a QColor '
                         'instance, a Qt.GlobalColor, an integer which in hex '
                         'is of the form 0xRRGGBB, a string of the form #RGB, '
                         '#RRGGBB, #RRRGGGBBB or #RRRRGGGGBBBB')

#-------------------------------------------------------------------------------
#  Standard colors:
#-------------------------------------------------------------------------------

# Note that this is slightly different from the wx implementation in that the
# names do not include spaces and the full set of SVG color keywords is
# supported.
standard_colors = {}
for name in QtGui.QColor.colorNames():
    standard_colors[str(name)] = QtGui.QColor(name)

#-------------------------------------------------------------------------------
#  Callable that returns an instance of the PyQtToolkitEditorFactory for color
#  editors.
#-------------------------------------------------------------------------------

### FIXME: We have declared the 'editor' to be a function instead of  the
# traitsui.qt4.color_editor.ToolkitEditorFactory class, since the
# latter is leading to too many circular imports. In the future, try to see if
# there is a better way to do this.
def get_color_editor(*args, **traits):
    from traitsui.qt4.color_editor import ToolkitEditorFactory
    return ToolkitEditorFactory(*args, **traits)

#-------------------------------------------------------------------------------
#  Define PyQt specific color traits:
#-------------------------------------------------------------------------------

def PyQtColor ( default = 'white', allow_none = False, **metadata ):
    """ Defines PyQt-specific color traits.
    """
    if allow_none:
        return Trait( default, None, standard_colors, convert_to_color,
                      editor = get_color_editor, **metadata )

    return Trait( default, standard_colors, convert_to_color,
                  editor = get_color_editor, **metadata )
