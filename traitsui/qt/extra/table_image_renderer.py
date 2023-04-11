# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" A renderer which will display a cell-specific image in addition to some
    text displayed in the same way the default renderer would.
"""

# System library imports
from pyface.qt import QtCore, QtGui

# ETS imports
from traits.api import Bool
from traitsui.qt.table_editor import TableDelegate


class TableImageRenderer(TableDelegate):
    """A renderer which will display a cell-specific image in addition to some
    text displayed in the same way the default renderer would.
    """

    #: Should the image be scaled to the size of the cell
    scale_to_cell = Bool(True)

    # -------------------------------------------------------------------------
    #  TableImageRenderer interface
    # -------------------------------------------------------------------------

    def get_image_for_obj(self, value, row, col):
        """Return the image for the cell given the raw cell value and the row
        and column numbers.
        """
        return None

    # -------------------------------------------------------------------------
    #  QAbstractItemDelegate interface
    # -------------------------------------------------------------------------

    def paint(self, painter, option, index):
        """Overriden to draw images."""
        # First draw any text/background by delegating to our superclass
        QtGui.QStyledItemDelegate.paint(self, painter, option, index)

        # Now draw the image, if possible
        value = index.data(QtCore.Qt.ItemDataRole.UserRole)
        image = self.get_image_for_obj(value, index.row(), index.column())
        if image:
            image = image.create_bitmap()
            if self.scale_to_cell:
                w = min(image.width(), option.rect.width())
                h = min(image.height(), option.rect.height())
            else:
                w = image.width()
                h = image.height()

            x = option.rect.x()
            y = option.rect.y() + (option.rect.height() - h) / 2

            target = QtCore.QRect(x, y, w, h)
            painter.drawPixmap(target, image)

    def sizeHint(self, option, index):
        """Overriden to take image size into account when providing a size
        hint.
        """
        size = QtGui.QStyledItemDelegate.sizeHint(self, option, index)

        value = index.data(QtCore.Qt.ItemDataRole.UserRole)
        image = self.get_image_for_obj(value, index.row(), index.column())
        if image:
            image = image.create_bitmap()
            size.setWidth(int(max(image.width(), size.width())))
            size.setHeight(int(max(image.height(), size.height())))

        return size
