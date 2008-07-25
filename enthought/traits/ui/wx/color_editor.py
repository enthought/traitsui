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
    import View

from editor_factory \
    import EditorFactory, SimpleEditor, TextEditor, ReadonlyEditor

from editor \
    import Editor

from helper \
    import traits_ui_panel, position_window, top_level_window_for, \
           init_wx_handlers
    
from constants \
    import WindowColor
    
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
                
            self._popup_dialog = ColorDialog( self )
        else:    
            update_handler = self.control.update_handler
            if update_handler is not None:
                update_handler( False )
            color_data = wx.ColourData()
            color_data.SetColour( self.factory.to_wx_color( self ) )
            color_data.SetChooseFull( True )
            dialog = wx.ColourDialog( self.control, color_data )
            position_window( dialog, parent = self.control )
            if dialog.ShowModal() == wx.ID_OK:
                self.value = self.factory.from_wx_color( 
                                  dialog.GetColourData().GetColour() )
                self.update_editor()
                
            dialog.Destroy() 
            
            if update_handler is not None:
                update_handler( True )
                
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
        self.value = color
        self.update_editor()
        
    #---------------------------------------------------------------------------
    #  Handles the user selecting a color:
    #---------------------------------------------------------------------------
        
    def color_selected ( self, object, name, old, color ):
        """ Handles the user selecting a color.
        """
        handler = object.control.update_handler
        if handler is not None:
            handler()

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
        self.control = traits_ui_panel( parent, -1, size = wx.Size( 50, 16 ) )

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

def color_editor_for ( editor, parent, update_handler = None ):
    """ Creates a custom color editor panel for a specified editor.
    """
    # Create a panel to hold all of the controls:
    panel = traits_ui_panel( parent, -1, size = wx.Size( 0, 0 ) )
    if update_handler is None:
        panel.Show( False )
        
    # Create the large color swatch:
    sizer = wx.BoxSizer( wx.HORIZONTAL )
    panel._swatch_editor = swatch_editor = editor.factory.simple_editor( 
              editor.ui, editor.object, editor.name, editor.description, panel )
    swatch_editor.prepare( panel )
    control = swatch_editor.control
    control.is_custom      = True
    control.update_handler = update_handler
    control.SetSize( wx.Size( 81, 61 ) )
    sizer.Add( control )
    
    # Create the color chip (color swatches) control:
    panel._color_chip = ColorChip( panel )
    panel._color_chip.on_trait_change(
        swatch_editor.update_object_from_swatch, 'color' )
    panel._color_chip.on_trait_change(
        swatch_editor.color_selected, 'selected' )
    control = panel._color_chip.control
    sizer.Add( control )
    editor.set_tooltip( control )
    control.update_handler = update_handler
   
    # Set-up the layout:
    panel.SetSizerAndFit( sizer )

    # Return the panel as the result:
    return panel

#-------------------------------------------------------------------------------
#  'ColorDialog' class:  
#-------------------------------------------------------------------------------

class ColorDialog ( wx.Dialog ):
    """ Dialog box for selecting a color.
    """
    
    #---------------------------------------------------------------------------
    #  Initializes the object:
    #---------------------------------------------------------------------------

    def __init__ ( self, editor ):
        """ Initializes the object.
        """
        control = editor.control
        wx.Dialog.__init__( self, control, -1, '',
                           style = wx.SIMPLE_BORDER | wx.FRAME_FLOAT_ON_PARENT )
        self.SetBackgroundColour( WindowColor )
        wx.EVT_ACTIVATE( self, self._on_close_dialog )
        self._closed    = False
        self._closeable = True

        panel = color_editor_for( editor, self, self._close_dialog )
        self._swatch_editor = panel._swatch_editor

        sizer = wx.BoxSizer( wx.VERTICAL )
        sizer.Add( panel )
        self.SetSizerAndFit( sizer )
        position_window( self, parent = control )
        
        tlw = top_level_window_for( control )
        if isinstance( tlw, wx.Dialog ) and tlw.IsModal():
            self.ShowModal()
        else:
            self.Show()

    #---------------------------------------------------------------------------
    #  Closes the dialog:
    #---------------------------------------------------------------------------

    def _on_close_dialog ( self, event, rc = False ):
        """ Called when the user closes the dialog.
        """
        if not event.GetActive():
            self._close_dialog()

    #---------------------------------------------------------------------------
    #  Closes the dialog:
    #---------------------------------------------------------------------------

    def _close_dialog ( self, closeable = None ):
        """ Closes the dialog.
        """
        if closeable is not None:
            self._closeable = closeable
            
        if self._closeable and (not self._closed):
            self._closed = True
            self._swatch_editor.dispose()
            self.Destroy()

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
    
    # The user has selected a color:
    selected = Event
    
    # The wx Window that implements the color chip:
    control = Instance( wx.Window )
    
    def __init__ ( self, parent ):
        """ Creates the color chip window and initializes it.
        """
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
        self.selected = True
        
    def _motion ( self, event ):
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
        
