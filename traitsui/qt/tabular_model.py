# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Defines the table model used by the tabular editor.
"""


import logging

from pyface.qt import QtCore, QtGui

from traitsui.ui_traits import SequenceTypes
from .clipboard import PyMimeData


# Mapping for trait alignment values to qt alignment values:
alignment_map = {
    "left": QtCore.Qt.AlignmentFlag.AlignLeft,
    "right": QtCore.Qt.AlignmentFlag.AlignRight,
    "center": QtCore.Qt.AlignmentFlag.AlignHCenter,
    "justify": QtCore.Qt.AlignmentFlag.AlignJustify,
}

# MIME type for internal table drag/drop operations
tabular_mime_type = "traits-ui-tabular-editor"

logger = logging.getLogger(__name__)


class TabularModel(QtCore.QAbstractTableModel):
    """The model for tabular data."""

    def __init__(self, editor, parent=None):
        """Initialise the object."""
        QtCore.QAbstractTableModel.__init__(self, parent)

        self._editor = editor

    # -------------------------------------------------------------------------
    #  QAbstractItemModel interface:
    # -------------------------------------------------------------------------

    def data(self, mi, role):
        """Reimplemented to return the data."""
        editor = self._editor
        adapter = editor.adapter
        obj, name = editor.object, editor.name
        row, column = mi.row(), mi.column()

        if role == QtCore.Qt.ItemDataRole.DisplayRole or role == QtCore.Qt.ItemDataRole.EditRole:
            return adapter.get_text(obj, name, row, column)

        elif role == QtCore.Qt.ItemDataRole.DecorationRole:
            image = editor._get_image(
                adapter.get_image(obj, name, row, column)
            )
            if image is not None:
                return image

        elif role == QtCore.Qt.ItemDataRole.ToolTipRole:
            tooltip = adapter.get_tooltip(obj, name, row, column)
            if tooltip:
                return tooltip

        elif role == QtCore.Qt.ItemDataRole.FontRole:
            font = adapter.get_font(obj, name, row, column)
            if font is not None:
                return QtGui.QFont(font)

        elif role == QtCore.Qt.ItemDataRole.TextAlignmentRole:
            string = adapter.get_alignment(obj, name, column)
            alignment = alignment_map.get(string, QtCore.Qt.AlignmentFlag.AlignLeft)
            return int(alignment | QtCore.Qt.AlignmentFlag.AlignVCenter)

        elif role == QtCore.Qt.ItemDataRole.BackgroundRole:
            color = adapter.get_bg_color(obj, name, row, column)
            if color is not None:
                if isinstance(color, SequenceTypes):
                    q_color = QtGui.QColor(*color)
                else:
                    q_color = QtGui.QColor(color)
                return QtGui.QBrush(q_color)

        elif role == QtCore.Qt.ItemDataRole.ForegroundRole:
            color = adapter.get_text_color(obj, name, row, column)
            if color is not None:
                if isinstance(color, SequenceTypes):
                    q_color = QtGui.QColor(*color)
                else:
                    q_color = QtGui.QColor(color)
                return QtGui.QBrush(q_color)

        return None

    def setData(self, mi, value, role):
        """Reimplmented to allow for modification for the object trait."""
        if role != QtCore.Qt.ItemDataRole.EditRole:
            return False

        editor = self._editor
        obj, name = editor.object, editor.name
        row, column = mi.row(), mi.column()

        editor.adapter.set_text(obj, name, row, column, value)
        self.dataChanged.emit(mi, mi)
        return True

    def flags(self, mi):
        """Reimplemented to set editable status and movable status."""
        editor = self._editor
        row = mi.row()
        column = mi.column()

        if not mi.isValid():
            return QtCore.Qt.ItemFlag.ItemIsDropEnabled

        flags = QtCore.Qt.ItemFlag.ItemIsEnabled
        if editor.factory.selectable:
            flags |= QtCore.Qt.ItemFlag.ItemIsSelectable

        # If the adapter defines get_can_edit_cell(), use it to determine
        # editability over the row-wise get_can_edit().
        if (
            editor.factory.editable
            and "edit" in editor.factory.operations
            and hasattr(editor.adapter, "get_can_edit_cell")
        ):
            if editor.adapter.get_can_edit_cell(
                editor.object, editor.name, row, column
            ):
                flags |= QtCore.Qt.ItemFlag.ItemIsEditable
        elif (
            editor.factory.editable
            and "edit" in editor.factory.operations
            and editor.adapter.get_can_edit(editor.object, editor.name, row)
        ):
            flags |= QtCore.Qt.ItemFlag.ItemIsEditable

        if (
            editor.adapter.get_drag(editor.object, editor.name, row)
            is not None
        ):
            flags |= QtCore.Qt.ItemFlag.ItemIsDragEnabled

        if editor.factory.editable:
            flags |= QtCore.Qt.ItemFlag.ItemIsDropEnabled

        return flags

    def headerData(self, section, orientation, role):
        """Reimplemented to return the header data."""
        if role != QtCore.Qt.ItemDataRole.DisplayRole:
            return None

        editor = self._editor

        label = None
        if orientation == QtCore.Qt.Orientation.Vertical:
            label = editor.adapter.get_row_label(section, editor.object)
        elif orientation == QtCore.Qt.Orientation.Horizontal:
            label = editor.adapter.get_label(section, editor.object)

        return label

    def rowCount(self, mi):
        """Reimplemented to return the number of rows."""
        editor = self._editor
        return editor.adapter.len(editor.object, editor.name)

    def columnCount(self, mi):
        """Reimplemented to return the number of columns."""
        editor = self._editor
        return len(editor.adapter.columns)

    def insertRow(self, row, parent=QtCore.QModelIndex(), obj=None):
        """Reimplemented to allow creation of new rows. Added an optional
        arg to allow the insertion of an existing row object.
        """
        editor = self._editor
        adapter = editor.adapter

        if obj is None:
            obj = adapter.get_default_value(editor.object, editor.name)
        self.beginInsertRows(parent, row, row)
        editor.callx(
            editor.adapter.insert, editor.object, editor.name, row, obj
        )
        self.endInsertRows()
        return True

    def insertRows(self, row, count, parent=QtCore.QModelIndex()):
        """Reimplemented to allow creation of new items."""
        editor = self._editor
        adapter = editor.adapter

        self.beginInsertRows(parent, row, row + count - 1)
        for i in range(count):
            value = adapter.get_default_value(editor.object, editor.name)
            editor.callx(
                adapter.insert, editor.object, editor.name, row, value
            )
        self.endInsertRows()
        return True

    def removeRows(self, row, count, parent=QtCore.QModelIndex()):
        """Reimplemented to allow row deletion, as well as reordering via drag
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
            # FIXME: what should the selection be?
            editor.multi_selected_rows = []
        return True

    def mimeTypes(self):
        """Reimplemented to expose our internal MIME type for drag and drop
        operations.
        """
        return [
            tabular_mime_type,
            PyMimeData.MIME_TYPE,
            PyMimeData.NOPICKLE_MIME_TYPE,
        ]

    def mimeData(self, indexes):
        """Reimplemented to generate MIME data containing the rows of the
        current selection.
        """
        rows = sorted({index.row() for index in indexes})
        items = [
            self._editor.adapter.get_drag(
                self._editor.object, self._editor.name, row
            )
            for row in rows
        ]
        mime_data = PyMimeData.coerce(items)
        data = QtCore.QByteArray(str(id(self)).encode("utf8"))
        for row in rows:
            data.append((" %i" % row).encode("utf8"))
        mime_data.setData(tabular_mime_type, data)
        return mime_data

    def dropMimeData(self, mime_data, action, row, column, parent):
        """Reimplemented to allow items to be moved."""
        if action == QtCore.Qt.DropAction.IgnoreAction:
            return False

        # If dropped directly onto the parent, both row and column are -1.
        # See https://doc.qt.io/qt-5/qabstractitemmodel.html#dropMimeData
        # When dropped below the list, the "parent" is invalid.
        if row == -1:
            if parent.isValid():
                row = parent.row()
            else:
                row = max(0, self.rowCount(None) - 1)

        # this is a drag from a tabular model
        data = mime_data.data(tabular_mime_type)
        if not data.isNull() and action == QtCore.Qt.DropAction.MoveAction:
            id_and_rows = [
                int(s) for s in data.data().decode("utf8").split(" ")
            ]
            table_id = id_and_rows[0]
            # is it from ourself?
            if table_id == id(self):
                current_rows = id_and_rows[1:]
                self.moveRows(current_rows, row)
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
            if all(
                adapter.get_can_drop(object, name, row, item) for item in data
            ):
                for item in reversed(data):
                    self.dropItem(item, row)
                return True
        return False

    def supportedDropActions(self):
        """Reimplemented to allow items to be moved."""
        return QtCore.Qt.DropAction.MoveAction | QtCore.Qt.DropAction.CopyAction

    # -------------------------------------------------------------------------
    #  TabularModel interface:
    # -------------------------------------------------------------------------

    def dropItem(self, item, row):
        """Handle a Python object being dropped onto a row"""
        editor = self._editor
        object = editor.object
        name = editor.name
        adapter = editor.adapter
        destination = adapter.get_dropped(object, name, row, item)

        if destination == "after":
            row += 1

        adapter.insert(object, name, row, item)

    def moveRow(self, old_row, new_row):
        """Convenience method to move a single row."""
        return self.moveRows([old_row], new_row)

    def moveRows(self, current_rows, new_row):
        """Moves a sequence of rows (provided as a list of row indexes) to a
        new row.
        """
        editor = self._editor

        if new_row == -1:
            # row should be nonnegative and less than the row count for this
            # model. See ``QAbstractItemModel.checkIndex``` for Qt 5.11+
            # This is a last resort to prevent segmentation faults.
            logger.debug(
                "Received invalid row %d. Adjusting to the last row.", new_row
            )
            new_row = max(0, self.rowCount(None) - 1)

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
            editor.multi_selected_rows = list(
                range(new_row, new_row + len(objects))
            )
        else:
            editor.setx(selected=objects[0])
            editor.selected_row = new_row
