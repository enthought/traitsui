#------------------------------------------------------------------------------
#
#  Copyright (c) 2005, Enthought, Inc.
#  All rights reserved.
#  
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#  Thanks for using Enthought open source!
#  
#  Author: David C. Morrill
#  Date:   10/13/2004
#
#------------------------------------------------------------------------------

""" Defines the ThemedCellRenderer class used to render theme-based cells for 
    the TableEditor.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import wx

from wx.grid \
    import PyGridCellRenderer, GridCellStringRenderer

#-------------------------------------------------------------------------------
#  'ThemedCellRenderer' class:
#-------------------------------------------------------------------------------
        
class ThemedCellRenderer ( PyGridCellRenderer ):
    """ Defines the ThemedCellRenderer class used to render theme-based cells 
        for the TableEditor.
    """
    
    def __init__( self, column ):
        """ Creates a new ThemedCellRenderer.
        """
        PyGridCellRenderer.__init__( self )
        
        # We are merging the pyface grid GridCellRenderer interface with the
        # wx.grid.PyGridCellRenderer interface, so we need to do this:
        self.renderer = self
        
        # Save the reference to the TableColumn:
        self.column = column

    #-- pyface grid GridCellRenderer Method Overrides --------------------------

    # Invoked on left-button mouse clicks:
    def on_left_click ( self, grid, row, col ):
        return False

    # Invoked on left-button mouse double clicks:
    def on_left_dclick ( self, grid, row, col ):
        return False

    # Invoked on right-button mouse clicks:
    def on_right_click ( self, grid, row, col ):
        return False

    # Invoked on right-button mouse double clicks:
    def on_right_dclick ( self, grid, row, col ):
        return False

    # Invoked on a key press:
    def on_key ( self, grid, row, col, key_event ):
        return False

    # Clean-up:
    def dispose ( self ):
        del self.renderer
        del self.column
    
    #-- wx.GridCellRenderer Method Overrides -----------------------------------
    
    def Draw ( self, grid, attr, dc, rect, row, col, is_selected ):
        """ Draws the contents of the specified grid cell.
        """
        # Draw the appropriate theme background:
        theme = self.column.cell_theme
        if is_selected:
            theme = self.column.selected_theme or theme
            
        slice = theme.image_slice
        slice.fill( dc, rect.GetX(),     rect.GetY(), 
                        rect.GetWidth(), rect.GetHeight() )
                  
        # If no text to display, then we are done:
        text = grid.GetCellValue( row, col )
        if text == '':
            return

        # Get the draw bounds:
        x  = x0 = rect.GetX()
        y  = y0 = rect.GetY()
        dx =      rect.GetWidth()
        dy =      rect.GetHeight()
        
        # Get the text size:
        dc.SetFont( attr.GetFont() )
        tdx, tdy = dc.GetTextExtent( text )
        
        # Get the alignment and theme information:
        halign, valign = attr.GetAlignment()
        margins        = theme.margins
        ox, oy         = theme.offset

        # Calculate the x-coordinate of the text:
        left   = slice.xleft   + margins.left
        top    = slice.xtop    + margins.top
        right  = slice.xright  + margins.right
        bottom = slice.xbottom + margins.bottom
        if halign == wx.ALIGN_LEFT:
            x += left
        elif halign == wx.ALIGN_CENTRE:
            x += (left + ((dx - left - right - tdx) / 2))
        else:
            x += (dx - right - tdx)

        # Calculate the y-coordinate of the text:
        if valign == wx.ALIGN_TOP:
            y += top
        elif valign == wx.ALIGN_CENTRE:
            y += (top + ((dy - top - bottom - tdy) / 2))
        else:
            y += (dy - bottom - tdy)

        # Finally, draw the text:
        dc.SetBackgroundMode( wx.TRANSPARENT )
        dc.SetTextForeground( slice.text_color )
        dc.SetClippingRegion( x0 + left, y0 + top, 
                              dx - left - right, dy - top - bottom ) 
        dc.DrawText( text, x + ox, y + oy )
        dc.DestroyClippingRegion()

    def GetBestSize ( self, grid, attr, dc, row, col ):
        """ Determine best size for the cell. """

        # Get the text for this cell:
        text = grid.GetCellValue( row, col ) or 'My'
        
        # Now calculate and return the best size for the text:
        dc.SetFont( attr.GetFont() )
        tdx, tdy = dc.GetTextExtent( text )
        theme    = self.column.cell_theme
        margins  = theme.margins
        tdx     += (margins.left + margins.right)
        tdy     += (margins.top  + margins.bottom)
        slice    = theme.image_slice
            
        return wx.Size( max( slice.left  + slice.right,
                             slice.xleft + slice.xright  + tdx ),
                        max( slice.top   + slice.bottom,
                             slice.xtop  + slice.xbottom + tdy ) )

    def Clone ( self ):
        return self.__class__( self.column )
        
