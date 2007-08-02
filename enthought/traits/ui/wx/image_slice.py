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
  
from numpy \
    import reshape, fromstring, uint8

from enthought.traits.api \
    import HasPrivateTraits, Instance, Int, List, Color, Str, Enum, Property, \
           cached_property

from enthought.pyface.image_resource \
    import ImageResource
    
from constants \
    import WindowColor

from themed_window \
    import ThemedWindow
    
from helper \
    import traits_ui_panel
    
#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Size of an empty text string:
ZeroTextSize = ( 0, 0, 0, 0 )
    
#-------------------------------------------------------------------------------
#  Recursively paint the parent's background if they have an associated image 
#  slice.
#-------------------------------------------------------------------------------

def paint_parent ( dc, window ):
    """ Recursively paint the parent's background if they have an associated
        image slice.
    """
    parent = window.GetParent()
    slice  = getattr( parent, '_image_slice', None )
    if slice is not None:
        x, y   = window.GetPositionTuple()
        dx, dy = parent.GetSizeTuple()
        slice.fill( dc, -x, -y, dx, dy )
    else:
        # Otherwise, just paint the normal window background color:
        dx, dy = window.GetClientSizeTuple()
        dc.SetBrush( wx.Brush( parent.GetBackgroundColour() ) )
        dc.SetPen( wx.TRANSPARENT_PEN )
        dc.DrawRectangle( 0, 0, dx, dy )

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
    
    # The maximum number of 'stretchable' rows and columns:
    stretch_rows    = Enum( 1, 2 )
    stretch_columns = Enum( 1, 2 )
    
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
    
    # The background color of the image:
    bg_color = Color
    
    #-- Private Traits ---------------------------------------------------------
    
    # The current image's opaque bitmap:
    opaque_bitmap = Instance( wx.Bitmap )
    
    # The current image's transparent bitmap:
    transparent_bitmap = Instance( wx.Bitmap )
    
    # Size of the current image:
    dx = Int
    dy = Int
    
    # Size of the current image's slices:
    dxs = List
    dys = List
    
    # Fixed minimum size of current image:
    fdx = Int
    fdy = Int
    
    #-- Public Methods ---------------------------------------------------------
    
    def fill ( self, dc, x, y, dx, dy, transparent = False ):
        """ 'Stretch fill' the specified region of a device context with the
            sliced image.
        """
        # Create the source image dc:
        idc = wx.MemoryDC()
        if transparent:
            idc.SelectObject( self.transparent_bitmap )
        else:
            idc.SelectObject( self.opaque_bitmap )
        
        # Set up the drawing parameters:
        sdx, sdy = self.dx, self.dx
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
    
    def _image_changed ( self, image ):
        """ Handles the 'image' trait being changed.
        """
        # Save the original bitmap as the transparent version:
        self.transparent_bitmap = bitmap = \
            image.create_image().ConvertToBitmap()
        
        # Save the bitmap size information:
        self.dx = dx = bitmap.GetWidth()
        self.dy = dy = bitmap.GetHeight()
        
        # Create the opaque version of the bitmap:
        self.opaque_bitmap = wx.EmptyBitmap( dx, dy )
        mdc2 = wx.MemoryDC()
        mdc2.SelectObject( self.opaque_bitmap )
        mdc2.SetBrush( wx.Brush( WindowColor ) )
        mdc2.SetPen( wx.TRANSPARENT_PEN )
        mdc2.DrawRectangle( 0, 0, dx, dy )
        mdc = wx.MemoryDC()
        mdc.SelectObject( bitmap )
        mdc2.Blit( 0, 0, dx, dy, mdc, 0, 0, useMask = True )
        mdc.SelectObject(  wx.NullBitmap )
        mdc2.SelectObject( wx.NullBitmap )
            
        # Finally, analyze the image to find out its characteristics:
        self._analyze_bitmap()
        
    #-- Private Methods --------------------------------------------------------
    
    def _analyze_bitmap ( self ):
        """ Analyzes the bitmap.
        """
        # Get the image data:
        threshold = self.threshold
        bitmap    = self.opaque_bitmap
        dx, dy    = self.dx, self.dy
        image     = bitmap.ConvertToImage()
        
        # Convert the bitmap data to a numpy array for analysis:
        data = reshape( fromstring( image.GetData(), uint8 ), ( dy, dx, 3 ) )
                             
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
            matches = [ ( dy / 2, 1 ) ]
        elif n > self.stretch_rows:
            matches.sort( lambda l, r: cmp( r[1], l[1] ) )
            matches = matches[ : self.stretch_rows ]
            
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
            matches = [ ( dx / 2, 1 ) ]
        elif n > self.stretch_columns:
            matches.sort( lambda l, r: cmp( r[1], l[1] ) )
            matches = matches[ : self.stretch_columns ]
         
        # Calculate and save the vertical slice sizes:
        self.fdx, self.dxs = self._calculate_dxy( dx, matches )
        
        # Save the border size information:
        self.top    = min( dy / 2, self.dys[0] )
        self.bottom = min( dy / 2, self.dys[-1] )
        self.left   = min( dx / 2, self.dxs[0] )
        self.right  = min( dx / 2, self.dxs[-1] )
        
        # Find the optimal size for the borders (i.e. xleft, xright, ... ):
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
#  Returns a (possibly cached) ImageSlice:
#-------------------------------------------------------------------------------

