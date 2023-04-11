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


from pyface.qt import QtCore, QtGui

from traitsui.ui_traits import SequenceTypes


# MIME type for internal table drag/drop operations
mime_type = "traits-ui-list-str-editor"


class ListStrModel(QtCore.QAbstractListModel):
    """A model for lists of strings."""

    def __init__(self, editor, parent=None):
        """Initialise the object."""
        QtCore.QAbstractListModel.__init__(self, parent)

        self._editor = editor

    # -------------------------------------------------------------------------
    #  QAbstractItemModel interface:
    # -------------------------------------------------------------------------

    def rowCount(self, mi):
        """Reimplemented to return items in the list."""
        editor = self._editor
        n = editor.adapter.len(editor.object, editor.name)
        if editor.factory.auto_add:
            n += 1
        return n

    def data(self, mi, role):
        """Reimplemented to return the data."""
        editor = self._editor
        adapter = editor.adapter
        index = mi.row()

        if role == QtCore.Qt.ItemDataRole.DisplayRole or role == QtCore.Qt.ItemDataRole.EditRole:
            if editor.is_auto_add(index):
                text = adapter.get_default_text(editor.object, editor.name)
            else:
                text = adapter.get_text(editor.object, editor.name, index)
            if role == QtCore.Qt.ItemDataRole.DisplayRole and text == "":
                # FIXME: This is a hack to make empty strings editable.
                text = " "
            return text

        elif role == QtCore.Qt.ItemDataRole.DecorationRole:
            if editor.is_auto_add(index):
                image = adapter.get_default_image(editor.object, editor.name)
            else:
                image = adapter.get_image(editor.object, editor.name, index)
            image = editor.get_image(image)
            if image is not None:
                return image

        elif role == QtCore.Qt.ItemDataRole.ToolTipRole:
            tooltip = adapter.get_tooltip(editor.object, editor.name, index)
            if tooltip:
                return tooltip

        elif role == QtCore.Qt.ItemDataRole.BackgroundRole:
            if editor.is_auto_add(index):
                color = adapter.get_default_bg_color(
                    editor.object, editor.name
                )
            else:
                color = adapter.get_bg_color(editor.object, editor.name, index)
            if color is not None:
                if isinstance(color, SequenceTypes):
                    q_color = QtGui.QColor(*color)
                else:
                    q_color = QtGui.QColor(color)
                return QtGui.QBrush(q_color)

        elif role == QtCore.Qt.ItemDataRole.ForegroundRole:
            if editor.is_auto_add(index):
                color = adapter.get_default_text_color(
                    editor.object, editor.name
                )
            else:
                color = adapter.get_text_color(
                    editor.object, editor.name, index
                )
            if color is not None:
                if isinstance(color, SequenceTypes):
                    q_color = QtGui.QColor(*color)
                else:
                    q_color = QtGui.QColor(color)
                return QtGui.QBrush(q_color)

        return None

    def setData(self, mi, value, role):
        """Reimplmented to allow for modification of the object trait."""
        editor = self._editor
        if editor.is_auto_add(mi.row()):
            method = editor.adapter.insert
        else:
            method = editor.adapter.set_text
        editor.callx(method, editor.object, editor.name, mi.row(), value)
        self.dataChanged.emit(mi, mi)
        return True

    def setItemData(self, mi, roles):
        """Reimplmented to reject all setItemData calls."""
        # FIXME: This is a hack to prevent the QListView from clearing out the
        # old row after a move operation. (The QTableView doesn't do this, for
        # some reason). This behavior is not overridable so far as I can tell,
        # but there may be a better way around this issue. Note that we cannot
        # simply use a CopyAction instead because InternalMove mode is hardcoded
        # in the Qt source to allow only MoveActions.
        return False

    def flags(self, mi):
        """Reimplemented to set editable status and movable status."""
        editor = self._editor
        index = mi.row()

        flags = QtCore.Qt.ItemFlag.ItemIsSelectable | QtCore.Qt.ItemFlag.ItemIsEnabled

        if (
            editor.factory.editable
            and "edit" in editor.factory.operations
            and editor.adapter.get_can_edit(editor.object, editor.name, index)
        ):
            flags |= QtCore.Qt.ItemFlag.ItemIsEditable

        if (
            editor.factory.editable
            and "move" in editor.factory.operations
            and editor.adapter.get_drag(editor.object, editor.name, index)
            is not None
        ):
            flags |= QtCore.Qt.ItemFlag.ItemIsDragEnabled | QtCore.Qt.ItemFlag.ItemIsDropEnabled

        return flags

    def headerData(self, section, orientation, role):
        """Reimplemented to return title for vertical header data."""
        if (
            orientation != QtCore.Qt.Orientation.Horizontal
            or role != QtCore.Qt.ItemDataRole.DisplayRole
        ):
            return None

        return self._editor.title

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
        return True

    def mimeTypes(self):
        """Reimplemented to expose our internal MIME type for drag and drop
        operations.
        """
        return [mime_type]

    def mimeData(self, indexes):
        """Reimplemented to generate MIME data containing the rows of the
        current selection.
        """
        mime_data = QtCore.QMimeData()
        rows = list({index.row() for index in indexes})
        data = QtCore.QByteArray(str(rows[0]).encode("utf8"))
        for row in rows[1:]:
            data.append((" %i" % row).encode("utf8"))
        mime_data.setData(mime_type, data)
        return mime_data

    def dropMimeData(self, mime_data, action, row, column, parent):
        """Reimplemented to allow items to be moved."""
        if action == QtCore.Qt.DropAction.IgnoreAction:
            return False

        data = mime_data.data(mime_type)
        if data.isNull():
            return False

        current_rows = [int(s) for s in data.data().decode("utf8").split(" ")]
        self.moveRows(current_rows, parent.row())
        return True

    def supportedDropActions(self):
        """Reimplemented to allow items to be moved."""
        return QtCore.Qt.DropAction.MoveAction

    # -------------------------------------------------------------------------
    #  ListStrModel interface:
    # -------------------------------------------------------------------------

    def moveRow(self, old_row, new_row):
        """Convenience method to move a single row."""
        return self.moveRows([old_row], new_row)

    def moveRows(self, current_rows, new_row):
        """Moves a sequence of rows (provided as a list of row indexes) to a
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
            editor.multi_selected_indices = list(
                range(new_row, new_row + len(objects))
            )
        else:
            editor.setx(selected=objects[0])
            editor.selected_index = new_row
