#  Copyright (c) 2005-20, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt


# XXX eventually should replace with traits.api
from traits.trait_factory import TraitFactory

from .toolkit import toolkit


def ColorTrait(*args, **traits):
    """ Returns a trait whose value must be a GUI toolkit-specific color.

    Description
    -----------
    For wxPython, the returned trait accepts any of the following values:

    * A wx.Colour instance
    * A wx.ColourPtr instance
    * an integer whose hexadecimal form is 0x*RRGGBB*, where *RR* is the red
      value, *GG* is the green value, and *BB* is the blue value

    Default Value
    -------------
    For wxPython, 0xffffff (that is, white)
    """
    return toolkit().color_trait(*args, **traits)


def RGBColorTrait(*args, **traits):
    """ Returns a trait whose value must be a GUI toolkit-specific RGB-based
        color.

    Description
    -----------
    For wxPython, the returned trait accepts any of the following values:

    * A tuple of the form (*r*, *g*, *b*), in which *r*, *g*, and *b* represent
      red, green, and blue values, respectively, and are floats in the range
      from 0.0 to 1.0
    * An integer whose hexadecimal form is 0x*RRGGBB*, where *RR* is the red
      value, *GG* is the green value, and *BB* is the blue value

    Default Value
    -------------
    For wxPython, (1.0, 1.0, 1.0) (that is, white)
    """
    return toolkit().rgb_color_trait(*args, **traits)


def FontTrait(*args, **traits):
    """ Returns a trait whose value must be a GUI toolkit-specific font.

    Description
    -----------
    For wxPython, the returned trait accepts any of the following:

    * a wx.Font instance
    * a wx.FontPtr instance
    * a string describing the font, including one or more of the font family,
      size, weight, style, and typeface name.

    Default Value
    -------------
    For wxPython, 'Arial 10'
    """
    return toolkit().font_trait(*args, **traits)


Color = TraitFactory(ColorTrait)

RGBColor = TraitFactory(RGBColorTrait)

Font = TraitFactory(FontTrait)