image_slice_cache = {}

def image_slice_for ( image ):
    """ Returns a (possibly cached) ImageSlice.
    """
    global image_slice_cache

    result = image_slice_cache.get( image )
    if result is None:
        image_slice_cache[ image ] = result = ImageSlice( image = image )
            
    return result

#-------------------------------------------------------------------------------
#  'ImagePanel' class:  
#-------------------------------------------------------------------------------    
                      
class ImagePanel ( ThemedWindow ):
    
    # The optional text to display in the top or bottom of the image slice:
    text = Str( event = 'updated' )
    
    # Is the image panel capable of displaying text?
    can_show_text = Property
    
    # The adjusted size of the panel, taking into account the size of its
    # current children and the image border:
    adjusted_size = Property
    
    # The best size of the panel, taking into account the best size of its
    # children and the image border:
    best_size = Property
    
    # The underlying wx.Panel control:
    control = Instance( wx.Panel )

    #-- Private Traits ---------------------------------------------------------
    
    # The size of the current text:
    text_size = Property( depends_on = 'text, control' )
    
    #-- Public Methods ---------------------------------------------------------
    
    def create_control ( self, parent ):
        """ Creates the underlying wx.Panel control.
        """
        self.control = control = traits_ui_panel( parent, -1,
                          style = wx.TAB_TRAVERSAL | wx.FULL_REPAINT_ON_RESIZE )
    
        # Set up the sizer for the control:                                                   
        control.SetSizer( ImageSizer( self.theme ) )
                                                   
        # Initialize the control (set-up event handlers, ...)
        self.init_control()
                                                    
        # Attach the image slice to the control:
        control._image_slice = self.theme.image_slice
        
        # Set the panel's background colour to the image slice bg_color:
        control.SetBackgroundColour( control._image_slice.bg_color )
        
        # Set up resize event handler:
        wx.EVT_SIZE( control, self._on_size )
        
        return control
        
    #-- Property Implementations -----------------------------------------------
    
    def _get_adjusted_size ( self ):
        """ Returns the adjusted size of the panel taking into account the
            size of its current children and the image border.
        """
        control = self.control
        dx, dy  = 0, 0
        for child in control.GetChildren():
            dx, dy = child.GetSizeTuple()
            
        size = self._adjusted_size_of( dx, dy ) 
        control.SetSize( size )
        
        return size
    
    def _get_best_size ( self ):
        """ Returns the best size of the panel taking into account the
            best size of its current children and the image border.
        """
        control = self.control
        dx, dy  = 0, 0
        for child in control.GetChildren():
            dx, dy = child.GetBestSize()
            
        return self._adjusted_size_of( dx, dy ) 
        
    @cached_property
    def _get_can_show_text ( self ):
        """ Returns whether or not the image panel is capable of displaying
            text.
        """
        tdx, tdy, descent, leading = self.control.GetFullTextExtent( 'Myj' )
        slice = self.theme.image_slice
        tdy  += 4
        return ((tdy <= slice.xtop) or (tdy <= slice.xbottom) or
                (slice.xleft >= 40) or (slice.xright >= 40))
        
    @cached_property
    def _get_text_size ( self ):
        """ Returns the text size information for the window.
        """
        if (self.text == '') or (self.control is None):
            return ZeroTextSize
            
        return self.control.GetFullTextExtent( self.text )
        
    #-- Trait Event Handlers ---------------------------------------------------
    
    def _updated_changed ( self ):
        """ Handles a change that requires the control to be updated.
        """
        if self.control is not None:
            self.control.Refresh()
    
    #-- wx.Python Event Handlers -----------------------------------------------
           
    def _on_paint ( self, event ):
        """ Paint the background using the associated ImageSlice object.
        """
        dc, slice = super( ImagePanel, self )._on_paint( event )
        
        # If we have text and have room to draw it, then do so:
        text = self.text
        if (text != '') and self.can_show_text:
            dc.SetBackgroundMode( wx.TRANSPARENT )
            dc.SetTextForeground( slice.text_color )
            dc.SetFont( self.control.GetFont() )
            
            alignment = self.theme.alignment
            wdx, wdy  = self.control.GetClientSizeTuple()
            tdx, tdy, descent, leading = self.text_size
            tx = None
            if (tdy + 4) <= slice.xtop:
                ty = (slice.xtop - tdy) / 2
            elif (tdy + 4) <= slice.xbottom:
                ty = wdy - ((slice.xbottom + tdy) / 2)
            else:
                ty = (wdy + slice.xtop - slice.xbottom - tdy) / 2
                if slice.xleft >= 40:
                    if alignment == 'left':
                        tx = 4
                    elif alignment == 'right':
                        tx = slice.xleft - tdx - 4
                    else:
                        tx = (slice.xleft - tdx) / 2
                elif alignment == 'left':
                    tx = wdx - slice.xright + 4
                elif alignment == 'right':
                    tx = wdx - tdx - 4
                else:
                    tx = wdx - ((slice.xright + tdx) / 2)
                    
            if tx is None:
                if alignment == 'left':
                    tx = slice.left + 4
                elif alignment == 'right':
                    tx = wdx - tdx - slice.right - 4
                else:
                    tx = (wdx + slice.left - slice.right - tdx) / 2
                
            # fixme: Might need to set clipping region here...
            ox, oy = self.theme.offset
            dc.DrawText( text, tx + ox, ty + oy )
            
    def _on_size ( self, event ):
        """ Handles the control being resized.
        """
        self.control.Layout()
        self.control.Refresh()
        
    #-- Private Methods --------------------------------------------------------
    
    def _adjusted_size_of ( self, dx, dy ):
        """ Returns the adjusted size of its children, taking into account the
            image slice border.
        """
        slice = self.theme.image_slice
        sizer = self.control.GetSizer()
        return wx.Size( dx + min( slice.left, slice.xleft )   + 
                             min( slice.right, slice.xright ) + 
                             sizer._left_padding + sizer._right_padding,
                        dy + min( slice.top, slice.xtop )       +
                             min( slice.bottom, slice.xbottom ) +
                             sizer._top_padding + sizer._bottom_padding )
            
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

    def __init__ ( self, theme ):
        """ Initializes the object.
        """
        super( ImageSizer, self ).__init__()
        
        # Save the ImageSlice object which determines the inset border size:
        self._image_slice = theme.image_slice
        
        # Save the padding information:
        margins = theme.margins
        if margins is not None:
            self._left_padding   = margins.left
            self._right_padding  = margins.right
            self._top_padding    = margins.top
            self._bottom_padding = margins.bottom
        else:
            self._left_padding   = self._right_padding = self._top_padding = \
            self._bottom_padding = 0

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

