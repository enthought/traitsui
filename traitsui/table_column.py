# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Defines the table column descriptor used by the editor and editor factory
    classes for numeric and table editors.
"""

import os

from traits.api import (
    Any,
    Bool,
    Callable,
    Constant,
    Dict,
    Enum,
    Expression,
    Float,
    HasPrivateTraits,
    Instance,
    Int,
    Property,
    Str,
    Union,
)

from traits.trait_base import user_name_for, xgetattr

from .editor_factory import EditorFactory
from .menu import Menu
from .ui_traits import Image, AView, EditorStyle
from .toolkit_traits import Color, Font
from .view import View

# Set up a logger:
import logging


logger = logging.getLogger(__name__)


# Flag used to indicate user has not specified a column label
UndefinedLabel = "???"


class TableColumn(HasPrivateTraits):
    """Represents a column in a table editor."""

    # -------------------------------------------------------------------------
    #  Trait definitions:
    # -------------------------------------------------------------------------

    #: Column label to use for this column:
    label = Str(UndefinedLabel)

    #: Type of data contained by the column:
    # XXX currently no other types supported, but potentially there could be...
    type = Enum("text", "bool")

    #: Text color for this column:
    text_color = Color("black")

    #: Text font for this column:
    text_font = Union(None, Font)

    #: Cell background color for this column:
    cell_color = Color("white", allow_none=True)

    #: Cell background color for non-editable columns:
    read_only_cell_color = Color(0xF4F3EE, allow_none=True)

    #: Cell graph color:
    graph_color = Color(0xDDD9CC)

    #: Horizontal alignment of text in the column:
    horizontal_alignment = Enum("left", ["left", "center", "right"])

    #: Vertical alignment of text in the column:
    vertical_alignment = Enum("center", ["top", "center", "bottom"])

    #: Horizontal cell margin
    horizontal_margin = Int(4)

    #: Vertical cell margin
    vertical_margin = Int(3)

    #: The image to display in the cell:
    image = Image

    #: Renderer used to render the contents of this column:
    renderer = Any  # A toolkit specific renderer

    #: Is the table column visible (i.e., viewable)?
    visible = Bool(True)

    #: Is this column editable?
    editable = Bool(True)

    #: Is the column automatically edited/viewed (i.e. should the column editor
    #: or popup be activated automatically on mouse over)?
    auto_editable = Bool(False)

    #: Should a checkbox be displayed instead of True/False?
    show_checkbox = Bool(True)

    #: Can external objects be dropped on the column?
    droppable = Bool(False)

    #: Context menu to display when this column is right-clicked:
    menu = Instance(Menu)

    #: The tooltip to display when the mouse is over the column:
    tooltip = Str()

    #: The width of the column (< 0.0: Default, 0.0..1.0: fraction of total
    #: table width, > 1.0: absolute width in pixels):
    width = Float(-1.0)

    #: The width of the column while it is being edited (< 0.0: Default,
    #: 0.0..1.0: fraction of total table width, > 1.0: absolute width in
    #: pixels):
    edit_width = Float(-1.0)

    #: The height of the column cell's row while it is being edited
    #: (< 0.0: Default, 0.0..1.0: fraction of total table height,
    #: > 1.0: absolute height in pixels):
    edit_height = Float(-1.0)

    #: The resize mode for this column.  This takes precedence over other
    #: settings (like **width**, above).
    #: - "interactive": column can be resized by users or programmatically
    #: - "fixed": users cannot resize the column, but it can be set programmatically
    #: - "stretch": the column will be resized to fill the available space
    #: - "resize_to_contents": column will be sized to fit the contents, but then cannot be resized
    resize_mode = Enum("interactive", "fixed", "stretch", "resize_to_contents")

    #: The view (if any) to display when clicking a non-editable cell:
    view = AView

    #: Optional maximum value a numeric cell value can have:
    maximum = Float(trait_value=True)

    # -------------------------------------------------------------------------
    #:  Returns the actual object being edited:
    # -------------------------------------------------------------------------

    def get_object(self, object):
        """Returns the actual object being edited."""
        return object

    def get_label(self):
        """Gets the label of the column."""
        return self.label

    def get_width(self):
        """Returns the width of the column."""
        return self.width

    def get_edit_width(self, object):
        """Returns the edit width of the column."""
        return self.edit_width

    def get_edit_height(self, object):
        """Returns the height of the column cell's row while it is being
        edited.
        """
        return self.edit_height

    def get_type(self, object):
        """Gets the type of data for the column for a specified object."""
        return self.type

    def get_text_color(self, object):
        """Returns the text color for the column for a specified object."""
        return self.text_color_

    def get_text_font(self, object):
        """Returns the text font for the column for a specified object."""
        return self.text_font

    def get_cell_color(self, object):
        """Returns the cell background color for the column for a specified
        object.
        """
        if self.is_editable(object):
            return self.cell_color_
        return self.read_only_cell_color_

    def get_graph_color(self, object):
        """Returns the cell background graph color for the column for a
        specified object.
        """
        return self.graph_color_

    def get_horizontal_alignment(self, object):
        """Returns the horizontal alignment for the column for a specified
        object.
        """
        return self.horizontal_alignment

    def get_vertical_alignment(self, object):
        """Returns the vertical alignment for the column for a specified
        object.
        """
        return self.vertical_alignment

    def get_image(self, object):
        """Returns the image to display for the column for a specified object."""
        return self.image

    def get_renderer(self, object):
        """Returns the renderer for the column of a specified object."""
        return self.renderer

    def is_editable(self, object):
        """Returns whether the column is editable for a specified object."""
        return self.editable

    def is_auto_editable(self, object):
        """Returns whether the column is automatically edited/viewed for a
        specified object.
        """
        return self.auto_editable

    def is_droppable(self, object, value):
        """Returns whether a specified value is valid for dropping on the
        column for a specified object.
        """
        return self.droppable

    def get_menu(self, object):
        """Returns the context menu to display when the user right-clicks on
        the column for a specified object.
        """
        return self.menu

    def get_tooltip(self, object):
        """Returns the tooltip to display when the user mouses over the column
        for a specified object.
        """
        return self.tooltip

    def get_view(self, object):
        """Returns the view to display when clicking a non-editable cell."""
        return self.view

    def get_maximum(self, object):
        """Returns the maximum value a numeric column can have."""
        return self.maximum

    def on_click(self, object):
        """Called when the user clicks on the column."""
        pass

    def on_dclick(self, object):
        """Called when the user clicks on the column."""
        pass

    def cmp(self, object1, object2):
        """Returns the result of comparing the column of two different objects.

        This is deprecated.
        """
        return (self.key(object1) > self.key(object2)) - (
            self.key(object1) < self.key(object2)
        )

    def __str__(self):
        """Returns the string representation of the table column."""
        return self.get_label()


class ObjectColumn(TableColumn):
    """A column for editing objects."""

    # -------------------------------------------------------------------------
    #  Trait definitions:
    # -------------------------------------------------------------------------

    #: Name of the object trait associated with this column:
    name = Str()

    #: Column label to use for this column:
    label = Property()

    #: Trait editor used to edit the contents of this column:
    editor = Instance(EditorFactory)

    #: The editor style to use to edit the contents of this column:
    style = EditorStyle

    #: Format string to apply to column values:
    format = Str("%s")

    #: Format function to apply to column values:
    format_func = Callable()

    # -------------------------------------------------------------------------
    #  Trait view definitions:
    # -------------------------------------------------------------------------

    traits_view = View(
        [
            ["name", "label", "type", "|[Column Information]"],
            [
                "horizontal_alignment{Horizontal}@",
                "vertical_alignment{Vertical}@",
                "|[Alignment]",
            ],
            ["editable", "9", "droppable", "9", "visible", "-[Options]>"],
            "|{Column}",
        ],
        [
            [
                "text_color@",
                "cell_color@",
                "read_only_cell_color@",
                "|[UI Colors]",
            ],
            "|{Colors}",
        ],
        [["text_font@", "|[Font]<>"], "|{Font}"],
        ["menu@", "|{Menu}"],
        ["editor@", "|{Editor}"],
    )

    def _get_label(self):
        """Gets the label of the column."""
        if self._label is not None:
            return self._label
        return user_name_for(self.name)

    def _set_label(self, label):
        old, self._label = self._label, label
        if old != label:
            self.trait_property_changed("label", old, label)

    def get_raw_value(self, object):
        """Gets the unformatted value of the column for a specified object."""
        try:
            return xgetattr(self.get_object(object), self.name)
        except Exception as e:
            from traitsui.api import raise_to_debug

            raise_to_debug()
            return None

    def get_value(self, object):
        """Gets the formatted value of the column for a specified object."""
        try:
            if self.format_func is not None:
                return self.format_func(self.get_raw_value(object))

            return self.format % (self.get_raw_value(object),)
        except:
            logger.exception(
                "Error occurred trying to format a %s value"
                % self.__class__.__name__
            )
            return "Format!"

    def get_drag_value(self, object):
        """Returns the drag value for the column."""
        return self.get_raw_value(object)

    def set_value(self, object, value):
        """Sets the value of the column for a specified object."""
        target, name = self.target_name(object)
        setattr(target, name, value)

    def get_editor(self, object):
        """Gets the editor for the column of a specified object."""
        if self.editor is not None:
            return self.editor

        target, name = self.target_name(object)

        return target.base_trait(name).get_editor()

    def get_style(self, object):
        """Gets the editor style for the column of a specified object."""
        return self.style

    def key(self, object):
        """Returns the value to use for sorting."""
        return self.get_raw_value(object)

    def is_droppable(self, object, value):
        """Returns whether a specified value is valid for dropping on the
        column for a specified object.
        """
        if self.droppable:
            try:
                target, name = self.target_name(object)
                target.base_trait(name).validate(target, name, value)
                return True
            except:
                pass

        return False

    def target_name(self, object):
        """Returns the target object and name for the column."""
        object = self.get_object(object)
        name = self.name
        col = name.rfind(".")
        if col < 0:
            return (object, name)

        return (xgetattr(object, name[:col]), name[col + 1 :])


class ExpressionColumn(ObjectColumn):
    """A column for displaying computed values."""

    # -------------------------------------------------------------------------
    #  Trait definitions:
    # -------------------------------------------------------------------------

    #: The Python expression used to return the value of the column:
    expression = Expression

    #: Is this column editable?
    editable = Constant(False)

    #: The globals dictionary that should be passed to the expression
    #: evaluation:
    globals = Dict()

    def get_raw_value(self, object):
        """Gets the unformatted value of the column for a specified object."""
        try:
            return eval(self.expression_, self.globals, {"object": object})
        except Exception:
            logger.exception(
                "Error evaluating table column expression: %s"
                % self.expression
            )
            return None


class NumericColumn(ObjectColumn):
    """A column for editing Numeric arrays."""

    # -------------------------------------------------------------------------
    #  Trait definitions:
    # -------------------------------------------------------------------------

    #: Column label to use for this column
    label = Property()

    #: Text color this column when selected
    selected_text_color = Color("black")

    #: Text font for this column when selected
    selected_text_font = Font

    #: Cell background color for this column when selected
    selected_cell_color = Color(0xD8FFD8)

    #: Formatting string for the cell value
    format = Str("%s")

    #: Horizontal alignment of text in the column; this value overrides the
    #: default.
    horizontal_alignment = "center"

    def _get_label(self):
        """Gets the label of the column."""
        if self._label is not None:
            return self._label
        return self.name

    def _set_label(self, label):
        old, self._label = self._label, label
        if old != label:
            self.trait_property_changed("label", old, label)

    def get_type(self, object):
        """Gets the type of data for the column for a specified object row."""
        return self.type

    def get_text_color(self, object):
        """Returns the text color for the column for a specified object row."""
        if self._is_selected(object):
            return self.selected_text_color_
        return self.text_color_

    def get_text_font(self, object):
        """Returns the text font for the column for a specified object row."""
        if self._is_selected(object):
            return self.selected_text_font
        return self.text_font

    def get_cell_color(self, object):
        """Returns the cell background color for the column for a specified
        object row.
        """
        if self.is_editable(object):
            if self._is_selected(object):
                return self.selected_cell_color_
            return self.cell_color_
        return self.read_only_cell_color_

    def get_horizontal_alignment(self, object):
        """Returns the horizontal alignment for the column for a specified
        object row.
        """
        return self.horizontal_alignment

    def get_vertical_alignment(self, object):
        """Returns the vertical alignment for the column for a specified
        object row.
        """
        return self.vertical_alignment

    def is_editable(self, object):
        """Returns whether the column is editable for a specified object row."""
        return self.editable

    def is_droppable(self, object, row, value):
        """Returns whether a specified value is valid for dropping on the
        column for a specified object row.
        """
        return self.droppable

    def get_menu(self, object, row):
        """Returns the context menu to display when the user right-clicks on
        the column for a specified object row.
        """
        return self.menu

    def get_value(self, object):
        """Gets the value of the column for a specified object row."""
        try:
            value = getattr(object, self.name)
            try:
                return self.format % (value,)
            except:
                return "Format!"
        except:
            return "Undefined!"

    def set_value(self, object, row, value):
        """Sets the value of the column for a specified object row."""
        column = self.get_data_column(object)
        column[row] = type(column[row])(value)

    def get_editor(self, object):
        """Gets the editor for the column of a specified object row."""
        return super().get_editor(object)

    def get_data_column(self, object):
        """Gets the entire contents of the specified object column."""
        return getattr(object, self.name)

    def _is_selected(self, object):
        """Returns whether a specified object row is selected."""
        if (
            hasattr(object, "model_selection")
            and object.model_selection is not None
        ):
            return True
        return False


class ListColumn(TableColumn):
    """A column for editing lists."""

    # -------------------------------------------------------------------------
    #  Trait definitions:
    # -------------------------------------------------------------------------

    # Label to use for this column
    label = Property()

    #: Index of the list element associated with this column
    index = Int()

    # Is this column editable? This value overrides the base class default.
    editable = False

    # -------------------------------------------------------------------------
    #  Trait view definitions:
    # -------------------------------------------------------------------------

    traits_view = View(
        [
            ["index", "label", "type", "|[Column Information]"],
            ["text_color@", "cell_color@", "|[UI Colors]"],
        ]
    )

    def _get_label(self):
        """Gets the label of the column."""
        if self._label is not None:
            return self._label
        return "Column %d" % (self.index + 1)

    def _set_label(self, label):
        old, self._label = self._label, label
        if old != label:
            self.trait_property_changed("label", old, label)

    def get_value(self, object):
        """Gets the value of the column for a specified object."""
        return str(object[self.index])

    def set_value(self, object, value):
        """Sets the value of the column for a specified object."""
        object[self.index] = value

    def get_editor(self, object):
        """Gets the editor for the column of a specified object."""
        return None

    def key(self, object):
        """Returns the value to use for sorting."""
        return object[self.index]
