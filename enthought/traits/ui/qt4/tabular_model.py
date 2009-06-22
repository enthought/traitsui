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

from PyQt4 import QtCore, QtGui

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

#-------------------------------------------------------------------------------
#  'TabularModel' class
#-------------------------------------------------------------------------------

class TabularModel(QtCore.QAbstractTableModel):
    """The model for tabular data."""

    def __init__(self, editor, parent=None):
        """Initialise the object."""

        QtCore.QAbstractTableModel.__init__(self, parent)

        self._editor = editor

    def data(self, mi, role):
        """ Reimplemented to return the data.
        """
        editor = self._editor
        adapter = editor.adapter
        obj, name = editor.object, editor.name
        row, column = mi.row(), mi.column()

        if role == QtCore.Qt.DisplayRole:
            return QtCore.QVariant(adapter.get_text(obj, name, row, column))

        elif role == QtCore.Qt.DecorationRole:
            image = editor._get_image(adapter.get_image(obj, name, row, column))
            if image is not None:
                return QtCore.QVariant(image)

        elif role == QtCore.Qt.ToolTipRole:
            return QtCore.QVariant(adapter.get_tooltip(obj, name, row, column))

        elif role == QtCore.Qt.FontRole:
            font = adapter.get_font(obj, name, row)
            if font is not None:
                return QtCore.QVariant(QtGui.QFont(font))

        elif role == QtCore.Qt.TextAlignmentRole:
            alignment = adapter.get_alignment(obj, name, column)
            return QtCore.QVariant(alignment_map.get(alignment, 
                                                     QtCore.Qt.AlignLeft))

        elif role == QtCore.Qt.BackgroundRole:
            color = adapter.get_bg_color(obj, name, row)
            if color is not None:
                return QtCore.QVariant(QtGui.QBrush(QtGui.QColor(color)))

        elif role == QtCore.Qt.ForegroundRole:
            color = adapter.get_text_color(obj, name, row)
            if color is not None:
                return QtCore.QVariant(QtGui.QBrush(QtGui.QColor(color)))

        return QtCore.QVariant()

    def setData(self, mi, value, role):
        """ Reimplmented to allow for modification for the object trait.
        """
        editor = self._editor
        obj, name = editor.object, editor.name
        row, column = mi.row(), mi.column()

        editor.adapter.set_text(obj, name, row, column, value.toString())
        signal = QtCore.SIGNAL('dataChanged(QModelIndex,QModelIndex)')
        self.emit(signal, mi, mi)
        return True

    def flags(self, mi):
        """ Reimplemented to set editable status.
        """
        editor = self._editor
        adapter = editor.adapter
        obj, name = editor.object, editor.name
        row, column = mi.row(), mi.column()

        flags = QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled

        if editor.factory.editable and adapter.get_can_edit(obj, name, row):
            flags |= QtCore.Qt.ItemIsEditable

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