class ImageText ( wx.PyWindow ):
    """ Defines a text control that displays an ImageSlice in its background.
    """
    
    #-- wx.PyWindow Method Overrides -------------------------------------------
    
    def __init__ ( self, parent, theme, text = '' ): 
        """ Initializes the object.
        """
        self._theme       = theme
        self._image_slice = theme.image_slice
                                            
        super( ImageText, self ).__init__( parent, -1, 
                                           style = wx.FULL_REPAINT_ON_RESIZE )
                                           
        self._text_size = self._fill = None  
        self.SetLabel( text )
        
        # Set up the painting event handlers:
        wx.EVT_ERASE_BACKGROUND( self, self._erase_background )
        wx.EVT_PAINT( self, self._on_paint )
        
        size = self.GetMinSize()
        self.SetMinSize( size )
        self.SetSize( size )
        
    def AcceptsFocus ( self ):
        """ Indicate that we are a static control that does not accept focus.
        """
        return False
        
    #-- wxPython Event Handlers ------------------------------------------------
    
    def _erase_background ( self, event ):
        """ Do not erase the background here (do it in the 'on_paint' handler).
        """
        pass
           
    def _on_paint ( self, event ):
        """ Paint the background using the associated ImageSlice object.
        """
        dc = wx.PaintDC( self )
        if self._fill is not False:
            paint_parent( dc, self )
            
        self._fill = True
        wdx, wdy   = self.GetClientSizeTuple()
        text       = self.GetLabel()
        self._image_slice.fill( dc, 0, 0, wdx, wdy, True )
        dc.SetBackgroundMode( wx.TRANSPARENT )
        dc.SetTextForeground( self._image_slice.text_color )
        dc.SetFont( self.GetFont() )
        tx, ty, tdx, tdy = self._get_text_bounds()
        dc.DrawText( text, tx, ty )
         
    def GetMinSize ( self ):
        """ Returns the minimum size for the window.
        """
        tdx, tdy, descent, leading = self._get_text_size()
        margins = self._theme.margins
        tdx    += (margins.left + margins.right)
        tdy    += (margins.top  + margins.bottom)
        slice   = self._image_slice
        
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
            self._fill = False
        
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
        wdx, wdy  = self.GetClientSizeTuple()
        slice     = self._image_slice
        theme     = self._theme
        margins   = theme.margins
        ady       = wdy - slice.xtop - slice.xbottom
        ty        = (wdy + slice.xtop + margins.top - slice.xtop - 
                           slice.xbottom - tdy) / 2
        alignment = theme.alignment
        if alignment == 'left':
            tx = slice.xleft + margins.left
        elif alignment == 'center':
            adx = wdx - slice.xleft - slice.xright
            tx  = slice.xleft + margins.left + 4 + ((adx - tdx) / 2)
        else:
            tx = wdx - tdx - slice.xright - margins.right
          
        ox, oy = theme.offset
        return ( tx + ox, ty + oy, tdx, tdy )
        
