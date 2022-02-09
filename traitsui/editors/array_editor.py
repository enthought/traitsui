# (C) Copyright 2004-2022 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Defines the array editor factory for all traits toolkit backends.
"""

import numpy

from traits.api import Bool, HasTraits, Int, Float, Instance, TraitError

from traitsui.editor import Editor
from traitsui.editor_factory import EditorFactory
from traitsui.group import Group
from traitsui.item import Item
from traitsui.view import View


class ArrayEditor(EditorFactory):
    """Editor factory for array editors."""

    # -------------------------------------------------------------------------
    #  Trait definitions:
    # -------------------------------------------------------------------------

    #: Width of the individual fields
    width = Int(-80)

    #: Is user input set on every keystroke?
    auto_set = Bool(True)

    #: Is user input set when the Enter key is pressed?
    enter_set = Bool(False)


class ArrayStructure(HasTraits):

    # -------------------------------------------------------------------------
    #  Trait definitions:
    # -------------------------------------------------------------------------

    #: Editor that this structure is linked to
    editor = Instance(Editor)

    #: The constructed View for the array
    view = Instance(View)

    def __init__(self, editor):
        """Initializes the object."""
        super().__init__(editor=editor)

        # Set up the field width for each item:
        width = editor.factory.width

        # Set up the correct style for each filed:
        style = "simple"
        if editor.readonly:
            style = "readonly"

        # Get the array we are mirroring:
        object = editor.value

        # Determine the correct trait type to use for each element:
        trait = Float()

        if object.dtype.kind == "i":
            trait = Int()

        if len(object.shape) == 1:
            self.view = self._one_dim_view(object, style, width, trait)
        elif len(object.shape) == 2:
            self.view = self._two_dim_view(object, style, width, trait)
        else:
            raise TraitError("Only 1D or 2D arrays supported")

    # -------------------------------------------------------------------------
    #  1D view:
    # -------------------------------------------------------------------------

    def _one_dim_view(self, object, style, width, trait):
        content = []
        shape = object.shape
        items = []
        format_func = self.editor.factory.format_func
        format_str = self.editor.factory.format_str
        for i in range(shape[0]):
            name = "f%d" % i
            self.add_trait(
                name,
                trait(
                    object[i],
                    event="field",
                    auto_set=self.editor.factory.auto_set,
                    enter_set=self.editor.factory.enter_set,
                ),
            )
            items.append(
                Item(
                    name=name,
                    style=style,
                    width=width,
                    format_func=format_func,
                    format_str=format_str,
                    padding=-3,
                )
            )

        group = Group(orientation="horizontal", show_labels=False, *items)
        content.append(group)

        return View(Group(show_labels=False, *content))

    # -------------------------------------------------------------------------
    #  2D view:
    # -------------------------------------------------------------------------

    def _two_dim_view(self, object, style, width, trait):
        content = []
        shape = object.shape
        format_func = self.editor.factory.format_func
        format_str = self.editor.factory.format_str
        for i in range(shape[0]):
            items = []
            for j in range(shape[1]):
                name = "f%d_%d" % (i, j)
                self.add_trait(
                    name,
                    trait(
                        object[i, j],
                        event="field",
                        auto_set=self.editor.factory.auto_set,
                        enter_set=self.editor.factory.enter_set,
                    ),
                )
                items.append(
                    Item(
                        name=name,
                        style=style,
                        width=width,
                        format_func=format_func,
                        format_str=format_str,
                        padding=-3,
                    )
                )

            group = Group(orientation="horizontal", show_labels=False, *items)
            content.append(group)

        return View(Group(show_labels=False, *content))

    def _field_changed(self):
        """Updates the underlying array when any field changes value."""

        if not self.editor._busy:
            # Get the array we are mirroring:
            object = self.editor.value
            shape = object.shape
            value = numpy.zeros(shape, object.dtype)

            # 1D
            if len(shape) == 1:
                for i in range(shape[0]):
                    value[i] = getattr(self, "f%d" % i)
            # 2D
            elif len(shape) == 2:
                for i in range(shape[0]):
                    for j in range(shape[1]):
                        value[i, j] = getattr(self, "f%d_%d" % (i, j))

            self.editor.update_array(value)


# -------------------------------------------------------------------------
#  Toolkit-independent 'SimpleEditor' class:
# -------------------------------------------------------------------------


class SimpleEditor(Editor):
    """Simple style of editor for arrays."""

    # -------------------------------------------------------------------------
    #  Trait definitions:
    # -------------------------------------------------------------------------

    #: Is the editor read-only?
    readonly = Bool(False)

    def init(self, parent):
        """Finishes initializing the editor by creating the underlying toolkit
        widget.
        """
        self._as = _as = ArrayStructure(self)
        ui = _as.view.ui(_as, parent, kind="subpanel")
        ui.parent = self.ui
        self.control = ui.control

    def update_editor(self):
        """Updates the editor when the object trait changes externally to the
        editor.
        """

        if not self._busy:
            self._busy = True
            object = self.value
            shape = object.shape
            _as = self._as

            # 1D
            if len(shape) == 1:
                for i in range(shape[0]):
                    setattr(_as, "f%d" % i, object[i])
            # 2D
            elif len(shape) == 2:
                for i in range(shape[0]):
                    for j in range(shape[1]):
                        setattr(_as, "f%d_%d" % (i, j), object[i, j])

            self._busy = False

    def update_array(self, value):
        """Updates the array value associated with the editor."""
        self._busy = True
        self.value = value
        self._busy = False


# This alias is deprecated and will be removed in TraitsUI 8.
ToolkitEditorFactory = ArrayEditor
