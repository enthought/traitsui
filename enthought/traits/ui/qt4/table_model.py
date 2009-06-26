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

from PyQt4 import QtCore, QtGui

from enthought.traits.ui.ui_traits import SequenceTypes

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
    'bottom': QtCore.Qt.AlignRight,
}

#-------------------------------------------------------------------------------
#  'TableModel' class:
#-------------------------------------------------------------------------------

class TableModel(QtCore.QAbstractTableModel):
    """The model for table data."""

    def __init__(self, editor, parent=None):
        """Initialise the object."""

        QtCore.QAbstractTableModel.__init__(self, parent)

        self._editor = editor

    def data(self, mi, role):
        """Reimplemented to return the data."""

        obj = self._editor.items()[mi.row()]
        column = self._editor.columns[mi.column()]

        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            text = column.get_value(obj)
            if text is not None:
                return QtCore.QVariant(text)

        elif role == QtCore.Qt.ToolTipRole:
            tooltip = column.get_tooltip(obj)
            if tooltip:
                return QtCore.QVariant(tooltip)

        elif role == QtCore.Qt.FontRole:
            font = column.get_text_font(obj)
            if font is not None:
                return QtCore.QVariant(QtGui.QFont(font))

        elif role == QtCore.Qt.TextAlignmentRole:
            string = column.get_horizontal_alignment(obj)
            h_alignment = h_alignment_map.get(string, QtCore.Qt.AlignLeft)
            string = column.get_vertical_alignment(obj)
            v_alignment = v_alignment_map.get(string, QtCore.Qt.AlignVCenter)
            return QtCore.QVariant(h_alignment | v_alignment)

        elif role == QtCore.Qt.BackgroundRole:
            color = column.get_cell_color(obj)
            if color is not None:
                if isinstance(color, SequenceTypes):
                    q_color = QtGui.QColor(*color)
                else:
                    q_color = QtGui.QColor(color)
                return QtCore.QVariant(QtGui.QBrush(q_color))

        elif role == QtCore.Qt.ForegroundRole:
            color = column.get_text_color(obj)
            if color is not None:
                if isinstance(color, SequenceTypes):
                    q_color = QtGui.QColor(*color)
                else:
                    q_color = QtGui.QColor(color)
                return QtCore.QVariant(QtGui.QBrush(q_color))

        elif role == QtCore.Qt.UserRole:
            return QtCore.QVariant(obj)

        return QtCore.QVariant()

    def flags(self, mi):
        """Reimplemented to set editable status."""

        editor = self._editor
        obj = editor.items()[mi.row()]
        column = editor.columns[mi.column()]

        flags = QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled

        if editor.factory.editable and column.is_editable(obj):
            flags |= QtCore.Qt.ItemIsEditable

        return flags

    def headerData(self, section, orientation, role):
        """Reimplemented to return the header data."""

        if orientation != QtCore.Qt.Horizontal or role != QtCore.Qt.DisplayRole:
            return QtCore.QVariant()

        return QtCore.QVariant(self._editor.columns[section].get_label())

    def rowCount(self, mi):
        """Reimplemented to return the number of rows."""

        return len(self._editor.items())

    def columnCount(self, mi):
        """Reimplemented to return the number of columns."""

        return len(self._editor.columns)
