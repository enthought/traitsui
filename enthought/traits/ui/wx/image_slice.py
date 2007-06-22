#-------------------------------------------------------------------------------
#  
#  Class to aid in automatically computing the 'slice' points for a specified
#  ImageResource and then drawing it that it can be 'stretched' to fit a larger
#  region than the original image.
#  
#  Written by: David C. Morrill
#  
#  Date: 06/06/2007
#  
#  Copyright 2007 by Enthought, Inc.
#  
#-------------------------------------------------------------------------------

""" Class to aid in automatically computing the 'slice' points for a specified
    ImageResource and then drawing it that it can be 'stretched' to fit a larger
    region than the original image.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import wx

from colorsys \
    import rgb_to_hls

from enthought.traits.api \
    import HasPrivateTraits, Instance, Str, Int, List, Bool, Color, Font, \
           Float, Enum

from enthought.pyface.image_resource \
    import ImageResource
    
from enthought.util.wx.do_later \
    import do_after
    
from constants \
    import WindowColor, ErrorColor
  
from numpy \
    import reshape, fromstring, uint8
    
#-------------------------------------------------------------------------------
#  Recursively paint the parent's background if they have an associated image 
#  slice.
#-------------------------------------------------------------------------------

def paint_parent ( dc, window, x, y ):
    """ Recursively paint the parent's background if they have an associated
        image slice.
    """
    parent = window.GetParent()
    slice  = getattr( parent, '_image_slice', None )
    if slice is not None:
        wx, wy = window.GetPositionTuple()
        x     += wx
        y     += wy
        paint_parent( dc, parent, x, y )
        dx, dy = parent.GetSizeTuple()
        slice.fill( dc, -x, -y, dx, dy )

    return slice
    
#-------------------------------------------------------------------------------
#  'ImageSlice' class:
#-------------------------------------------------------------------------------

class ImageSlice ( HasPrivateTraits ):
    
    #-- Trait Definitions ------------------------------------------------------
    
    # The ImageResource to be sliced and drawn:
    image = Instance( ImageResource )
    
    # The minimum number of adjacent, identical rows/columns needed to identify 
    # a repeatable section:
    threshold = Int( 10 )
    
    # Should transparent regions be left unchanged:
    transparent = Bool( False )
    
    # Orginal size of the current image:
    width  = Int
    height = Int
    
    # Width/height of the image borders:
    top    = Int
    bottom = Int
    left   = Int
    right  = Int
    
    # Width/height of the extended image borders:
    xtop    = Int
    xbottom = Int
    xleft   = Int
    xright  = Int
    
    # The color to use for overlaid text:
    text_color = Instance( wx.Colour )
    
    #-- Private Traits ---------------------------------------------------------
    
    # The current image's bitmap:
    bitmap = Instance( wx.Bitmap )
    
    # Size of the current image:
    dx = Int
    dy = Int
    
    # Size of the current image's slices:
    dxs = List
    dys = List
    
    # Fixed minimum size of current image:
    fdx = Int
    fdy = Int
    
    # The background color of the image:
    bg_color = Color
    
    #-- Public Methods ---------------------------------------------------------
    
    def fill ( self, dc, x, y, dx, dy ):
        """ 'Stretch fill' the specified region of a device context with the
            sliced image.
        """
        # Create the source image dc:
        idc = wx.MemoryDC()
        idc.SelectObject( self.bitmap )
        
        # Set up the drawing parameters:
        sdx, sdy = self.dx,  self.dy
        dxs, dys = self.dxs, self.dys
        tdx, tdy = dx - self.fdx, dy - self.fdy
        
        # Calculate vertical slice sizes to use for source and destination:
        n = len( dxs )
        if n == 1:
            pdxs = [ ( 0, 0 ), ( 1, max( 1, tdx/2 ) ), ( sdx - 2, sdx - 2 ),
                     ( 1, max( 1, tdx - (tdx/2) ) ), ( 0, 0 ) ]
        elif n == 3:
            pdxs = [ ( dxs[0], dxs[0] ), ( dxs[1], max( 0, tdx ) ), ( 0, 0 ),
                     ( 0, 0 ), ( dxs[2], dxs[2] ) ]
        else:
            pdxs = [ ( dxs[0], dxs[0] ), ( dxs[1], max( 0, tdx/2 ) ), 
                     ( dxs[2], dxs[2] ), ( dxs[3], max( 0, tdx - (tdx/2) ) ),
                     ( dxs[4], dxs[4] ) ]
                     
        # Calculate horizontal slice sizes to use for source and destination:
        n = len( dys )
        if n == 1:
            pdys = [ ( 0, 0 ), ( 1, max( 1, tdy/2 ) ), ( sdy - 2, sdy - 2 ), 
                     ( 1, max( 1, tdy - (tdy/2) ) ), ( 0, 0 ) ]
        elif n == 3:
            pdys = [ ( dys[0], dys[0] ), ( dys[1], max( 0, tdy ) ), ( 0, 0 ),
                     ( 0, 0 ), ( dys[2], dys[2] ) ]
        else:
            pdys = [ ( dys[0], dys[0] ), ( dys[1], max( 0, tdy/2 ) ), 
                     ( dys[2], dys[2] ), ( dys[3], max( 0, tdy - (tdy/2) ) ),
                     ( dys[4], dys[4] ) ]
          
        # Iterate over each cell, performing a stretch fill from the source 
        # image to the destination window:
        last_x, last_y = x + dx, y + dy
        iy = 0
        for idy, wdy in pdys:
            if y >= last_y:
                break
                
            if wdy != 0:
                x0, ix0 = x, 0
                for idx, wdx in pdxs:
                    if x0 >= last_x:
                        break
                        
                    if wdx != 0:
                        self._fill( idc, ix0, iy, idx, idy, 
                                    dc,  x0,  y,  wdx, wdy )
                        x0 += wdx
                    ix0 += idx
                y += wdy
            iy += idy
    
    #-- Event Handlers ---------------------------------------------------------
    
    def _image_changed ( self ):
        """ Handles the 'image' trait being changed.
        """
        image = self.image.create_image()
        self.width, self.height = image.GetWidth(), image.GetHeight()
        self._analyze_bitmap( image.ConvertToBitmap() )
        
    #-- Private Methods --------------------------------------------------------
    
    def _analyze_bitmap ( self, bitmap ):
        """ Analyzes a specified bitmap.
        """
        # Get the image data:
        threshold = self.threshold
        self.dy   = dy = bitmap.GetHeight()
        self.dx   = dx = bitmap.GetWidth()
        
        # Create a new bitmap using the default window background color:
        if self.transparent:
            self.bitmap = bitmap
        else:
            self.bitmap = wx.EmptyBitmap( dx, dy )
            mdc2        = wx.MemoryDC()
            mdc2.SelectObject( self.bitmap )
            mdc2.SetBrush( wx.Brush( WindowColor ) )
            mdc2.SetPen( wx.TRANSPARENT_PEN )
            mdc2.DrawRectangle( 0, 0, dx, dy )
            mdc = wx.MemoryDC()
            mdc.SelectObject( bitmap )
            mdc2.Blit( 0, 0, dx, dy, mdc, 0, 0, useMask = True )
            mdc2.SelectObject( wx.NullBitmap )
            
        image = self.bitmap.ConvertToImage()
        
        # Convert the bitmap data to a numpy array for analysis:
        data = reshape( fromstring( image.GetData(), uint8 ), 
                               ( dy, dx, 3 ) )
                               
        # Assume we will not have to regenerate the bitmap (for speed):
        regen = False
                             
        # Find the horizontal slices:
        matches  = []
        y, last  = 0, dy - 1
        max_diff = 0.10 * dx
        while y < last:
            y_data = data[y]
            for y2 in xrange( y + 1, dy ):
                if abs( y_data - data[y2] ).sum() > max_diff:
                    break
                    
            n = y2 - y
            if n >= threshold:
                matches.append( ( y, n ) )
                
            y = y2
           
        n = len( matches )
        if n == 0:
            regen   = True
            matches = [ ( dy / 2, 1 ) ]
        elif n > 2:
            matches.sort( lambda l, r: cmp( r[1], l[1] ) )
            matches = matches[:2]
            
        # Calculate and save the horizontal slice sizes:
        self.fdy, self.dys = self._calculate_dxy( dy, matches )
            
        # Find the vertical slices:
        matches  = []
        x, last  = 0, dx - 1
        max_diff = 0.10 * dy
        while x < last:
            x_data = data[:,x]
            for x2 in xrange( x + 1, dx ):
                if abs( x_data - data[:,x2] ).sum() > max_diff:
                    break
                    
            n = x2 - x
            if n >= threshold:
                matches.append( ( x, n ) )
                
            x = x2
            
        n = len( matches )
        if n == 0:
            regen   = True
            matches = [ ( dx / 2, 1 ) ]
        elif n > 2:
            matches.sort( lambda l, r: cmp( r[1], l[1] ) )
            matches = matches[:2]
         
        # Calculate and save the vertical slice sizes:
        self.fdx, self.dxs = self._calculate_dxy( dx, matches )
        
        # Check if we have to regenerate the bitmap:
        # fixme: We can't do a 'regen' for a transparent bitmap because we are
        # not able to regenerate the associated wx.Mask for the bitmap
        # correctly (yet).
        if regen and (not self.transparent):
            # Create a bigger version of the bitmap, so that the repeatable
            # sections are larger (faster Blits):
            ndx, ndy = dx + 2 * threshold, dy + 2 * threshold
            bitmap   = wx.EmptyBitmap( ndx, ndy )
            mdc      = wx.MemoryDC()
            mdc.SelectObject( bitmap )
            self.fill( mdc, 0, 0, ndx, ndy )
            mdc.SelectObject( wx.NullBitmap )
            
            # Re-analyze the new bitmap:
            self._analyze_bitmap( bitmap )
        else:
            self.top    = min( dy / 2, self.dys[0] )
            self.bottom = min( dy / 2, self.dys[-1] )
            self.left   = min( dx / 2, self.dxs[0] )
            self.right  = min( dx / 2, self.dxs[-1] )
            
            self._find_best_borders( data )

            # Save the background color:            
            r, g, b       = data[ dy / 2, dx / 2 ]
            self.bg_color = (0x10000 * r) + (0x100 * g) + b
            
            # Find the best contrasting text color (black or white):
            h, l, s = rgb_to_hls( r / 255.0, g / 255.0, b / 255.0 )
            self.text_color = wx.BLACK
            if l < 0.50:
                self.text_color = wx.WHITE
    
    def _fill ( self, idc, ix, iy, idx, idy, dc, x, y, dx, dy ):
        """ Performs a stretch fill of a region of an image into a region of a
            window device context.
        """
        last_x, last_y = x + dx, y + dy
        while y < last_y:
            ddy = min( idy, last_y - y )
            x0  = x
            while x0 < last_x:
                ddx = min( idx, last_x - x0 )
                dc.Blit( x0, y, ddx, ddy, idc, ix, iy, useMask = True )
                x0 += ddx
            y += ddy
    
    def _calculate_dxy ( self, d, matches ):
        """ Calculate the size of all image slices for a specified set of 
            matches.
        """
        if len( matches ) == 1:
            d1, d2 = matches[0]
            
            return ( d - d2, [ d1, d2, d - d1 - d2 ] )
            
        d1, d2 = matches[0]
        d3, d4 = matches[1]
        
        return ( d - d2 - d4, [ d1, d2, d3 - d1 - d2, d4, d - d3 - d4 ] )
        
    def _find_best_borders ( self, data ):
        """ Find the best set of image slice border sizes (e.g. for images with
            rounded corners, there should exist a better set of borders than
            the ones computed by the image slice algorithm.
        """
        # Make sure the image size is worth bothering about:
        dx, dy = self.dx, self.dy
        if (dx < 5) or (dy < 5):
            return
            
        # Calculate the starting point:
        left = right  = dx / 2
        top  = bottom = dy / 2
        
        # Calculate the end points:
        last_y = dy - 1
        last_x = dx - 1
        
        # Mark which edges as 'scanning':
        # Note, we currently only scan up and down because it seems to produce
        # more eye-pleasing results with rounded corners.
        t = b = True
        l = r = False
        
        # Keep looping while at last one edge is still 'scanning':
        while l or r or t or b:
            
            # Calculate the current core area size:
            height = bottom - top + 1
            width  = right - left + 1
            
            # Try to extend all edges that are still 'scanning':
            nl = (l and (left > 0) and
                  self._is_equal( data, left - 1, top, left, top, 1, height ))
                
            nr = (r and (right < last_x) and
                  self._is_equal( data, right + 1, top, right, top, 1, height ))
                
            nt = (t and (top > 0) and
                 self._is_equal( data, left, top - 1, left, top, width, 1 ))
                
            nb = (b and (bottom < last_y) and
                  self._is_equal( data, left, bottom + 1, left, bottom, 
                                  width, 1 ))
                
            # Now check the corners of the edges:
            tl = ((not nl) or (not nt) or
                  self._is_equal( data, left - 1, top - 1, left, top, 1, 1 ))
                  
            tr = ((not nr) or (not nt) or
                  self._is_equal( data, right + 1, top - 1, right, top, 1, 1 ))
                  
            bl = ((not nl) or (not nb) or
                  self._is_equal( data, left - 1, bottom + 1, left, bottom,
                                  1, 1 ))
                  
            br = ((not nr) or (not nb) or
                  self._is_equal( data, right + 1, bottom + 1, right, bottom,
                                  1, 1 ))
            
            # Calculate the new edge 'scanning' values:
            l = nl and tl and bl
            r = nr and tr and br
            t = nt and tl and tr
            b = nb and bl and br
            
            # Adjust the coordinate of an edge if it is still 'scanning':
            left   -= l
            right  += r
            top    -= t
            bottom += b
                
        # Now compute the best set of image border sizes using the current set
        # and the ones we just calculated:
        self.xleft   = min( self.left,   left )
        self.xright  = min( self.right,  dx - right - 1 )
        self.xtop    = min( self.top,    top )
        self.xbottom = min( self.bottom, dy - bottom - 1 )
        
    def _is_equal ( self, data, x0, y0, x1, y1, dx, dy ):
        """ Determines if two identically sized regions of an image array are
            'the same' (i.e. within some slight color variance of each other).
        """
        return (abs( data[ y0: y0 + dy, x0: x0 + dx ] - 
                     data[ y1: y1 + dy, x1: x1 + dx ] ).sum() < 0.10 * dx * dy)
                     
# Define a reusable, default ImageSlice object:
default_image_slice = ImageSlice()

#-------------------------------------------------------------------------------
#  'StaticText' class:  
#-------------------------------------------------------------------------------    
                      
class StaticText ( wx.StaticText ):
    """ Draws a static text control that is compatible with the operation of 
        an ImageSlice (i.e. paints background using the associated ImageSlice).
    """
    
    def __init__ ( self, *args, **kw ):
        """ Initializes the object.
        """
        super( StaticText, self ).__init__( *args, **kw )
        
        # Set up the event handlers we need to override:
        wx.EVT_ERASE_BACKGROUND( self, self._erase_background )
        wx.EVT_PAINT( self, self._on_paint )
            
    def _erase_background ( self, event ):
        """ Do not erase the background here (do it in the 'on_paint' handler).
        """
        pass
           
    def _on_paint ( self, event ):
        """ Paints the static text after first filling the background the the
            parent object's ImageSlice object.
        """
        # Fill the background using the parent's ImageSlice object:
        dc    = wx.PaintDC( self )
        slice = paint_parent( dc, self, 0, 0 )
        
        # Now draw the text over it:
        dc.SetBackgroundMode( wx.TRANSPARENT )
        dc.SetTextForeground( slice.text_color )
        dc.SetFont( wx.SystemSettings_GetFont( wx.SYS_DEFAULT_GUI_FONT ) )
        dc.DrawText( self.GetLabel(), 0, 0 )

#-------------------------------------------------------------------------------
#  'ImagePanel' class:  
#-------------------------------------------------------------------------------    
                      
class ImagePanel ( wx.Panel ):
    
    def __init__ ( self, parent, image_slice ):
        """ Defines a panel whose background is defined by an ImageSlice object.
        """
        
        super( ImagePanel, self ).__init__( parent, -1, 
                                            style = wx.TAB_TRAVERSAL | 
                                                    wx.FULL_REPAINT_ON_RESIZE )
                                                    
        # Save the ImageSlice object we will use to paint the background:
        self._image_slice = image_slice
        
        # Set up the painting event handlers:
        wx.EVT_ERASE_BACKGROUND( self, self._erase_background )
        wx.EVT_PAINT( self, self._on_paint )
        
    def GetAdjustedSize ( self ):
        """ Returns the adjusted size of the panel taking into account the
            size of its current children and the image border.
        """
        dx, dy = 0, 0
        for control in self.GetChildren():
            dx, dy = control.GetSizeTuple()
            
        slice = self._image_slice
        sizer = self.GetSizer()
        size  = wx.Size( dx + min( slice.left, slice.xleft )   + 
                              min( slice.right, slice.xright ) + 
                              sizer._left_padding + sizer._right_padding,
                         dy + min( slice.top, slice.xtop )       +
                              min( slice.bottom, slice.xbottom ) +
                              sizer._top_padding + sizer._bottom_padding )
        self.SetSize( size )
        
        return size
            
    def _erase_background ( self, event ):
        """ Do not erase the background here (do it in the 'on_paint' handler).
        """
        pass
           
    def _on_paint ( self, event ):
        """ Paint the background using the associated ImageSlice object.
        """
        dc = wx.PaintDC( self )
        paint_parent( dc, self, 0, 0 )
        wdx, wdy = self.GetSizeTuple()
        self._image_slice.fill( dc, 0, 0, wdx, wdy )
            
#-------------------------------------------------------------------------------
#  'ImageSizer' class:
#-------------------------------------------------------------------------------

class ImageSizer ( wx.PySizer ):
    """ Defines a sizer that correctly sizes a window's children to fit within
        the borders implicitly defined by a background ImageSlice object,
    """

    #---------------------------------------------------------------------------
    #  Initializes the object:
    #---------------------------------------------------------------------------

    def __init__ ( self, image_slice, top_padding = 0, bottom_padding = 0,
                         left_padding = 0, right_padding = 0):
        """ Initializes the object.
        """
        super( ImageSizer, self ).__init__()
        
        # Save the ImageSlice object which determines the inset border size:
        self._image_slice = image_slice
        
        # Save the padding information:
        self._top_padding    = top_padding
        self._bottom_padding = bottom_padding
        self._left_padding   = left_padding
        self._right_padding  = right_padding

    #---------------------------------------------------------------------------
    #  Calculates the minimum size needed by the sizer:
    #---------------------------------------------------------------------------

    def CalcMin ( self ):
        """ Calculates the minimum size of the control by adding its contents
            minimum size to the ImageSlice object's border size.
        """
        dx, dy = 0, 0
        for item in self.GetChildren():
            if item.IsSizer():
                dx, dy = item.GetSizer().CalcMin()
            else:
                dx, dy = item.GetWindow().GetBestSize()
                
        slice = self._image_slice
        
        return wx.Size( max( slice.left + slice.right,
                             slice.xleft + slice.xright + 
                             self._left_padding + self._right_padding + dx ),
                        max( slice.top + slice.bottom,
                             slice.xtop + slice.xbottom + 
                             self._top_padding + self._bottom_padding + dy ) )

    #---------------------------------------------------------------------------
    #  Layout the contents of the sizer based on the sizer's current size and
    #  position:
    #---------------------------------------------------------------------------

    def RecalcSizes ( self ):
        """ Layout the contents of the sizer based on the sizer's current size
            and position.
        """
        x,   y = self.GetPositionTuple()
        dx, dy = self.GetSizeTuple()
        slice  = self._image_slice
        left   = slice.xleft + self._left_padding
        top    = slice.xtop  + self._top_padding
        ix, iy, idx, idy = ( x + left, 
                             y + top,
                             dx - left - slice.xright  - self._right_padding,
                             dy - top  - slice.xbottom - self._bottom_padding )
                         
        for item in self.GetChildren():
            if item.IsSizer():
                item.GetSizer().SetDimension( ix, iy, idx, idy )
            else:
                item.GetWindow().SetDimensions( ix, iy, idx, idy )

#-------------------------------------------------------------------------------
#  Class 'ImageText'  
#-------------------------------------------------------------------------------

class ImageText ( wx.Window ):
    """ Defines a text control that displays an ImageSlice in its background.
    """
    
    alignment_map = {
        'left':   0,
        'center': 1,
        'right':  2
    }
    
    def __init__ ( self, parent, image, text = '', alignment = 'center' ):
        """ Initializes the object.
        """
        self._image_slice = None
        if image is not None:
            self._image_slice = ImageSlice( transparent = True ).set(
                                            image       = image )
                                            
        super( ImageText, self ).__init__( parent, -1, 
                                           style = wx.FULL_REPAINT_ON_RESIZE )
                                           
        self._alignment = self.alignment_map.get( alignment, 1 )
        self._text_size = self._fill = None  
        self.SetLabel( text )
        
        # Set up the painting event handlers:
        wx.EVT_ERASE_BACKGROUND( self, self._erase_background )
        wx.EVT_PAINT( self, self._on_paint )
        
        size = self.GetMinSize()
        self.SetMinSize( size )
        self.SetSize( size )
            
    def _erase_background ( self, event ):
        """ Do not erase the background here (do it in the 'on_paint' handler).
        """
        pass
           
    def _on_paint ( self, event ):
        """ Paint the background using the associated ImageSlice object.
        """
        dc = wx.PaintDC( self )
        if self._fill is not False:
            slice = paint_parent( dc, self, 0, 0 )
            
        self._fill = True
        wdx, wdy   = self.GetClientSizeTuple()
        text       = self.GetLabel()
        if self._image_slice is not None:
            slice = self._image_slice
            slice.fill( dc, 0, 0, wdx, wdy )
        dc.SetBackgroundMode( wx.TRANSPARENT )
        dc.SetTextForeground( slice.text_color )
        dc.SetFont( self.GetFont() )
        tx, ty, tdx, tdy = self._get_text_bounds()
        dc.DrawText( text, tx, ty )
         
    def GetMinSize ( self ):
        """ Returns the minimum size for the window.
        """
        tdx, tdy, descent, leading = self._get_text_size()
        
        slice = self._image_slice
        if slice is None:
            return wx.Size( tdx, tdy )
        
        return wx.Size( max( slice.left  + slice.right,
                             slice.xleft + slice.xright  + tdx + 8 ),
                        max( slice.top   + slice.bottom,
                             slice.xtop  + slice.xbottom + tdy + 4 ) )
                        
    def SetFont ( self, font ):
        """ Set the window font.
        """
        super( ImageText, self ).SetFont( font )
        
        self._refresh()
                        
    def SetLabel ( self, label ):
        """ Set the window label.
        """
        super( ImageText, self ).SetLabel( label )
        
        self._refresh()

    def _refresh ( self ):
        """ Refreshes the contents of the control.
        """
        if self._fill is True:
            self._fill = (self._image_slice is None)
        
        if self._text_size is not None:
            self.RefreshRect( wx.Rect( *self._get_text_bounds() ), False )
            self._text_size = None
            
        self.SetMinSize( self.GetMinSize() )
        self.RefreshRect( wx.Rect( *self._get_text_bounds() ), False )
        
    def _get_text_size ( self, text = None ):
        """ Returns the text size information for the window.
        """
        if self._text_size is None:
            if text is None:
                text = self.GetLabel()
                
            if text.strip() == '':
                text = 'M'
                
            self._text_size = self.GetFullTextExtent( text )
            
        return self._text_size

    def _get_text_bounds ( self ):
        """ Get the window bounds of where the current text should be
            displayed.
        """
        tdx, tdy, descent, leading = self._get_text_size()
        wdx, wdy = self.GetClientSizeTuple()
        slice    = self._image_slice or default_image_slice
        ady      = wdy - slice.xtop  - slice.xbottom
        ty       = slice.xtop  + ((ady - (tdy - descent)) / 2) - 1
        if self._alignment == 0:
            tx = slice.xleft + 4
        elif self._alignment == 1:
            adx = wdx - slice.xleft - slice.xright
            tx  = slice.xleft + (adx - tdx) / 2
        else:
            tx = wdx - tdx - slice.xright - 4
            
        return ( tx, ty, tdx, tdy )

#-------------------------------------------------------------------------------
#  Class 'ImageSlider'  
#-------------------------------------------------------------------------------

class ImageSlider ( HasPrivateTraits ):
    """ Defines a slider control that displays an ImageSlice in its background.
    """
    
    # The low end of the slider range:
    low = Float
    
    # The high end of the slider range:
    high = Float
    
    # The smallest allowed increment:
    increment = Float
    
    # The current value:
    value = Float
    
    # Should the current value be displayed as text?
    show_value = Bool( True )
    
    # The alignment of the text within the slider:
    alignment = Enum( 'center', 'left', 'right' )
    
    # The color to use for the slider bar:
    slider_color = Color( 0xC0C0C0 )
    
    # The background color for the slider:
    bg_color = Color( 'white' )
    
    # The color of the slider tip:
    tip_color = Color( 0xFF7300 )
    
    # The color to use for the value text:
    text_color = Color( 'black' )
    
    #-- Private Traits ---------------------------------------------------------
    
    # The wxPython controlfor this object:
    control = Instance( wx.Window )
    
    # The current text being displayed:
    text = Str
    
    #-- Public Methods ---------------------------------------------------------
    
    def create_control ( self, parent ):
        """ Creates the underlying wx.Window for the object.
        """
        self.control = control = wx.Window( parent, -1,
                                            size  = wx.Size( 100, 20 ),
                                            style = wx.FULL_REPAINT_ON_RESIZE |
                                                    wx.TAB_TRAVERSAL )
                                           
        # Set up the painting event handlers:
        wx.EVT_ERASE_BACKGROUND( control, self._erase_background )
        wx.EVT_PAINT( control, self._on_paint )
        wx.EVT_SET_FOCUS( control, self._set_focus )
        
        # Set up mouse event handlers:
        wx.EVT_LEFT_DOWN( control, self._left_down )
        wx.EVT_LEFT_UP(   control, self._left_up )
        wx.EVT_MOTION(    control, self._mouse_move )
        
        # Make sure the text value gets initialized:
        self._value_changed()
        
        return control
        
    #-- Private Methods --------------------------------------------------------

    def _get_text_bounds ( self ):
        """ Get the window bounds of where the current text should be
            displayed.
        """
        tdx, tdy, descent, leading = self._get_text_size()
        wdx, wdy = self.control.GetClientSizeTuple()
        ty       = ((wdy - (tdy - descent)) / 2) - 2
        if self.alignment == 'left':
            tx = 4
        elif self.alignment == 'center':
            tx = (wdx - tdx) / 2
        else:
            tx = wdx - tdx - 4
            
        return ( tx, ty, tdx, tdy )
        
    def _get_text_size ( self ):
        """ Returns the text size information for the window.
        """
        if self._text_size is None:
            self._text_size = self.control.GetFullTextExtent( 
                                               self.text.strip() or 'M' )
            
        return self._text_size
        
    def _refresh ( self ):
        """ Refreshes the contents of the control.
        """
        if self.control is not None:
            self.control.Refresh()
        
    def _set_slider_position ( self, x, y ):
        """ Calculates a new slider value for a specified (x,y) coordinate.
        """
        wdx, wdy = self.control.GetSizeTuple()
        if (3 <= x < wdx) and (0 <= y < wdy):
            value = self.low + (((x - 3) * (self.high - self.low)) / (wdx - 4))
            increment = self.increment
            if increment > 0:
                value = round( value / increment ) * increment
            self.value = value
            
    def _delayed_click ( self ):
        """ Handle a delayed click response.
        """
        if self._pending:
            self._pending = False
            self._set_slider_position( self._x, self._y )

    def _pop_up_text ( self ):
        """ Pop-up a text control to allow the user to enter a value using
            the keyboard.
        """
        control = self.control
        text    = wx.TextCtrl( control, -1, self.text,
                               size = control.GetSize(),
                               style = wx.TE_PROCESS_ENTER )
        text.SetSelection( -1, -1 )
        text.SetFocus()
        wx.EVT_TEXT_ENTER( control, text.GetId(), self._text_completed )
        wx.EVT_KILL_FOCUS( text, self._text_completed )
        wx.EVT_CHAR( text, self._key_entered )

    def _destroy_text ( self ):
        """ Destroys the current text control.
        """
        # We set '_x' to prevent a SetFocus event from causing an infinite
        # loop when we destroy the text control (then we clear it):
        self._x = 1
        self.control.DestroyChildren()
        self._x = None
        
    #--- wxPython Event Handlers -----------------------------------------------
            
    def _erase_background ( self, event ):
        """ Do not erase the background here (do it in the 'on_paint' handler).
        """
        pass
           
    def _on_paint ( self, event ):
        """ Paint the background using the associated ImageSlice object.
        """
        control = self.control
        dc      = wx.PaintDC( control )
            
        # Draw the slider bar:
        wdx, wdy = control.GetClientSizeTuple()
        dx = max( 0, min( wdx - 2, 
                  int( round( ((wdx - 3) * (self.value - self.low)) / 
                                           (self.high - self.low) ) ) ) )
        
        dc.SetBrush( wx.Brush( self.slider_color_ ) )
        dc.SetPen( wx.TRANSPARENT_PEN )
        dc.DrawRectangle( 0, 0, dx + 3, wdy )
        
        # Draw the rest of the background:
        dc.SetBrush( wx.Brush( self.bg_color_ ) )
        dc.DrawRectangle( dx + 3, 0, wdx - dx - 3, wdy )
        
        # Draw the slider tip:
        dc.SetBrush( wx.Brush( self.tip_color_ ) )
        dc.DrawRectangle( dx, 0, 3, wdy )
        
        # Draw the current text value (if requested):
        if self.show_value:
            dc.SetBackgroundMode( wx.TRANSPARENT )
            dc.SetTextForeground( self.text_color_ )
            tx, ty, tdx, tdy = self._get_text_bounds()
            dc.DrawText( self.text, tx, ty )
    
    def _set_focus ( self, event ):
        """ Handle the control getting the keyboard focus.
        """
        if self._x is None:
            self._pop_up_text()
            
        event.Skip()
    
    def _left_down ( self, event ):
        """ Handles the left mouse being pressed.
        """
        self._x, self._y = event.GetX(), event.GetY()
        self._pending    = True
        self.control.CaptureMouse()
        self.control.SetFocus()
        do_after( 150, self._delayed_click )
    
    def _left_up ( self, event ):
        """ Handles the left mouse button being released.
        """
        self.control.ReleaseMouse()
        if self._pending:
            self._pop_up_text()
            
        self._x = self._y = self._pending = None
        
    def _mouse_move ( self, event ):
        """ Handles the mouse moving.
        """
        if self._x is not None:
            x, y = event.GetX(), event.GetY()
            if self._pending:
                if (abs( x - self._x ) + abs( y - self._y )) < 3:
                    return
                self._pending = False
            self._set_slider_position( x, y )
            
    def _text_completed ( self, event ):
        control = event.GetEventObject()
        try:
            self.value = float( control.GetValue() )
            self._destroy_text()
        except:
            control.SetBackgroundColour( ErrorColor )
        
    def _key_entered ( self, event ):
        key_code = event.GetKeyCode()
        if key_code == wx.WXK_ESCAPE:
            self._destroy_text()
            return
        
        if key_code == wx.WXK_TAB:
            if event.ShiftDown():
                self.control.Navigate( 0 )
            else:
                self.control.Navigate()
            return
            
        event.Skip()
            
    #-- Trait Event Handlers ---------------------------------------------------
    
    def _value_changed ( self ):
        self.text       = '%g' % self.value
        self._text_size = None
        self._refresh()

#-------------------------------------------------------------------------------
#  Class 'CenteredImageResource'  
#-------------------------------------------------------------------------------
        
class CenteredImageResource ( ImageResource ):
    
    # The image resource being centered:
    image_resource = Instance( ImageResource )
    
    # The background color to use:
    bg_color = Color( 0xE0E0E0 )
    
    # Optional text to display centered over image:
    text = Str
    
    # The color of the text:
    text_color = Color( 'black' )
    
    # The font to use for displaying the text:
    font = Font( 'Arial 12' )
    
    # The size of the image to center in:
    width  = Int
    height = Int

    #-- Private Traits ---------------------------------------------------------
    
    # The cached version of the centered image:
    _image = Instance( wx.Image )
    
    #-- object Method Implementations ------------------------------------------
    
    def __init__ ( self, **traits ):
        """ Initializes the object. """
        self.set( **traits )
        
    #-- ImageResource Method Implementations -----------------------------------
    
    def create_image( self, size = None ):
        """ Creates a toolkit specific image for this resource. """
        if self._image is None:
            dx, dy = self.width, self.height
            bitmap = wx.EmptyBitmap( dx, dy )
            mdc    = wx.MemoryDC()
            mdc.SelectObject( bitmap )
            mdc.SetBrush( wx.Brush( self.bg_color_ ) )
            mdc.SetPen( wx.TRANSPARENT_PEN )
            mdc.DrawRectangle( 0, 0, dx, dy )
            
            bitmap2  = self.image_resource.create_bitmap()
            bdx, bdy = bitmap2.GetWidth(), bitmap2.GetHeight()
            mdc2     = wx.MemoryDC()
            mdc2.SelectObject( bitmap2 )
            
            mdc.Blit( (dx - bdx) / 2, (dy - bdy) / 2, bdx, bdy, mdc2, 0, 0, 
                      useMask = True )
                      
            text = self.text
            if text != '':
                mdc.SetBackgroundMode( wx.TRANSPARENT )
                mdc.SetTextForeground( self.text_color_ )
                mdc.SetFont( self.font )
                tdx, tdy, descent, leading = mdc.GetFullTextExtent( text )  
                mdc.DrawText( text, (dx - tdx) / 2, ((dy - tdy) / 2) - 1 )
                
            mdc.SelectObject(  wx.NullBitmap )
            mdc2.SelectObject( wx.NullBitmap )
            
            self._image = bitmap.ConvertToImage()
            
        return self._image
