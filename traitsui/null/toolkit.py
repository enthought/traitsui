# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Defines the concrete implementations of the traits Toolkit interface for
    the 'null' (do nothing) user interface toolkit.
"""


from ..toolkit import Toolkit


class GUIToolkit(Toolkit):

    # -------------------------------------------------------------------------
    #  GUI toolkit dependent trait definitions:
    # -------------------------------------------------------------------------

    def color_trait(self, *args, **traits):
        from . import color_trait as ct

        return ct.NullColor(*args, **traits)

    def rgb_color_trait(self, *args, **traits):
        from . import rgb_color_trait as rgbct

        return rgbct.RGBColor(*args, **traits)

    def font_trait(self, *args, **traits):
        from . import font_trait as ft

        return ft.NullFont(*args, **traits)

    def kiva_font_trait(self, *args, **traits):
        from . import font_trait as ft

        return ft.NullFont(*args, **traits)

    def constants(self, *args, **traits):
        constants = {
            "WindowColor": (236 / 255.0, 233 / 255.0, 216 / 255.0, 1.0)
        }
        return constants
