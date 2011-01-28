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
""" A SimpleGridModel simply builds a table from a 2-dimensional
list/array containing the data. Optionally users can pass in specifications
for rows and columns. By default these are built off the data itself,
with row/column labels as the index + 1."""

# Enthought library imports
from enthought.pyface.action.api import Action, Group, MenuManager, Separator
from enthought.traits.api import HasTraits, Any, List, Str, Bool, Trait
from enthought.util.wx.drag_and_drop import clipboard as enClipboard

# local imports
from grid_model import GridColumn, GridModel, GridRow

class SimpleGridModel(GridModel):
    """ A SimpleGridModel simply builds a table from a 2-dimensional
    list/array containing the data. Optionally users can pass in specifications
    for rows and columns. By default these are built off the data itself,
    with row/column labels as the index + 1."""

    # A 2-dimensional list/array containing the grid data.
    data = Any

    # The rows in the model.
    rows = Trait(None, None, List(GridRow))

    # The columns in the model.
    columns = Trait(None, None, List(GridColumn))

    #########################################################################
    # 'object' interface.
    #########################################################################
    def __init__(self, **traits):
        """ Create a SimpleGridModel object. """

        # Base class constructor
        super(SimpleGridModel, self).__init__(**traits)

        return

    #########################################################################
    # 'GridModel' interface.
    #########################################################################

    def get_column_count(self):
        """ Return the number of columns for this table. """

        if self.columns is not None:
            # if we have an explicit declaration then use it
            count = len(self.columns)
        else:
            # otherwise look at the length of the first row
            # note: the data had better be 2D
            count = len(self.data[0])

        return count

    def get_column_name(self, index):
        """ Return the name of the column specified by the
        (zero-based) index. """

        if self.columns is not None:
            # if we have an explicit declaration then use it
            try:
                name = self.columns[index].label
            except IndexError:
                name = ''
        else:
            # otherwise return the index plus 1
            name = str(index + 1)

        return name

    def get_cols_drag_value(self, cols):
        """ Return the value to use when the specified columns are dragged or
        copied and pasted. cols is a list of column indexes. """

        # if there is only one column in cols, then we return a 1-dimensional
        # list
        if len(cols) == 1:
            value = self.__get_data_column(cols[0])
        else:
            # iterate over every column, building a list of the values in that
            # column
            value = []
            for col in cols:
                value.append(self.__get_data_column(col))

        return value

    def is_column_read_only(self, index):
        """ Return True if the column specified by the zero-based index
        is read-only. """

        # if there is no declaration then assume the column is not
        # read only
        read_only = False
        if self.columns is not None:
            # if we have an explicit declaration then use it
            try:
                read_only = self.columns[index].read_only
            except IndexError:
                pass
        return read_only

    def get_row_count(self):
        """ Return the number of rows for this table. """

        if self.rows is not None:
            # if we have an explicit declaration then use it
            count = len(self.rows)
        else:
            # otherwise look at the data
            count = len(self.data)

        return count

    def get_row_name(self, index):
        """ Return the name of the row specified by the
        (zero-based) index. """

        if self.rows is not None:
            # if we have an explicit declaration then use it
            try:
                name = self.rows[index].label
            except IndexError:
                name = str(index + 1)
        else:
            # otherwise return the index plus 1
            name = str(index + 1)

        return name

    def get_rows_drag_value(self, rows):
        """ Return the value to use when the specified rows are dragged or
        copied and pasted. rows is a list of row indexes. """

        # if there is only one row in rows, then we return a 1-dimensional
        # list
        if len(rows) == 1:
            value = self.__get_data_row(rows[0])
        else:
            # iterate over every row, building a list of the values in that
            # row
            value = []
            for row in rows:
                value.append(self.__get_data_row(row))

        return value

    def is_row_read_only(self, index):
        """ Return True if the row specified by the zero-based index
        is read-only. """

        # if there is no declaration then assume the row is not
        # read only
        read_only = False
        if self.rows is not None:
            # if we have an explicit declaration then use it
            try:
                read_only = self.rows[index].read_only
            except IndexError:
                pass

        return read_only

    def get_value(self, row, col):
        """ Return the value stored in the table at (row, col). """

        try:
            return self.data[row][col]

        except IndexError:
            pass

        return ''

    def is_cell_empty(self, row, col):
        """ Returns True if the cell at (row, col) has a None value,
        False otherwise."""

        if row >= self.get_row_count() or col >= self.get_column_count():
            empty = True

        else:
            try:
                value = self.get_value(row, col)
                empty = value is None
            except IndexError:
                empty = True

        return empty

    def get_cell_context_menu(self, row, col):
        """ Return a MenuManager object that will generate the appropriate
        context menu for this cell."""

        context_menu = MenuManager(
            Group(
                _CopyAction(self, row, col, name='Copy'),
                id = 'Group'
                )
            )

        return context_menu

    def is_cell_editable(self, row, col):
        """ Returns True if the cell at (row, col) is editable,
        False otherwise. """
        return True

    #########################################################################
    # protected 'GridModel' interface.
    #########################################################################
    def _set_value(self, row, col, value):
        """ Sets the value of the cell at (row, col) to value.

        Raises a ValueError if the value is vetoed or the cell at
        (row, col) does not exist. """
        new_rows = 0
        try:
            self.data[row][col] = value
        except IndexError:
            # Add a new row.
            self.data.append([0] * self.GetNumberCols())
            self.data[row][col] = value
            new_rows = 1

        return new_rows

    def _delete_rows(self, pos, num_rows):
        """ Removes rows pos through pos + num_rows from the model. """

        if pos + num_rows >= self.get_row_count():
            num_rows = self.get_rows_count() - pos

        del self.data[pos, pos + num_rows]

        return num_rows

    ###########################################################################
    # private interface.
    ###########################################################################

    def __get_data_column(self, col):
        """ Return a 1-d list of data from the column indexed by col. """

        row_count = self.get_row_count()

        coldata = []
        for row in range(row_count):
            try:
                coldata.append(self.get_value(row, col))
            except IndexError:
                coldata.append(None)

        return coldata

    def __get_data_row(self, row):
        """ Return a 1-d list of data from the row indexed by row. """

        col_count = self.get_column_count()

        rowdata = []
        for col in range(col_count):
            try:
                rowdata.append(self.get_value(row, col))
            except IndexError:
                rowdata.append(None)

        return rowdata

# Private class
class _CopyAction(Action):

    def __init__(self, model, row, col, **kw):

        super(_CopyAction, self).__init__(**kw)
        self._model = model
        self._row = row
        self._col = col

    def perform(self):

        # grab the specified value from the model and add it to the
        # clipboard
        value = self._model.get_cell_drag_value(self._row, self._col)
        enClipboard.data = value


#### EOF ####################################################################

