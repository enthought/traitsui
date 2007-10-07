#-------------------------------------------------------------------------------
#  
#  Defines 'ThemedControl, a themed control based class. A 'themed' control is
#  a control (optionally) supporting a stretchable background image.
#  
#  Written by: David C. Morrill
#  
#  Date: 07/03/2007
#  
#  (c) Copyright 2007 by Enthought, Inc.
#  
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import wx

from enthought.traits.api \
    import HasTraits, Str, Int, Enum, Bool, Property, Event, Tuple, Instance, \
           cached_property, on_trait_change
    
from enthought.traits.ui.api \
    import default_theme
    
from enthought.traits.ui.ui_traits \
    import Image, HasPadding, Padding, Position, Alignment, Spacing
    
from image_slice \
    import default_image_slice
    
from themed_window \
    import ThemedWindow
    
#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# The size of an empty text string:
ZeroTextSize = ( 0, 0, 0, 0 )

# An empty position and size bounds:
EmptyBounds = ( 0, 0, 0, 0 )

# Targets for '_get_bounds_for' method:
TheText    = 0
TheBitmap  = 1
TheControl = 2

#-------------------------------------------------------------------------------
#  'ThemedControl' class:
#-------------------------------------------------------------------------------

class ThemedControl ( ThemedWindow ):
    
    #-- Public Traits ----------------------------------------------------------
    
    # An (optional) image to be drawn inside the control:
    image = Image( event = 'updated' )
    
    # The (optional) text to be displayed inside the control:
    text = Str( event = 'updated' )
    
    # The position of the image relative to the text:
    position = Position( event = 'updated' )
    
    # The amount of spacing between the image and the text:
    spacing = Spacing( event = 'updated' )
    
    # Is the text value private (like a password):
    password = Bool( False, event = 'updated' )
    
    # An additional, optional offset to apply to the text/image position:
    offset = Tuple( Int, Int )
    
    # Minimum default size for the control:
    min_size = Tuple( Int, Int )
    
    # Is the control enabled:
    enabled = Bool( True )
    
    #-- Private Traits ---------------------------------------------------------
    
    # An event fired when any display related value changes:
    updated = Event
    
    # The underlying wx.Window control:
    control = Instance( wx.Window )
    
    # The current text value to display:
    current_text = Property( depends_on = 'text, password' )
    
    # The best size for the control:
    best_size = Property
    
    # The size of the current text:
    text_size = Property( depends_on = 'current_text, control' )
    
    # The position and size of the current text within the control:
    text_bounds = Property( depends_on = 'updated' )
    
    # The position and size of the current bitmap within the control:
    bitmap_bounds = Property( depends_on = 'updated' )
    
    #-- Public Methods ---------------------------------------------------------
    
    def create_control ( self, parent ):
        """ Creates the underlying wx.Window object.
        """
        self.control = control = wx.Window( parent, -1,
                            size  = wx.Size( 70, 20 ),
                            style = wx.FULL_REPAINT_ON_RESIZE | wx.WANTS_CHARS )
            
        # Initialize the control (set-up event handlers, ...):
        self.init_control()
        
        # Make sure the control is sized correctly:
        size = self.best_size
        control.SetMinSize( size )
        control.SetSize( size )
        
        return control
        
    #-- Property Implementations -----------------------------------------------
        
    @cached_property
    def _get_current_text ( self ):
        """ Returns the current text to display.
        """
        if self.password:
            return '*' * len( self.text )
            
        return self.text
        
    def _get_best_size ( self ):
        """ Returns the 'best' size for the control.
        """
        cx, cy, cdx, cdy = self._get_bounds_for( TheControl )
        mdx, mdy         = self.min_size
        return wx.Size( max( cdx, mdx ), max( cdy, mdy ) )
        
    @cached_property
    def _get_text_size ( self ):
        """ Returns the text size information for the window.
        """
        text = self.current_text
        if (text == '') or (self.control is None):
            return ZeroTextSize
            
        return self.control.GetFullTextExtent( text )
        
    @cached_property
    def _get_text_bounds ( self ):
        """ Returns the position and size of the text within the window.
        """
        return self._get_bounds_for( TheText )
        
    @cached_property
    def _get_bitmap_bounds ( self ):
        """ Returns the size and position of the bitmap within the window.
        """
        return self._get_bounds_for( TheBitmap )
    
    #-- Event Handlers ---------------------------------------------------------
    
    def _updated_changed ( self ):
        """ Handles any update related trait being changed.
        """
        if self.control is not None:
            self.control.Refresh()
        
    @on_trait_change( 'theme.+' )
    def _on_theme_changed ( self ):
        self._updated_changed()
        
    def _image_changed ( self, image ):
        """ Handles the image being changed by updating the corresponding 
            bitmap.
        """
        if image is None:
            self._bitmap = None
        else:
            self._bitmap = image.create_image().ConvertToBitmap()
        
    #-- wxPython Event Handlers ------------------------------------------------
    
    def _erase_background ( self, event ):
        """ Do not erase the background here (do it in the 'on_paint' handler).
        """
        pass
           
    def _paint ( self, event ):
        """ Paint the background using the associated ImageSlice object.
        """
        self.enabled = self.control.IsEnabled()
        
        dc, slice = super( ThemedControl, self )._paint( event )
        
        # Get the text and image offset to use:
        ox, oy   = (self.theme or default_theme).offset
        ox2, oy2 = self.offset
        ox      += ox2
        oy      += oy2
        
        # Draw the bitmap (if any):
        ix, iy, idx, idy = self.bitmap_bounds
        if idx != 0:
            dc.DrawBitmap( self._bitmap, ix + ox, iy + oy, True )
            
        # Draw the text (if any):
        tx, ty, tdx, tdy = self.text_bounds
        if tdx != 0:
            dc.SetBackgroundMode( wx.TRANSPARENT )
            dc.SetTextForeground( slice.text_color )
            dc.SetFont( self.control.GetFont() )
            dc.DrawText( self.current_text, tx + ox, ty + oy )
        
    def _size ( self, event ):
        """ Handles the control being resized.
        """
        super( ThemedControl, self )._size( event )
        self.updated = True
        
    #-- Private Methods --------------------------------------------------------
        
    def _get_bounds_for ( self, item ):
        """ Returns all text and image related position and size information.
        """
        control = self.control
        if control is None:
            return EmptyBounds
            
        tdx, tdy, descent, leading = self.text_size
        bitmap = self._bitmap
        if bitmap is None:
            bdx, bdy = 0, 0
        else:
            bdx, bdy = bitmap.GetWidth(), bitmap.GetHeight()
        if (tdx + bdx) == 0:
            return EmptyBounds
            
        wdx, wdy  = control.GetClientSizeTuple()
        spacing   = (tdx != 0) * (bdx != 0) * self.spacing
        theme     = self.theme or default_theme
        slice     = theme.image_slice or default_image_slice
        margins   = theme.margins
        
        position = self.position
        if position in ( 'above', 'below' ):
            cdx = max( tdx, bdx )
            cdy = tdy + spacing + bdy
        else:
            cdx = tdx + spacing + bdx
            cdy = max( tdy, bdy )
        
        if item == TheControl:
            cdx += margins.left + margins.right
            cdy += margins.top  + margins.bottom
            
            return ( 0, 0, max( slice.left  + slice.right,
                                slice.xleft + slice.xright  + cdx ),
                           max( slice.top   + slice.bottom,
                                slice.xtop  + slice.xbottom + cdy ) )
        
        alignment = theme.alignment
        if alignment == 'default':
            alignment = self.default_alignment
        if alignment == 'left':
            x = slice.xleft + margins.left
        elif alignment == 'center':
            x = slice.xleft + margins.left + ((wdx - slice.xleft - slice.xright
                            - margins.left - margins.right - cdx) / 2)
        else:
            x = wdx - slice.xright - margins.right - cdx
            
        if position == 'left':
            bx = x
            tx = bx + bdx + spacing
        elif position == 'right':
            tx = x
            bx = tx + tdx + spacing
        else:
            x += (max( tdx, bdx ) / 2)
            tx = x - (tdx / 2 )
            bx = x - (bdx / 2 )
            
        y = slice.xtop + margins.top + ((wdy - slice.xtop - slice.xbottom - 
                         margins.top - margins.bottom - cdy) / 2)
        if position == 'above':
            by = y
            ty = by + bdy + spacing
        elif position == 'below':
            ty = y
            by = ty + tdy + spacing
        else:
            y += (max( tdy, bdy ) / 2)
            ty = y - ((tdy + 1) / 2)
            by = y - (bdy / 2)
            
        if item == TheText:
            return ( tx, ty, tdx, tdy )
            
        return ( bx, by, bdx, bdy )
        
