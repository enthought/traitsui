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
""" A TraitGridModel builds a grid from a list of traits objects. Each row
represents on object, each column one trait from those objects. All the objects
must be of the same type. Optionally a user may pass in a list of trait names
defining which traits will be shown in the columns and in which order. If this
list is not passed in, then the first object is inspected and every trait
from that object gets a column."""

# Enthought library imports
from enthought.traits.api import Any, Bool, Callable, Dict, Function, HasTraits, \
     Int, List, Str, Trait, TraitError, Type

# local imports
from grid_model import GridColumn, GridModel, GridSortEvent
from trait_grid_cell_adapter import TraitGridCellAdapter

# The classes below are part of the table specification.
class TraitGridColumn(GridColumn):
    """ Structure for holding column specifications in a TraitGridModel. """

    # The trait name for this column. This takes precedence over method
    name = Trait(None, None, Str)

    # A method name to call to get the value for this column
    method = Trait(None, None, Str)

    # A method to be used to sort on this column
    sorter = Trait(None, None, Callable)

    # A dictionary of formats for the display of different types. If it is
    # defined as a callable, then that callable must accept a single argument.
    formats = Dict(key_trait = Type, value_trait=Trait('', Str, Callable))

    # A name to designate the type of this column
    typename = Trait(None, None, Str)
    # note: context menus should go in here as well? but we need
    #       more info than we have available at this point

    size = Int(-1)

class TraitGridSelection(HasTraits):
    """ Structure for holding specification information. """

    # The selected object
    obj = Trait(HasTraits)

    # The specific trait selected on the object
    trait_name = Trait(None, None, Str)

