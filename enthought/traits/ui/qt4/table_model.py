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

from enthought.qt.api import QtCore, QtGui, QVariant, Qt

from enthought.traits.ui.ui_traits import SequenceTypes

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Mapping for trait alignment values to qt4 horizontal alignment constants
h_alignment_map = {
    'left':   Qt.AlignLeft,
    'center': Qt.AlignHCenter,
    'right':  Qt.AlignRight,
}

# Mapping for trait alignment values to qt4 vertical alignment constants
v_alignment_map = {
    'top':    Qt.AlignTop,
    'center': Qt.AlignVCenter,
    'bottom': Qt.AlignBottom,
}

# MIME type for internal table drag/drop operations
mime_type = 'enthought/traits-ui-table-editor'

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

        if role == Qt.DisplayRole or role == Qt.EditRole:
            text = column.get_value(obj)
            if text is not None:
                return QVariant(text)

        elif role == Qt.ToolTipRole:
            tooltip = column.get_tooltip(obj)
            if tooltip:
                return QVariant(tooltip)

        elif role == Qt.FontRole:
            font = column.get_text_font(obj)
            if font is not None:
                return QVariant(QtGui.QFont(font))

        elif role == Qt.TextAlignmentRole:
            string = column.get_horizontal_alignment(obj)
            h_alignment = h_alignment_map.get(string, Qt.AlignLeft)
            string = column.get_vertical_alignment(obj)
            v_alignment = v_alignment_map.get(string, Qt.AlignVCenter)
            return QVariant(h_alignment | v_alignment)

        elif role == Qt.BackgroundRole:
            color = column.get_cell_color(obj)
            if color is not None:
                if isinstance(color, SequenceTypes):
                    q_color = QtGui.QColor(*color)
                else:
                    q_color = QtGui.QColor(color)
                return QVariant(QtGui.QBrush(q_color))

        elif role == Qt.ForegroundRole:
            color = column.get_text_color(obj)
            if color is not None:
                if isinstance(color, SequenceTypes):
                    q_color = QtGui.QColor(*color)
                else:
                    q_color = QtGui.QColor(color)
                return QVariant(QtGui.QBrush(q_color))

        elif role == Qt.UserRole:
            return QVariant(obj)

        return QVariant()

    def flags(self, mi):
        """Reimplemented to set editable and movable status."""
        
        flags = Qt.ItemIsSelectable | Qt.ItemIsEnabled

        if not mi.isValid():
            return flags

        editor = self._editor
        obj = editor.items()[mi.row()]
        column = editor.columns[mi.column()]

        if editor.factory.editable and column.is_editable(obj):
            flags |= Qt.ItemIsEditable

        if editor.factory.reorderable:
            flags |= Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled
            
        return flags

    def headerData(self, section, orientation, role):
        """Reimplemented to return the header data."""

        if orientation == Qt.Horizontal:

            editor = self._editor
            column = editor.columns[section]

            if role == Qt.DisplayRole:
                return QVariant(column.get_label())

        elif orientation == Qt.Vertical:
            
            if role == Qt.DisplayRole:
                return QVariant(str(section + 1))

        return QVariant()

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

        types = QtCore.QStringList()
        types.append(mime_type)
        return types

    def mimeData(self, indexes):
        """Reimplemented to generate MIME data containing the rows of the
        current selection."""

        mime_data = QtCore.QMimeData()
        rows = list(set([ index.row() for index in indexes ]))
        data = QtCore.QByteArray(str(rows[0]))
        for row in rows[1:]:
            data.append(' %i' % row)
        mime_data.setData(mime_type, data)
        return mime_data

    def dropMimeData(self, mime_data, action, row, column, parent):
        """Reimplemented to allow items to be moved."""

        if action == Qt.IgnoreAction:
            return False
        
        data = mime_data.data(mime_type)
        if data.isNull():
            return False

        current_rows = map(int, str(data).split(' '))
        self.moveRows(current_rows, parent.row())
        return True

    def supportedDropActions(self):
        """Reimplemented to allow items to be moved."""
        
        return Qt.MoveAction

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
