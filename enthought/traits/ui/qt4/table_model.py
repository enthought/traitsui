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
    'bottom': QtCore.Qt.AlignBottom,
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
        
        flags = QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled

        editor = self._editor
        items = editor.items()
        row, column = mi.row(), mi.column()
        if row >= len(items) or column >= len(editor.columns):
            return flags

        obj = items[row]
        column = editor.columns[column]
        if editor.factory.editable and column.is_editable(obj):
            flags |= QtCore.Qt.ItemIsEditable

        return flags

    def headerData(self, section, orientation, role):
        """Reimplemented to return the header data."""

        if orientation == QtCore.Qt.Horizontal:

            editor = self._editor
            column = editor.columns[section]

            if role == QtCore.Qt.DisplayRole:
                return QtCore.QVariant(column.get_label())

            elif role == QtCore.Qt.SizeHintRole and editor.factory:
                width = column.get_width()
                if width < 0:
                    if not editor.factory.show_column_labels:
                        return QtCore.QVariant(QtCore.QSize(0, 0))
                else:
                    if editor.factory.show_column_labels:
                        style = QtGui.QApplication.instance().style()
                        header = QtGui.QStyle.CT_HeaderSection
                        option = QtGui.QStyleOptionHeader()
                        size = style.sizeFromContents(header, option, 
                                                      QtCore.QSize(0, 0))
                        height = size.height()
                    else:
                        height = 0
                    return QtCore.QVariant(QtCore.QSize(width, height))

        elif orientation == QtCore.Qt.Vertical:
            
            if role == QtCore.Qt.DisplayRole:
                return QtCore.QVariant(QtCore.QString.number(section + 1))

        return QtCore.QVariant()

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

    def filterAcceptsRow(self, source_row, source_parent):
        """"Reimplemented to use a TableFilter for filtering rows."""

        if self._editor._filtered_cache is None:
            return True # Editor is initializing
        else:
            return self._editor._filtered_cache[source_row]

    def lessThan(self, left_mi, right_mi):
        """Reimplemented to sort according to the 'cmp' method defined for 
        TableColumn."""
        
        editor = self._editor
        column = editor.columns[left_mi.column()]
        items = editor.items()
        left, right = items[left_mi.row()], items[right_mi.row()]

        return column.cmp(left, right) < 0
