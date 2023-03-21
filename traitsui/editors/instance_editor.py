# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Defines the instance editor factory for all traits user interface
toolkits.
"""

from traits.api import Bool, Enum, List, Str, Type

from traitsui.editor_factory import EditorFactory
from traitsui.instance_choice import InstanceChoice, InstanceChoiceItem
from traitsui.ui_traits import AView
from traitsui.view import View, AKind


class InstanceEditor(EditorFactory):
    """Editor factory for instance editors."""

    # -------------------------------------------------------------------------
    #  Trait definitions:
    # -------------------------------------------------------------------------

    #: List of items describing the types of selectable or editable instances
    values = List(InstanceChoiceItem)

    #: Extended name of the context object trait containing the list of types
    #: of selectable or editable instances
    name = Str()

    #: Is the current value of the object trait editable (vs. merely
    #: selectable)?
    editable = Bool(True)

    #: Should the object trait value be selectable from a list of objects (a
    #: value of True forces a selection list to be displayed, while a value of
    #: False displays a selection list only if at least one object in the list
    #: of possible object values is selectable):
    selectable = Bool(False)

    #: Should the editor support drag and drop of objects to set the trait
    #: value (a value of True forces the editor to allow drag and drop, while
    #: a value of False only supports drag and drop if at least one item in the
    #: list of possible objects supports drag and drop):
    droppable = Bool(False)

    #: Should factory-created objects be cached?
    cachable = Bool(True)

    #: Optional label for button
    label = Str()

    #: Optional instance view to use
    view = AView

    #: Extended name of the context object trait containing the view, or name
    #: of the view, to use
    view_name = Str()

    #: The ID to use with the view
    id = Str()

    #: Kind of pop-up editor (live, modal, nonmodal, wizard)
    kind = AKind

    #: The orientation of the instance editor relative to the instance selector
    orientation = Enum("default", "horizontal", "vertical")

    #: The default adapter class used to create InstanceChoice compatible
    #: adapters for instance objects:
    adapter = Type(InstanceChoice, allow_none=False)

    # -------------------------------------------------------------------------
    #  Traits view definitions:
    # -------------------------------------------------------------------------

    traits_view = View(
        [
            ["label{Button label}", "view{View name}", "|[]"],
            ["kind@", "|[Pop-up editor style]<>"],
        ]
    )


# This alias is deprecated and will be removed in TraitsUI 8.
ToolkitEditorFactory = InstanceEditor
