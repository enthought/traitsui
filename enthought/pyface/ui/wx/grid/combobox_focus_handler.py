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
""" Workaround for combobox focus problem in wx 2.6. """

# Major package imports
import wx

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Mapping from key code to key event handler names:
Handlers = {
    wx.WXK_LEFT:   '_left_key',
    wx.WXK_RIGHT:  '_right_key',
    wx.WXK_UP:     '_up_key',
    wx.WXK_DOWN:   '_down_key',
    wx.WXK_ESCAPE: '_escape_key'
}

#-------------------------------------------------------------------------------
#  'ComboboxFocusHandler' class:
#-------------------------------------------------------------------------------

class ComboboxFocusHandler(wx.EvtHandler):

    def __init__(self, grid):
        wx.EvtHandler.__init__(self)

        self._grid = grid
        wx.EVT_KEY_DOWN(self, self._on_key)

    def _on_key(self, evt):
        """ Called when a key is pressed. """
        getattr( self, Handlers.get( evt.GetKeyCode(), '_ignore_key' ))( evt )

#-- Key Event Handlers --------------------------------------------------------

    def _ignore_key ( self, evt ):
        evt.Skip()

    def _escape_key ( self, evt ):
        self._grid.DisableCellEditControl()

    def _left_key ( self, evt ):
        if not (evt.ControlDown() or evt.AltDown()):
            evt.Skip()
            return

        grid, row, col, rows, cols = self._grid_info()

        grid._no_reset_row = True

        first = True
        while first or (not self._edit_cell( row, col )):
            col -= 1
            if col < 0:
                col  = cols - 1
                row -= 1
                if row < 0:
                    if not first:
                        break

                    row = rows - 1

            first = False

    def _right_key ( self, evt ):
        if not (evt.ControlDown() or evt.AltDown()):
            evt.Skip()
            return

        grid, row, col, rows, cols = self._grid_info()

        grid._no_reset_row = True

        first = True
        while first or (not self._edit_cell( row, col )):
            col += 1
            if col >= cols:
                col  = 0
                row += 1
                if row >= rows:
                    if not first:
                        break

                    row = 0

            first = False

    def _up_key ( self, evt ):
        if not (evt.ControlDown() or evt.AltDown()):
            evt.Skip()
            return

        grid, row, col, rows, cols = self._grid_info()

        grid._no_reset_col = True

        row -= 1
        if row < 0:
            row = rows - 1

        self._edit_cell( row, col )

    def _down_key ( self, evt ):
        if not (evt.ControlDown() or evt.AltDown()):
            evt.Skip()
            return

        grid, row, col, rows, cols = self._grid_info()

        grid._no_reset_col = True

        row += 1
        if row >= rows:
            row = 0

        self._edit_cell( row, col )

#-- Private Methods -----------------------------------------------------------

    def _grid_info ( self ):
        g = self._grid
        return ( g, g.GetGridCursorRow(), g.GetGridCursorCol(),
                    g.GetNumberRows(),    g.GetNumberCols() )

    def _edit_cell ( self, row, col ):
        grid = self._grid
        grid.DisableCellEditControl()
        grid.SetGridCursor( row, col )
        if not grid.CanEnableCellControl():
            return False

        grid.EnableCellEditControl()
        grid.MakeCellVisible( row, col )

        return True

#### EOF ####################################################################
