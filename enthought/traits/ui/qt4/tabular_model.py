#-------------------------------------------------------------------------------
#
#  Copyright (c) 2009, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
#  Author: Evan Patterson
#  Date:   06/22/2009
#
#-------------------------------------------------------------------------------

""" Defines the table model used by the tabular editor.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from enthought.qt import QtCore, QtGui

from enthought.traits.ui.ui_traits import SequenceTypes

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Mapping for trait alignment values to qt4 alignment values:
alignment_map = {
    'left':    QtCore.Qt.AlignLeft,
    'right':   QtCore.Qt.AlignRight,
    'center':  QtCore.Qt.AlignHCenter,
    'justify': QtCore.Qt.AlignJustify
}

# MIME type for internal table drag/drop operations
mime_type = 'enthought/traits-ui-tabular-editor'

#-------------------------------------------------------------------------------
#  'TabularModel' class:
#-------------------------------------------------------------------------------

class TabularModel(QtCore.QAbstractTableModel):
    """ The model for tabular data."""

    def __init__(self, editor, parent=None):
        """ Initialise the object.
        """
        QtCore.QAbstractTableModel.__init__(self, parent)

        self._editor = editor

    #---------------------------------------------------------------------------
    #  QAbstractItemModel interface:
    #---------------------------------------------------------------------------

    def data(self, mi, role):
        """ Reimplemented to return the data.
        """
        editor = self._editor
        adapter = editor.adapter
        obj, name = editor.object, editor.name
        row, column = mi.row(), mi.column()

        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            return QtCore.QVariant(adapter.get_text(obj, name, row, column))

        elif role == QtCore.Qt.DecorationRole:
            image = editor._get_image(adapter.get_image(obj, name, row, column))
            if image is not None:
                return QtCore.QVariant(image)

        elif role == QtCore.Qt.ToolTipRole:
            tooltip = adapter.get_tooltip(obj, name, row, column)
            if tooltip:
                return QtCore.QVariant(tooltip)

        elif role == QtCore.Qt.FontRole:
            font = adapter.get_font(obj, name, row)
            if font is not None:
                return QtCore.QVariant(QtGui.QFont(font))

        elif role == QtCore.Qt.TextAlignmentRole:
            string = adapter.get_alignment(obj, name, column)
            alignment = alignment_map.get(string, QtCore.Qt.AlignLeft)
            return QtCore.QVariant(alignment | QtCore.Qt.AlignVCenter)

        elif role == QtCore.Qt.BackgroundRole:
            color = adapter.get_bg_color(obj, name, row)
            if color is not None:
                if isinstance(color, SequenceTypes):
                    q_color = QtGui.QColor(*color)
                else:
                    q_color = QtGui.QColor(color)
                return QtCore.QVariant(QtGui.QBrush(q_color))

        elif role == QtCore.Qt.ForegroundRole:
            color = adapter.get_text_color(obj, name, row)
            if color is not None:
                if isinstance(color, SequenceTypes):
                    q_color = QtGui.QColor(*color)
                else:
                    q_color = QtGui.QColor(color)
                return QtCore.QVariant(QtGui.QBrush(q_color))

        return QtCore.QVariant()

    def setData(self, mi, value, role):
        """ Reimplmented to allow for modification for the object trait.
        """
        if role != QtCore.Qt.EditRole:
            return False

        editor = self._editor
        obj, name = editor.object, editor.name
        row, column = mi.row(), mi.column()

        editor.adapter.set_text(obj, name, row, column, str(value.toString()))
        signal = QtCore.SIGNAL('dataChanged(QModelIndex,QModelIndex)')
        self.emit(signal, mi, mi)
        return True

    def flags(self, mi):
        """ Reimplemented to set editable status and movable status.
        """
        editor = self._editor
        index = mi.row()

        flags = QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled

        if (editor.factory.editable and 'edit' in editor.factory.operations and
            editor.adapter.get_can_edit(editor.object, editor.name, index)):
            flags |= QtCore.Qt.ItemIsEditable

        if (editor.factory.editable and 'move' in editor.factory.operations and
            editor.adapter.get_drag(editor.object, editor.name, index) is not None):
            flags |= QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsDropEnabled

        return flags

    def headerData(self, section, orientation, role):
        """ Reimplemented to return the header data.
        """
        if orientation != QtCore.Qt.Horizontal or role != QtCore.Qt.DisplayRole:
            return QtCore.QVariant()

        editor = self._editor
        label = editor.adapter.label_map[section]
        return QtCore.QVariant(label)

    def rowCount(self, mi):
        """ Reimplemented to return the number of rows.
        """
        editor = self._editor
        return editor.adapter.len(editor.object, editor.name)

    def columnCount(self, mi):
        """ Reimplemented to return the number of columns.
        """
        editor = self._editor
        return len(editor.adapter.columns)

    def insertRow(self, row, parent=QtCore.QModelIndex(), obj=None):
        """ Reimplemented to allow creation of new rows. Added an optional
            arg to allow the insertion of an existing row object.
        """
        editor = self._editor
        adapter = editor.adapter

        if obj is None:
            obj = adapter.get_default_value(editor.object, editor.name)
        self.beginInsertRows(parent, row, row)
        editor.callx(editor.adapter.insert, editor.object, editor.name, row, obj)
        self.endInsertRows()
        return True

    def insertRows(self, row, count, parent=QtCore.QModelIndex()):
        """ Reimplemented to allow creation of new items.
        """
        editor = self._editor
        adapter = editor.adapter

        self.beginInsertRows(parent, row, row + count - 1)
        for i in xrange(count):
            value = adapter.get_default_value(editor.object, editor.name)
            editor.callx(adapter.insert, editor.object, editor.name, row, value)
        self.endInsertRows()
        return True

    def removeRows(self, row, count, parent=QtCore.QModelIndex()):
        """ Reimplemented to allow row deletion, as well as reordering via drag
            and drop.
        """
        editor = self._editor
        adapter = editor.adapter

        self.beginRemoveRows(parent, row, row + count - 1)
        for i in xrange(count):
            editor.callx(adapter.delete, editor.object, editor.name, row)
        self.endRemoveRows()
        return True

    def mimeTypes(self):
        """ Reimplemented to expose our internal MIME type for drag and drop
            operations.
        """
        types = QtCore.QStringList()
        types.append(mime_type)
        return types

    def mimeData(self, indexes):
        """ Reimplemented to generate MIME data containing the rows of the
            current selection.
        """
        mime_data = QtCore.QMimeData()
        rows = list(set([ index.row() for index in indexes ]))
        data = QtCore.QByteArray(str(rows[0]))
        for row in rows[1:]:
            data.append(' %i' % row)
        mime_data.setData(mime_type, data)
        return mime_data

    def dropMimeData(self, mime_data, action, row, column, parent):
        """ Reimplemented to allow items to be moved.
        """
        if action == QtCore.Qt.IgnoreAction:
            return False

        data = mime_data.data(mime_type)
        if data.isNull():
            return False

        current_rows = map(int, str(data).split(' '))
        self.moveRows(current_rows, parent.row())
        return True

    def supportedDropActions(self):
        """ Reimplemented to allow items to be moved.
        """
        return QtCore.Qt.MoveAction

    #---------------------------------------------------------------------------
    #  TabularModel interface:
    #---------------------------------------------------------------------------

    def moveRow(self, old_row, new_row):
        """ Convenience method to move a single row.
        """
        return self.moveRows([old_row], new_row)

    def moveRows(self, current_rows, new_row):
        """ Moves a sequence of rows (provided as a list of row indexes) to a
            new row.
        """
        editor = self._editor

        # Sort rows in descending order so they can be removed without
        # invalidating the indices.
        current_rows.sort()
        current_rows.reverse()

        # If the the highest selected row is lower than the destination, do an
        # insertion before rather than after the destination.
        if current_rows[-1] < new_row:
            new_row += 1

        # Remove selected rows...
        objects = []
        for row in current_rows:
            if row <= new_row:
                new_row -= 1
            obj = editor.adapter.get_item(editor.object, editor.name, row)
            objects.insert(0, obj)
            self.removeRow(row)

        # ...and add them at the new location.
        for i, obj in enumerate(objects):
            self.insertRow(new_row + i, obj=obj)

        # Update the selection for the new location.
        if editor.factory.multi_select:
            editor.setx(multi_selected = objects)
            editor.multi_selected_rows = range(new_row, new_row + len(objects))
        else:
            editor.setx(selected = objects[0])
            editor.selected_row = new_row
