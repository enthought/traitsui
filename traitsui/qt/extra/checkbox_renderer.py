# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" A renderer which displays a checked-box for a True value and an unchecked
    box for a false value.
"""

# System library imports
from pyface.qt import QtCore, QtGui

# ETS imports
from traitsui.qt.table_editor import TableDelegate


class CheckboxRenderer(TableDelegate):
    """A renderer which displays a checked-box for a True value and an
    unchecked box for a false value.
    """

    # -------------------------------------------------------------------------
    #  QAbstractItemDelegate interface
    # -------------------------------------------------------------------------

    def editorEvent(self, event, model, option, index):
        """Reimplemented to handle mouse button clicks."""
        if (
            event.type() == QtCore.QEvent.Type.MouseButtonRelease
            and event.button() == QtCore.Qt.MouseButton.LeftButton
        ):
            column = index.model()._editor.columns[index.column()]
            obj = index.data(QtCore.Qt.ItemDataRole.UserRole)
            checked = bool(column.get_raw_value(obj))
            column.set_value(obj, not checked)
            return True
        else:
            return False

    def paint(self, painter, option, index):
        """Reimplemented to paint the checkbox."""
        # Determine whether the checkbox is check or unchecked
        column = index.model()._editor.columns[index.column()]
        obj = index.data(QtCore.Qt.ItemDataRole.UserRole)
        checked = column.get_raw_value(obj)

        # First draw the background
        painter.save()
        row_brushes = [option.palette.base(), option.palette.alternateBase()]
        if option.state & QtGui.QStyle.StateFlag.State_Selected:
            if option.state & QtGui.QStyle.StateFlag.State_Active:
                color_group = QtGui.QPalette.ColorGroup.Active
            else:
                color_group = QtGui.QPalette.ColorGroup.Inactive
            bg_brush = option.palette.brush(
                color_group, QtGui.QPalette.ColorRole.Highlight
            )
        else:
            bg_brush = index.data(QtCore.Qt.ItemDataRole.BackgroundRole)
            if bg_brush == NotImplemented or bg_brush is None:
                if index.model()._editor.factory.alternate_bg_color:
                    bg_brush = row_brushes[index.row() % 2]
                else:
                    bg_brush = row_brushes[0]
        painter.fillRect(option.rect, bg_brush)

        # Then draw the checkbox
        style = QtGui.QApplication.instance().style()
        box = QtGui.QStyleOptionButton()
        box.palette = option.palette

        # Align the checkbox appropriately.
        box.rect = option.rect
        size = style.sizeFromContents(
            QtGui.QStyle.ContentsType.CT_CheckBox, box, QtCore.QSize(), None
        )
        box.rect.setWidth(size.width())
        margin = style.pixelMetric(QtGui.QStyle.PixelMetric.PM_ButtonMargin, box)
        alignment = column.horizontal_alignment
        if alignment == "left":
            box.rect.setLeft(option.rect.left() + margin)
        elif alignment == "right":
            box.rect.setLeft(option.rect.right() - size.width() - margin)
        else:
            # FIXME: I don't know why I need the 2 pixels, but I do.
            box.rect.setLeft(
                option.rect.left()
                + option.rect.width() // 2
                - size.width() // 2
                + margin
                - 2
            )

        # We mark the checkbox always active even when not selected, so
        # it's clear if it's ticked or not on OSX. See bug #439
        if option.state & QtGui.QStyle.StateFlag.State_Enabled:
            box.state = QtGui.QStyle.StateFlag.State_Enabled | QtGui.QStyle.StateFlag.State_Active

        if checked:
            box.state |= QtGui.QStyle.StateFlag.State_On
        else:
            box.state |= QtGui.QStyle.StateFlag.State_Off
        style.drawControl(QtGui.QStyle.ControlElement.CE_CheckBox, box, painter)
        painter.restore()

    def sizeHint(self, option, index):
        """Reimplemented to provide size hint based on a checkbox"""
        box = QtGui.QStyleOptionButton()
        style = QtGui.QApplication.instance().style()
        return style.sizeFromContents(
            QtGui.QStyle.ContentsType.CT_CheckBox, box, QtCore.QSize(), None
        )
