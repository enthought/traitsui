#-------------------------------------------------------------------------------
#
#  Copyright (c) 2007, Enthought, Inc.
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
#  Date:   07/09/2007
#
#-------------------------------------------------------------------------------

""" Defines a ThemedWindow base class for creating themed windows.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import wx

from traits.api \
    import HasPrivateTraits, HasTraits, Instance, Str, Enum, Any, Bool

from traitsui.ui_traits \
    import ATheme

from helper \
    import init_wx_handlers, BufferDC

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
        wdx, wdy = self.control.GetClientSize()
        return ((0 <= x < wdx) and (0 <= y < wdy))

    def refresh ( self ):
        """ Refreshes the contents of the control.
        """
        if self.control is not None:
            self.control.Refresh()

    def capture_mouse ( self ):
        """ Grab control of the mouse and indicate that we are controlling it.
        """
        if not self._has_capture:
            self._has_capture = True
            self.control.CaptureMouse()

    def release_mouse ( self ):
        """ Grab control of the mouse and indicate that we are controlling it.
        """
        if self._has_capture:
            self._has_capture = False
            self.control.ReleaseMouse()

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
        dc = BufferDC( self.control )
        self._paint_bg( dc )
        self._paint_fg( dc )
        dc.copy()

    def _paint_bg ( self, dc ):
        """ Paints the background into the supplied device context using the
            associated ImageSlice object and returns the image slice used (if
            any).
        """
        from image_slice import paint_parent

        # Repaint the parent's theme (if necessary):
        paint_parent( dc, self.control )

        # Draw the background theme (if any):
        if self.theme is not None:
            slice = self.theme.image_slice
            if slice is not None:
                wdx, wdy = self.control.GetClientSize()
                slice.fill( dc, 0, 0, wdx, wdy, True )

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
                    x = slice.xleft + content.left
                    y = slice.xtop  + content.top
                    dc.DrawRectangle( x - 1, y - 1,
                           wdx - slice.xright  - content.right  - x + 2,
                           wdy - slice.xbottom - content.bottom - y + 2 )

                    label = theme.label
                    if slice.xtop >= slice.xbottom:
                        y, dy = 0, slice.xtop
                    else:
                        y, dy = wdy - slice.xbottom, slice.xbottom

                    if dy >= 13:
                        x  = slice.xleft + label.left
                        y += label.top
                        dc.DrawRectangle( x - 1, y - 1,
                            wdx - slice.xright - label.right - x + 2,
                            dy - label.bottom - label.top + 2 )

    def _paint_fg ( self, dc ):
        """ Paints the foreground of the window into the supplied device
            context.
        """
        pass

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
        self.capture_mouse()
        self._mouse_event( 'left_down', event )

    def _left_up ( self, event ):
        """ Handles a left mouse button up event.
        """
        if self._has_capture:
            self._has_capture = False
            self.control.ReleaseMouse()
            self._mouse_event( 'left_up', event )

    def _left_dclick ( self, event ):
        """ Handles a left mouse button double click event.
        """
        self.capture_mouse()
        self._mouse_event( 'left_dclick', event )

    def _middle_down ( self, event ):
        """ Handles a middle mouse button down event.
        """
        self.capture_mouse()
        self._mouse_event( 'middle_down', event )

    def _middle_up ( self, event ):
        """ Handles a middle mouse button up event.
        """
        self.release_mouse()
        self._mouse_event( 'middle_up', event )

    def _middle_dclick ( self, event ):
        """ Handles a middle mouse button double click event.
        """
        self.capture_mouse()
        self._mouse_event( 'middle_dclick', event )

    def _right_down ( self, event ):
        """ Handles a right mouse button down event.
        """
        self.capture_mouse()
        self._mouse_event( 'right_down', event )

    def _right_up ( self, event ):
        """ Handles a right mouse button up event.
        """
        self.release_mouse()
        self._mouse_event( 'right_up', event )

    def _right_dclick ( self, event ):
        """ Handles a right mouse button double click event.
        """
        self.capture_mouse()
        self._mouse_event( 'right_dclick', event )

    def _motion ( self, event ):
        """ Handles a mouse move event.
        """
        self._mouse_event( 'motion', event )

    def _enter ( self, event ):
        """ Handles the mouse entering the window event.
        """
        self._mouse_event( 'enter', event )

    def _leave ( self, event ):
        """ Handles the mouse leaving the window event.
        """
        self._mouse_event( 'leave', event )

    def _wheel ( self, event ):
        """ Handles a mouse wheel event.
        """
        self._mouse_event( 'wheel', event )

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

