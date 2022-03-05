# (C) Copyright 2004-2022 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Trait definition for a wxPython-based font.
"""


import wx

from pyface.font import Font as PyfaceFont
from traits.api import Trait, TraitHandler, TraitError

# -------------------------------------------------------------------------
#  Convert a string into a valid 'wxFont' object (if possible):
# -------------------------------------------------------------------------

# Mapping of strings to valid wxFont families
font_families = {
    "default": wx.FONTFAMILY_DEFAULT,
    "decorative": wx.FONTFAMILY_DECORATIVE,
    "roman": wx.FONTFAMILY_ROMAN,
    "script": wx.FONTFAMILY_SCRIPT,
    "swiss": wx.FONTFAMILY_SWISS,
    "modern": wx.FONTFAMILY_MODERN,
    "typewriter": wx.FONTFAMILY_TELETYPE,
}

# Mapping of strings to wxFont styles
font_styles = {
    "slant": wx.FONTSTYLE_SLANT,
    "oblique": wx.FONTSTYLE_SLANT,
    "italic": wx.FONTSTYLE_ITALIC,
}

# Mapping of strings wxFont weights
font_weights = {"light": wx.FONTWEIGHT_LIGHT, "bold": wx.FONTWEIGHT_BOLD}

# Strings to ignore in text representations of fonts
font_noise = ["pt", "point", "family"]


def font_to_str(font):
    """Converts a wx.Font into a string description of itself."""
    family = {
        wx.FONTFAMILY_DECORATIVE: "decorative family",
        wx.FONTFAMILY_ROMAN: "roman family",
        wx.FONTFAMILY_SCRIPT: "script family",
        wx.FONTFAMILY_SWISS: "swiss family",
        wx.FONTFAMILY_MODERN: "modern family",
        wx.FONTFAMILY_TELETYPE: "typewriter family",
    }.get(font.GetFamily(), "")
    weight = {wx.FONTWEIGHT_LIGHT: " Light", wx.FONTWEIGHT_BOLD: " Bold"}.get(
        font.GetWeight(), ""
    )
    style = {wx.FONTSTYLE_SLANT: " Oblique", wx.FONTSTYLE_ITALIC: " Italic"}.get(
        font.GetStyle(), ""
    )
    underline = ""
    if font.GetUnderlined():
        underline = " underline"
    return "%s point %s%s%s%s%s" % (
        font.GetPointSize(),
        family,
        font.GetFaceName(),
        style,
        weight,
        underline,
    )


def create_traitsfont(value):
    """Create a TraitsFont object from a string description."""
    if isinstance(value, PyfaceFont):
        return TraitsFont(value.to_toolkit())
    if isinstance(value, wx.Font):
        return TraitsFont(value)

    point_size = None
    family = wx.FONTFAMILY_DEFAULT
    style = wx.FONTSTYLE_NORMAL
    weight = wx.FONTWEIGHT_NORMAL
    underline = 0
    facename = []
    for word in value.split():
        lword = word.lower()
        if lword in font_families:
            family = font_families[lword]
        elif lword in font_styles:
            style = font_styles[lword]
        elif lword in font_weights:
            weight = font_weights[lword]
        elif lword == "underline":
            underline = 1
        elif lword not in font_noise:
            if point_size is None:
                try:
                    point_size = int(lword)
                    continue
                except ValueError:
                    pass
            facename.append(word)
    if facename:
        font = TraitsFont(
            point_size or 10, family, style, weight, underline, " ".join(facename)
        )
        return font
    else:
        return TraitsFont(
            point_size or 10, family, style, weight, underline
        )


class TraitsFont(wx.Font):
    """A Traits-specific wx.Font."""

    def __reduce_ex__(self, protocol):
        """Returns the pickleable form of a TraitsFont object."""
        return (create_traitsfont, (font_to_str(self),))

    def __str__(self):
        """Returns a printable form of the font."""
        return font_to_str(self)


# -------------------------------------------------------------------------
#  'TraitWXFont' class'
# -------------------------------------------------------------------------


class TraitWXFont(TraitHandler):
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
#  Define a wxPython specific font trait:
# -------------------------------------------------------------------------

### Note: Declare the editor to be a function which returns the FontEditor
# class from traits ui to avoid circular import issues. For backwards
# compatibility with previous Traits versions, the 'editors' folder in Traits
# project declares 'from api import *' in its __init__.py. The 'api' in turn
# can contain classes that have a Font trait which lead to this file getting
# imported. This leads to a circular import when declaring a Font trait.


def get_font_editor(*args, **traits):
    from .font_editor import ToolkitEditorFactory

    return ToolkitEditorFactory(*args, **traits)


fh = TraitWXFont()
WxFont = Trait(
    wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT),
    fh,
    editor=get_font_editor,
)
