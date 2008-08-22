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
#  Date:   10/21/2004
#
#------------------------------------------------------------------------------

""" Defines the various color editors and the color editor factory, for the 
    wxPython user interface toolkit.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import wx

from colorsys \
    import rgb_to_hls, hls_to_rgb
    
from enthought.pyface.api \
    import ImageResource

from enthought.traits.api \
    import HasPrivateTraits, Bool, Instance, Str, Color, Tuple, Float, Any, \
           Event, on_trait_change

from enthought.traits.ui.api \
    import View, Item, Handler

from editor_factory \
    import EditorFactory, SimpleEditor, TextEditor, ReadonlyEditor
    
from basic_editor_factory \
    import BasicEditorFactory

from editor \
    import Editor
    
from ui_editor \
    import UIEditor

from constants \
    import is_mac, WindowColor
    
from helper \
    import traits_ui_panel, position_window, init_wx_handlers, BufferDC
    
# Version dependent imports (ColourPtr not defined in wxPython 2.5):
try:
    ColorTypes = ( wx.Colour, wx.ColourPtr )    
except:
    ColorTypes = wx.Colour

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# The color drawn around the edges of the HLSSelector:
EdgeColor = wx.Colour( 64, 64, 64 )

#-------------------------------------------------------------------------------
#  'ToolkitEditorFactory' class:
#-------------------------------------------------------------------------------

class ToolkitEditorFactory ( EditorFactory ):
    """ wxPython editor factory for color editors.
    """
    
    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------
    
    # Is the underlying color trait mapped?
    mapped = Bool( True )
    
    #---------------------------------------------------------------------------
    #  Traits view definition:  
    #---------------------------------------------------------------------------
    
    traits_view = View( [ 'mapped{Is value mapped?}', '|[]>' ] )    
    
    #---------------------------------------------------------------------------
    #  'Editor' factory methods:
    #---------------------------------------------------------------------------
    
    def simple_editor ( self, ui, object, name, description, parent ):
        return SimpleColorEditor( parent,
                                  factory     = self, 
                                  ui          = ui, 
                                  object      = object, 
                                  name        = name, 
                                  description = description ) 
    
    def custom_editor ( self, ui, object, name, description, parent ):
        return CustomColorEditor( parent,
                                  factory     = self, 
                                  ui          = ui, 
                                  object      = object, 
                                  name        = name, 
                                  description = description ) 
    
    def text_editor ( self, ui, object, name, description, parent ):
        return TextColorEditor( parent,
                                factory     = self, 
                                ui          = ui, 
                                object      = object, 
                                name        = name, 
                                description = description ) 
    
    def readonly_editor ( self, ui, object, name, description, parent ):
        return ReadonlyColorEditor( parent,
                                    factory     = self, 
                                    ui          = ui, 
                                    object      = object, 
                                    name        = name, 
                                    description = description ) 
       
    #---------------------------------------------------------------------------
    #  Gets the wxPython color equivalent of the object trait:
    #---------------------------------------------------------------------------
    
    def to_wx_color ( self, editor ):
        """ Gets the wxPython color equivalent of the object trait.
        """
        if self.mapped:
            return getattr( editor.object, editor.name + '_' )

        return getattr( editor.object, editor.name )
 
    #---------------------------------------------------------------------------
    #  Gets the application equivalent of a wxPython value:
    #---------------------------------------------------------------------------
    
    def from_wx_color ( self, color ):
        """ Gets the application equivalent of a wxPython value.
        """
        return color
        
    #---------------------------------------------------------------------------
    #  Returns the text representation of a specified color value:
    #---------------------------------------------------------------------------
  
    def str_color ( self, color ):
        """ Returns the text representation of a specified color value.
        """
        if isinstance( color, ColorTypes ):
            alpha = color.Alpha()
            if alpha == 255:
                return "(%d,%d,%d)" % (
                        color.Red(), color.Green(), color.Blue() )

            return "(%d,%d,%d,%d)" % (
                    color.Red(), color.Green(), color.Blue(), alpha )
            
        return color
                                      
#-------------------------------------------------------------------------------
#  'SimpleColorEditor' class:
#-------------------------------------------------------------------------------
                               
class SimpleColorEditor ( SimpleEditor ):
    """ Simple style of color editor, which displays a text field whose 
        background color is the color value. Selecting the text field displays
        a dialog box for selecting a new color value.
    """
    
    # The color sample control used to display the current color:
    color_sample = Any
    
    # Is the editor busy (which means any popups should not close right now)?
    busy = Bool( False )
    
    #---------------------------------------------------------------------------
    #  Invokes the pop-up editor for an object trait:
    #---------------------------------------------------------------------------
 
    def popup_editor ( self, event ):
        """ Invokes the pop-up editor for an object trait.
        """
        # Fixes a problem with the edit field having the focus:
        if self.control.HasCapture():
            self.control.ReleaseMouse()
        
        self.object.edit_traits( view = View( 
                Item(
                    self.name, 
                    id         = 'color_editor',
                    show_label = False, 
                    padding    = -4,
                    editor     = PopupColorEditor( factory = self.factory )
                ),
                kind    = 'popup' ),
            parent = self.control )
                
    #---------------------------------------------------------------------------
    #  Creates the control to use for the simple editor:
    #---------------------------------------------------------------------------
    
    def create_control ( self, parent ):
        """ Creates the control to use for the simple editor.
        """
        self.color_sample = ColorSample( parent )
        return self.color_sample.control

    #---------------------------------------------------------------------------
    #  Updates the object trait when a color swatch is clicked:
    #---------------------------------------------------------------------------

    def update_object_from_swatch ( self, color ):
        """ Updates the object trait when a color swatch is clicked.
        """
        self.value = self.factory.from_wx_color( color )
        self.update_editor()

    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------

    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the 
            editor.
        """
        self.color_sample.text = self.str_value
        set_color( self )

    #---------------------------------------------------------------------------
    #  Returns the text representation of a specified color value:
    #---------------------------------------------------------------------------

    def string_value ( self, color ):
        """ Returns the text representation of a specified color value.
        """
        return self.factory.str_color( color ) 

