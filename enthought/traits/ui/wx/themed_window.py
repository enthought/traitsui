#-------------------------------------------------------------------------------
#  
#  Defines a ThemedWindow base class for creating themed windows.
#  
#  Written by: David C. Morrill
#  
#  Date: 07/09/2007
#  
#  (c) Copyright 2007 by Enthought, Inc.
#  
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import wx

from enthought.traits.api \
    import HasPrivateTraits, HasTraits, Instance, Str, Enum, Any

from enthought.traits.ui.ui_traits \
    import ATheme
    
#-------------------------------------------------------------------------------
#  'ThemedWindow' class:
#-------------------------------------------------------------------------------
        
class ThemedWindow ( HasPrivateTraits ):

    #-- Public Traits ----------------------------------------------------------
    
    # The theme associated with this window:
    theme = ATheme
    
    # The default alignment to use:
    default_alignment = Enum( 'left', 'center', 'right' )
    
    # The current mouse event state:
    state = Str( 'normal' )
    
    # Optional controller used for overriding event handling:
    controller = Instance( HasTraits )
    
    #-- Public Methods ---------------------------------------------------------
    
    def init_control ( self ):
        """ Initializes the underlying wx.Window object.
        """
        control = self.control
        
        # Set up the painting event handlers:
        wx.EVT_ERASE_BACKGROUND( control, self._erase_background )
        wx.EVT_PAINT( control, self._on_paint )
        
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
        
    def in_control ( self, x, y ):
        """ Returns whether a specified (x,y) coordinate is inside the control
            or not.
        """
        wdx, wdy = self.control.GetClientSizeTuple()
        return ((0 <= x < wdx) and (0 <= y < wdy))
        
    #-- wxPython Event Handlers ------------------------------------------------
    
    def _erase_background ( self, event ):
        """ Do not erase the background here (do it in the 'on_paint' handler).
        """
        pass
           
    def _on_paint ( self, event ):
        """ Paint the background using the associated ImageSlice object.
        """
        from image_slice import paint_parent
        
        control = self.control
        dc      = wx.PaintDC( control )
        
        # Repaint the parent's theme (if necessary):
        slice = paint_parent( dc, control )
        
        # Draw the background theme (if any):
        if self.theme is not None:
            slice2 = self.theme.image_slice
            if slice2 is not None:
                wdx, wdy = control.GetClientSizeTuple()
                slice2.fill( dc, 0, 0, wdx, wdy, slice is not None )
                
                return ( dc, slice2 )
    
        return ( dc, slice )
    
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
        method      = None
        
        if self.controller is not None:
            method = getattr( self.controller, method_name, None )
            
        if method is None:
            method = getattr( self, method_name, None )
            
        if method is not None:
            method( event.GetX(), event.GetY(), event )
        
