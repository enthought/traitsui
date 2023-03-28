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

""" Trait definition for a PyQt-based font.
"""


from pyface.qt import QtGui
from pyface.font import Font as PyfaceFont
from traits.api import Trait, TraitHandler, TraitError


# -------------------------------------------------------------------------
#  Convert a string into a valid QFont object (if possible):
# -------------------------------------------------------------------------

# Mapping of strings to valid QFont style hints.
font_families = {
    "default": QtGui.QFont.StyleHint.AnyStyle,
    "decorative": QtGui.QFont.StyleHint.Decorative,
    "roman": QtGui.QFont.StyleHint.Serif,
    "script": QtGui.QFont.StyleHint.Cursive,
    "swiss": QtGui.QFont.StyleHint.SansSerif,
    "modern": QtGui.QFont.StyleHint.TypeWriter,
}

# Mapping of strings to QFont styles.
font_styles = {
    "slant": QtGui.QFont.Style.StyleOblique,
    "oblique": QtGui.QFont.Style.StyleOblique,
    "italic": QtGui.QFont.Style.StyleItalic,
}

# Mapping of strings to QFont weights.
font_weights = {"light": QtGui.QFont.Weight.Light, "bold": QtGui.QFont.Weight.Bold}

# Strings to ignore in text representations of fonts
font_noise = ["pt", "point", "family"]


def font_to_str(font):
    """Converts a QFont into a string description of itself."""
    style_hint = {
        QtGui.QFont.StyleHint.Decorative: "decorative",
        QtGui.QFont.StyleHint.Serif: "roman",
        QtGui.QFont.StyleHint.Cursive: "script",
        QtGui.QFont.StyleHint.SansSerif: "swiss",
        QtGui.QFont.StyleHint.TypeWriter: "modern",
    }.get(font.styleHint(), "")
    weight = {QtGui.QFont.Weight.Light: " Light", QtGui.QFont.Weight.Bold: " Bold"}.get(
        font.weight(), ""
    )
    style = {
        QtGui.QFont.Style.StyleOblique: " Oblique",
        QtGui.QFont.Style.StyleItalic: " Italic",
    }.get(font.style(), "")
    underline = ""
    if font.underline():
        underline = " underline"
    return "%s point %s%s%s%s" % (
        font.pointSize(),
        str(font.family()),
        style,
        weight,
        underline,
    )


def create_traitsfont(value):
    """Create a TraitsFont object.

    This can take either a string description, a QFont, or a Pyface Font.
    """
    if isinstance(value, PyfaceFont):
        return TraitsFont(value.to_toolkit())
    if isinstance(value, QtGui.QFont):
        return TraitsFont(value)

    point_size = None
    family = ""
    style_hint = QtGui.QFont.StyleHint.AnyStyle
    style = QtGui.QFont.Style.StyleNormal
    weight = QtGui.QFont.Weight.Normal
    underline = False
    facename = []

    for word in value.split():
        lword = word.lower()
        if lword in font_families:
            style_hint = font_families[lword]
        elif lword in font_styles:
            style = font_styles[lword]
        elif lword in font_weights:
            weight = font_weights[lword]
        elif lword == "underline":
            underline = True
        elif lword not in font_noise:
            if point_size is None:
                try:
                    point_size = int(lword)
                    continue
                except ValueError:
                    pass
            facename.append(word)

    if facename:
        family = " ".join(facename)

    if family:
        fnt = TraitsFont(family)
    else:
        fnt = TraitsFont()

    fnt.setStyleHint(style_hint)
    fnt.setStyle(style)
    fnt.setWeight(weight)
    fnt.setUnderline(underline)

    if point_size is None:
        fnt.setPointSize(QtGui.QApplication.font().pointSize())
    else:
        fnt.setPointSize(point_size)

    return fnt


class TraitsFont(QtGui.QFont):
    """A Traits-specific QFont."""

    def __reduce_ex__(self, protocol):
        """Returns the pickleable form of a TraitsFont object."""
        return (create_traitsfont, (font_to_str(self),))

    def __str__(self):
        """Returns a printable form of the font."""
        return font_to_str(self)


# -------------------------------------------------------------------------
#  'TraitPyQtFont' class'
# -------------------------------------------------------------------------


class TraitPyQtFont(TraitHandler):
    """Ensures that values assigned to a trait attribute are valid font
    descriptor strings; the value actually assigned is the corresponding
    TraitsFont.
    """

    def validate(self, object, name, value):
        """Validates that the value is a valid font descriptor string. If so,
        it returns the corresponding TraitsFont; otherwise, it raises a
        TraitError.
        """
        if value is None:
            return None

        try:
            return create_traitsfont(value)
        except:
            pass

        raise TraitError(object, name, "a font descriptor string", repr(value))

    def info(self):
        return (
            "a string describing a font (e.g. '12 pt bold italic "
            "swiss family Arial' or 'default 12')"
        )


# -------------------------------------------------------------------------
#  Callable that returns an instance of the PyQtToolkitEditorFactory for font
#  editors.
# -------------------------------------------------------------------------

### FIXME: We have declared the 'editor' to be a function instead of  the
# traitsui.qt.font_editor.ToolkitEditorFactory class, since the
# latter is leading to too many circular imports. In the future, try to see if
# there is a better way to do this.


def get_font_editor(*args, **traits):
    from traitsui.qt.font_editor import ToolkitEditorFactory

    return ToolkitEditorFactory(*args, **traits)


# -------------------------------------------------------------------------
#  Define a PyQt specific font trait:
# -------------------------------------------------------------------------

PyQtFont = Trait(TraitsFont(), TraitPyQtFont(), editor=get_font_editor)
