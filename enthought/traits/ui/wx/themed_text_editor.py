#-------------------------------------------------------------------------------
#
#  Traits UI simple, read-only single line text editor with a themed (i.e.
#  image) background.
#
#  Written by: David C. Morrill
#
#  Date: 06/13/2007
#
#  (c) Copyright 2007 by Enthought, Inc.
#
#-------------------------------------------------------------------------------

""" Traits UI simple, read-only single line text editor with a themed 
    (i.e. image) background.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import wx

from enthought.traits.api \
    import Enum, Instance, Bool, Dict, Str, Any, TraitError
    
from enthought.traits.ui.wx.editor \
    import Editor
    
from enthought.traits.ui.wx.editor_factory \
    import EditorFactory
    
from enthought.traits.ui.ui_traits \
    import Image

from enthought.pyface.image_resource \
    import ImageResource
    
from image_slice \
    import ImageSlice, paint_parent, default_image_slice
    
from constants \
    import OKColor, ErrorColor

#-------------------------------------------------------------------------------
#  Define a simple identity mapping:
#-------------------------------------------------------------------------------

class _Identity ( object ):
    """ A simple indentity mapping.
    """
    def __call__ ( self, value ):    
        return value

#-------------------------------------------------------------------------------
#  'ThemedTextEditor' class:
#-------------------------------------------------------------------------------

class ThemedTextEditor ( EditorFactory ):
    """ Traits UI simple, single line text editor with a themed (i.e. image) 
        background.
    """
    
    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------
    
    # The background theme image to display:
    theme = Image
    
    # The alignment of the text within the control:
    alignment = Enum( 'left', 'right', 'center' )
    
    # Dictionary that maps user input to other values:
    mapping = Dict( Str, Any )
    
    # Is user input set on every keystroke?
    auto_set = Bool( True )
    
    # Is user input set when the Enter key is pressed?
    enter_set = Bool( False )
    
    # Is user input unreadable? (e.g., for a password)
    password = Bool( False )
    
    # Function to evaluate textual user input:
    evaluate = Any
    
    # The object trait containing the function used to evaluate user input:
    evaluate_name = Str
    
    #---------------------------------------------------------------------------
    #  'Editor' factory methods:
    #---------------------------------------------------------------------------
    
    def simple_editor ( self, ui, object, name, description, parent ):
        return _ThemedTextEditor( parent,
                                  factory     = self, 
                                  ui          = ui, 
                                  object      = object, 
                                  name        = name, 
                                  description = description ) 
    
    def custom_editor ( self, ui, object, name, description, parent ):
        return _ThemedTextEditor( parent,
                                  factory     = self, 
                                  ui          = ui, 
                                  object      = object, 
                                  name        = name, 
                                  description = description ) 
    
    def text_editor ( self, ui, object, name, description, parent ):
        return _ThemedTextEditor( parent,
                                  factory     = self, 
                                  ui          = ui, 
                                  object      = object, 
                                  name        = name, 
                                  description = description ) 
    
    def readonly_editor ( self, ui, object, name, description, parent ):
        return _ThemedTextEditor( parent,
                                  factory     = self, 
                                  ui          = ui, 
                                  object      = object, 
                                  name        = name, 
                                  description = description,
                                  readonly    = True )

#-------------------------------------------------------------------------------
#  '_ThemedTextEditor' class:
#-------------------------------------------------------------------------------
                               
class _ThemedTextEditor ( Editor ):
    """ Traits UI simple, read-only single line text editor with a themed
        (i.e. image background).
    """
    
    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------
    
    # Is the editor read-only?
    readonly = Bool( False )
        
    # Function used to evaluate textual user input:
    evaluate = Any
    
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
        factory  = self.factory
        evaluate = factory.evaluate
        if evaluate is None:
            handler  = self.object.trait( self.name ).handler
            evaluate = getattr( handler, 'evaluate', None )
            if evaluate is None:
                evaluate = _Identity()
        self.evaluate = evaluate
        self.sync_value( factory.evaluate_name, 'evaluate', 'from' )
        
        self._image_slice     = None
        padding_x = padding_y = 0
        if factory.theme is not None:
            self._image_slice = slice = ImageSlice(
                               transparent = True ).set( image = factory.theme )
            padding_x = slice.xleft + slice.xright                                            
            padding_y = slice.xtop  + slice.xbottom                                            
                                            
        self.control = control = wx.Window( parent, -1,
                            size  = wx.Size( padding_x + 70, padding_y + 20 ),
                            style = wx.FULL_REPAINT_ON_RESIZE | wx.WANTS_CHARS )
                                           
        self._text_size = self._fill = None  
        
        # Set up the painting event handlers:
        wx.EVT_ERASE_BACKGROUND( control, self._erase_background )
        wx.EVT_PAINT( control, self._on_paint )
        wx.EVT_CHAR(  control, self._inactive_key_entered )
        
        # Only handle 'focus' events if we are not read-only:
        if not self.readonly:
            wx.EVT_SET_FOCUS( control, self._set_focus )
            wx.EVT_LEFT_UP(   control, self._set_focus )
           
        self.set_tooltip()
        
    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------
        
    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        if self._text is None:
            self._refresh()
            return
            
        if self._get_user_value() != self.value:
            self._no_update = True
            self._text.SetValue( self.str_value )
            self._no_update = False
            
        if self._error is not None:
            self._error     = None
            self.ui.errors -= 1
            self._text.SetBackgroundColour( self.ok_color )
            self._text.Refresh()

    #---------------------------------------------------------------------------
    #  Handles the user entering input data in the edit control:
    #---------------------------------------------------------------------------
  
    def update_object ( self, event ):
        """ Handles the user entering input data in the edit control.
        """
        if not self._no_update:
            try:
                self.value = self._get_user_value()
                self._text.SetBackgroundColour( OKColor )
                self._text.Refresh()
                
                if self._error is not None:
                    self._error     = None
                    self.ui.errors -= 1
                return True
                    
            except TraitError, excp:
                return False

    #---------------------------------------------------------------------------
    #  Gets the actual value corresponding to what the user typed:
    #---------------------------------------------------------------------------
 
    def _get_user_value ( self ):
        """ Gets the actual value corresponding to what the user typed.
        """
        value = self._text.GetValue()
        try:
            value = self.evaluate( value )
        except:
            pass
            
        return self.factory.mapping.get( value, value )
        
    #---------------------------------------------------------------------------
    #  Handles an error that occurs while setting the object's trait value:
    #---------------------------------------------------------------------------
        
    def error ( self, excp ):
        """ Handles an error that occurs while setting the object's trait value.
        """
        self._text.SetBackgroundColour( ErrorColor )
        self._text.Refresh()
        wx.Bell()
        
        if self._error is None:
            self._error     = True
            self.ui.errors += 1

    #-- Private Methods --------------------------------------------------------

    def _pop_up_text ( self ):
        """ Pop-up a text control to allow the user to enter a value using
            the keyboard.
        """
        control = self.control
        factory = self.factory
        style   = (self.text_styles[ self.factory.alignment ] | 
                   wx.TE_PROCESS_ENTER)
        if factory.password:
            style |= wx.TE_PASSWORD
            
        self._text = text = wx.TextCtrl( control, -1, self.str_value, 
                                   size = control.GetSize(), style = style )
        text.SetSelection( -1, -1 )
        text.SetFocus()
        
        wx.EVT_KILL_FOCUS( text, self._text_completed )
        wx.EVT_CHAR( text, self._key_entered )
        wx.EVT_TEXT_ENTER( control, text.GetId(), self.update_object )
        
        if factory.auto_set and (not factory.is_grid_cell):
           wx.EVT_TEXT( control, text.GetId(), self.update_object )

    def _destroy_text ( self ):
        """ Destroys the current text control.
        """
        self.control.DestroyChildren()
        self._text = None

    def _refresh ( self ):
        """ Refreshes the contents of the control.
        """
        if self._fill is True:
            self._fill = (self._image_slice is None)
        
        if self._text_size is not None:
            self.control.RefreshRect( wx.Rect( *self._get_text_bounds() ), 
                                      False )
            self._text_size = None
            
        self.control.RefreshRect( wx.Rect( *self._get_text_bounds() ), False )
        
    def _get_text_size ( self ):
        """ Returns the text size information for the window.
        """
        if self._text_size is None:
            self._text_size = self.control.GetFullTextExtent( 
                                               self._get_text() or 'M' )
            
        return self._text_size

    def _get_text_bounds ( self ):
        """ Get the window bounds of where the current text should be
            displayed.
        """
        tdx, tdy, descent, leading = self._get_text_size()
        wdx, wdy  = self.control.GetClientSizeTuple()
        slice     = self._image_slice or default_image_slice
        ady       = wdy - slice.xtop  - slice.xbottom
        ty        = slice.xtop  + ((ady - (tdy - descent)) / 2) - 1
        alignment = self.factory.alignment
        if alignment == 'left':
            tx = slice.xleft + 4
        elif alignment == 'center':
            adx = wdx - slice.xleft - slice.xright
            tx  = slice.xleft + (adx - tdx) / 2
        else:
            tx = wdx - tdx - slice.xright - 4
            
        return ( tx, ty, tdx, tdy )
        
    def _get_text ( self ):
        """ Returns the current text to display.
        """
        if self.factory.password:
            return '*' * len( self.str_value )
            
        return self.str_value

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
        if self._fill is not False:
            slice = paint_parent( dc, control, 0, 0 )
            
        self._fill = True
        wdx, wdy   = control.GetClientSizeTuple()
        if self._image_slice is not None:
            slice = self._image_slice
            slice.fill( dc, 0, 0, wdx, wdy )
        dc.SetBackgroundMode( wx.TRANSPARENT )
        dc.SetTextForeground( slice.text_color )
        dc.SetFont( control.GetFont() )
        tx, ty, tdx, tdy = self._get_text_bounds()
        dc.DrawText( self._get_text(), tx, ty )
    
    def _set_focus ( self, event ):
        """ Handle the control getting the keyboard focus.
        """
        if self._text is None:
            self._pop_up_text()
            
        event.Skip()
            
    def _text_completed ( self, event ):
        """ Handles the user transferring focus out of the text control.
        """
        if self.update_object( event ):
            self._destroy_text()
        
    def _key_entered ( self, event ):
        """ Handles individual key strokes while the text control is active.
        """
        key_code = event.GetKeyCode()
        if key_code == wx.WXK_ESCAPE:
            self._destroy_text()
            return
        
        if key_code == wx.WXK_TAB:
            if self.update_object( event ):
                if event.ShiftDown():
                    self.control.Navigate( 0 )
                else:
                    self.control.Navigate()
                    
            return
            
        event.Skip()
        
    def _inactive_key_entered ( self, event ):
        """ Handles individual key strokes while the text control is inactive.
        """
        if event.GetKeyCode() == wx.WXK_RETURN:
            if self._text is None:
                self._pop_up_text()
                
            return
            
        event.Skip()
                 
