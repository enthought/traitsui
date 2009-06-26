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
""" Model for grid views. """

# Major package imports

# Enthought library imports.
from enthought.traits.api import Any, Bool, Event, HasPrivateTraits, HasTraits, \
     Instance, Int, Str, Tuple

# The classes below are part of the table specification.
class GridRow(HasTraits):
    """ Structure for holding row/column specifications. """

    # Is the data in this column read-only?
    read_only = Bool(False)

    # The label for this column
    label = Str

# We specify the same info for rows and for columns, but add a GridColumn
# name for clarity.
GridColumn = GridRow

class GridSortData(HasTraits):
    """ An event that signals a sorting has taken place.

        The index attribute should be set to the row or column
        on which the data was sorted. An index of -1 indicates that
        no sort has been applied (or a previous sort has been unapplied).
        The reversed flag indicates that the sort has been done in reverse
        order. """
    index = Int(-1)
    reversed = Bool(False)

# for backwards compatibility
GridSortEvent = GridSortData

class GridModel(HasPrivateTraits):
    """ Model for grid views. """

    #### 'GridModel' interface ################################################

    # Fire when the structure of the underlying grid model has changed.
    structure_changed = Event

    # Fire when the content of the underlying grid model has changed.
    content_changed = Event

    # Column model is currently sorted on.
    column_sorted = Instance(GridSortData)

    # The cell (row, col) the mouse is currently in.
    mouse_cell = Tuple(Int, Int)
    
    #### Events ####

    # A row was inserted or appended to this model
    rows_added = Event

    # A column was inserted or appended to this model
    columns_added = Event

    # A row sort took place
    row_sorted = Event
    
    # Event fired when a cell is clicked on:
    click = Event # = (row, column) that was clicked on
    
    # Event fired when a cell is double-clicked on:
    dclick = Event # = (row, column) that was double-clicked on

    #########################################################################
    # 'object' interface.
    #########################################################################
    def __init__(self, **traits):
        """ Creates a new grid model. """

        # Base class constructors.
        super(GridModel, self).__init__(**traits)
        
        return
    
    #########################################################################
    # 'GridModel' interface -- Subclasses MUST override the following
    #########################################################################

    def get_column_count(self):
        """ Return the number of columns for this table. """
        raise NotImplementedError

    def get_column_name(self, index):
        """ Return the name of the column specified by the
        (zero-based) index. """
        raise NotImplementedError

    def get_row_count(self):
        """ Return the number of rows for this table. """
        raise NotImplementedError

    def get_row_name(self, index):
        """ Return the name of the row specified by the
        (zero-based) index. """
        raise NotImplementedError

    def get_value(self, row, col):
        """ Return the value stored in the table at (row, col). """
        raise NotImplementedError

    def is_cell_empty(self, row, col):
        """ Returns True if the cell at (row, col) has a None value,
        False otherwise."""
        raise NotImplementedError

    #########################################################################
    # 'GridModel' interface -- Subclasses MAY override the following
    #########################################################################

    def get_cols_drag_value(self, cols):
        """ Return the value to use when the specified columns are dragged or
        copied and pasted. cols is a list of column indexes. """
        pass

    def get_cols_selection_value(self, cols):
        """ Return the value to use when the specified cols are selected.
        This value should be enough to specify to other listeners what is
        going on in the grid. rows is a list of row indexes. """

        cols_data = []
        row_count = self.get_row_count()
        for col in cols:
            col_data = []
            for row in range(row_count):
                col_data.append(self.get_value(row, col))

            cols_data.append(col_data)
            
        return cols_data

    def get_column_context_menu(self, col):
        """ Return a MenuManager object that will generate the appropriate
        context menu for this column."""

        pass

    def get_column_size(self, col):
        """ Return the size in pixels of the column indexed by col.
            A value of -1 or None means use the default. """

        return None

    def sort_by_column(self, col, reverse=False):
        """ Sort model data by the column indexed by col. The reverse flag
        indicates that the sort should be done in reverse. """
        pass

    def no_column_sort(self):
        """ Turn off any column sorting of the model data. """
        raise NotImplementedError
    
    def is_column_read_only(self, index):
        """ Return True if the column specified by the zero-based index
        is read-only. """
        return False

    def get_rows_drag_value(self, rows):
        """ Return the value to use when the specified rows are dragged or
        copied and pasted. rows is a list of row indexes. """
        pass

    def get_rows_selection_value(self, rows):
        """ Return the value to use when the specified rows are selected.
        This value should be enough to specify to other listeners what is
        going on in the grid. rows is a list of row indexes. """

        rows_data = []
        column_count = self.get_column_count()
        for row in rows:
            row_data = []
            for col in range(column_count):
                row_data.append(self.get_value(row, col))

            rows_data.append(row_data)
            
        return rows_data

    def get_row_context_menu(self, row):
        """ Return a MenuManager object that will generate the appropriate
        context menu for this row."""
        pass

    def get_row_size(self, row):
        """ Return the size in pixels of the row indexed by 'row'.
            A value of -1 or None means use the default. """

        return None

    def sort_by_row(self, row, reverse=False):
        """ Sort model data by the data row indexed by row. The reverse flag
        indicates that the sort should be done in reverse. """
        pass

    def no_row_sort(self):
        """ Turn off any row sorting of the model data. """
        raise NotImplementedError

    def is_row_read_only(self, index):
        """ Return True if the row specified by the zero-based index
        is read-only. """
        return False

    def get_type(self, row, col):
        """ Return the value stored in the table at (row, col). """
        raise NotImplementedError

    def get_cell_drag_value(self, row, col):
        """ Return the value to use when the specified cell is dragged or
        copied and pasted. """

        # by default we just use the cell value
        return self.get_value(row, col)

    def get_cell_selection_value(self, row, col):
        """ Return the value stored in the table at (row, col). """
        pass

    def get_cell_editor(self, row, col):
        """ Return the editor for the specified cell. """
        return None

    def get_cell_renderer(self, row, col):
        """ Return the renderer for the specified cell. """
        return None

    def resolve_selection(self, selection_list):
        """ Returns a list of (row, col) grid-cell coordinates that
        correspond to the objects in selection_list. For each coordinate, if
        the row is -1 it indicates that the entire column is selected. Likewise
        coordinates with a column of -1 indicate an entire row that is
        selected. Note that the objects in selection_list are
        model-specific. """

        return selection_list


    # fixme: this context menu stuff is going in here for now, but it
    # seems like this is really more of a view piece than a model piece.
    # this is how the tree control does it, however, so we're duplicating
    # that here.
    def get_cell_context_menu(self, row, col):
        """ Return a MenuManager object that will generate the appropriate
        context menu for this cell."""

        pass

    def is_valid_cell_value(self, row, col, value):
        """ Tests whether value is valid for the cell at row, col. Returns
            True if value is acceptable, False otherwise. """
        return False

    def set_value(self, row, col, value):
        """ Sets the value of the cell at (row, col) to value.

        Raises a ValueError if the value is vetoed.

        Note that subclasses should not override this method, but should
        override the _set_value method instead.
        """
        #print 'GridModel.set_value row: ', row, ' col: ', col, ' value: ', value
        rows_appended = self._set_value(row, col, value)

        self.fire_content_changed()
        return
    
    def is_cell_read_only(self, row, col):
        """ Returns True if the cell at (row, col) is not editable,
        False otherwise. """
        return False

    def get_cell_bg_color(self, row, col):
        """ Return a wxColour object specifying what the background color
            of the specified cell should be. """
        return None

    def get_cell_text_color(self, row, col):
        """ Return a wxColour object specifying what the text color
            of the specified cell should be. """
        return None

    def get_cell_font(self, row, col):
        """ Return a wxFont object specifying what the font
            of the specified cell should be. """
        return None

    def get_cell_halignment(self, row, col):
        """ Return a string specifying what the horizontal alignment
            of the specified cell should be.

            Return 'left' for left alignment, 'right' for right alignment,
            or 'center' for center alignment. """
        return None

    def get_cell_valignment(self, row, col):
        """ Return a string specifying what the vertical alignment
            of the specified cell should be.

            Return 'top' for top alignment, 'bottom' for bottom alignment,
            or 'center' for center alignment. """
        return None

    #########################################################################
    # 'GridModel' interface -- Subclasses MAY NOT override the following
    #########################################################################

    def fire_content_changed(self):
        """ Fires the appearance changed event. """

        self.content_changed = 'changed'
        
        return

    def fire_structure_changed(self):
        """ Fires the appearance changed event. """

        self.structure_changed = 'changed'
        
        return

    def delete_rows(self, pos, num_rows):
        """ Removes rows pos through pos + num_rows from the model.
        Subclasses should not override this method, but should override
        _delete_rows instead. """

        deleted = self._delete_rows(pos, num_rows)

        if deleted > 0:
            self.fire_structure_changed()
        
        return True

    def insert_rows(self, pos, num_rows):
        """ Inserts rows at pos through pos + num_rows into the model.
        Subclasses should not override this method, but should override
        _insert_rows instead. """

        inserted = self._insert_rows(pos, num_rows)

        if inserted > 0:
            self.fire_structure_changed()
        
        return True

    def delete_columns(self, pos, num_cols):
        """ Removes columns pos through pos + num_cols from the model.
        Subclasses should not override this method, but should override
        _delete_columns instead. """

        deleted = self._delete_columns(pos, num_cols)

        if deleted > 0:
            self.fire_structure_changed()
        
        return True

    def insert_columns(self, pos, num_cols):
        """ Inserts columns at pos through pos + num_cols into the model.
        Subclasses should not override this method, but should override
        _insert_columns instead. """

        inserted = self._insert_columns(pos, num_cols)

        if inserted > 0:
            self.fire_structure_changed()
        
        return True

    #########################################################################
    # protected 'GridModel' interface -- Subclasses should override these
    #                                    if they wish to support the
    #                                    specific actions.
    #########################################################################
    def _delete_rows(self, pos, num_rows):
        """ Implementation method for delete_rows. Should return the
        number of rows that were deleted. """
        
        pass

    def _insert_rows(self, pos, num_rows):
        """ Implementation method for insert_rows. Should return the
        number of rows that were inserted. """
        
        pass

    def _delete_columns(self, pos, num_cols):
        """ Implementation method for delete_cols. Should return the
        number of columns that were deleted. """
        
        pass

    def _insert_columns(self, pos, num_cols):
        """ Implementation method for insert_columns. Should return the
        number of columns that were inserted. """
        
        pass

    def _set_value(self, row, col, value):
        """ Implementation method for set_value. Should return the
        number of rows or columns, if any, that were appended. """
        
        pass

    def _move_column(self, frm, to):
        """ Moves a specified **frm** column to before the specified **to**
        column. Returns **True** if successful; **False** otherwise.
        """
        return False

    def _move_row(self, frm, to):
        """ Moves a specified **frm** row to before the specified **to** row.
        Returns **True** if successful; **False** otherwise.
        """
        return False

#### EOF ####################################################################
