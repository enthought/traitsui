""" An adapter model that inverts all of its row/column targets. Use
this class with the CompositeGridModel to make models with different
orientations match, or use it to visually flip the data without modifying
the underlying model's sense of row and column. """

# Enthought library imports
from enthought.traits.api import Instance

# local imports
from grid_model import GridModel

class InvertedGridModel(GridModel):
    """ An adapter model that inverts all of its row/column targets. Use
    this class with the CompositeGridModel to make models with different
    orientations match, or use it to visually flip the data without modifying
    the underlying model's sense of row and column. """

    model = Instance(GridModel, ())
    
    #########################################################################
    # 'GridModel' interface.
    #########################################################################

    def get_column_count(self):

        return self.model.get_row_count()

    def get_column_name(self, index):

        return self.model.get_row_name(index)

    def get_cols_drag_value(self, cols):

        return self.model.get_rows_drag_value(cols)

    def get_cols_selection_value(self, cols):

        return self.model.get_rows_selection_value(cols)

    def get_column_context_menu(self, col):

        return self.model.get_row_context_menu(col)

    def sort_by_column(self, col, reverse=False):

        return self.model.sort_by_row(col, reverse)
    
    def is_column_read_only(self, index):

        return self.model.is_row_read_only(index)
    
    def get_row_count(self):

        return self.model.get_column_count()

    def get_row_name(self, index):

        return self.model.get_column_name(index)

    def get_rows_drag_value(self, rows):

        return self.model.get_cols_drag_value(rows)

    def get_rows_selection_value(self, rows):

        return self.model.get_cols_selection_value(rows)

    def get_row_context_menu(self, row):

        return self.model.get_col_context_menu(row)

    def sort_by_row(self, row, reverse=False):

        return self.model.sort_by_col(row, reverse)

    def is_row_read_only(self, index):
        
        return self.model.is_column_read_only(index)

    def delete_rows(self, pos, num_rows):

        return self.model.delete_cols(pos, num_rows)

    def insert_cols(self, pos, num_rows):

        return self.model.insert_rows(pos, num_rows)

    def get_value(self, row, col):

        return self.model.get_value(col, row)

    def get_cell_drag_value(self, row, col):

        return self.model.get_cell_drag_value(col, row)

    def get_cell_selection_value(self, row, col):

        return self.model.get_cell_selection_value(col, row)

    def resolve_selection(self, selection_list):

        return self.model.resolve_selection(selection_list)

    def get_cell_context_menu(self, row, col):

        return self.model.get_cell_context_menu(col, row)

    def set_value(self, row, col, value):

        return self.model.set_value(col, row, value)
    
    def is_cell_empty(self, row, col):

        return self.model.is_cell_empty(col, row)

    def is_cell_editable(self, row, col):

        return self.model.is_cell_editable(col, row)



#### EOF ######################################################################
