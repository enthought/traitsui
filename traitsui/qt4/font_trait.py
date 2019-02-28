#------------------------------------------------------------------------------
# Copyright (c) 2007, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD license.
# However, when used with the GPL version of PyQt the additional terms
# described in the PyQt GPL exception also apply

#
# Author: Riverbank Computing Limited
#------------------------------------------------------------------------------

""" Trait definition for a PyQt-based font.
"""

#-------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------

from __future__ import absolute_import
from pyface.qt import QtGui

from traits.api \
    import Trait, TraitHandler, TraitError
import six

#-------------------------------------------------------------------------
#  Convert a string into a valid QFont object (if possible):
#-------------------------------------------------------------------------

# Mapping of strings to valid QFont style hints.
font_families = {
    'default': QtGui.QFont.AnyStyle,
    'decorative': QtGui.QFont.Decorative,
    'roman': QtGui.QFont.Serif,
    'script': QtGui.QFont.SansSerif,
    'swiss': QtGui.QFont.SansSerif,
    'modern': QtGui.QFont.TypeWriter
}

# Mapping of strings to QFont styles.
font_styles = {
    'slant': QtGui.QFont.StyleOblique,
    'italic': QtGui.QFont.StyleItalic
}

# Mapping of strings to QFont weights.
font_weights = {
    'light': QtGui.QFont.Light,
    'bold': QtGui.QFont.Bold
}

# Strings to ignore in text representations of fonts
font_noise = ['pt', 'point', 'family']

#-------------------------------------------------------------------------
#  Converts a QFont into a string description of itself:
#-------------------------------------------------------------------------


def font_to_str(font):
    """ Converts a QFont into a string description of itself.
    """
    weight = {QtGui.QFont.Light: ' Light',
              QtGui.QFont.Bold: ' Bold'}.get(font.weight(), '')
    style = {QtGui.QFont.StyleOblique: ' Slant',
             QtGui.QFont.StyleItalic: ' Italic'}.get(font.style(), '')
    underline = ''
    if font.underline():
        underline = ' underline'
    return '%s point %s%s%s%s' % (
           font.pointSize(), six.text_type(font.family()), style, weight, underline)

#-------------------------------------------------------------------------
#  Create a TraitFont object from a string description:
#-------------------------------------------------------------------------


def create_traitsfont(value):
    """ Create a TraitFont object from a string description.
    """
    if isinstance(value, QtGui.QFont):
        return TraitsFont(value)

    point_size = None
    family = ''
    style = QtGui.QFont.StyleNormal
    weight = QtGui.QFont.Normal
    underline = False
    facename = []

    for word in value.split():
        lword = word.lower()
        if lword in font_families:
            f = QtGui.QFont()
            f.setStyleHint(font_families[lword])
            family = f.defaultFamily()
        elif lword in font_styles:
            style = font_styles[lword]
        elif lword in font_weights:
            weight = font_weights[lword]
        elif lword == 'underline':
            underline = True
        elif lword not in font_noise:
            if point_size is None:
                try:
                    point_size = int(lword)
                    continue
                except:
                    pass
            facename.append(word)

    if facename:
        family = ' '.join(facename)

    if family:
        fnt = TraitsFont(family)
    else:
        fnt = TraitsFont()

    fnt.setStyle(style)
    fnt.setWeight(weight)
    fnt.setUnderline(underline)

    if point_size is None:
        fnt.setPointSize(QtGui.QApplication.font().pointSize())
    else:
        fnt.setPointSize(point_size)

    return fnt

#-------------------------------------------------------------------------
#  'TraitsFont' class:
#-------------------------------------------------------------------------


class TraitsFont(QtGui.QFont):
    """ A Traits-specific QFont.
    """
    #-------------------------------------------------------------------------
    #  Returns the pickleable form of a TraitsFont object:
    #-------------------------------------------------------------------------

    def __reduce_ex__(self, protocol):
        """ Returns the pickleable form of a TraitsFont object.
        """
        return (create_traitsfont, (font_to_str(self), ))

    #-------------------------------------------------------------------------
    #  Returns a printable form of the font:
    #-------------------------------------------------------------------------

    def __str__(self):
        """ Returns a printable form of the font.
        """
        return font_to_str(self)

#-------------------------------------------------------------------------
#  'TraitPyQtFont' class'
#-------------------------------------------------------------------------


class TraitPyQtFont(TraitHandler):
    """ Ensures that values assigned to a trait attribute are valid font
    descriptor strings; the value actually assigned is the corresponding
    TraitsFont.
    """
    #-------------------------------------------------------------------------
    #  Validates that the value is a valid font:
    #-------------------------------------------------------------------------

    def validate(self, object, name, value):
        """ Validates that the value is a valid font descriptor string. If so,
        it returns the corresponding TraitsFont; otherwise, it raises a
        TraitError.
        """
        if value is None:
            return None

        try:
            return create_traitsfont(value)
        except:
            pass

        raise TraitError(object, name, 'a font descriptor string',
                         repr(value))

    def info(self):
        return ("a string describing a font (e.g. '12 pt bold italic "
                "swiss family Arial' or 'default 12')")

#-------------------------------------------------------------------------
#  Callable that returns an instance of the PyQtToolkitEditorFactory for font
#  editors.
#-------------------------------------------------------------------------

### FIXME: We have declared the 'editor' to be a function instead of  the
# traitsui.qt4.font_editor.ToolkitEditorFactory class, since the
# latter is leading to too many circular imports. In the future, try to see if
# there is a better way to do this.


def get_font_editor(*args, **traits):
    from traitsui.qt4.font_editor import ToolkitEditorFactory
    return ToolkitEditorFactory(*args, **traits)

#-------------------------------------------------------------------------
#  Define a PyQt specific font trait:
#-------------------------------------------------------------------------

PyQtFont = Trait(TraitsFont(), TraitPyQtFont(), editor=get_font_editor)
