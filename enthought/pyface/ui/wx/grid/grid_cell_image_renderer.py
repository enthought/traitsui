#------------------------------------------------------------------------------
# Copyright (c) 2005, Enthought, Inc.
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in enthought/LICENSE.txt and may be redistributed only
# under the conditions described in the aforementioned license.  The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
# Thanks for using Enthought open source!
#
# Author: Enthought, Inc.
# Description: <Enthought pyface package component>
#------------------------------------------------------------------------------
""" A renderer which will display a cell-specific image in addition to some
    text displayed in the same way the standard string renderer normally
    would. """

# Major package imports
import wx

from wx.grid import PyGridCellRenderer
from wx.grid import GridCellStringRenderer
from wx import SOLID, Brush, Rect, TRANSPARENT_PEN

class GridCellImageRenderer(PyGridCellRenderer):
    """ A renderer which will display a cell-specific image in addition to some
        text displayed in the same way the standard string renderer normally
        would. """

    def __init__(self, provider = None):
        """ Build a new PyGridCellImageRenderer.

            'provider', if provided, should implement
            get_image_for_cell(row, col) to specify an image to appear
            in the cell at row, col. """

        PyGridCellRenderer.__init__(self)

        # save the string renderer to use for text.
        self._string_renderer = GridCellStringRenderer()

        self._provider = provider

        return

    #########################################################################
    # GridCellRenderer interface.
    #########################################################################
    def Draw(self, grid, attr, dc, rect, row, col, isSelected):
        """ Draw the appropriate icon into the specified grid cell. """

        # clear the cell first
        if isSelected:
            bgcolor = grid.GetSelectionBackground()
        else:
            bgcolor = grid.GetCellBackgroundColour(row, col)

        dc.SetBackgroundMode(SOLID)
        dc.SetBrush(Brush(bgcolor, SOLID))
        dc.SetPen(TRANSPARENT_PEN)
        dc.DrawRectangle(rect.x, rect.y, rect.width, rect.height)

        # find the correct image for this cell
        bmp = self._get_image(grid, row, col)
        # find the correct text for this cell
        text = self._get_text(grid, row, col)

        # figure out placement -- we try to center things!
        # fixme: we should be responding to the horizontal/vertical
        #        alignment info in the attr object!
        size = self.GetBestSize(grid, attr, dc, row, col)

        halign, valign = attr.GetAlignment()

        # width first
        wdelta = rect.width - size.GetWidth()
        x = rect.x
        if halign == wx.ALIGN_CENTRE and wdelta > 0:
            x += wdelta / 2

        # now height
        hdelta = rect.height - size.GetHeight()

        y = rect.y
        if valign == wx.ALIGN_CENTRE and hdelta > 0:
            y += hdelta / 2

        dc.SetClippingRegion(*rect)

        if bmp is not None:
            # now draw our image into it
            dc.DrawBitmap(bmp, x, y, 1)
            x += bmp.GetWidth()

        if text is not None and text != '':
            width = rect.x + rect.width - x
            height = rect.y + rect.height - y
            # draw any text that should be included
            new_rect = Rect(x, y, width, height)
            self._string_renderer.Draw(grid, attr, dc, new_rect,
                                       row, col, isSelected)

        dc.DestroyClippingRegion()

        return

    def GetBestSize(self, grid, attr, dc, row, col):
        """ Determine best size for the cell. """

        # find the correct image
        bmp = self._get_image(grid, row, col)

        if bmp is not None:
            bmp_size = wx.Size(bmp.GetWidth(), bmp.GetHeight())
        else:
            bmp_size = wx.Size(0, 0)


        # find the correct text for this cell
        text = self._get_text(grid, row, col)

        if text is not None:
            text_size = self._string_renderer.GetBestSize(grid, attr, dc,
                                                          row, col)
        else:
            text_size = wx.Size(0, 0)

        result = wx.Size(bmp_size.width + text_size.width,
                         max(bmp_size.height, text_size.height))

        return result

    def Clone(self):
        return GridCellImageRenderer(self._provider)

    #########################################################################
    # protected 'GridCellIconRenderer' interface.
    #########################################################################
    def _get_image(self, grid, row, col):
        """ Returns the correct bmp for the data at row, col. """
        bmp = None
        if self._provider is not None and \
           hasattr(self._provider, 'get_image_for_cell'):
            # get the image from the specified provider
            img = self._provider.get_image_for_cell(grid, row, col)
            if img is not None:
                bmp = img.create_bitmap()
            else:
                bmp = None

        return bmp

    def _get_text(self, grid, row, col):
        """ Returns the correct text for the data at row, col. """

        text = None
        if self._provider is not None and \
           hasattr(self._provider, 'get_text_for_cell'):
            # get the image from the specified provider
            text = self._provider.get_text_for_cell(grid, row, col)
        else:
            text = grid.GetCellValue(row, col)

        return text

#### EOF ######################################################################

