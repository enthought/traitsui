#  (C) Copyright 2007-2022 Enthought, Inc., Austin, TX
#  License: BSD Style.

# override_editor.py --- Example of overriding a trait
#                        editor
from traits.api import HasTraits, Trait
from traitsui.api import Color, ColorEditor


class Polygon(HasTraits):
    line_color = Trait(Color((0, 0, 0)), editor=ColorEditor())


Polygon().configure_traits()
