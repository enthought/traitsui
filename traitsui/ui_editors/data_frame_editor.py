# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import logging
import warnings

from traits.api import (
    Bool,
    Dict,
    Enum,
    Instance,
    List,
    Property,
    Str,
    Tuple,
    Union,
)

from traitsui.basic_editor_factory import BasicEditorFactory
from traitsui.editors.tabular_editor import TabularEditor
from traitsui.item import Item
from traitsui.tabular_adapter import TabularAdapter
from traitsui.toolkit import toolkit_object
from traitsui.toolkit_traits import Font
from traitsui.ui_editor import UIEditor
from traitsui.view import View


logger = logging.getLogger(__name__)


class DataFrameAdapter(TabularAdapter):
    """Generic tabular adapter for data frames"""

    #: The text to use for a generic entry.
    text = Property()

    #: The alignment for each cell
    alignment = Property(Enum("left", "center", "right"))

    #: The text to use for a row index.
    index_text = Property()

    #: The alignment to use for a row index.
    index_alignment = Property()

    #: The font to use for each column
    font = Property()

    #: The format to use for each column
    format = Property()

    #: The format for each element, or a mapping column ID to format.
    _formats = Union(Str, Dict, default_value="%s")

    #: The font for each element, or a mapping column ID to font.
    _fonts = Union(Font, Dict, default_value="Courier 10")

    def _get_index_alignment(self):
        import numpy as np

        index = getattr(self.object, self.name).index
        if np.issubdtype(index.dtype, np.number):
            return "right"
        else:
            return "left"

    def _get_alignment(self):
        import numpy as np

        column = self.item[self.column_id]
        if np.issubdtype(column.dtype, np.number):
            return "right"
        else:
            return "left"

    def _get_font(self):
        if isinstance(self._fonts, toolkit_object("font_trait:TraitsFont")):
            return self._fonts
        else:
            return self._fonts.get(self.column_id, "Courier 10")

    def _get_format(self):
        if isinstance(self._formats, str):
            return self._formats
        else:
            return self._formats.get(self.column_id, "%s")

    def _get_content(self):
        return self.item[self.column_id].iloc[0]

    def _get_text(self):
        format = self.get_format(self.object, self.name, self.row, self.column)
        return format % self.get_content(
            self.object, self.name, self.row, self.column
        )

    def _set_text(self, value):
        df = getattr(self.object, self.name)
        dtype = df.iloc[:, self.column].dtype
        try:
            value = dtype.type(value)
            df.iloc[self.row, self.column] = value
        except Exception:
            logger.debug(
                "User entered invalid value %r for column %r row %r",
                value,
                self.column,
                self.row,
                exc_info=True,
            )

    def _get_index_text(self):
        return str(self.item.index[0])

    def _set_index_text(self, value):
        index = getattr(self.object, self.name).index
        dtype = index.dtype
        try:
            value = dtype.type(value)
            index.values[self.row] = value
        except Exception:
            logger.debug(
                "User entered invalid value %r for index", value, exc_info=True
            )

    # ---- Adapter methods that are not sensitive to item type ----------------

    def get_item(self, object, trait, row):
        """Override the base implementation to work with DataFrames

        This returns a dataframe with one row, rather than a series, since
        using a dataframe preserves dtypes.

        """
        return getattr(object, trait).iloc[row : row + 1]

    def delete(self, object, trait, row):
        """Override the base implementation to work with DataFrames

        Unavoidably does a copy of the data, setting the trait with the new
        value.
        """
        import pandas as pd

        df = getattr(object, trait)
        if 0 < row < len(df) - 1:
            new_df = pd.concat([df.iloc[:row, :], df.iloc[row + 1 :, :]])
        elif row == 0:
            new_df = df.iloc[row + 1 :, :]
        else:
            new_df = df.iloc[:row, :]
        setattr(object, trait, new_df)

    def insert(self, object, trait, row, value):
        """Override the base implementation to work with DataFrames

        Unavoidably does a copy of the data, setting the trait with the new
        value.
        """
        import pandas as pd

        df = getattr(object, trait)
        if 0 < row < len(df) - 1:
            new_df = pd.concat([df.iloc[:row, :], value, df.iloc[row:, :]])
        elif row == 0:
            new_df = pd.concat([value, df])
        else:
            new_df = pd.concat([df, value])
        setattr(object, trait, new_df)