#-------------------------------------------------------------------------------
#  'CustomColorEditor' class:
#-------------------------------------------------------------------------------

class CustomColorEditor ( Editor ):
    
    # The HLSSelector control used by the editor:
    selector = Instance( 'HLSSelector' )

    #-- Editor Methods ---------------------------------------------------------
    
    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.selector = HLSSelector( parent )
        self.control  = self.selector.control
        self.set_tooltip()

    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the 
            editor.
        """
        if not self._no_update:
            self.selector.color = self.factory.to_wx_color( self )
        
    @on_trait_change( 'selector:color' )
    def _color_changed ( self, color ):
        self._no_update = True
        self.value      = self.factory.from_wx_color( color )
        self._no_update = False

#-------------------------------------------------------------------------------
#  'TextColorEditor' class:
#-------------------------------------------------------------------------------

class TextColorEditor ( TextEditor ):
    """ Text style of color editor, which displays a text field whose 
        background color is the color value.
    """
    
    #---------------------------------------------------------------------------
    #  Handles the user changing the contents of the edit control:
    #---------------------------------------------------------------------------

    def update_object ( self, event ):
        """ Handles the user changing the contents of the edit control.
        """
        self.value = self.control.GetValue()

    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------

    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the 
            editor.
        """
        super( TextColorEditor, self ).update_editor()
        set_color( self )

    #---------------------------------------------------------------------------
    #  Returns the text representation of a specified color value:
    #---------------------------------------------------------------------------

    def string_value ( self, color ):
        """ Returns the text representation of a specified color value.
        """
        return self.factory.str_color( color ) 

#-------------------------------------------------------------------------------
#  'ReadonlyColorEditor' class:
#-------------------------------------------------------------------------------

