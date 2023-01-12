# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

from traits.api import TraitFactory

from .toolkit import toolkit


def ColorTrait(*args, **traits):
    """Returns a trait whose value is a GUI toolkit-specific color.

    A number of different values are accepted for setting the value, including:

    * tuples of the form (r, g, b) and (r, g, b, a)
    * strings which match standard color names
    * strings of the form "(r, g, b)" and "(r, g, b, a)"
    * integers whose hex value is of the form 0xRRGGBB
    * toolkit-specific color classes

    Tuple values are expected to be in the range 0 to 255.

    Exact behaviour (eg. precisely what values are accepted, and what the
    "standard" color names are) is toolkit-dependent.

    The default value is white.  The default editor is a ColorEditor.

    Parameters
    ----------
    default: color
        The default color for the trait.
    allow_none: bool
        Whether to allow None as a value.
    **metadata
        Trait metadata to be passed through.
    """
    return toolkit().color_trait(*args, **traits)


def RGBColorTrait(*args, **traits):
    """Returns a trait whose value is a RGB tuple with values from 0 to 1.

    A number of different values are accepted for setting the value, including:

    * tuples of the form (r, g, b) with values from 0.0 to 1.0
    * strings which match standard color names
    * integers whose hex value is of the form 0xRRGGBB

    The default value is (1.0, 1.0, 1.0).  The default editor is a
    RGBColorEditor.

    Parameters
    ----------
    **metadata
        Trait metadata to be passed through.
    """
    return toolkit().rgb_color_trait(*args, **traits)


def FontTrait(*args, **traits):
    """Returns a trait whose value is a GUI toolkit-specific font.

    This trait accepts either a toolkit-specific font object, or a string
    containing a font description.  The string description can contain:

    * a font name or family.  The following generic names are understood:
      "default", "decorative", "roman", "script", "swiss", and "modern".
    * a size, in points.
    * a style, which is one of: "slant" or "italic"
    * a weight, which is one of: "light" or "bold"
    * whether the font is underlined, indicated by the inclusion of
      "underlined".

    Where values aren't supplied, the application defaults will be used
    instead.

    The default value is the application default font, which is toolkit
    and platform dependent.  The default editor is FontEditor.

    Parameters
    ----------
    **metadata
        Trait metadata to be passed through.
    """
    return toolkit().font_trait(*args, **traits)


Color = TraitFactory(ColorTrait)

RGBColor = TraitFactory(RGBColorTrait)

Font = TraitFactory(FontTrait)