class _DataFrameEditor(UIEditor):
    """TraitsUI-based editor implementation for data frames"""

    #: Indicate that the editor is scrollable/resizable:
    scrollable = True

    #: Should column titles be displayed:
    show_titles = Bool(True)

    #: The tabular adapter being used for the editor view:
    adapter = Instance(DataFrameAdapter)

    # -- Private Methods ------------------------------------------------------

    def _target_name(self, name):
        if name:
            return "object.object." + name
        else:
            return ""

    def _data_frame_view(self):
        """Return the view used by the editor."""

        return View(
            Item(
                self._target_name(self.name),
                id="tabular_editor",
                show_label=False,
                editor=TabularEditor(
                    show_titles=self.factory.show_titles,
                    editable=self.factory.editable,
                    adapter=self.adapter,
                    selected=self._target_name(self.factory.selected),
                    selected_row=self._target_name(self.factory.selected_row),
                    selectable=self.factory.selectable,
                    multi_select=self.factory.multi_select,
                    activated=self._target_name(self.factory.activated),
                    activated_row=self._target_name(
                        self.factory.activated_row
                    ),  # noqa
                    clicked=self._target_name(self.factory.clicked),
                    dclicked=self._target_name(self.factory.dclicked),
                    scroll_to_row=self._target_name(
                        self.factory.scroll_to_row
                    ),  # noqa
                    scroll_to_position_hint=(
                        self.factory.scroll_to_position_hint
                    ),
                    scroll_to_column=self._target_name(
                        self.factory.scroll_to_column
                    ),  # noqa
                    right_clicked=self._target_name(
                        self.factory.right_clicked
                    ),  # noqa
                    right_dclicked=self._target_name(
                        self.factory.right_dclicked
                    ),  # noqa
                    column_clicked=self._target_name(
                        self.factory.column_clicked
                    ),  # noqa
                    column_right_clicked=self._target_name(
                        self.factory.column_right_clicked
                    ),  # noqa
                    operations=self.factory.operations,
                    update=self._target_name(self.factory.update),
                    refresh=self._target_name(self.factory.refresh),
                ),
            ),
            id="data_frame_editor",
            resizable=True,
        )

    def init_ui(self, parent):
        """Creates the Traits UI for displaying the array."""
        factory = self.factory
        if factory.columns != []:
            columns = []
            for column in factory.columns:
                if isinstance(column, str):
                    title = column
                    column_id = column
                else:
                    title, column_id = column
                if column_id not in self.value.columns:
                    continue
                columns.append((title, column_id))
        else:
            columns = [
                (column_id, column_id) for column_id in self.value.columns
            ]

        if factory.show_index:
            index_name = self.value.index.name
            if index_name is None:
                index_name = ""
            columns.insert(0, (index_name, "index"))

        if factory.adapter is not None:
            self.adapter = factory.adapter
            self.adapter._formats = factory.formats
            self.adapter._fonts = factory.fonts
            if not self.adapter.columns:
                self.adapter.columns = columns
        else:
            self.adapter = DataFrameAdapter(
                columns=columns, _formats=factory.formats, _fonts=factory.fonts
            )

        return self.edit_traits(
            view="_data_frame_view", parent=parent, kind="subpanel"
        )


class DataFrameEditor(BasicEditorFactory):
    """Editor factory for basic data frame editor"""

    #: The editor implementation class.
    klass = Property()

    #: Should an index column be displayed.
    show_index = Bool(True)

    #: Should column headers be displayed.
    show_titles = Bool(True)

    #: Optional list of either column ID or pairs of (column title, column ID).
    columns = List(Union(Str, Tuple(Str, Str)))

    #: The format for each element, or a mapping column ID to format.
    formats = Union(Str, Dict, default_value="%s")

    #: The font for each element, or a mapping column ID to font.
    fonts = Union(Font, Dict, default_value="Courier 10")

    #: The optional extended name of the trait to synchronize the selection
    #: values with:
    selected = Str()

    #: The optional extended name of the trait to synchronize the selection rows
    #: with:
    selected_row = Str()

    #: Whether or not to allow selection.
    selectable = Bool(True)

    #: Whether or not to allow for multiple selections
    multi_select = Bool(False)

    #: The optional extended name of the trait to synchronize the activated
    #: value with:
    activated = Str()

    #: The optional extended name of the trait to synchronize the activated
    #: value's row with:
    activated_row = Str()

    #: The optional extended name of the trait to synchronize left click data
    #: with. The data is a TabularEditorEvent:
    clicked = Str()

    #: The optional extended name of the trait to synchronize left double click
    #: data with. The data is a TabularEditorEvent:
    dclicked = Str()

    #: The optional extended name of the Event trait that should be used to
    #: trigger a scroll-to command. The data is an integer giving the row.
    scroll_to_row = Str()

    #: Deprecated: Controls behavior of scroll to row and scroll to column
    scroll_to_row_hint = Property(Str, observe="scroll_to_position_hint")

    #: (replacement of scroll_to_row_hint, but more clearly named)
    #: Controls behavior of scroll to row and scroll to column
    scroll_to_position_hint = Enum("visible", "center", "top", "bottom")

    #: The optional extended name of the Event trait that should be used to
    #: trigger a scroll-to command. The data is an integer giving the column.
    scroll_to_column = Str()

    #: The optional extended name of the trait to synchronize right click data
    #: with. The data is a TabularEditorEvent:
    right_clicked = Str()

    #: The optional extended name of the trait to synchronize right double
    #: clicked data with. The data is a TabularEditorEvent:
    right_dclicked = Str()

    #: The optional extended name of the trait to synchronize column
    #: clicked data with. The data is a TabularEditorEvent:
    column_clicked = Str()

    #: The optional extended name of the trait to synchronize column
    #: right clicked data with. The data is a TabularEditorEvent:
    column_right_clicked = Str()

    #: Whether or not the entries can be edited.
    editable = Bool(False)

    #: What type of operations are allowed on the list:
    operations = List(
        Enum("delete", "insert", "append", "edit", "move"),
        ["delete", "insert", "append", "edit", "move"],
    )

    #: The optional extended name of the trait used to indicate that a complete
    #: table update is needed:
    update = Str()

    #: The optional extended name of the trait used to indicate that the table
    #: just needs to be repainted.
    refresh = Str()

    #: Set to override the default dataframe adapter
    adapter = Instance(DataFrameAdapter)

    def _get_klass(self):
        """The class used to construct editor objects."""
        return toolkit_object("data_frame_editor:_DataFrameEditor")

    def _get_scroll_to_row_hint(self):
        warnings.warn(
            "Use of scroll_to_row_hint trait is deprecated. "
            "Use scroll_to_position_hint instead.",
            DeprecationWarning,
        )
        return self.scroll_to_position_hint

    def _set_scroll_to_row_hint(self, hint):
        warnings.warn(
            "Use of scroll_to_row_hint trait is deprecated. "
            "Use scroll_to_position_hint instead.",
            DeprecationWarning,
        )
        self.scroll_to_position_hint = hint
