#------------------------------------------------------------------------------
# Copyright (c) 2010, Enthought Inc
# All rights reserved.
# 
# This software is provided without warranty under the terms of the BSD license.

# 
# Author: Enthought Inc
# Description: <Enthought pyface code editor>
#------------------------------------------------------------------------------

import math

from PyQt4 import QtGui, QtCore


class GutterWidget(QtGui.QWidget):

    min_width = 5

    def sizeHint(self):
        return QtCore.QSize(self.min_width, 0)

    def paintEvent(self, event):
        """ Paint the line numbers.
        """
        painter = QtGui.QPainter(self)
        painter.fillRect(event.rect(), QtCore.Qt.lightGray)

    def wheelEvent(self, event):
        """ Delegate mouse wheel events to parent for seamless scrolling.
        """
        self.parent().wheelEvent(event)


class LineNumberWidget(GutterWidget):
    """ Draw line numbers.
    """

    min_char_width = 4

    def fontMetrics(self):
        # QWidget's fontMetrics method does not provide an up to date
        # font metrics, just one corresponding to the initial font
        return QtGui.QFontMetrics(self.font)

    def set_font(self, font):
        self.font = font

    def digits_width(self):
        nlines = max(1, self.parent().blockCount())
        ndigits = max(self.min_char_width,
                      int(math.floor(math.log10(nlines) + 1)))
        width = max(self.fontMetrics().width(u'0' * ndigits) + 3,
                    self.min_width)
        return width

    def sizeHint(self):
        return QtCore.QSize(self.digits_width(), 0)

    def paintEvent(self, event):
        """ Paint the line numbers.
        """
        painter = QtGui.QPainter(self)
        painter.setFont(self.font)
        painter.fillRect(event.rect(), QtCore.Qt.lightGray)
        
        cw = self.parent()
        block = cw.firstVisibleBlock()
        blocknum = block.blockNumber()
        top = cw.blockBoundingGeometry(block).translated(
            cw.contentOffset()).top()
        bottom = top + int(cw.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                painter.setPen(QtCore.Qt.black)
                painter.drawText(0, top, self.width() - 2,
                                 self.fontMetrics().height(),
                                 QtCore.Qt.AlignRight, str(blocknum + 1))
            block = block.next()
            top = bottom
            bottom = top + int(cw.blockBoundingRect(block).height())
            blocknum += 1
            
