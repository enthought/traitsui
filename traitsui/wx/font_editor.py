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

""" Defines the various font editors and the font editor factory, for the
    wxPython user interface toolkit..
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import wx

from traits.api import Bool

from traitsui.editors.font_editor \
    import ToolkitEditorFactory as BaseToolkitEditorFactory

from editor_factory \
    import SimpleEditor as BaseSimpleEditor, \
    TextEditor as BaseTextEditor, \
    ReadonlyEditor as BaseReadonlyEditor

from editor \
    import Editor

from helper \
    import TraitsUIPanel, disconnect

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Standard font point sizes
PointSizes = [
   '8',  '9', '10', '11', '12', '14', '16', '18',
  '20', '22', '24', '26', '28', '36', '48', '72'
]

# All available font styles
Styles = ['Normal', 'Slant', 'Italic']

# All available font weights
Weights = ['Normal', 'Light', 'Bold']

# All available font facenames
facenames = None

#---------------------------------------------------------------------------
#  The wxPython ToolkitEditorFactory class.
#---------------------------------------------------------------------------
## We need to add wx-specific methods to the editor factory, and so we create
## a subclass of the BaseToolkitEditorFactory.

class ToolkitEditorFactory(BaseToolkitEditorFactory):
    """ wxPython editor factory for font editors.
    """

    show_style = Bool(False)
    show_weight = Bool(False)

    #---------------------------------------------------------------------------
    #  Returns a wxFont object corresponding to a specified object's font trait:
    #---------------------------------------------------------------------------

    def to_wx_font ( self, editor ):
        """ Returns a wxFont object corresponding to a specified object's font
        trait.
        """
        font = editor.value
        return wx.Font( font.GetPointSize(), font.GetFamily(), font.GetStyle(),
                        font.GetWeight(),    font.GetUnderlined(),
                        font.GetFaceName() )

    #---------------------------------------------------------------------------
    #  Gets the application equivalent of a wxPython Font value:
    #---------------------------------------------------------------------------

    def from_wx_font ( self, font ):
        """ Gets the application equivalent of a wxPython Font value.
        """
        return font

    #---------------------------------------------------------------------------
    #  Returns the text representation of the specified object trait value:
    #---------------------------------------------------------------------------

    def str_font ( self, font ):
        """ Returns the text representation of the specified object trait value.
        """
        weight = { wx.LIGHT: ' Light',
                    wx.BOLD:  ' Bold'   }.get( font.GetWeight(), '' )
        style  = { wx.SLANT: ' Slant',
                    wx.ITALIC:' Italic' }.get( font.GetStyle(), '' )
        return '%s point %s%s%s' % (
                font.GetPointSize(), font.GetFaceName(), style, weight )

    #---------------------------------------------------------------------------
    #  Returns a list of all available font facenames:
    #---------------------------------------------------------------------------

    def all_facenames ( self ):
        """ Returns a list of all available font facenames.
        """
        global facenames

        if facenames is None:
            facenames = FontEnumerator().facenames()
            facenames.sort()
        return facenames

#-------------------------------------------------------------------------------
#  'SimpleFontEditor' class:
#-------------------------------------------------------------------------------

class SimpleFontEditor ( BaseSimpleEditor ):
    """ Simple style of font editor, which displays a text field that contains
        a text representation of the font value (using that font if possible).
        Clicking the field displays a font selection dialog box.
    """

    #---------------------------------------------------------------------------
    #  Invokes the pop-up editor for an object trait:
    #---------------------------------------------------------------------------

    def popup_editor ( self, event ):
        """ Invokes the pop-up editor for an object trait.
        """
        font_data = wx.FontData()
        font_data.SetInitialFont( self.factory.to_wx_font( self ) )
        dialog = wx.FontDialog( self.control, font_data )
        if dialog.ShowModal() == wx.ID_OK:
            self.value = self.factory.from_wx_font(
                              dialog.GetFontData().GetChosenFont() )
            self.update_editor()

        dialog.Destroy()

    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------

    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        super( SimpleFontEditor, self ).update_editor()
        set_font( self )

    #---------------------------------------------------------------------------
    #  Returns the text representation of a specified font value:
    #---------------------------------------------------------------------------

    def string_value ( self, font ):
        """ Returns the text representation of a specified font value.
        """
        return self.factory.str_font( font )

#-------------------------------------------------------------------------------
#  'CustomFontEditor' class:
#-------------------------------------------------------------------------------

class CustomFontEditor ( Editor ):
    """ Custom style of font editor, which displays the following:

        * A combo box containing all available type face names.
        * A combo box containing the available type sizes.
        * A combo box containing the available type styles
    """

    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        # Create a panel to hold all of the buttons:
        self.control = panel = TraitsUIPanel( parent, -1 )
        sizer = wx.BoxSizer( wx.VERTICAL )

        # Add all of the font choice controls:
        sizer2    = wx.BoxSizer( wx.HORIZONTAL )
        facenames = self.factory.all_facenames()
        control   = self._facename = wx.Choice( panel, -1, wx.Point( 0, 0 ),
                                                wx.Size( -1, -1 ), facenames )

        sizer2.Add( control, 4, wx.EXPAND )
        wx.EVT_CHOICE( panel, control.GetId(), self.update_object_parts )

        control = self._point_size = wx.Choice( panel, -1, wx.Point( 0, 0 ),
                                                wx.Size( -1, -1 ), PointSizes )
        sizer2.Add( control, 1, wx.EXPAND | wx.LEFT, 3 )
        wx.EVT_CHOICE( panel, control.GetId(), self.update_object_parts )

        if self.factory.show_style:
            self._style = wx.Choice(panel, -1, wx.Point(0,0),
                                    wx.Size(-1, -1), Styles)
            sizer2.Add(self._style, 1, wx.EXPAND | wx.LEFT, 3)
            wx.EVT_CHOICE( panel, self._style.GetId(), self.update_object_parts )

        if self.factory.show_weight:
            self._weight = wx.Choice(panel, -1, wx.Point(0,0),
                                    wx.Size(-1, -1), Weights)
            sizer2.Add(self._weight, 1, wx.EXPAND | wx.LEFT, 3)
            wx.EVT_CHOICE( panel, self._weight.GetId(), self.update_object_parts )

        sizer.Add( sizer2, 0, wx.EXPAND )


        # Set-up the layout:
        panel.SetSizer( sizer )

        self.set_tooltip()

    #---------------------------------------------------------------------------
    #  Disposes of the contents of an editor:
    #---------------------------------------------------------------------------

    def dispose ( self ):
        """ Disposes of the contents of an editor.
        """
        disconnect( self._facename,   wx.EVT_CHOICE )
        disconnect( self._point_size, wx.EVT_CHOICE )
        if self.factory.show_style:
            disconnect(self._style, wx.EVT_CHOICE)
        if self.factory.show_weight:
            disconnect(self._weight, wx.EVT_CHOICE)

        super( CustomFontEditor, self ).dispose()

    #---------------------------------------------------------------------------
    #  Handles the user modifying one of the font components:
    #---------------------------------------------------------------------------

    def update_object_parts ( self, event ):
        """ Handles the user modifying one of the font components.
        """
        point_size = int( self._point_size.GetStringSelection() )
        facename   = self._facename.GetStringSelection()

        style = wx.FONTSTYLE_NORMAL
        if self.factory.show_style:
            style += self._style.GetCurrentSelection()

        weight = wx.FONTWEIGHT_NORMAL
        if self.factory.show_weight:
            weight += self._weight.GetCurrentSelection()

        font       = wx.Font( point_size, wx.DEFAULT, style, weight,
                              faceName = facename )
        self.value = self.factory.from_wx_font( font )

    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------

    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        font = self.factory.to_wx_font( self )

        try:
           self._facename.SetStringSelection( font.GetFaceName() )
        except:
           self._facename.SetSelection( 0 )

        try:
           self._point_size.SetStringSelection( str( font.GetPointSize() ) )
        except:
           self._point_size.SetSelection( 0 )

    #---------------------------------------------------------------------------
    #  Returns the text representation of a specified font value:
    #---------------------------------------------------------------------------

    def string_value ( self, font ):
        """ Returns the text representation of a specified font value.
        """
        return self.factory.str_font( font )


#-------------------------------------------------------------------------------
#  'TextFontEditor' class:
#-------------------------------------------------------------------------------

class TextFontEditor ( BaseTextEditor ):
    """ Text style of font editor, which displays an editable text field
        containing a text representation of the font value (using that font if
        possible).
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
        """ Updates the editor when the object trait changes external to the
            editor.
        """
        super( TextFontEditor, self ).update_editor()
        set_font( self )

    #---------------------------------------------------------------------------
    #  Returns the text representation of a specified font value:
    #---------------------------------------------------------------------------

    def string_value ( self, font ):
        """ Returns the text representation of a specified font value.
        """
        return self.factory.str_font( font )