class ReadonlyColorEditor ( ReadonlyEditor ):
    """ Read-only style of color editor, which displays a read-only text field
    whose background color is the color value.
    """
    
    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.control = ColorSample( parent ).control

    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------

    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the 
            editor.
        """
        set_color( self )

#-------------------------------------------------------------------------------
#   Sets the color of the specified editor's color control: 
#-------------------------------------------------------------------------------

def set_color ( editor ):
    """  Sets the color of the specified color control.
    """
    color   = editor.factory.to_wx_color( editor )
    control = editor.control
    control.SetBackgroundColour( color )
    if ((color.Red()   > 192) or
        (color.Blue()  > 192) or
        (color.Green() > 192)):
        control.SetForegroundColour( wx.BLACK )
    else:
        control.SetForegroundColour( wx.WHITE )
        
    control.Refresh()

#-------------------------------------------------------------------------------
#  'ColorSample' class:
#-------------------------------------------------------------------------------

class ColorSample ( HasPrivateTraits ):
    
    # The wx Window that implements the color sample:
    control = Instance( wx.Window )
    
    # The text to display in the control:
    text = Str
    
    def __init__ ( self, parent ):
        """ Creates the color chip window and initializes it.
        """
        self.control = wx.Window( parent, -1, 
                                  style = wx.FULL_REPAINT_ON_RESIZE )
        init_wx_handlers( self.control, self )
        
        if is_mac:
            self.control.SetSize( wx.Size( -1, 23 ) )
        
    #-- wxPython Event Handlers ------------------------------------------------
        
    def _erase_background ( self, event ):
        pass
    
    def _paint ( self, event ):
        control = self.control
        dc      = BufferDC( control )
        dx, dy  = control.GetClientSize()
        dc.SetPen( wx.Pen( EdgeColor ) )
        dc.SetBrush( wx.Brush( control.GetBackgroundColour(), wx.SOLID ) )
        dc.DrawRectangle( 0, 0, dx, dy )
        
        if self.text != '':
            dc.SetFont( control.GetFont() )
            dc.DrawText( self.text, 3, 3 )
            
        dc.copy()
        
#-------------------------------------------------------------------------------
#   'HLSSelector' class:  
#-------------------------------------------------------------------------------        
    
class HLSSelector ( HasPrivateTraits ):        

    # The HS color map bitmap (class constant):
    color_map_bitmap = \
        ImageResource( 'hs_color_map' ).create_image().ConvertToBitmap()
    
    # The wx Window that implements the color sample:
    control = Instance( wx.Window )
    
    # The current selected color:
    color = Color( 0xFF0000 )
    
    # The HLS values corresponding to the current color:
    hls = Tuple( Float, Float, Float )
    
    #-- Public Methods ---------------------------------------------------------
    
    def __init__ ( self, parent ):
        """ Creates the HLSSelector window and initializes it.
        """
        self.control = wx.Window( parent, -1,
                                  size  = wx.Size( 228, 102 ),
                                  style = wx.FULL_REPAINT_ON_RESIZE )
        
        init_wx_handlers( self.control, self )
        
    #-- Trait Default Values ---------------------------------------------------
    
    def _hls_default ( self ):
        return self._wx_to_hls( self.color_ ) 
        
    #-- Trait Event Handlers ---------------------------------------------------
    
    def _color_changed ( self ):
        """ Updates the display when the current color changes.
        """
        self.hls = self._wx_to_hls( self.color_ ) 
            
        if self.control is not None:
            self.control.Refresh()
        
    #-- wxPython Event Handlers ------------------------------------------------
        
    def _erase_background ( self, event ):
        pass
    
    def _paint ( self, event ):
        dc = BufferDC( self.control )
        
        # Draw the unpainted portions of the background:
        wdx, wdy = self.control.GetClientSize()
        dc.SetPen( wx.TRANSPARENT_PEN )
        dc.SetBrush( wx.Brush( WindowColor ) )
        dc.DrawRectangle( 0, 0, wdx, wdy )
        
        # Draw the current color sample (if there is room):
        dc.SetPen( wx.Pen( EdgeColor ) )
        if wdx >= 240:
            dc.SetBrush( wx.Brush( self.color_ ) )
            dc.DrawRectangle( 228, 0, wdx - 228, 102 )
        
        # Draw the 'HS' color map and frame:
        dc.SetBrush( wx.TRANSPARENT_BRUSH )
        dc.DrawRectangle( 0, 0, 202, 102 )
        dc.DrawBitmap( self.color_map_bitmap, 1, 1, False )
        
        # Draw the 'L' selector frame:
        dc.DrawRectangle( 206, 0, 18, 102 )
        
        # Draw the 'L' selector color range based upon the current color:
        h, l, s = self.hls
        lp      = 1.0
        lstep   = 1.0 / 99
        for y in xrange( 1, 101 ):
            dc.SetPen( wx.Pen( self._hls_to_wx( h, lp, s ) ) )
            dc.DrawLine( 207, y, 223, y )
            lp -= lstep
            
        # Draw the current 'HS' selector:
        dc.SetPen( wx.BLACK_PEN )
        dc.SetBrush( wx.TRANSPARENT_BRUSH )
        dc.DrawCircle( int( round( 199 * h ) ) + 1, 
                       int( round(  99 * ( 1.0 - s ) ) ) + 1, 3 )
        
        # Draw the current 'L' selector:
        y = int( round( 99 * (1.0 - l) ) ) + 1
        dc.DrawLine( 203, y,     227, y )
        dc.DrawLine( 204, y - 1, 204, y + 2 )
        dc.DrawLine( 225, y - 1, 225, y + 2 )
        dc.DrawLine( 205, y - 2, 205, y + 3 )
        dc.DrawLine( 224, y - 2, 224, y + 3 )
        
        # Copy the buffer to the display:
        dc.copy()
        
    def _left_down ( self, event ):
        self._active = True
        self.control.CaptureMouse()
        self._set_color( event )
        
    def _left_up ( self, event ):
        self._active = False
        self.control.ReleaseMouse()
        self._set_color( event )
        
    def _motion ( self, event ):
        if self._active:
            self._set_color( event )
            
    #-- Private Methods --------------------------------------------------------
    
    def _set_color ( self, event ):
        """ Sets the color based on the current mouse position.
        """
        x, y = event.GetX(), event.GetY()
        
        if 1 <= y <= 100:
            h, l, s = h0, l0, s0 = self.hls

            if 1 <= x <= 200:
                h = (x - 1) / 199.0
                s = 1.0 - ((y - 1) / 99.0)
            elif 206 <= x <= 223:
                l = 1.0 - ((y - 1) / 99.0)
            else:
                return
                
            if (h != h0) or (l != l0) or (s != s0):
                self.color = self._hls_to_wx( h, l, s )
                self.hls   = ( h, l, s )
                if ((l == 0.0) or (l == 1.0)) and (self.control is not None):
                    self.control.Refresh()
        
    def _wx_to_hls ( self, color ):
        """ Returns a wx.Colour converted to an HLS tuple.
        """        
        return rgb_to_hls( color.Red()   / 255.0, 
                           color.Green() / 255.0,
                           color.Blue()  / 255.0 )
        
    def _hls_to_wx ( self, h, l, s ):
        """ Converts HLS values to a wx.Colour.
        """
        return wx.Colour( *[ int( round( c * 255.0 ) )
                             for c in hls_to_rgb( h, l, s ) ] )
    
#-------------------------------------------------------------------------------
#  'PopupColorEditor' editor definition:
#-------------------------------------------------------------------------------

class _PopupColorEditor ( UIEditor ):
        
    #---------------------------------------------------------------------------
    #  Creates the traits UI for the editor (can be overridden by a subclass):  
    #---------------------------------------------------------------------------
                
    def init_ui ( self, parent ):
        """ Creates the traits UI for the editor.
        """
        return self.object.edit_traits( 
            parent = parent,
            view   = View(
                         Item( self.name, 
                               id         = 'color_editor',
                               style      = 'custom',
                               show_label = False,
                               editor     = self.factory.factory ),
                         kind = 'subpanel' ) )

class PopupColorEditor ( BasicEditorFactory ):

    klass = _PopupColorEditor
    
    # The editor factory to be used by the sub-editor:
    factory = Instance( EditorFactory )
        
