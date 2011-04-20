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
#  Date:   06/22/2007
#
#-------------------------------------------------------------------------------

""" Traits UI simple, themed slider-based integer or float value editor.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import wx

from math \
   import log10, pow

from traits.api \
    import HasPrivateTraits, Instance, Enum, Range, Str, Float, Bool, Color, \
           TraitError

from traitsui.ui_traits \
    import Alignment

from traitsui.wx.editor \
    import Editor

from traitsui.basic_editor_factory \
    import BasicEditorFactory

from pyface.timer.api \
    import do_after

from constants \
    import ErrorColor

from helper \
    import disconnect, disconnect_no_id, BufferDC

#-------------------------------------------------------------------------------
#  '_ThemedSliderEditor' class:
#-------------------------------------------------------------------------------

class _ThemedSliderEditor ( Editor ):
    """ Traits UI simple, themed slider-based integer or float value editor.
    """

    # The low end of the slider range:
    low = Float

    # The high end of the slider range:
    high = Float

    # The smallest allowed increment:
    increment = Float

    # The current text being displayed:
    text = Str

    #-- Class Variables --------------------------------------------------------

    text_styles = {
        'left':   wx.TE_LEFT,
        'center': wx.TE_CENTRE,
        'right':  wx.TE_RIGHT
    }

    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        factory = self.factory
        # Establish the range of the slider:
        low, high = factory.low, factory.high
        if high <= low:
            low = high = None
            range      = self.object.trait( self.name ).handler
            if isinstance( range, Range ):
                low, high = range._low, range._high
            if low is None:
                if high is None:
                    high = 1.0
                low = high - 1.0
            elif high is None:
                high = low + 1.0

        # Establish the slider increment:
        increment = factory.increment
        if increment <= 0.0:
            if isinstance( low, int ):
                increment = 1.0
            else:
                increment = pow( 10, int( log10( (high - low) / 1000.0 ) ) )

        # Save the values we calculated:
        self.set( low = low, high = high, increment = increment )

        # Create the control:
        self.control = control = wx.Window( parent, -1,
                                            size  = wx.Size( 70, 20 ),
                                            style = wx.FULL_REPAINT_ON_RESIZE |
                                                    wx.TAB_TRAVERSAL )

        # Set up the painting event handlers:
        wx.EVT_ERASE_BACKGROUND( control, self._erase_background )
        wx.EVT_PAINT( control, self._on_paint )
        wx.EVT_SET_FOCUS(  control, self._set_focus )

        # Set up mouse event handlers:
        wx.EVT_LEFT_DOWN(    control, self._left_down )
        wx.EVT_LEFT_UP(      control, self._left_up )
        wx.EVT_MOTION(       control, self._motion )
        wx.EVT_MOUSEWHEEL(   control, self._mouse_wheel )
        wx.EVT_ENTER_WINDOW( control, self._enter_window )
        wx.EVT_LEAVE_WINDOW( control, self._leave_window )

        # Set up the control resize handler:
        wx.EVT_SIZE( control, self._resize )

        # Set the tooltip:
        if not self.set_tooltip():
            control.SetToolTipString( '[%g..%g]' % ( low, high ) )

    #---------------------------------------------------------------------------
    #  Disposes of the contents of an editor:
    #---------------------------------------------------------------------------

    def dispose ( self ):
        """ Disposes of the contents of an editor.
        """
        disconnect_no_id( self.control, wx.EVT_ERASE_BACKGROUND, wx.EVT_PAINT,
            wx.EVT_SET_FOCUS, wx.EVT_LEFT_DOWN, wx.EVT_LEFT_UP, wx.EVT_MOTION,
            wx.EVT_MOUSEWHEEL, wx.EVT_ENTER_WINDOW, wx.EVT_LEAVE_WINDOW,
            wx.EVT_SIZE )

        if self._text is not None:
            disconnect( self._text, wx.EVT_TEXT_ENTER )
            disconnect_no_id( self._text, wx.EVT_KILL_FOCUS,
                wx.EVT_ENTER_WINDOW, wx.EVT_LEAVE_WINDOW, wx.EVT_CHAR )

        super( _ThemedSliderEditor, self ).dispose()

    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------

    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        self.text       = '%g' % self.value
        self._text_size = None
        self._refresh()

        if self._text is not None:
            self._text.SetValue( self.text )

    #---------------------------------------------------------------------------
    #  Updates the object when the control slider value changes:
    #---------------------------------------------------------------------------

    def update_object ( self, value ):
        """ Updates the object when the control slider value changes.
        """
        try:
            self.value = value
        except TraitError:
            self.value = int( value )

        self.update_editor()

    #---------------------------------------------------------------------------
    #  Handles an error that occurs while setting the object's trait value:
    #---------------------------------------------------------------------------

    def error ( self, excp ):
        """ Handles an error that occurs while setting the object's trait value.
        """
        pass

    #-- Private Methods --------------------------------------------------------

    def _get_text_bounds ( self ):
        """ Get the window bounds of where the current text should be
            displayed.
        """
        tdx, tdy, descent, leading = self._get_text_size()
        wdx, wdy  = self.control.GetClientSizeTuple()
        ty        = ((wdy - (tdy - descent)) / 2) - 2
        alignment = self.factory.alignment
        if alignment == 'left':
            tx = 4
        elif alignment == 'center':
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

    def _set_slider_position ( self, x ):
        """ Calculates a new slider value for a specified (x,y) coordinate.
        """
        wdx, wdy = self.control.GetSizeTuple()
        if 3 <= x < wdx:
            value = self.low + (((x - 3) * (self.high - self.low)) / (wdx - 4))
            increment = self.increment
            if increment > 0:
                value = round( value / increment ) * increment
            self.update_object( value )

    def _delayed_click ( self ):
        """ Handle a delayed click response.
        """
        if self._pending:
            self._pending = False
            self._set_slider_position( self._x )

    def _pop_up_text ( self ):
        """ Pop-up a text control to allow the user to enter a value using
            the keyboard.
        """
        control    = self.control
        self._text = text = wx.TextCtrl( control, -1, self.text,
                            size  = control.GetSize(),
                            style = self.text_styles[ self.factory.alignment ] |
                                    wx.TE_PROCESS_ENTER )
        text.SetSelection( -1, -1 )
        text.SetFocus()
        wx.EVT_TEXT_ENTER( control, text.GetId(), self._text_completed )
        wx.EVT_KILL_FOCUS( text, self._text_completed )
        wx.EVT_ENTER_WINDOW( text, self._enter_text )
        wx.EVT_LEAVE_WINDOW( text, self._leave_text )
        wx.EVT_CHAR( text, self._key_entered )

    def _destroy_text ( self ):
        """ Destroys the current text control.
        """
        self._ignore_focus = self._in_text_window
        disconnect( self._text, wx.EVT_TEXT_ENTER )
        disconnect_no_id( self._text, wx.EVT_KILL_FOCUS, wx.EVT_ENTER_WINDOW,
            wx.EVT_LEAVE_WINDOW, wx.EVT_CHAR )
        self.control.DestroyChildren()
        self._text = None

    #--- wxPython Event Handlers -----------------------------------------------

    def _erase_background ( self, event ):
        """ Do not erase the background here (do it in the 'on_paint' handler).
        """
        pass

    def _on_paint ( self, event ):
        """ Paint the background using the associated ImageSlice object.
        """
        control = self.control
        dc      = BufferDC( control )

        # Draw the slider bar:
        wdx, wdy = control.GetClientSize()
        dx       = max( 0, min( wdx - 2,
                        int( round( ((wdx - 3) * (self.value - self.low)) /
                                                 (self.high - self.low) ) ) ) )

        factory = self.factory
        dc.SetBrush( wx.Brush( factory.slider_color_ ) )
        dc.SetPen( wx.TRANSPARENT_PEN )
        dc.DrawRectangle( 0, 0, dx + 3, wdy )

        # Draw the rest of the background:
        dc.SetBrush( wx.Brush( factory.bg_color_ ) )
        dc.DrawRectangle( dx + 3, 0, wdx - dx - 3, wdy )

        # Draw the slider tip:
        dc.SetBrush( wx.Brush( factory.tip_color_ ) )
        dc.DrawRectangle( dx, 0, 3, wdy )

        # Draw the current text value (if requested):
        if factory.show_value:
            dc.SetBackgroundMode( wx.TRANSPARENT )
            dc.SetTextForeground( factory.text_color_ )
            dc.SetFont( control.GetFont() )
            tx, ty, tdx, tdy = self._get_text_bounds()
            dc.DrawText( self.text, tx, ty )

        # Copy the buffer to the display:
        dc.copy()

    def _resize ( self, event ):
        """ Handles the control being resized.
        """
        if self._text is not None:
            self._text.SetSize( self.control.GetSize() )

    def _set_focus ( self, event ):
        """ Handle the control getting the keyboard focus.
        """
        if ((not self._ignore_focus) and
            (self._x is None)        and
            (self._text is None)):
            self._pop_up_text()

        event.Skip()

    def _left_down ( self, event ):
        """ Handles the left mouse being pressed.
        """
        self._x, self._y = event.GetX(), event.GetY()
        self._pending    = True
        self.control.CaptureMouse()
        do_after( 150, self._delayed_click )

    def _left_up ( self, event ):
        """ Handles the left mouse button being released.
        """
        if self._x is not None:
            self.control.ReleaseMouse()

        if self._pending:
            self._pop_up_text()

        self._x = self._y = self._pending = None

    def _motion ( self, event ):
        """ Handles the mouse moving.
        """
        if self._x is not None:
            x, y = event.GetX(), event.GetY()
            if self._pending:
                if (abs( x - self._x ) + abs( y - self._y )) < 3:
                    return
                self._pending = False
            self._set_slider_position( x )

    def _mouse_wheel ( self, event ):
        """ Handles the mouse wheel rotating.
        """
        if self._in_window:
            increment = event.GetWheelRotation() / event.GetWheelDelta()
            delta     = (self.high - self.low) / 100.0
            if isinstance( self.value, int ) and (abs( delta ) < 1):
                delta = int( abs( delta ) / delta )

            self.update_object( min( max( self.value + increment * delta,
                                          self.low ), self.high ) )

    def _enter_window ( self, event ):
        """ Handles the mouse pointer entering the control.
        """
        self._in_window = True

        if not self._ignore_focus:
            self._ignore_focus = True
            self.control.SetFocus()

        self._ignore_focus = False

    def _leave_window ( self, event ):
        """ Handles the mouse pointer leaving the control.
        """
        self._in_window = False

    def _update_value ( self, event ):
        """ Updates the object value from the current text control value.
        """
        control = event.GetEventObject()
        try:
            self.update_object( float( control.GetValue() ) )

            return True

        except TraitError:
            control.SetBackgroundColour( ErrorColor )
            control.Refresh()

            return False

    def _enter_text ( self, event ):
        """ Handles the mouse entering the pop-up text control.
        """
        self._in_text_window = True

    def _leave_text ( self, event ):
        """ Handles the mouse leaving the pop-up text control.
        """
        self._in_text_window = False

    def _text_completed ( self, event ):
        """ Handles the user pressing the 'Enter' key in the text control.
        """
        if self._update_value( event ):
            self._destroy_text()

    def _key_entered ( self, event ):
        """ Handles individual key strokes while the text control is active.
        """
        key_code = event.GetKeyCode()
        if key_code == wx.WXK_ESCAPE:
            self._destroy_text()
            return

        if key_code == wx.WXK_TAB:
            if self._update_value( event ):
                if event.ShiftDown():
                    self.control.Navigate( 0 )
                else:
                    self.control.Navigate()
            return

        event.Skip()

#-------------------------------------------------------------------------------
#  Create the editor factory object:
#-------------------------------------------------------------------------------

# wxPython editor factory for themed slider editors:
class ThemedSliderEditor ( BasicEditorFactory ):

    # The editor class to be created:
    klass = _ThemedSliderEditor

    # The low end of the slider range:
    low = Float

    # The high end of the slider range:
    high = Float

    # The smallest allowed increment:
    increment = Float

    # Should the current value be displayed as text?
    show_value = Bool( True )

    # The alignment of the text within the slider:
    alignment = Alignment( 'center' )

    # The color to use for the slider bar:
    slider_color = Color( 0xC0C0C0 )

    # The background color for the slider:
    bg_color = Color( 'white' )

    # The color of the slider tip:
    tip_color = Color( 0xFF7300 )

    # The color to use for the value text:
    text_color = Color( 'black' )

