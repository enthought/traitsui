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
    import HasTraits, HasPrivateTraits, Str, Int, Enum, Bool, Property, Event, \
           Tuple, Instance, cached_property
    
from enthought.traits.ui.ui_traits \
    import Image, HasPadding, Padding, Position, Alignment, Spacing
    
from image_slice \
    import image_slice_for, paint_parent, default_image_slice
    
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

class ThemedControl ( HasPrivateTraits ):
    
    #-- Public Traits ----------------------------------------------------------
    
    # The (optional) theme to be drawn in the control's background:
    theme = Image( event = 'updated' )
    
    # Should the theme be transparent?
    transparent = Bool( True )
    
    # An (optional) image to be drawn inside the control:
    image = Image( event = 'updated' )
    
    # The (optional) text to be displayed inside the control:
    text = Str( event = 'updated' )
    
    # The position of the image relative to the text:
    position = Position( event = 'updated' )
    
    # The alignment of the text within the control:
    alignment = Alignment( event = 'updated' )
    
    # The amount of spacing between the image and the text:
    spacing = Spacing( event = 'updated' )
    
    # The amount of padding between the image/text and the border:
    padding = HasPadding( Padding( left = 4, right = 4, top = 2, bottom = 2 ),
                          event = 'updated' )
    
    # Is the text value private (like a password):
    password = Bool( False, event = 'updated' )
    
    # Optional controller used for overriding event handling:
    controller = Instance( HasTraits )
    
    # Offset to display text and image from calculated position:
    offset = Tuple( Int, Int, event = 'updated' )
    
    # Minimum default size for the control:
    min_size = Tuple( Int, Int )
    
    #-- Private Traits ---------------------------------------------------------
    
    # An event fired when any display related value changes:
    updated = Event
    
    # The current mouse event state:
    state = Str( 'normal' )
    
    # The underlying wx.Window control:
    control = Instance( wx.Window )
    
    # The current text value to display:
    current_text = Property( depends_on = 'text, password' )
    
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
                            
        # Set up the painting event handlers:
        wx.EVT_ERASE_BACKGROUND( control, self._erase_background )
        wx.EVT_PAINT( control, self._on_paint )
        
        # Set up the resize event handler:
        wx.EVT_SIZE( control, self._on_resize )
        
        # Set up mouse event handlers:
        wx.EVT_LEFT_DOWN(     control, self._left_down )
        wx.EVT_LEFT_UP(       control, self._left_up )
        wx.EVT_LEFT_DCLICK(   control, self._left_dclick )
        wx.EVT_MIDDLE_DOWN(   control, self._middle_down )
        wx.EVT_MIDDLE_UP(     control, self._middle_up )
        wx.EVT_MIDDLE_DCLICK( control, self._middle_dclick )
        wx.EVT_RIGHT_DOWN(    control, self._right_down )
        wx.EVT_RIGHT_UP(      control, self._right_up )
        wx.EVT_RIGHT_DCLICK(  control, self._right_dclick )
        wx.EVT_MOTION(        control, self._mouse_move )
        
        # Make sure the control is sized correctly:
        cx, cy, cdx, cdy = self._get_bounds_for( TheControl )
        mdx, mdy         = self.min_size
        size             = wx.Size( max( cdx, mdx ), max( cdy, mdy ) )
        control.SetMinSize( size )
        control.SetSize( size )
        
        return control
        
    def in_control ( self, x, y ):
        """ Returns whether a specified (x,y) coordinate is inside the control
            or not.
        """
        wdx, wdy = self.control.GetClientSizeTuple()
        return ((0 <= x < wdx) and (0 <= y < wdy))
        
    #-- Property Implementations -----------------------------------------------
        
    @cached_property
    def _get_current_text ( self ):
        """ Returns the current text to display.
        """
        if self.password:
            return '*' * len( self.text )
            
        return self.text
        
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
        
    def _theme_changed ( self, theme ):
        if theme is None:
            self._image_slice = None
        else:
            self._image_slice = image_slice_for( theme, self.transparent )
        
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
           
    def _on_paint ( self, event ):
        """ Paint the background using the associated ImageSlice object.
        """
        control = self.control
        dc      = wx.PaintDC( control )
        
        # Repaint the parent's theme (if necessary):
        if self._fill is not False:
            slice = paint_parent( dc, control, 0, 0 )
        self._fill = True
        
        # Draw the background theme (if any):
        wdx, wdy = control.GetClientSizeTuple()
        if self._image_slice is not None:
            slice = self._image_slice
            slice.fill( dc, 0, 0, wdx, wdy )
        
        # Get the text and image offset to use:
        ox, oy = self.offset
        
        # Draw the bitmap (if any):
        ix, iy, idx, idy = self.bitmap_bounds
        if idx != 0:
            dc.DrawBitmap( self._bitmap, ix + ox, iy + oy, True )
            
        # Draw the text (if any):
        tx, ty, tdx, tdy = self.text_bounds
        if tdx != 0:
            dc.SetBackgroundMode( wx.TRANSPARENT )
            dc.SetTextForeground( slice.text_color )
            dc.SetFont( control.GetFont() )
            dc.DrawText( self.current_text, tx + ox, ty + oy )
            
    def _on_resize ( self, event ):
        """ Handles the control being resized.
        """
        self.updated = True
    
    def _left_down ( self, event ):
        """ Handles a left mouse button down event.
        """
        self.control.SetFocus()
        self._mouse_event( 'left_down', event )
        self.control.CaptureMouse()
        
    def _left_up ( self, event ):
        """ Handles a left mouse button up event.
        """
        self.control.ReleaseMouse()
        self._mouse_event( 'left_up', event )
    
    def _left_dclick ( self, event ):
        """ Handles a left mouse button double click event.
        """
        self._mouse_event( 'left_dclick', event )
        self.control.CaptureMouse()
    
    def _middle_down ( self, event ):
        """ Handles a middle mouse button down event.
        """
        self._mouse_event( 'middle_down', event )
        self.control.CaptureMouse()
        
    def _middle_up ( self, event ):
        """ Handles a middle mouse button up event.
        """
        self.control.ReleaseMouse()
        self._mouse_event( 'middle_up', event )
    
    def _middle_dclick ( self, event ):
        """ Handles a middle mouse button double click event.
        """
        self._mouse_event( 'middle_dclick', event )
        self.control.CaptureMouse()
    
    def _right_down ( self, event ):
        """ Handles a right mouse button down event.
        """
        self._mouse_event( 'right_down', event )
        self.control.CaptureMouse()
        
    def _right_up ( self, event ):
        """ Handles a right mouse button up event.
        """
        self.control.ReleaseMouse()
        self._mouse_event( 'right_up', event )
    
    def _right_dclick ( self, event ):
        """ Handles a right mouse button double click event.
        """
        self._mouse_event( 'right_dclick', event )
        self.control.CaptureMouse()
        
    def _mouse_move ( self, event ):
        """ Handles a mouse move event.
        """
        self._mouse_event( 'mouse_move', event )
        
    #-- Private Methods --------------------------------------------------------
    
    def _mouse_event ( self, name, event ):
        """ Routes a mouse event to the proper handler (if any).
        """
        method_name = '%s_%s' % ( self.state, name )
        
        if self.controller is not None:
            method = getattr( self.controller, method_name, None )
            
        if method is None:
            method = getattr( self, method_name, None )
            
        if method is not None:
            method( event.GetX(), event.GetY(), event )
        
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
        slice     = self._image_slice or default_image_slice
        spacing   = (tdx != 0) * (bdx != 0) * self.spacing
        padding   = self.padding
        alignment = self.alignment
        
        position = self.position
        if position in ( 'above', 'below' ):
            cdx = max( tdx, bdx )
            cdy = tdy + spacing + bdy
        else:
            cdx = tdx + spacing + bdx
            cdy = max( tdy, bdy )
        
        if item == TheControl:
            cdx += padding.left + padding.right
            cdy += padding.top  + padding.bottom
            
            return ( 0, 0, max( slice.left  + slice.right,
                                slice.xleft + slice.xright  + cdx ),
                           max( slice.top   + slice.bottom,
                                slice.xtop  + slice.xbottom + cdy ) )
        
        if alignment == 'left':
            x = slice.xleft + padding.left
        elif alignment == 'center':
            x = slice.xleft + padding.left + ((wdx - slice.xleft - slice.xright
                            - padding.left - padding.right - cdx) / 2)
        else:
            x = wdx - slice.xright - padding.right - cdx
            
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
            
        y = slice.xtop + padding.top + ((wdy - slice.xtop - slice.xbottom - 
                         padding.top - padding.bottom - cdy) / 2)
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
        