#-------------------------------------------------------------------------------
#  'ReadonlyFontEditor' class:
#-------------------------------------------------------------------------------

class ReadonlyFontEditor ( BaseReadonlyEditor ):
    """ Read-only style of font editor, which displays a read-only text field
        containing a text representation of the font value (using that font if
        possible).
    """

    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------

    def update_editor ( self ):
        """ Updates the editor when the object trait changes external to the
            editor.
        """
        super( ReadonlyFontEditor, self ).update_editor()
        set_font( self )

    #---------------------------------------------------------------------------
    #  Returns the text representation of a specified font value:
    #---------------------------------------------------------------------------

    def string_value ( self, font ):
        """ Returns the text representation of a specified font value.
        """
        return self.factory.str_font( font )

#-------------------------------------------------------------------------------
#  Set the editor control's font to match a specified font:
#-------------------------------------------------------------------------------

def set_font ( editor ):
    """ Sets the editor control's font to match a specified font.
    """
    font = editor.factory.to_wx_font( editor )
    font.SetPointSize( min( 10, font.GetPointSize() ) )
    editor.control.SetFont( font )

#-------------------------------------------------------------------------------
#  'FontEnumerator' class:
#-------------------------------------------------------------------------------

class FontEnumerator ( wx.FontEnumerator ):
    """ An enumeration of fonts.
    """
    #---------------------------------------------------------------------------
    #  Returns a list of all available font facenames:
    #---------------------------------------------------------------------------

    def facenames ( self ):
        """ Returns a list of all available font facenames.
        """
        self._facenames = []
        self.EnumerateFacenames()
        return self._facenames

    #---------------------------------------------------------------------------
    #  Adds a facename to the list of facenames:
    #---------------------------------------------------------------------------

    def OnFacename ( self, facename ):
        """ Adds a facename to the list of facenames.
        """
        self._facenames.append( facename )
        return True

# Define the names SimpleEditor, CustomEditor, TextEditor and ReadonlyEditor
# which are looked up by the editor factory for the font editor.
SimpleEditor = SimpleFontEditor
CustomEditor = CustomFontEditor
TextEditor = TextFontEditor
ReadonlyEditor = ReadonlyFontEditor

### EOF #######################################################################