# The meat.
class TraitGridModel(GridModel):
    """ A TraitGridModel builds a grid from a list of traits objects. Each row
    represents on object, each column one trait from those objects. All the
    objects must be of the same type. Optionally a user may pass in a list of
    trait names defining which traits will be shown in the columns and in
    which order. If this list is not passed in, then the first object is
    inspected and every trait from that object gets a column."""

    # A 2-dimensional list/array containing the grid data.
    data = List()#HasTraits)
    
    # The column definitions
    columns = Trait(None, None, List(Trait(None, Str, TraitGridColumn)))

    # The trait to look at to get the row name
    row_name_trait = Trait(None, None, Str)

    # Allow column sorting?
    allow_column_sort = Bool(True)

    # A factory to generate new rows. If this is not None then it must
    # be a no-argument function.
    row_factory = Trait(None, None, Function)

    #########################################################################
    # 'object' interface.
    #########################################################################
    def __init__(self, **traits):
        """ Create a TraitGridModel object. """

        # Base class constructor
        super(TraitGridModel, self).__init__(**traits)

        # if no columns are pass in then create the list of names
        # from the first trait in the list. if the list is empty,
        # the columns should be an empty list as well.
        self._auto_columns = self.columns
        
        if self.columns is None or len(self.columns) == 0:
            if self.data is not None and len(self.data) > 0:
                self._auto_columns = []

                # we only add traits that aren't events, since events
                # are write-only
                for name, trait in self.data[0].traits().items():
                    if trait.type != 'event':
                        self._auto_columns.append(TraitGridColumn(name = name))
            else:
                self._auto_columns = []

        # attach trait handlers to the list object
        self.on_trait_event(self._on_data_changed, 'data')
        self.on_trait_event(self._on_data_items_changed, 'data_items')

        # attach appropriate trait handlers to objects in the list
        self.__manage_data_listeners(self.data)

        # attach a listener to the column definitions so we refresh when
        # they change
        self.on_trait_change(self._on_columns_changed,
                             'columns')
        self.on_trait_event(self._on_columns_items_changed,
                            'columns_items')
        # attach listeners to the column definitions themselves
        self.__manage_column_listeners(self.columns)
            
        # attach a listener to the row_name_trait
        self.on_trait_change(self._on_row_name_trait_changed, 'row_name_trait')

        return

    #########################################################################
    # 'GridModel' interface.
    #########################################################################

    def get_column_count(self):
        """ Return the number of columns for this table. """

        return len(self._auto_columns)

    def get_column_name(self, index):
        """ Return the label of the column specified by the
        (zero-based) index. """

        try:
            name = col = self._auto_columns[index]
            if isinstance(col, TraitGridColumn):
                if col.label is not None:
                    name = col.label
                else:
                    name = col.name
        except IndexError:
            name = ''

        return name

    def get_column_size(self, index):
        """ Return the size in pixels of the column indexed by col.
            A value of -1 or None means use the default. """

        size = -1
        try:
            col = self._auto_columns[index]
            if isinstance(col, TraitGridColumn):
                size = col.size
        except IndexError:
            pass

        return size

    def get_cols_drag_value(self, cols):
        """ Return the value to use when the specified columns are dragged or
        copied and pasted. cols is a list of column indexes. """

        # iterate over every column, building a list of the values in that
        # column
        value = []
        for col in cols:
            value.append(self.__get_data_column(col))

        return value

    def get_cols_selection_value(self, cols):
        """ Returns a list of TraitGridSelection objects containing the
        object corresponding to the grid rows and the traits corresponding
        to the specified columns. """

        values = []
        for obj in self.data:
            for col in cols:
                values.append(TraitGridSelection(obj = obj,
                                                 trait_name = self.__get_column_name(col)))

        return values

    def sort_by_column(self, col, reverse=False):
        """ Sort model data by the column indexed by col. """

        # first check to see if we allow sorts by column
        if not self.allow_column_sort:
            return

        # see if a sorter is specified for this column
        try:
            column = self._auto_columns[col]
            name = self.__get_column_name(col)
            # by default we use cmp to sort on the traits
            sorter = cmp
            if isinstance(column, TraitGridColumn) and \
                   column.sorter is not None:
                sorter = column.sorter
        except IndexError:
            return

        # now sort the data appropriately
        def sort_function(a, b):
            if hasattr(a, name):
                a_trait = getattr(a, name)
            else:
                a_trait = None

            if hasattr(b, name):
                b_trait = getattr(b, name)
            else:
                b_trait = None

            return sorter(a_trait, b_trait)

        self.data.sort(sort_function)

        if reverse:
            self.data.reverse()

        # now fire an event to tell the grid we're sorted
        print 'firing sort event'
        self.column_sorted = GridSortEvent(index = col, reversed = reverse)

        return
        

    def is_column_read_only(self, index):
        """ Return True if the column specified by the zero-based index
        is read-only. """

        return self.__get_column_readonly(index)
    
    def get_row_count(self):
        """ Return the number of rows for this table. """

        if self.data is not None:
            count = len(self.data)
        else:
            count = 0

        return count

    def get_row_name(self, index):
        """ Return the name of the row specified by the
        (zero-based) index. """

        if self.row_name_trait is not None:
            try:
                row = self._get_row(index)
                if hasattr(row, self.row_name_trait):
                    name = getattr(row, self.row_name_trait)
            except IndexError:
                name = str(index + 1)

        else:
            name = str(index + 1)
            
        return name

    def get_rows_drag_value(self, rows):
        """ Return the value to use when the specified rows are dragged or
        copied and pasted. rows is a list of row indexes. If there is only
        one row listed, return the corresponding trait object. If more than
        one row is listed then return a list of objects. """

        # return a list of objects
        value = []

        for index in rows:
            try:
                # note that we can't use get_value for this because it
                # sometimes returns strings instead of the actual value,
                # e.g. in cases where a float_format is specified
                value.append(self._get_row(index))
            except IndexError:
                value.append(None)

        return value

    def get_rows_selection_value(self, rows):
        """ Returns a list of TraitGridSelection objects containing the
        object corresponding to the selected rows. """

        values = []
        for row_index in rows:
            values.append(TraitGridSelection(obj = self.data[row_index]))

        return values

    def is_row_read_only(self, index):
        """ Return True if the row specified by the zero-based index
        is read-only. """

        return False

    def get_cell_editor(self, row, col):
        """ Return the editor for the specified cell. """

        # print 'TraitGridModel.get_cell_editor row: ', row, ' col: ', col

        obj        = self.data[row]
        trait_name = self.__get_column_name(col)
        trait      = obj.base_trait(trait_name)
        if trait is None:
            return None

        factory = trait.get_editor()

        return TraitGridCellAdapter(factory, obj, trait_name, '')

    def get_cell_drag_value(self, row, col):
        """ Return the value to use when the specified cell is dragged or
        copied and pasted. """

        # find the name of the column indexed by col
        # note that this code is the same as the get_value code but without
        # the potential string formatting
        column = self.__get_column(col)
        obj = self._get_row(row)

        value = self._get_data_from_row(obj, column)

        return value

    def get_cell_selection_value(self, row, col):
        """ Returns a TraitGridSelection object specifying the data stored
        in the table at (row, col). """

        obj = self.data[row]
        trait_name = self.__get_column_name(col)

        return TraitGridSelection(obj = obj, trait_name = trait_name)

    def resolve_selection(self, selection_list):
        """ Returns a list of (row, col) grid-cell coordinates that
        correspond to the objects in objlist. For each coordinate, if the
        row is -1 it indicates that the entire column is selected. Likewise
        coordinates with a column of -1 indicate an entire row that is
        selected. For the TraitGridModel, the objects in objlist must
        be TraitGridSelection objects. """

        cells = []
        for selection in selection_list:
            try:
                row = self.data.index(selection.obj)
            except ValueError:
                continue

            column = -1
            if selection.trait_name is not None:
                column = self._get_column_index_by_trait(selection.trait_name)
                if column is None:
                    continue
                
            cells.append((row, column))

        return cells

    def get_type(self, row, col):
        """ Return the value stored in the table at (row, col). """

        typename = self.__get_column_typename(col)

        return typename

    def get_value(self, row, col):
        """ Return the value stored in the table at (row, col). """

        value = self.get_cell_drag_value(row, col)
        formats = self.__get_column_formats(col)

        if value is not None and formats is not None and \
               formats.has_key(type(value)) and \
               formats[type(value)] is not None:
            try:
                format = formats[type(value)]
                if callable(format):
                    value = format(value)
                else:
                    value = format % value
            except TypeError:
                # not enough arguments? wrong kind of arguments?
                pass

        return value

    def is_cell_empty(self, row, col):
        """ Returns True if the cell at (row, col) has a None value,
        False otherwise."""

        value = self.get_value(row, col)

        return value is None

    def is_cell_editable(self, row, col):
        """ Returns True if the cell at (row, col) is editable,
        False otherwise. """
        return not self.is_column_read_only(col)

    #########################################################################
    # protected 'GridModel' interface.
    #########################################################################
    def _insert_rows(self, pos, num_rows):
        """ Inserts num_rows at pos and fires an event iff a factory method
        for new rows is defined. Otherwise returns 0. """

        count = 0
        if self.row_factory is not None:
            new_data = []
            for i in range(num_rows):
                new_data.append(self.row_factory())

            count = self._insert_rows_into_model(pos, new_data)
            self.rows_added = ('added', pos, new_data)

        return count

    def _delete_rows(self, pos, num_rows):
        """ Removes rows pos through pos + num_rows from the model. """

        if pos + num_rows >= self.get_row_count():
            num_rows = self.get_rows_count() - pos

        return self._delete_rows_from_model(pos, num_rows)

    def _set_value(self, row, col, value):
        """ Sets the value of the cell at (row, col) to value.

        Raises a ValueError if the value is vetoed or the cell at
        (row, col) does not exist. """

        #print 'TraitGridModel._set_value: new: ', value

        new_rows = 0
        # find the column indexed by col
        column = self.__get_column(col)
        obj = self._get_row(row)
        success = False
        if obj is not None:
            success = self._set_data_on_row(obj, column, value)
        else:
            # Add a new row.
            new_rows = self._insert_rows(self.get_row_count(), 1)
            if new_rows > 0:
                # now set the value on the new object
                obj = self._get_row(self.get_row_count() - 1)
                success = self._set_data_on_row(obj, column, value)

        if not success:
            # fixme: what do we do in this case? veto the set somehow? raise
            #        an exception?
            pass

        return new_rows

    #########################################################################
    # protected interface.
    #########################################################################
    def _get_row(self, index):
        """ Return the object that corresponds to the row at index. Override
        this to handle very large data sets. """

        return self.data[index]

    def _get_data_from_row(self, row, column):
        """ Retrieve the data specified by column for this row. Attribute
        can be either a member of the row object, or a no-argument method
        on that object. Override this method to provide alternative ways
        of accessing the data in the object. """

        value = None

        if row is not None and column is not None:
            if not isinstance(column, TraitGridColumn):
                # first handle the case where the column
                # definition might be just a string
                if hasattr(row, column):
                    value = getattr(row, column)
            elif column.name is not None and hasattr(row, column.name):
                # this is the case when the trait name is specified
                value = getattr(row, column.name)
            elif column.method is not None and hasattr(row, column.method):
                # this is the case when an object method is specified
                value = getattr(row, column.method)()

        return value

    def _set_data_on_row(self, row, column, value):
        """ Retrieve the data specified by column for this row. Attribute
        can be either a member of the row object, or a no-argument method
        on that object. Override this method to provide alternative ways
        of accessing the data in the object. """

        success = False

        if row is not None and column is not None:
            if not isinstance(column, TraitGridColumn):
                if hasattr(row, column):
                    # sometimes the underlying grid gives us 0/1 instead
                    # of True/False. do some conversion here to make that
                    # case worl.
                    #if type(getattr(row, column)) == bool and \
                    #       type(value) != bool:
                        # convert the value to a boolean
                    #    value = bool(value)
                        
                    setattr(row, column, value)
                    success = True
            elif column.name is not None and hasattr(row, column.name):
                # sometimes the underlying grid gives us 0/1 instead
                # of True/False. do some conversion here to make that
                # case worl.
                #if type(getattr(row, column.name)) == bool and \
                #       type(value) != bool:
                    # convert the value to a boolean
                #    value = bool(value)
                setattr(row, column.name, value)
                sucess = True

            # do nothing in the method case as we don't allow rows
            # defined to return a method value to set the value
            
        return success
    
    def _insert_rows_into_model(self, pos, new_data):
        """ Insert the given new rows into the model. Override this method
        to handle very large data sets. """

        for data in new_data:
            self.data.insert(pos, data)
            pos += 1

        return

    def _delete_rows_from_model(self, pos, num_rows):
        """ Delete the specified rows from the model. Override this method
        to handle very large data sets. """
        del self.data[pos, pos + num_rows]

        return num_rows

    ###########################################################################
    # trait handlers
    ###########################################################################

    def _on_row_name_trait_changed(self, new):
        """ Force the grid to refresh when any underlying trait changes. """
        self.fire_content_changed()
        return
        
    def _on_columns_changed(self, object, name, old, new):
        """ Force the grid to refresh when any underlying trait changes. """
        self.__manage_column_listeners(old, remove=True)
        self.__manage_column_listeners(self.columns)
        self._auto_columns = self.columns
        self.fire_structure_changed()
        return

    def _on_columns_items_changed(self, event):
        """ Force the grid to refresh when any underlying trait changes. """

        self.__manage_column_listeners(event.removed, remove=True)
        self.__manage_column_listeners(event.added)
        self.fire_structure_changed()
        return

    def _on_contained_trait_changed(self, new):
        """ Force the grid to refresh when any underlying trait changes. """
        self.fire_content_changed()
        return

    def _on_data_changed(self, object, name, old, new):
        """ Force the grid to refresh when the underlying list changes. """

        self.__manage_data_listeners(old, remove=True)
        self.__manage_data_listeners(self.data)
        self.fire_structure_changed()
        return

    def _on_data_items_changed(self, event):
        """ Force the grid to refresh when the underlying list changes. """

        # if an item was removed then remove that item's listener
        self.__manage_data_listeners(event.removed, remove=True)

        # if items were added then add trait change listeners on those items
        self.__manage_data_listeners(event.added)

        self.fire_content_changed()
        return

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


    def __get_column(self, col):

        try:
            column = self._auto_columns[col]
        except IndexError:
            column = None

        return column

    def __get_column_name(self, col):

        name = column = self.__get_column(col)
        if isinstance(column, TraitGridColumn):
            name = column.name

        return name

    def __get_column_typename(self, col):

        name = column = self.__get_column(col)
        typename = None
        if isinstance(column, TraitGridColumn):
            typename = column.typename

        return typename

    def __get_column_readonly(self, col):

        read_only = False
        column = self.__get_column(col)
        if isinstance(column, TraitGridColumn):
            read_only = column.read_only

        return read_only

    def __get_column_formats(self, col):

        formats = None
        column = self.__get_column(col)
        if isinstance(column, TraitGridColumn):
            formats = column.formats

        return formats

    def _get_column_index_by_trait(self, trait_name):

        cols = self._auto_columns
        for i in range(len(cols)):
            col = cols[i]
            if isinstance(col, TraitGridColumn):
                col_name = col.name
            else:
                col_name = col

            if col_name == trait_name:
                return i

        return None

    def __manage_data_listeners(self, list, remove=False):
        # attach appropriate trait handlers to objects in the list
        if list is not None:
            for item in list:
                item.on_trait_change(self._on_contained_trait_changed,
                                     remove = remove)
        return

    def __manage_column_listeners(self, collist, remove=False):

        if collist is not None:
            for col in collist:
                if isinstance(col, TraitGridColumn):
                    col.on_trait_change(self._on_columns_changed,
                                        remove = remove)

        return
    
#### EOF ####################################################################

