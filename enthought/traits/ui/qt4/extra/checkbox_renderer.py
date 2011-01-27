#------------------------------------------------------------------------------
# Copyright (c) 2009, Enthought, Inc.
# All rights reserved.
# 
# This software is provided without warranty under the terms of the BSD
# license included in enthought/LICENSE.txt and may be redistributed only
# under the conditions described in the aforementioned license.  The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
# Thanks for using Enthought open source!
# 
# Author: Evan Patterson
# Date: 06/26/09
#------------------------------------------------------------------------------

""" A renderer which displays a checked-box for a True value and an unchecked
    box for a false value.
"""

# System library imports
from enthought.qt import QtCore, QtGui, qt_api

# ETS imports
from enthought.traits.ui.qt4.table_editor import TableDelegate


class CheckboxRenderer(TableDelegate):
    """ A renderer which displays a checked-box for a True value and an 
        unchecked box for a false value.
    """
    
    #---------------------------------------------------------------------------
    #  QAbstractItemDelegate interface
    #---------------------------------------------------------------------------

    def editorEvent(self, event, model, option, index):
        """ Reimplemented to handle mouse button clicks.
        """
        if event.type() == QtCore.QEvent.MouseButtonRelease and \
                event.button() == QtCore.Qt.LeftButton:
            column = index.model()._editor.columns[index.column()]
            if qt_api == 'pyqt':
                obj = index.data(QtCore.Qt.UserRole).toPyObject()
            else:
                obj = index.data(QtCore.Qt.UserRole)                
            checked = bool(column.get_raw_value(obj))
            column.set_value(obj, not checked)
            return True
        else:
            return False

    def paint(self, painter, option, index):
        """ Reimplemented to paint the checkbox.
        """
        # Determine whether the checkbox is check or unchecked
        column = index.model()._editor.columns[index.column()]
        if qt_api == 'pyqt':
            obj = index.data(QtCore.Qt.UserRole).toPyObject()
        else:
            obj = index.data(QtCore.Qt.UserRole)
        checked = column.get_raw_value(obj)

        # First draw the background
        painter.save()
        if option.state & QtGui.QStyle.State_Selected:
            bg_brush = option.palette.highlight()
        else:
            if qt_api == 'pyqt':
                bg_brush = index.data(QtCore.Qt.BackgroundRole).toPyObject()
            else:
                bg_brush = index.data(QtCore.Qt.BackgroundRole)
                
            if bg_brush == NotImplemented:
                bg_brush = option.palette.light()
        painter.fillRect(option.rect, bg_brush)

        # Then draw the checkbox
        box = QtGui.QStyleOptionButton()
        box.palette = option.palette
        box.rect = option.rect
        box.state = QtGui.QStyle.State_Enabled
        if checked:
            box.state |= QtGui.QStyle.State_On
        else:
            box.state |= QtGui.QStyle.State_Off
        style = QtGui.QApplication.instance().style()
        style.drawControl(QtGui.QStyle.CE_CheckBox, box, painter)
        painter.restore()

    def sizeHint(self, option, index):
        """ Reimplemented to provide size hint based on a checkbox
        """
        box = QtGui.QStyleOptionButton()
        style = QtGui.QApplication.instance().style()
        return style.sizeFromContents(QtGui.QStyle.CT_CheckBox, box, 
                                      QtCore.QSize())
