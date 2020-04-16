# ------------------------------------------------------------------------------
#
#  Copyright (c) 2008, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
#  Author: David C. Morrill
#  Date:   10/21/2004
#
# ------------------------------------------------------------------------------

""" Defines the button editor factory for all traits toolkit backends.
"""



from pyface.ui_traits import Image
from traits.api import Str, Range, Enum, Property, Either

from ..editor_factory import EditorFactory
from ..ui_traits import AView
from ..view import View


# -------------------------------------------------------------------------
#  'ToolkitEditorFactory' class:
# -------------------------------------------------------------------------


class ToolkitEditorFactory(EditorFactory):
    """ Editor factory for buttons.
    """

    # -------------------------------------------------------------------------
    #  Trait definitions:
    # -------------------------------------------------------------------------

    # Value to set when the button is clicked
    value = Property()

    # Optional label for the button
    label = Str()

    # The name of the external object trait that the button label is synced to
    label_value = Str()

    # The name of the trait on the object that contains the list of possible
    # values.  If this is set, then the value, label, and label_value traits
    # are ignored; instead, they will be set from this list.  When this button
    # is clicked, the value set will be the one selected from the drop-down.
    values_trait = Either(None, Str)

    # (Optional) Image to display on the button
    image = Image

    # Extra padding to add to both the left and the right sides
    width_padding = Range(0, 31, 7)

    # Extra padding to add to both the top and the bottom sides
    height_padding = Range(0, 31, 5)

    # Presentation style
    style = Enum("button", "radio", "toolbar", "checkbox")

    # Orientation of the text relative to the image
    orientation = Enum("vertical", "horizontal")

    # The optional view to display when the button is clicked:
    view = AView

    # -------------------------------------------------------------------------
    #  Traits view definition:
    # -------------------------------------------------------------------------

    traits_view = View(["label", "value", "|[]"])

    def _get_value(self):
        return self._value

    def _set_value(self, value):
        self._value = value
        if isinstance(value, str):
            try:
                self._value = int(value)
            except:
                try:
                    self._value = float(value)
                except:
                    pass

    def __init__(self, **traits):
        self._value = 0
        super(ToolkitEditorFactory, self).__init__(**traits)


# Define the ButtonEditor class
ButtonEditor = ToolkitEditorFactory
