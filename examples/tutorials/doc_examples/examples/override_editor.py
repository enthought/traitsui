#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

# override_editor.py --- Example of overriding a trait
#                        editor
from traits.api import HasTraits, Trait
from traitsui.api import Color, ColorEditor


class Polygon(HasTraits):
    line_color = Trait(Color((0, 0, 0)),
                       editor=ColorEditor())

Polygon().configure_traits()
