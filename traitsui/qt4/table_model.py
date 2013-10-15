#------------------------------------------------------------------------------
# Copyright (c) 2008, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD license.
# However, when used with the GPL version of PyQt the additional terms described
# in the PyQt GPL exception also apply.
#
# Author: Riverbank Computing Limited
#------------------------------------------------------------------------------

""" Defines the table model used by the table editor.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from pyface.qt import QtCore, QtGui

from traitsui.ui_traits import SequenceTypes

from .clipboard import PyMimeData 

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Mapping for trait alignment values to qt4 horizontal alignment constants
h_alignment_map = {
    'left':   QtCore.Qt.AlignLeft,
    'center': QtCore.Qt.AlignHCenter,
    'right':  QtCore.Qt.AlignRight,
}

# Mapping for trait alignment values to qt4 vertical alignment constants
v_alignment_map = {
    'top':    QtCore.Qt.AlignTop,
    'center': QtCore.Qt.AlignVCenter,
    'bottom': QtCore.Qt.AlignBottom,
}

# MIME type for internal table drag/drop operations
mime_type = 'traits-ui-table-editor'

def as_qcolor(color):
    """ Convert a color specification (maybe a tuple) into a QColor.
    """
    if isinstance(color, SequenceTypes):
        return QtGui.QColor(*color)
    else:
        return QtGui.QColor(color)

#-------------------------------------------------------------------------------
#  'TableModel' class:
#-------------------------------------------------------------------------------

class TableModel(QtCore.QAbstractTableModel):
    """The model for table data."""

    def __init__(self, editor, parent=None):
        """Initialise the object."""

        QtCore.QAbstractTableModel.__init__(self, parent)

        self._editor = editor

    #---------------------------------------------------------------------------
    #  QAbstractTableModel interface:
    #---------------------------------------------------------------------------

    def rowCount(self, mi):
        """Reimplemented to return the number of rows."""

        return len(self._editor.items())

    def columnCount(self, mi):
        """Reimplemented to return the number of columns."""

        return len(self._editor.columns)

    def data(self, mi, role):
        """Reimplemented to return the data."""

        obj = self._editor.items()[mi.row()]
        column = self._editor.columns[mi.column()]

        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            text = column.get_value(obj)
            if text is not None:
                return text

        elif role == QtCore.Qt.DecorationRole:
            image = self._editor._get_image(column.get_image(obj))
            if image is not None:
                return image

        elif role == QtCore.Qt.ToolTipRole:
            tooltip = column.get_tooltip(obj)
            if tooltip:
                return tooltip

        elif role == QtCore.Qt.FontRole:
            font = column.get_text_font(obj)
            if font is not None:
                return QtGui.QFont(font)

        elif role == QtCore.Qt.TextAlignmentRole:
            string = column.get_horizontal_alignment(obj)
            h_alignment = h_alignment_map.get(string, QtCore.Qt.AlignLeft)
            string = column.get_vertical_alignment(obj)
            v_alignment = v_alignment_map.get(string, QtCore.Qt.AlignVCenter)
            return (h_alignment | v_alignment)

        elif role == QtCore.Qt.BackgroundRole:
            color = column.get_cell_color(obj)
            if color is None:
                # FIXME: Yes, this is weird. It should work fine to fall through
                # to the catch-all None at the end, but it doesn't.
                return None
            else:
                q_color = as_qcolor(color)
                return QtGui.QBrush(q_color)

        elif role == QtCore.Qt.ForegroundRole:
            color = column.get_text_color(obj)
            if color is not None:
                q_color = as_qcolor(color)
                return QtGui.QBrush(q_color)

        elif role == QtCore.Qt.UserRole:
            return obj

        elif role == QtCore.Qt.CheckStateRole:
            if column.get_type(obj) == "bool" and column.show_checkbox:
                if column.get_raw_value(obj):
                    return QtCore.Qt.Checked
                else:
                    return QtCore.Qt.Unchecked

        return None

    def flags(self, mi):
        """Reimplemented to set editable and movable status."""

        editor = self._editor

        if not mi.isValid():
            if editor.factory.reorderable:
                return QtCore.Qt.ItemIsDropEnabled
            else:
                return

        flags = QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | \
                QtCore.Qt.ItemIsDragEnabled 

        obj = editor.items()[mi.row()]
        column = editor.columns[mi.column()]

        if editor.factory.editable and column.is_editable(obj):
            flags |= QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsDropEnabled

        if editor.factory.reorderable:
            flags |= QtCore.Qt.ItemIsDropEnabled

        if column.get_type(obj) == "bool" and column.show_checkbox:
            flags |= QtCore.Qt.ItemIsUserCheckable

        return flags

    def headerData(self, section, orientation, role):
        """Reimplemented to return the header data."""

        if orientation == QtCore.Qt.Horizontal:

            editor = self._editor
            column = editor.columns[section]

            if role == QtCore.Qt.DisplayRole:
                return column.get_label()

        elif orientation == QtCore.Qt.Vertical:

            if role == QtCore.Qt.DisplayRole:
                return str(section + 1)

        return None

    def insertRow(self, row, parent=QtCore.QModelIndex(), obj=None):
        """Reimplemented to allow creation of new rows. Added an optional
        arg to allow the insertion of an existing row object."""

        editor = self._editor
        if obj is None:
            obj = editor.create_new_row()

        self.beginInsertRows(parent, row, row)
        editor.callx(editor.items().insert, row, obj)
        self.endInsertRows()
        return True

    def insertRows(self, row, count, parent=QtCore.QModelIndex()):
        """Reimplemented to allow creation of new rows."""

        editor = self._editor
        items = editor.items()
        self.beginInsertRows(parent, row, row + count - 1)
        for i in xrange(count):
            editor.callx(items.insert, row + i, editor.create_new_row())
        self.endInsertRows()
        return True

    def removeRows(self, row, count, parent=QtCore.QModelIndex()):
        """Reimplemented to allow row deletion, as well as reordering via drag
        and drop."""

        editor = self._editor
        items = editor.items()
        self.beginRemoveRows(parent, row, row + count - 1)
        for i in xrange(count):
            editor.callx(items.pop, row + i)
        self.endRemoveRows()
        return True

    def mimeTypes(self):
        """Reimplemented to expose our internal MIME type for drag and drop
        operations."""

        return [mime_type, PyMimeData.MIME_TYPE, PyMimeData.NOPICKLE_MIME_TYPE]

    def mimeData(self, indexes):
        """Reimplemented to generate MIME data containing the rows of the
        current selection."""
        
        editor = self._editor
        selection_mode = editor.factory.selection_mode
        
        if selection_mode.startswith("cell"):
            data = [self._get_cell_drag_value(index.row(), index.column())
                for index in indexes]
        elif selection_mode.startswith("column"):
            columns = sorted(set(index.column() for index in indexes))
            data = self._get_columns_drag_value(columns)
        else:
            rows = sorted(set(index.row() for index in indexes))
            data = self._get_rows_drag_value(rows)
        
        mime_data = PyMimeData.coerce(data)
        
        # handle re-ordering via internal drags
        if editor.factory.reorderable:
            rows = sorted(set([ index.row() for index in indexes ]))
            data = QtCore.QByteArray(str(id(self)))
            for row in rows:
                data.append(' %i' % row)
            mime_data.setData(mime_type, data)
        return mime_data

    def dropMimeData(self, mime_data, action, row, column, parent):
        """Reimplemented to allow items to be moved."""

        if action == QtCore.Qt.IgnoreAction:
            return False
            
        # this is a drag from a table model?
        data = mime_data.data(mime_type)
        if not data.isNull() and action == QtCore.Qt.MoveAction:
            id_and_rows = map(int, str(data).split(' '))
            table_id = id_and_rows[0]
            # is it from ourself?
            if table_id == id(self):
                current_rows = id_and_rows[1:]
                if not parent.isValid():
                    row = len(self._editor.items())-1
                else:
                    row == parent.row()
                    
                self.moveRows(current_rows, row)
                return True

        data = PyMimeData.coerce(mime_data).instance()
        if data is not None:
            editor = self._editor
            
            if row == -1 and column == -1 and parent.isValid():
                row = parent.row()
                column = parent.column()
            
            if row != -1 and column != - 1:
                object = editor.items()[row]
                column = editor.columns[column]                
                if column.is_droppable(object, data):
                    column.set_value(object, data)
                    return True
            
        return False

    def supportedDropActions(self):
        """Reimplemented to allow items to be moved."""
    
        return QtCore.Qt.MoveAction

    #---------------------------------------------------------------------------
    #  Utility methods
    #---------------------------------------------------------------------------
    
    def _get_columns_drag_value(self, columns):
        """ Returns the value to use when the specified columns are dragged or
            copied and pasted. The parameter *cols* is a list of column indexes.
        """
        return [self._get_column_data(column) for column in columns]

    def _get_column_data(self, column):
        """ Return the model data for the column as a list """
        editor = self._editor
        column_obj = editor.columns[column]
        return [column_obj.get_value(item) for item in editor.items()]

    def _get_rows_drag_value(self, rows):
        """ Returns the value to use when the specified rows are dragged or
            copied and pasted. The parameter *rows* is a list of row indexes.
            Return a list of objects.
        """
        items = self._editor.items()
        return [items[row] for row in rows]

    def _get_cell_drag_value(self, row, column):
        """ Returns the value to use when the specified cell is dragged or
            copied and pasted.
        """
        editor = self._editor
        item = editor.items()[row]
        drag_value = editor.columns[column].get_drag_value(item)
        return drag_value

    #---------------------------------------------------------------------------
    #  TableModel interface:
    #---------------------------------------------------------------------------
    
    def moveRow(self, old_row, new_row):
        """Convenience method to move a single row."""

        return self.moveRows([old_row], new_row)

    def moveRows(self, current_rows, new_row):
        """Moves a sequence of rows (provided as a list of row indexes) to a new
        row."""

        # Sort rows in descending order so they can be removed without
        # invalidating the indices.
        current_rows.sort()
        current_rows.reverse()

        # If the the highest selected row is lower than the destination, do an
        # insertion before rather than after the destination.
        if current_rows[-1] < new_row:
            new_row += 1

        # Remove selected rows...
        items = self._editor.items()
        objects = []
        for row in current_rows:
            if row <= new_row:
                new_row -= 1
            objects.insert(0, items[row])
            self.removeRow(row)

        # ...and add them at the new location.
        for i, obj in enumerate(objects):
            self.insertRow(new_row + i, obj=obj)

        # Update the selection for the new location.
        self._editor.set_selection(objects)

#-------------------------------------------------------------------------------
#  'SortFilterTableModel' class:
#-------------------------------------------------------------------------------

class SortFilterTableModel(QtGui.QSortFilterProxyModel):
    """A wrapper for the TableModel which provides sorting and filtering
    capability."""

    def __init__(self, editor, parent=None):
        """Initialise the object."""

        QtGui.QSortFilterProxyModel.__init__(self, parent)

        self._editor = editor

    #---------------------------------------------------------------------------
    #  QSortFilterProxyModel interface:
    #---------------------------------------------------------------------------

    def filterAcceptsRow(self, source_row, source_parent):
        """"Reimplemented to use a TableFilter for filtering rows."""

        if self._editor._filtered_cache is None:
            return True
        else:
            return self._editor._filtered_cache[source_row]

    def filterAcceptsColumn(self, source_column, source_parent):
        """Reimplemented to save time, because we always return True."""

        return True

    def lessThan(self, left_mi, right_mi):
        """Reimplemented to sort according to the 'cmp' method defined for
        TableColumn."""

        editor = self._editor
        column = editor.columns[left_mi.column()]
        items = editor.items()
        left, right = items[left_mi.row()], items[right_mi.row()]

        return column.cmp(left, right) < 0

    #---------------------------------------------------------------------------
    #  SortFilterTableModel interface:
    #---------------------------------------------------------------------------

    def moveRow(self, old_row, new_row):
        """Convenience method to move a single row."""

        return self.moveRows([old_row], new_row)

    def moveRows(self, current_rows, new_row):
        """Delegate to source model with mapped rows."""

        source = self.sourceModel()
        current_rows = [ self.mapToSource(self.index(row, 0)).row()
                         for row in current_rows ]
        new_row = self.mapToSource(self.index(new_row, 0)).row()
        source.moveRows(current_rows, new_row)
