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

""" Defines the various color editors for the wxPython user interface toolkit.
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
    import Bool, Instance, Str, Color, Tuple, Float, Any, on_trait_change

from enthought.traits.ui.api \
    import View, Item

from editor_factory \
    import SimpleEditor as BaseSimpleEditor, \
    ReadonlyEditor as BaseReadonlyEditor
    
from enthought.traits.ui.basic_editor_factory import \
    BasicEditorFactory
    
from enthought.traits.ui.editor_factory import \
    EditorFactory
    
from editor \
    import Editor
    
from ui_editor \
    import UIEditor
    
from ui_window \
    import UIWindow

from constants \
    import is_mac
    
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

#---------------------------------------------------------------------------
#  Gets the wxPython color equivalent of the object trait:
#---------------------------------------------------------------------------
    
def to_wx_color ( editor ):
    """ Gets the wxPython color equivalent of the object trait.
    """
    if editor.factory.mapped:
        return getattr( editor.object, editor.name + '_' )

    return getattr( editor.object, editor.name )
 
#---------------------------------------------------------------------------
#  Gets the application equivalent of a wxPython value:
#---------------------------------------------------------------------------
    
def from_wx_color ( color ):
    """ Gets the application equivalent of a wxPython value.
    """
    return color
        
#---------------------------------------------------------------------------
#  Returns the text representation of a specified color value:
#---------------------------------------------------------------------------
  
def str_color ( color ):
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

class SimpleColorEditor ( Editor ):
    
    # The HLSSelector control used by the editor:
    selector = Instance( 'BaseHLSSelector' )

    #-- Editor Methods ---------------------------------------------------------
    
    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.selector = self.create_selector( parent )
        self.control  = self.selector.control
        self.set_tooltip()
        
    def create_selector ( self, parent ):
        """ Creates the HLS selector for this style of editor.
        """
        return SimpleHLSSelector( parent )

    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the 
            editor.
        """
        if not self._no_update:
            self.selector.color = to_wx_color( self )
        
    @on_trait_change( 'selector:color' )
    def _color_changed ( self, color ):
        self._no_update = True
        self.value      = from_wx_color( color )
        self._no_update = False

#-------------------------------------------------------------------------------
#  'CustomColorEditor' class:
#-------------------------------------------------------------------------------

class CustomColorEditor ( SimpleColorEditor ):
        
    def create_selector ( self, parent ):
        """ Creates the HLS selector for this style of editor.
        """
        return CustomHLSSelector( parent )
                                      
#-------------------------------------------------------------------------------
#  'TextColorEditor' class:
#-------------------------------------------------------------------------------
                               
