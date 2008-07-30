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

from enthought.traits.api \
    import HasPrivateTraits, Bool, Instance, Str, Color, Any, Event

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
    import is_mac
    
from helper \
    import traits_ui_panel, position_window, init_wx_handlers
    
# Version dependent imports (ColourPtr not defined in wxPython 2.5):
try:
    ColorTypes = ( wx.Colour, wx.ColourPtr )    
except:
    ColorTypes = wx.Colour

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
        if not hasattr( self.control, 'is_custom' ):
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
                    kind    = 'popup',
                    handler = PopupColorHandler() ),
                parent = self.control )
        else:   
            self.busy  = True
            factory    = self.factory
            color_data = wx.ColourData()
            color_data.SetColour( self.factory.to_wx_color( self ) )
            color_data.SetChooseFull( True )
            dialog = wx.ColourDialog( self.control, color_data )
            position_window( dialog, parent = self.control )
            if dialog.ShowModal() == wx.ID_OK:
                self.value = factory.from_wx_color( 
                                  dialog.GetColourData().GetColour() )
                self.update_editor()
                
            dialog.Destroy() 
            self.busy = False
                
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

class CustomColorEditor ( SimpleColorEditor ):
    """ Custom style of color editor, which displays a color editor panel.
    """
    
    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.control = color_editor_for( self, parent )

    #---------------------------------------------------------------------------
    #  Disposes of the contents of an editor:    
    #---------------------------------------------------------------------------

    def dispose ( self ):
        """ Disposes of the contents of an editor.
        """
        self.control._swatch_editor.dispose()
        
        super( CustomColorEditor, self ).dispose()

    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------

    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the 
            editor.
        """
        pass

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

#----------------------------------------------------------------------------
#  Creates a custom color editor panel for a specified editor:
#----------------------------------------------------------------------------

def color_editor_for ( editor, parent ):
    """ Creates a custom color editor panel for a specified editor.
    """
    # Create a panel to hold all of the controls:
    panel = traits_ui_panel( parent, -1, size = wx.Size( 0, 0 ) )
        
    # Create the large color swatch:
    sizer = wx.BoxSizer( wx.HORIZONTAL )
    panel._swatch_editor = swatch_editor = editor.factory.simple_editor(
              editor.ui, editor.object, editor.name, editor.description, panel )
    swatch_editor.prepare( panel )
    control = swatch_editor.control
    control.is_custom = True
    control.SetSize( wx.Size( 101, 61 ) )
    sizer.Add( control, 0, wx.EXPAND )
    
    # Create the color chip (color swatches) control:
    panel._color_chip = ColorChip( panel )
    panel._color_chip.on_trait_change(
        swatch_editor.update_object_from_swatch, 'color' )
    control = panel._color_chip.control
    sizer.Add( control )
    editor.set_tooltip( control )
   
    # Set-up the layout:
    panel.SetSizerAndFit( sizer )

    # Return the panel as the result:
    return panel

#-------------------------------------------------------------------------------
#  'ColorChip' class:
#-------------------------------------------------------------------------------

# Standard color samples:
color_choices = ( 0, 51, 102, 153, 204, 255 )
color_samples = [ None ] * 216
i             = 0
for r in color_choices:
    for g in color_choices:
        for b in color_choices:
            color_samples[i] = wx.Colour( r, g, b )
            i += 1  
            
# The color drawn around the edge of each sample:            
EdgeColor = wx.Colour( 64, 64, 64 )             

class ColorChip ( HasPrivateTraits ):
    
    # The current color:
    color = Color
    
    # The wx Window that implements the color chip:
    control = Instance( wx.Window )
    
    def __init__ ( self, parent, **traits ):
        """ Creates the color chip window and initializes it.
        """
        super( ColorChip, self ).__init__( **traits )
        
        self.control = wx.Window( parent, -1, size = wx.Size( 361, 61 ) )
        init_wx_handlers( self.control, self )
        
    #-- Private Methods --------------------------------------------------------
    
    def _set_color ( self, event ):
        """ Sets the current color based upon the position of the pointer.
        """
        x,  y  = event.GetX(), event.GetY()
        dx, dy = self.control.GetSizeTuple()
        if (0 <= x < (dx - 1)) and (0 <= y < (dy - 1)):
            color = color_samples[ (36 * (y / 10)) + (x / 10) ]
            self.color = ( color.Red(), color.Green(), color.Blue() )
        
    #-- wxPython Event Handlers ------------------------------------------------
        
    def _erase_background ( self, event ):
        pass
    
    def _paint ( self, event ):
        dc = wx.PaintDC( self.control )
        dc.SetPen( wx.Pen( EdgeColor ) )
        i = 0
        for y in xrange( 6 ):
            for x in xrange( 36 ):
                dc.SetBrush( wx.Brush( color_samples[i], wx.SOLID ) )
                dc.DrawRectangle( 10 * x, 10 * y, 11, 11 )
                i += 1
        
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
        self.control = wx.Window( parent, -1 )
        init_wx_handlers( self.control, self )
        
        if is_mac:
            self.control.SetSize( wx.Size( -1, 23 ) )
        
    #-- wxPython Event Handlers ------------------------------------------------
        
    def _erase_background ( self, event ):
        pass
    
    def _paint ( self, event ):
        control = self.control
        dx, dy  = control.GetSizeTuple()
        dc      = wx.PaintDC( control )
        dc.SetPen( wx.Pen( EdgeColor ) )
        dc.SetBrush( wx.Brush( control.GetBackgroundColour(), wx.SOLID ) )
        dc.DrawRectangle( 0, 0, dx, dy )
        dc.SetFont( control.GetFont() )
        dc.DrawText( self.text, 3, 3 )
        
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
                         Item( self.name, id         = 'color_editor',
                                          style      = 'custom',
                                          show_label = False,
                                          padding    = -4,
                                          editor     = self.factory.factory ),
                         kind = 'subpanel' ) )

class PopupColorEditor ( BasicEditorFactory ):

    klass = _PopupColorEditor
    
    # The factory to use for creating sub color editors:
    factory = Instance( EditorFactory )
    
#-------------------------------------------------------------------------------
#  'PopupColorHandler' class:
#-------------------------------------------------------------------------------

class PopupColorHandler ( Handler ):
    
    def close ( self, info, result ):
        """ Returns whether the view can be closed now or not.
        """
        # fixme: Hmmm...I would if there is a cleaner way to do this...
        return (not info.color_editor.editor_ui.info.color_editor.control.
                         _swatch_editor.busy)
        
