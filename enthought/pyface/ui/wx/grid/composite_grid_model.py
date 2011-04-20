#------------------------------------------------------------------------------
# Copyright (c) 2005, Enthought, Inc.
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in enthought/LICENSE.txt and may be redistributed only
# under the conditions described in the aforementioned license.  The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
# Thanks for using Enthought open source!
#
# Author: Enthought, Inc.
# Description: <Enthought pyface package component>
#------------------------------------------------------------------------------

# Enthought library imports.
from enthought.traits.api import Dict, List, Trait

# local imports
from grid_model import GridModel, GridRow

class CompositeGridModel(GridModel):
    """ A CompositeGridModel is a model whose underlying data is
    a collection of other grid models. """

    # The models this model is comprised of.
    data = List(GridModel)

    # The rows in the model.
    rows = Trait(None, None, List(GridRow))

    # The cached data indexes.
    _data_index = Dict

    #########################################################################
    # 'object' interface.
    #########################################################################
    def __init__(self, **traits):
        """ Create a CompositeGridModel object. """

        # Base class constructor
        super(CompositeGridModel, self).__init__(**traits)

        self._row_count = None

        return

    #########################################################################
    # 'GridModel' interface.
    #########################################################################
    def get_column_count(self):
        """ Return the number of columns for this table. """

        # for the composite grid model, this is simply the sum of the
        # column counts for the underlying models
        count = 0
        for model in self.data:
            count += model.get_column_count()

        return count

    def get_column_name(self, index):
        """ Return the name of the column specified by the
        (zero-based) index. """

        model, new_index = self._resolve_column_index(index)

        return model.get_column_name(new_index)

    def get_column_size(self, index):
        """ Return the size in pixels of the column indexed by col.
            A value of -1 or None means use the default. """

        model, new_index = self._resolve_column_index(index)
        return model.get_column_size(new_index)

    def get_cols_drag_value(self, cols):
        """ Return the value to use when the specified columns are dragged or
        copied and pasted. cols is a list of column indexes. """

        values = []
        for col in cols:
            model, real_col = self._resolve_column_index(col)
            values.append(model.get_cols_drag_value([real_col]))

        return values

    def get_cols_selection_value(self, cols):
        """ Return the value to use when the specified cols are selected.
        This value should be enough to specify to other listeners what is
        going on in the grid. rows is a list of row indexes. """

        return self.get_cols_drag_value(self, cols)

    def get_column_context_menu(self, col):
        """ Return a MenuManager object that will generate the appropriate
        context menu for this column."""

        model, new_index = self._resolve_column_index(col)

        return model.get_column_context_menu(new_index)

    def sort_by_column(self, col, reverse=False):
        """ Sort model data by the column indexed by col. The reverse flag
        indicates that the sort should be done in reverse. """
        pass

    def is_column_read_only(self, index):
        """ Return True if the column specified by the zero-based index
        is read-only. """
        model, new_index = self._resolve_column_index(index)

        return model.is_column_read_only(new_index)

    def get_row_count(self):
        """ Return the number of rows for this table. """

        # see if we've already calculated the row_count
        if self._row_count is None:
            row_count = 0
            # return the maximum rows of any of the contained models
            for model in self.data:
                rows = model.get_row_count()
                if rows > row_count:
                    row_count = rows

            # save the result for next time
            self._row_count = row_count

        return self._row_count

    def get_row_name(self, index):
        """ Return the name of the row specified by the
        (zero-based) index. """

        label = None
        # if the rows list exists then grab the label from there...
        if self.rows is not None:
            if len(self.rows) > index:
                label = self.rows[index].label
        # ... otherwise generate it from the zero-based index.
        else:
            label = str(index + 1)

        return label

    def get_rows_drag_value(self, rows):
        """ Return the value to use when the specified rows are dragged or
        copied and pasted. rows is a list of row indexes. """
        row_values = []
        for rindex in rows:
            row = []
            for model in self.data:
                new_data = model.get_rows_drag_value([rindex])
                # if it's a list then we assume that it represents more than
                # one column's worth of values
                if isinstance(new_data, list):
                    row.extend(new_data)
                else:
                    row.append(new_data)

            # now save our new row value
            row_values.append(row)

        return row_values

    def is_row_read_only(self, index):
        """ Return True if the row specified by the zero-based index
        is read-only. """

        read_only = False
        if self.rows is not None and len(self.rows) > index:
            read_only = self.rows[index].read_only

        return read_only

    def get_type(self, row, col):
        """ Return the type of the value stored in the table at (row, col). """
        model, new_col = self._resolve_column_index(col)

        return model.get_type(row, new_col)


    def get_value(self, row, col):
        """ Return the value stored in the table at (row, col). """
        model, new_col = self._resolve_column_index(col)

        return model.get_value(row, new_col)

    def get_cell_selection_value(self, row, col):
        """ Return the value stored in the table at (row, col). """
        model, new_col = self._resolve_column_index(col)

        return model.get_cell_selection_value(row, new_col)

    def resolve_selection(self, selection_list):
        """ Returns a list of (row, col) grid-cell coordinates that
        correspond to the objects in selection_list. For each coordinate, if
        the row is -1 it indicates that the entire column is selected. Likewise
        coordinates with a column of -1 indicate an entire row that is
        selected. Note that the objects in selection_list are
        model-specific. """

        coords = []
        for selection in selection_list:
            # we have to look through each of the models in order
            # for the selected object
            for model in self.data:
                cells = model.resolve_selection([selection])
                # we know this model found the object if cells comes back
                # non-empty
                if cells is not None and len(cells) > 0:
                    coords.extend(cells)
                    break

        return coords


    # fixme: this context menu stuff is going in here for now, but it
    # seems like this is really more of a view piece than a model piece.
    # this is how the tree control does it, however, so we're duplicating
    # that here.
    def get_cell_context_menu(self, row, col):
        """ Return a MenuManager object that will generate the appropriate
        context menu for this cell."""

        model, new_col = self._resolve_column_index(col)

        return model.get_cell_context_menu(row, new_col)

    def is_cell_empty(self, row, col):
        """ Returns True if the cell at (row, col) has a None value,
        False otherwise."""
        model, new_col = self._resolve_column_index(col)

        if model is None:
            return True

        else:
            return model.is_cell_empty(row, new_col)

    def is_cell_editable(self, row, col):
        """ Returns True if the cell at (row, col) is editable,
        False otherwise. """
        model, new_col = self._resolve_column_index(col)

        return model.is_cell_editable(row, new_col)

    def is_cell_read_only(self, row, col):
        """ Returns True if the cell at (row, col) is not editable,
        False otherwise. """

        model, new_col = self._resolve_column_index(col)

        return model.is_cell_read_only(row, new_col)

    def get_cell_bg_color(self, row, col):
        """ Return a wxColour object specifying what the background color
            of the specified cell should be. """
        model, new_col = self._resolve_column_index(col)

        return model.get_cell_bg_color(row, new_col)

    def get_cell_text_color(self, row, col):
        """ Return a wxColour object specifying what the text color
            of the specified cell should be. """
        model, new_col = self._resolve_column_index(col)

        return model.get_cell_text_color(row, new_col)

    def get_cell_font(self, row, col):
        """ Return a wxFont object specifying what the font
            of the specified cell should be. """
        model, new_col = self._resolve_column_index(col)

        return model.get_cell_font(row, new_col)

    def get_cell_halignment(self, row, col):
        """ Return a string specifying what the horizontal alignment
            of the specified cell should be.

            Return 'left' for left alignment, 'right' for right alignment,
            or 'center' for center alignment. """
        model, new_col = self._resolve_column_index(col)

        return model.get_cell_halignment(row, new_col)

    def get_cell_valignment(self, row, col):
        """ Return a string specifying what the vertical alignment
            of the specified cell should be.

            Return 'top' for top alignment, 'bottom' for bottom alignment,
            or 'center' for center alignment. """
        model, new_col = self._resolve_column_index(col)

        return model.get_cell_valignment(row, new_col)

    #########################################################################
    # protected 'GridModel' interface.
    #########################################################################
    def _delete_rows(self, pos, num_rows):
        """ Implementation method for delete_rows. Should return the
        number of rows that were deleted. """

        for model in self.data:
            model._delete_rows(pos, num_rows)

        return num_rows

    def _insert_rows(self, pos, num_rows):
        """ Implementation method for insert_rows. Should return the
        number of rows that were inserted. """

        for model in self.data:
            model._insert_rows(pos, num_rows)

        return num_rows

    def _set_value(self, row, col, value):
        """ Implementation method for set_value. Should return the
        number of rows, if any, that were appended. """

        model, new_col = self._resolve_column_index(col)
        model._set_value(row, new_col, value)
        return 0

    #########################################################################
    # private interface
    #########################################################################

    def _resolve_column_index(self, index):
        """ Resolves a column index into the correct model and adjusted
        index. Returns the target model and the corrected index. """

        real_index = index
        cached = None #self._data_index.get(index)
        if cached is not None:
            model, col_index = cached
        else:
            model = None
            for m in self.data:
                cols = m.get_column_count()
                if real_index < cols:
                    model = m
                    break
                else:
                    real_index -= cols
            self._data_index[index] = (model, real_index)

        return model, real_index

    def _data_changed(self):
        """ Called when the data trait is changed.

        Since this is called when our underlying models change, the cached
        results of the column lookups is wrong and needs to be invalidated.
        """

        self._data_index.clear()

        return

    def _data_items_changed(self):
        """ Called when the members of the data trait have changed.

        Since this is called when our underlying model change, the cached
        results of the column lookups is wrong and needs to be invalidated.
        """
        self._data_index.clear()

        return

#### EOF ####################################################################
