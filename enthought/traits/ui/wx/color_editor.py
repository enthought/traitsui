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
#------------------------------------------------------------------------------

""" Defines the various color editors for the Wx user interface toolkit.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import wx

from enthought.traits.ui.editors.color_editor \
    import ToolkitEditorFactory as BaseToolkitEditorFactory

from editor_factory \
    import SimpleEditor as BaseSimpleEditor, \
    ReadonlyEditor as BaseReadonlyEditor

# Version dependent imports (ColourPtr not defined in wxPython 2.5):
try:
    ColorTypes = (wx.Colour, wx.ColourPtr)
except:
    ColorTypes = wx.Colour

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Standard color samples:
color_samples = []

#---------------------------------------------------------------------------
#  The Wx ToolkitEditorFactory class.
#---------------------------------------------------------------------------

class ToolkitEditorFactory(BaseToolkitEditorFactory):
    """ Wx editor factory for color editors.
    """
    
    def to_wx_color ( self, editor ):
        """ Gets the wxPython color equivalent of the object trait.
        """
        if self.mapped:
            attr = getattr( editor.object, editor.name + '_' )
        else:
            attr = getattr( editor.object, editor.name )
           
        if isinstance(attr, tuple):
            attr = wx.Colour( *[ int( round( c * 255.0 ) )
                             for c in attr ] )
        return attr
           
         
    #---------------------------------------------------------------------------
    #  Gets the application equivalent of a wxPython value:
    #---------------------------------------------------------------------------
        
    def from_wx_color ( self, color ):
        """ Gets the application equivalent of a wxPython value.
        """
        return color.Red(), color.Green(), color.Blue()
           
    #---------------------------------------------------------------------------
    #  Returns the text representation of a specified color value:
    #---------------------------------------------------------------------------
      
    def str_color ( self, color ):
        """ Returns the text representation of a specified color value.
        """
        if isinstance( color, ColorTypes ):
            alpha = color.Alpha()
            if alpha == 255:
                return "rgb(%d,%d,%d)" % (
                        color.Red(), color.Green(), color.Blue() )
   
            return "rgb(%d,%d,%d,%d)" % (
                    color.Red(), color.Green(), color.Blue(), alpha )
               
        return color
    
#-------------------------------------------------------------------------------
#  'SimpleColorEditor' class:
#-------------------------------------------------------------------------------
                               
class SimpleColorEditor ( BaseSimpleEditor ):
    """ Simple style of color editor, which displays a text field whose 
    background color is the color value. Selecting the text field displays
    a dialog box for selecting a new color value.
    """
    
    #---------------------------------------------------------------------------
    #  Invokes the pop-up editor for an object trait:
    #---------------------------------------------------------------------------
 
    def init ( self, parent ):
        """
        Finishes initializing the editor by creating the underlying widget.
        """
        
        self.control = wx.ColourPickerCtrl(parent,
                                           size = (160,-1),
                                           style = wx.CLRP_USE_TEXTCTRL
                                                |  wx.CLRP_SHOW_LABEL)
        self.control.SetColour(self.factory.to_wx_color(self))
        
        self.control.Bind(wx.EVT_COLOURPICKER_CHANGED, self.color_selected)                
        return

    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------

    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the 
            editor.
        """
        self.control.SetColour(self.factory.to_wx_color(self))


    def color_selected(self, event):
        """
        Event for when color is selected
        """
        
        color = event.GetColour()
        try:
            self.value = self.factory.from_wx_color(color)
        except ValueError:
            pass
            
        return

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
        self.control = wx.TextCtrl(parent, style=wx.TE_READONLY)

    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------

    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the 
            editor.
        """
        #super( ReadonlyColorEditor, self ).update_editor()
        self.control.SetValue(self.string_value(self.value))
        set_color( self )

    #---------------------------------------------------------------------------
    #  Returns the text representation of a specified color value:
    #---------------------------------------------------------------------------

    def string_value ( self, color ):
        """ Returns the text representation of a specified color value.
        """
        return self.factory.str_color( color ) 

#-------------------------------------------------------------------------------
#   Sets the color of the specified editor's color control: 
#-------------------------------------------------------------------------------

def set_color ( editor ):
    """  Sets the color of the specified color control.
    """
    color = editor.factory.to_wx_color(editor)
    editor.control.SetBackgroundColour(color)


# Define the SimpleEditor, CustomEditor, etc. classes which are used by the
# editor factory for the color editor.
SimpleEditor = CustomEditor = TextEditor = SimpleColorEditor
ReadonlyEditor = ReadonlyColorEditor
#SimpleEditor   = SimpleColorEditor
#CustomEditor   = CustomColorEditor
#TextEditor     = TextColorEditor
#ReadonlyEditor = ReadonlyColorEditor