class TextColorEditor ( BaseSimpleEditor ):
    """ Text style of color editor, which displays a text field whose 
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
        self.value = from_wx_color( color )
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
        return str_color( color ) 

#-------------------------------------------------------------------------------
#  'ReadonlyColorEditor' class:
#-------------------------------------------------------------------------------

class ReadonlyColorEditor ( BaseReadonlyEditor ):
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
    color   = to_wx_color( editor )
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

class ColorSample ( UIWindow ):
    
    # The text to display in the control:
    text = Str
    
    def __init__ ( self, parent ):
        """ Creates the color chip window and initializes it.
        """
        super( ColorSample, self ).__init__( parent )
        
        if is_mac:
            self.control.SetSize( wx.Size( -1, 23 ) )
        
    #-- wxPython Event Handlers ------------------------------------------------
    
    def _paint_dc ( self, dc ):
        control = self.control
        dc.SetPen( wx.Pen( EdgeColor ) )
        dc.SetBrush( wx.Brush( control.GetBackgroundColour(), wx.SOLID ) )
        dc.DrawRectangle( 0, 0, self.width, self.height )
        
        if self.text != '':
            dc.SetFont( control.GetFont() )
            dc.DrawText( self.text, 3, 3 )
        
#-------------------------------------------------------------------------------
#   'BaseHLSSelector' class:  
#-------------------------------------------------------------------------------        
    
class BaseHLSSelector ( UIWindow ):
    """ Abstract base class for creating HSL color space color selectors.
    """
    
    # The current selected color:
    color = Color( 0xFF0000 )
    
    # The HLS values corresponding to the current color:
    hls = Tuple( Float, Float, Float )
    
    #-- Trait Default Values ---------------------------------------------------
    
    def _hls_default ( self ):
        return self._wx_to_hls( self.color_ ) 
        
    #-- Trait Event Handlers ---------------------------------------------------
    
    def _color_changed ( self ):
        """ Updates the display when the current color changes.
        """
        self.hls = self._wx_to_hls( self.color_ ) 
        self.refresh()

    #-- wxPython Event Handlers ------------------------------------------------
    
    def _left_down ( self, event ):
        self._active = True
        self.capture()
        self._set_color( event )
        
    def _left_up ( self, event ):
        self._active = False
        self.release()
        self._set_color( event )
        
    def _motion ( self, event ):
        if self._active:
            self._set_color( event )
        
    #-- Private Methods --------------------------------------------------------
        
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
#   'SimpleHLSSelector' class:  
#-------------------------------------------------------------------------------        
    
class SimpleHLSSelector ( BaseHLSSelector ):
    """ Simple 'one line' multi-bar HSL color space color selector.
    """
    size = Instance( wx.Size, ( 200, -1 ) )
    
    #-- wxPython Event Handlers ------------------------------------------------
    
    def _paint_dc ( self, dc ):
        """ Paints the HLS selector on the display.
        """
        # Calculate the size and position of each HLS selector:
        wdx, wdy  = self.width, self.height
        self._sdx = sdx = ((wdx - 12) / 4) - 2
        self._hx0 = hx0 = 1
        self._sx0 = sx0 = hx0 + sdx + 6
        self._lx0 = lx0 = sx0 + sdx + 6
        self._cx0 = cx0 = lx0 + sdx + 6
        
        # Draw the selector boundaries:
        dc.SetPen( wx.Pen( EdgeColor ) )
        dc.SetBrush( wx.TRANSPARENT_BRUSH )
        dc.DrawRectangle( hx0 - 1, 0, sdx + 2, wdy )
        dc.DrawRectangle( lx0 - 1, 0, sdx + 2, wdy )
        dc.DrawRectangle( sx0 - 1, 0, sdx + 2, wdy )
        
        # Draw the current color sample:
        dc.SetBrush( wx.Brush( self.color_ ) )
        dc.DrawRectangle( cx0 - 1, 0, sdx + 2, wdy )
        
        # Now fill the contents of each of the HLS selectors:
        h, l, s = self.hls
        range   = sdx - 1
        step    = 1.0 / range
        ey      = wdy - 1
        
        # Draw the 'H' selector color range based upon the current color:
        hp = 0.0
        for x in xrange( hx0, hx0 + sdx ):
            dc.SetPen( wx.Pen( self._hls_to_wx( hp, 0.5, 1.0 ) ) )
            dc.DrawLine( x, 1, x, ey )
            hp += step
        
        # Draw the 'S' selector color range based upon the current color:
        sp = 1.0
        for x in xrange( sx0, sx0 + sdx ):
            dc.SetPen( wx.Pen( self._hls_to_wx( h, 0.5, sp ) ) )
            dc.DrawLine( x, 1, x, ey )
            sp -= step
        
        # Draw the 'L' selector color range based upon the current color:
        lp = 1.0
        for x in xrange( lx0, lx0 + sdx ):
            dc.SetPen( wx.Pen( self._hls_to_wx( h, lp, 1.0 ) ) )
            dc.DrawLine( x, 1, x, ey )
            lp -= step
        
        # Draw the current HLS selectors:
        dc.SetPen( wx.Pen( EdgeColor ) )
        self._draw_selector( dc, wdy, hx0 + int( round( range * h ) ) )
        self._draw_selector( dc, wdy, sx0 + int( round( range * (1.0 - s) ) ) )
        self._draw_selector( dc, wdy, lx0 + int( round( range * (1.0 - l) ) ) )
            
    #-- Private Methods --------------------------------------------------------

    def _draw_selector ( self, dc, dy, x ):
        """ Draws the current position of one of the HLS selectors.
        """
        dc.DrawLine( x, 3, x, dy - 3 )
        #dc.DrawLine( x - 3, 1, x + 4, 1 )
        #dc.DrawLine( x - 3, dy - 2, x + 4, dy - 2 )
        dc.DrawLine( x - 2, 1, x + 3, 1 )
        dc.DrawLine( x - 2, dy - 2, x + 3, dy - 2 )
        dc.DrawLine( x - 1, 2, x + 2, 2 )
        dc.DrawLine( x - 1, dy - 3, x + 2, dy - 3 )
        
    def _set_color ( self, event ):
        """ Sets the color based on the current mouse position.
        """
        x, y = event.GetX(), event.GetY()
        
        if 0 <= y < self.height:
            h, l, s = h0, l0, s0 = self.hls
            sdx     = float( self._sdx - 1 )

            if self._hx0 <= x <= self._hx0 + sdx:
                h = (x - self._hx0) / sdx
            elif self._lx0 <= x <= self._lx0 + sdx:
                l = 1.0 - ((x - self._lx0) / sdx)
            elif self._sx0 <= x <= self._sx0 + sdx:
                s = 1.0 - ((x - self._sx0) / sdx)
            else:
                return
                
            if (h != h0) or (l != l0) or (s != s0):
                self.color = self._hls_to_wx( h, l, s )
                self.hls   = ( h, l, s )
                if ((l == 0.0) or (l == 1.0)):
                    self.refresh()
        
#-------------------------------------------------------------------------------
#   'CustomHLSSelector' class:  
#-------------------------------------------------------------------------------        
    
class CustomHLSSelector ( BaseHLSSelector ):
    """ A larger (i.e. custom) HSL color space color selector.
    """

    # The HS color map bitmap (class constant):
    color_map_bitmap = \
        ImageResource( 'hs_color_map' ).create_image().ConvertToBitmap()
    
    # Override the default size for the window:
    size = Instance( wx.Size, ( 228, 102 ) )
        
    #-- wxPython Event Handlers ------------------------------------------------
    
    def _paint_dc ( self, dc ):
        """ Paints the HLS selector on the display.
        """
        # Draw the current color sample (if there is room):
        dc.SetPen( wx.Pen( EdgeColor ) )
        wdx = self.width
        if wdx >= 230:
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
                    self.refresh()
    
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
        
# Define the SimpleEditor, CustomEditor, etc. classes which are used by the
# editor factory for the color editor.
SimpleEditor   = SimpleColorEditor
CustomEditor   = CustomColorEditor
TextEditor     = TextColorEditor
ReadonlyEditor = ReadonlyColorEditor

### EOF #######################################################################