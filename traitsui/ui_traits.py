# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Defines common traits used within the traits.ui package.
"""

from pyface.ui_traits import (
    Alignment,
    Border,
    HasBorder,
    HasMargin,
    Image,
    Margin,
    Position,
    convert_bitmap,
    convert_image,
)
from traits.api import (
    Any,
    Delegate,
    Enum,
    Expression,
    Float,
    HasStrictTraits,
    List,
    PrefixList,
    Range,
    Str,
    TraitError,
    TraitType,
)

from .helper import SequenceTypes

# -------------------------------------------------------------------------
#  Trait definitions:
# -------------------------------------------------------------------------

# Orientation trait:
Orientation = PrefixList(("vertical", "horizontal"))

# Styles for user interface elements:
EditorStyle = style_trait = PrefixList(
    ("simple", "custom", "text", "readonly"), cols=4
)

# Group layout trait:
Layout = PrefixList(("normal", "split", "tabbed", "flow", "fold"))

# Trait for the default object being edited:
AnObject = Expression("object")

# The default dock style to use:
DockStyle = dock_style_trait = Enum(
    "fixed",
    "horizontal",
    "vertical",
    "tab",
    desc="the default docking style to use",
)

# The category of elements dragged out of the view:
ExportType = Str(desc="the category of elements dragged out of the view")

# Delegate a trait value to the object's **container** trait:
ContainerDelegate = container_delegate = Delegate(
    "container", listenable=False
)

# An identifier for the external help context:
HelpId = help_id_trait = Str(desc="the external help context identifier")

# A button to add to a view:
AButton = Any()
# AButton = Trait( '', Str, Instance( 'traitsui.menu.Action' ) )

# The set of buttons to add to the view:
Buttons = List(
    AButton, desc="the action buttons to add to the bottom of the view"
)

# View trait specified by name or instance:
AView = Any()
# AView = Trait( '', Str, Instance( 'traitsui.view.View' ) )

# FIXME: on AButton and AView: TraitCompound handlers with deferred-import
# Instance traits are just broken. The Instance trait tries to update the
# top-level CTrait's fast_validate table when the import is resolved. However,
# sometimes the CTrait gets copied for unknown reasons and the copy's
# fast_validate table is not updated although the TraitCompound's
# slow_validates table is modified.

# -------------------------------------------------------------------------
#  'StatusItem' class:
# -------------------------------------------------------------------------


class StatusItem(HasStrictTraits):

    #: The name of the trait the status information will be synched with:
    name = Str("status")

    #: The width of the status field. The possible values are:
    #:
    #:   - abs( width )  > 1.0: Width of the field in pixels = abs( width )
    #:   - abs( width ) <= 1.0: Relative width of the field when compared to
    #:                          the other relative width fields.
    width = Float(0.5)

    def __init__(self, value=None, **traits):
        """Initializes the item object."""
        super().__init__(**traits)

        if value is not None:
            self.name = value


# -------------------------------------------------------------------------
#  'ViewStatus' trait:
# -------------------------------------------------------------------------


class ViewStatus(TraitType):
    """Defines a trait whose value must be a single StatusItem instance or a
    list of StatusItem instances.
    """

    #: Define the default value for the trait:
    default_value = None

    #: A description of the type of value this trait accepts:
    info_text = (
        "None, a string, a single StatusItem instance, or a list or "
        "tuple of strings and/or StatusItem instances"
    )

    def validate(self, object, name, value):
        """Validates that a specified value is valid for this trait."""
        if isinstance(value, str):
            return [StatusItem(name=value)]

        if isinstance(value, StatusItem):
            return [value]

        if value is None:
            return value

        result = []
        if isinstance(value, SequenceTypes):
            for item in value:
                if isinstance(item, str):
                    result.append(StatusItem(name=item))
                elif isinstance(item, StatusItem):
                    result.append(item)
                else:
                    break
            else:
                return result

        self.error(object, name, value)


# -------------------------------------------------------------------------
#  'ATheme' trait:
# -------------------------------------------------------------------------


def convert_theme(value, level=3):
    """Converts a specified value to a Theme if possible."""
    if not isinstance(value, str):
        return value

    if (value[:1] == "@") and (value.find(":") >= 2):
        try:
            from .image.image import ImageLibrary

            info = ImageLibrary.image_info(value)
        except:
            info = None

        if info is not None:
            return info.theme

    from .theme import Theme

    return Theme(image=convert_image(value, level + 1))


class ATheme(TraitType):
    """Defines a trait whose value must be a traits UI Theme or a string that
    can be converted to one.
    """

    #: Define the default value for the trait:
    default_value = None

    #: A description of the type of value this trait accepts:
    info_text = "a Theme or string that can be used to define one"

    def __init__(self, value=None, **metadata):
        """Creates an ATheme trait.

        Parameters
        ----------
        value : string or Theme
            The default value for the ATheme, either a Theme object, or a
            string from which a Theme object can be derived.
        """
        super().__init__(convert_theme(value), **metadata)

    def validate(self, object, name, value):
        """Validates that a specified value is valid for this trait."""
        from .theme import Theme

        if value is None:
            return None

        new_value = convert_theme(value, 4)
        if isinstance(new_value, Theme):
            return new_value

        self.error(object, name, value)


# -------------------------------------------------------------------------------
#  Other trait definitions:
# -------------------------------------------------------------------------

# The spacing between two items:
Spacing = Range(-32, 32, 3)
