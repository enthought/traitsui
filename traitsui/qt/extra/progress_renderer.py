# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" A renderer which displays a progress bar. """

# System library imports
import sys
from pyface.qt import QtCore, QtGui

# ETS imports
from traitsui.qt.table_editor import TableDelegate


class ProgressRenderer(TableDelegate):
    """A renderer which displays a progress bar."""

    # -------------------------------------------------------------------------
    #  QAbstractItemDelegate interface
    # -------------------------------------------------------------------------

    def paint(self, painter, option, index):
        """Paint the progressbar."""
        # Get the column and object
        column = index.model()._editor.columns[index.column()]
        obj = index.data(QtCore.Qt.ItemDataRole.UserRole)

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
        if sys.platform == "darwin":
            # Save painter state, translate painter to cell location, and then
            # restore painter state after drawing to solve enthought/traitsui#964
            # This seems to be mac only.
            # ref: https://forum.qt.io/topic/105375/qitemdelegate-for-drawing-progress-bar-working-but-won-t-move-off-origin  # noqa: E501
            painter.save()
            painter.translate(option.rect.left(), option.rect.top())
            style.drawControl(
                QtGui.QStyle.ControlElement.CE_ProgressBar, progress_bar_option, painter
            )
            painter.restore()
        else:
            # For non-mac platforms, just draw.
            style.drawControl(
                QtGui.QStyle.ControlElement.CE_ProgressBar, progress_bar_option, painter
            )
