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
    import HasPrivateTraits, HasTraits, Instance, Str, Enum, Any, Bool

from enthought.traits.ui.ui_traits \
    import ATheme
    
from helper \
    import init_wx_handlers
    
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
    
    # Should debugging information be overlaid on the theme?
    debug = Bool( False )
    
    #-- Public Methods ---------------------------------------------------------
    
    def init_control ( self ):
        """ Initializes the underlying wx.Window object.
        """
        init_wx_handlers( self.control, self )
        
    def in_control ( self, x, y ):
        """ Returns whether a specified (x,y) coordinate is inside the control
            or not.
        """
        wdx, wdy = self.control.GetClientSizeTuple()
        return ((0 <= x < wdx) and (0 <= y < wdy))
        
    def refresh ( self ):
        """ Refreshes the contents of the control.
        """
        if self.control is not None:
            self.control.Refresh()
        
    #-- Trait Event Handlers ---------------------------------------------------
    
    def _theme_changed ( self ):
        """ Handles the 'theme' trait being changed.
        """
        self.refresh()
        
    #-- wxPython Event Handlers ------------------------------------------------
    
    def _erase_background ( self, event ):
        """ Do not erase the background here (do it in the 'on_paint' handler).
        """
        pass
           
    def _paint ( self, event ):
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
                slice2.fill( dc, 0, 0, wdx, wdy, True )
                
                if self.debug:
                    dc.SetPen( wx.Pen( wx.RED ) )
                    dc.SetBrush( wx.TRANSPARENT_BRUSH )
                    theme  = self.theme
                    border = theme.border
                    dc.DrawRectangle( border.left, border.top, 
                                      wdx - border.right  - border.left, 
                                      wdy - border.bottom - border.top )
                    dc.DrawRectangle( border.left + 3, border.top + 3, 
                                      wdx - border.right  - border.left - 6, 
                                      wdy - border.bottom - border.top  - 6 )
                    content = theme.content
                    x = slice2.xleft + content.left - 1
                    y = slice2.xtop  + content.top  - 1
                    dc.DrawRectangle( x, y,
                           wdx - slice2.xright  - content.right  - x + 1,
                           wdy - slice2.xbottom - content.bottom - y + 1 )
                           
                    label = theme.label
                    if slice2.xtop >= slice2.xbottom:
                        top, bottom = 0, slice2.xtop
                    else:
                        top, bottom = wdy - slice2.xbottom, slice2.xbottom
                        
                    if bottom >= 13:
                        x = slice2.xleft + label.left - 1
                        y = top + label.top - 1
                        dc.DrawRectangle( x, y,
                            wdx - slice2.xright - label.right  - x + 1,
                            bottom - label.bottom + 1 )
                
                return ( dc, slice2 )
    
        return ( dc, slice )
        
    def _size ( self, event ):
        """ Handles the control being resized.
        """
        control = self.control
        if control is not None:
            control.Layout()
            control.Refresh()
    
    def _left_down ( self, event ):
        """ Handles a left mouse button down event.
        """
        self.control.SetFocus()
        self.control.CaptureMouse()
        self._mouse_event( 'left_down', event )
        
    def _left_up ( self, event ):
        """ Handles a left mouse button up event.
        """
        self.control.ReleaseMouse()
        self._mouse_event( 'left_up', event )
    
    def _left_dclick ( self, event ):
        """ Handles a left mouse button double click event.
        """
        self.control.CaptureMouse()
        self._mouse_event( 'left_dclick', event )
    
    def _middle_down ( self, event ):
        """ Handles a middle mouse button down event.
        """
        self.control.CaptureMouse()
        self._mouse_event( 'middle_down', event )
        
    def _middle_up ( self, event ):
        """ Handles a middle mouse button up event.
        """
        self.control.ReleaseMouse()
        self._mouse_event( 'middle_up', event )
    
    def _middle_dclick ( self, event ):
        """ Handles a middle mouse button double click event.
        """
        self.control.CaptureMouse()
        self._mouse_event( 'middle_dclick', event )
    
    def _right_down ( self, event ):
        """ Handles a right mouse button down event.
        """
        self.control.CaptureMouse()
        self._mouse_event( 'right_down', event )
        
    def _right_up ( self, event ):
        """ Handles a right mouse button up event.
        """
        self.control.ReleaseMouse()
        self._mouse_event( 'right_up', event )
    
    def _right_dclick ( self, event ):
        """ Handles a right mouse button double click event.
        """
        self.control.CaptureMouse()
        self._mouse_event( 'right_dclick', event )
        
    def _motion ( self, event ):
        """ Handles a mouse move event.
        """
        self._mouse_event( 'motion', event )
        
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
        
