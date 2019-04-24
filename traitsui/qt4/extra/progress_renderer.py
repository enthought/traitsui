#------------------------------------------------------------------------------
# Copyright (c) 2016, Enthought, Inc.
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in enthought/LICENSE.txt and may be redistributed only
# under the conditions described in the aforementioned license.  The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
# Thanks for using Enthought open source!
#
# Author: Corran Webster
#------------------------------------------------------------------------------

""" A renderer which displays a progress bar. """

# System library imports
from __future__ import absolute_import
from pyface.qt import QtCore, QtGui

# ETS imports
from traitsui.qt4.table_editor import TableDelegate


class ProgressRenderer(TableDelegate):
    """ A renderer which displays a progress bar.
    """

    #-------------------------------------------------------------------------
    #  QAbstractItemDelegate interface
    #-------------------------------------------------------------------------

    def paint(self, painter, option, index):
        """ Paint the progressbar. """
        # Get the column and object
        column = index.model()._editor.columns[index.column()]
        obj = index.data(QtCore.Qt.UserRole)

        # set up progress bar options
        progress_bar_option = QtGui.QStyleOptionProgressBar()
        progress_bar_option.rect = option.rect
        progress_bar_option.minimum = column.get_minimum(obj)
        progress_bar_option.maximum = column.get_maximum(obj)
        progress_bar_option.progress = int(column.get_raw_value(obj))
        progress_bar_option.textVisible = column.get_text_visible()
        progress_bar_option.text = column.get_value(obj)

        # Draw it
        style = QtGui.QApplication.instance().style()
        style.drawControl(QtGui.QStyle.CE_ProgressBar, progress_bar_option,
                          painter)
