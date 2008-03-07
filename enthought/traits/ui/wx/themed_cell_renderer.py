#------------------------------------------------------------------------------
#
#  Copyright (c) 2005, Enthought, Inc.
#  All rights reserved.
#  
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
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
    
from enthought.traits.ui.ui_traits \
    import convert_bitmap

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
        # Get the model object this cell is being rendered for:
        model  = grid.grid.model
        object = model.get_filtered_item( row )
        
        # Get the draw bounds:
        x0 = x = rect.x
        y0 = y = rect.y
        dx = rect.width
        dy = rect.height
        
        # Draw the appropriate theme background:
        column = self.column
        if is_selected:
            theme = (column.get_selected_theme( object ) or
                     column.get_cell_theme(     object ))
        else:
            theme = column.get_cell_theme( object )
        
        # If no column theme is specified, try to get the global theme from the
        # model:
        if theme is None:
            if row & 1:
                theme = model.alt_theme or model.cell_theme
            else:
                theme = model.cell_theme
                
            if is_selected:
                theme = model.selected_theme or theme
                
        if theme is not None:
            content = theme.content
            slice   = theme.image_slice
            slice.fill( dc, x, y, dx, dy )
            
            # Set up the correct text color to use:
            dc.SetTextForeground( theme.content_color )
            
            # Calculate the margins for the draw area:
            left   = slice.xleft   + content.left
            top    = slice.xtop    + content.top
            right  = slice.xright  + content.right
            bottom = slice.xbottom + content.bottom
            ox, oy = theme.label.left, theme.label.top
        else:
            if is_selected:
                bg_color = grid.GetSelectionBackground()
            else:
                bg_color = attr.GetBackgroundColour()
        
            dc.SetBackgroundMode( wx.SOLID )
            dc.SetBrush( wx.Brush( bg_color, wx.SOLID ) )
            dc.SetPen( wx.TRANSPARENT_PEN )
            dc.DrawRectangle( x, y, dx, dy )
            
            # Set up the correct text color to use:
            dc.SetTextForeground( attr.GetTextColour() )
            
            # Calculate the margins for the draw area:
            left = right  = 4
            top  = bottom = 3
            ox   = oy     = 0
        
        # Get the optional image bitmap and text:
        bitmap = convert_bitmap( column.get_image( object ) )
        text   = grid.GetCellValue( row, col )
                  
        # If no text or bitmap to display, then we are done:
        if (bitmap is None) and (text == ''):
            return
            
        # Get the bitmap size:
        idx = idy = tdx = tdy = 0
        if bitmap is not None:
            idx = bitmap.GetWidth()
            idy = bitmap.GetHeight()
        
        # Get the text size:
        if text != '':
            dc.SetFont( attr.GetFont() )
            tdx, tdy = dc.GetTextExtent( text )
            
            # Get the spacing between text and image:
            if bitmap is not None:
                idx += 4
        
        # Get the alignment and theme information:
        halign, valign = attr.GetAlignment()

        # Calculate the x-coordinate of the image/text:
        if halign == wx.ALIGN_LEFT:
            x += left
        elif halign == wx.ALIGN_CENTRE:
            x += (left + ((dx - left - right - tdx - idx) / 2))
        else:
            x += (dx - right - tdx - idx)

        # Calculate the y-coordinate of the image/text:
        max_dy = max( tdy, idy )
        if valign == wx.ALIGN_TOP:
            y += top
        elif valign == wx.ALIGN_CENTRE:
            y += (top + ((dy - top - bottom - max_dy) / 2))
        else:
            y += (dy - bottom - max_dy)

        # Set up the clipping region to prevent drawing outside the margins:
        dc.SetClippingRegion( x0 + left, y0 + top, 
                              dx - left - right, dy - top - bottom ) 
            
        # Draw the image (if left or center aligned):
        if (bitmap is not None) and (halign != wx.ALIGN_RIGHT):
            dc.DrawBitmap( bitmap, x, y + ((max_dy - idy) / 2),  True )
            x += idx
            
        # Finally, draw the text:
        if text != '':
            dc.SetBackgroundMode( wx.TRANSPARENT )
            dc.DrawText( text, x + ox, y + oy )
            x += tdx + 4
            
        # Draw the image (if right-aligned):
        if (bitmap is not None) and (halign == wx.ALIGN_RIGHT):
            dc.DrawBitmap( bitmap, x, y + ((max_dy - idy) / 2),  True )
            
        # Discard the clipping region:
        dc.DestroyClippingRegion()

    def GetBestSize ( self, grid, attr, dc, row, col ):
        """ Determine best size for the cell. """
        # Get the model object this cell is being rendered for:
        object = grid.grid.model.get_filtered_item( row )

        # Get the text for this cell:
        text = grid.GetCellValue( row, col ) or 'My'
        
        # Now calculate and return the best size for the text and image:
        dc.SetFont( attr.GetFont() )
        tdx, tdy = dc.GetTextExtent( text )
        
        column = self.column
        bitmap = convert_bitmap( column.get_image( object ) )
        if bitmap is not None:
            tdx += (bitmap.GetWdth() + 4)
            tdy  = max( tdy, bitmap.GetHeight() )
            
        theme = column.get_cell_theme( object )
        if theme is None:
            return wx.Size( tdx + 8, tdy + 6 )
            
        content = theme.content
        tdx    += (content.left + content.right)
        tdy    += (content.top  + content.bottom)
        slice   = theme.image_slice
            
        return wx.Size( max( slice.left  + slice.right,
                             slice.xleft + slice.xright  + tdx ),
                        max( slice.top   + slice.bottom,
                             slice.xtop  + slice.xbottom + tdy ) )

    def Clone ( self ):
        return self.__class__( self.column )
        
