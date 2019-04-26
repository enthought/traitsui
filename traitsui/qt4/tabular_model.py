#-------------------------------------------------------------------------
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
#-------------------------------------------------------------------------

""" Defines the table model used by the tabular editor.
"""

#-------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------

from __future__ import absolute_import, unicode_literals

import six

from pyface.qt import QtCore, QtGui

from traitsui.ui_traits import SequenceTypes
from .clipboard import PyMimeData

#-------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------

# Mapping for trait alignment values to qt4 alignment values:
alignment_map = {
    'left': QtCore.Qt.AlignLeft,
    'right': QtCore.Qt.AlignRight,
    'center': QtCore.Qt.AlignHCenter,
    'justify': QtCore.Qt.AlignJustify
}

# MIME type for internal table drag/drop operations
tabular_mime_type = 'traits-ui-tabular-editor'

#-------------------------------------------------------------------------
#  'TabularModel' class:
#-------------------------------------------------------------------------


class TabularModel(QtCore.QAbstractTableModel):
    """ The model for tabular data."""

    def __init__(self, editor, parent=None):
        """ Initialise the object.
        """
        QtCore.QAbstractTableModel.__init__(self, parent)

        self._editor = editor

    #-------------------------------------------------------------------------
    #  QAbstractItemModel interface:
    #-------------------------------------------------------------------------

    def data(self, mi, role):
        """ Reimplemented to return the data.
        """
        editor = self._editor
        adapter = editor.adapter
        obj, name = editor.object, editor.name
        row, column = mi.row(), mi.column()

        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            return adapter.get_text(obj, name, row, column)

        elif role == QtCore.Qt.DecorationRole:
            image = editor._get_image(
                adapter.get_image(
                    obj, name, row, column))
            if image is not None:
                return image

        elif role == QtCore.Qt.ToolTipRole:
            tooltip = adapter.get_tooltip(obj, name, row, column)
            if tooltip:
                return tooltip

        elif role == QtCore.Qt.FontRole:
            font = adapter.get_font(obj, name, row, column)
            if font is not None:
                return QtGui.QFont(font)

        elif role == QtCore.Qt.TextAlignmentRole:
            string = adapter.get_alignment(obj, name, column)
            alignment = alignment_map.get(string, QtCore.Qt.AlignLeft)
            return int(alignment | QtCore.Qt.AlignVCenter)

        elif role == QtCore.Qt.BackgroundRole:
            color = adapter.get_bg_color(obj, name, row, column)
            if color is not None:
                if isinstance(color, SequenceTypes):
                    q_color = QtGui.QColor(*color)
                else:
                    q_color = QtGui.QColor(color)
                return QtGui.QBrush(q_color)

        elif role == QtCore.Qt.ForegroundRole:
            color = adapter.get_text_color(obj, name, row, column)
            if color is not None:
                if isinstance(color, SequenceTypes):
                    q_color = QtGui.QColor(*color)
                else:
                    q_color = QtGui.QColor(color)
                return QtGui.QBrush(q_color)

        return None

    def setData(self, mi, value, role):
        """ Reimplmented to allow for modification for the object trait.
        """
        if role != QtCore.Qt.EditRole:
            return False

        editor = self._editor
        obj, name = editor.object, editor.name
        row, column = mi.row(), mi.column()

        editor.adapter.set_text(obj, name, row, column, value)
        self.dataChanged.emit(mi, mi)
        return True

    def flags(self, mi):
        """ Reimplemented to set editable status and movable status.
        """
        editor = self._editor
        row = mi.row()
        column = mi.column()

        if not mi.isValid():
            return QtCore.Qt.ItemIsDropEnabled

        flags = QtCore.Qt.ItemIsEnabled
        if editor.factory.selectable:
            flags |= QtCore.Qt.ItemIsSelectable

        # If the adapter defines get_can_edit_cell(), use it to determine
        # editability over the row-wise get_can_edit().
        if (editor.factory.editable and 'edit' in editor.factory.operations and
                hasattr(editor.adapter, 'get_can_edit_cell')):
            if editor.adapter.get_can_edit_cell(editor.object, editor.name,
                                                row, column):
                flags |= QtCore.Qt.ItemIsEditable
        elif (editor.factory.editable and 'edit' in editor.factory.operations and
                editor.adapter.get_can_edit(editor.object, editor.name, row)):
            flags |= QtCore.Qt.ItemIsEditable

        if editor.adapter.get_drag(
                editor.object,
                editor.name,
                row) is not None:
            flags |= QtCore.Qt.ItemIsDragEnabled

        if editor.factory.editable:
            flags |= QtCore.Qt.ItemIsDropEnabled

        return flags

    def headerData(self, section, orientation, role):
        """ Reimplemented to return the header data.
        """
        if role != QtCore.Qt.DisplayRole:
            return None

        editor = self._editor

        label = None
        if orientation == QtCore.Qt.Vertical:
            label = editor.adapter.get_row_label(section, editor.object)
        elif orientation == QtCore.Qt.Horizontal:
            label = editor.adapter.get_label(section, editor.object)

        return label

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
        editor.callx(
            editor.adapter.insert,
            editor.object,
            editor.name,
            row,
            obj)
        self.endInsertRows()
        return True

    def insertRows(self, row, count, parent=QtCore.QModelIndex()):
        """ Reimplemented to allow creation of new items.
        """
        editor = self._editor
        adapter = editor.adapter

        self.beginInsertRows(parent, row, row + count - 1)
        for i in range(count):
            value = adapter.get_default_value(editor.object, editor.name)
            editor.callx(
                adapter.insert,
                editor.object,
                editor.name,
                row,
                value)
        self.endInsertRows()
        return True

    def removeRows(self, row, count, parent=QtCore.QModelIndex()):
        """ Reimplemented to allow row deletion, as well as reordering via drag
            and drop.
        """
        editor = self._editor
        adapter = editor.adapter
        self.beginRemoveRows(parent, row, row + count - 1)
        for i in range(count):
            editor.callx(adapter.delete, editor.object, editor.name, row)
        self.endRemoveRows()
        n = self.rowCount(None)
        if not editor.factory.multi_select:
            editor.selected_row = row if row < n else row - 1
        else:
            #FIXME: what should the selection be?
            editor.multi_selected_rows = []
        return True

    def mimeTypes(self):
        """ Reimplemented to expose our internal MIME type for drag and drop
            operations.
        """
        return [tabular_mime_type, PyMimeData.MIME_TYPE,
                PyMimeData.NOPICKLE_MIME_TYPE]

    def mimeData(self, indexes):
        """ Reimplemented to generate MIME data containing the rows of the
            current selection.
        """
        rows = sorted({index.row() for index in indexes})
        items = [self._editor.adapter.get_drag(
            self._editor.object, self._editor.name, row)
            for row in rows]
        mime_data = PyMimeData.coerce(items)
        data = QtCore.QByteArray(six.text_type(id(self)).encode('utf8'))
        for row in rows:
            data.append((' %i' % row).encode('utf8'))
        mime_data.setData(tabular_mime_type, data)
        return mime_data

    def dropMimeData(self, mime_data, action, row, column, parent):
        """ Reimplemented to allow items to be moved.
        """
        if action == QtCore.Qt.IgnoreAction:
            return False

        # this is a drag from a tabular model
        data = mime_data.data(tabular_mime_type)
        if not data.isNull() and action == QtCore.Qt.MoveAction:
            id_and_rows = [int(s) for s in data.data().decode('utf8').split(' ')]
            table_id = id_and_rows[0]
            # is it from ourself?
            if table_id == id(self):
                current_rows = id_and_rows[1:]
                self.moveRows(current_rows, parent.row())
                return True

        # this is an external drag
        data = PyMimeData.coerce(mime_data).instance()
        if data is not None:
            if not isinstance(data, list):
                data = [data]
            editor = self._editor
            object = editor.object
            name = editor.name
            adapter = editor.adapter
            if row == -1 and parent.isValid():
                # find correct row number
                row = parent.row()
            if row == -1 and adapter.len(object, name) == 0:
                # if empty list, target is after end of list
                row = 0
            if all(adapter.get_can_drop(object, name, row, item)
                   for item in data):
                for item in reversed(data):
                    self.dropItem(item, row)
                return True
        return False

    def supportedDropActions(self):
        """ Reimplemented to allow items to be moved.
        """
        return QtCore.Qt.MoveAction | QtCore.Qt.CopyAction

    #-------------------------------------------------------------------------
    #  TabularModel interface:
    #-------------------------------------------------------------------------

    def dropItem(self, item, row):
        """ Handle a Python object being dropped onto a row """
        editor = self._editor
        object = editor.object
        name = editor.name
        adapter = editor.adapter
        destination = adapter.get_dropped(object, name, row, item)

        if destination == 'after':
            row += 1

        adapter.insert(object, name, row, item)

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
            editor.setx(multi_selected=objects)
            editor.multi_selected_rows = list(range(new_row, new_row + len(objects)))
        else:
            editor.setx(selected=objects[0])
            editor.selected_row = new_row
