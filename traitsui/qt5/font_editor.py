#------------------------------------------------------------------------------
# Copyright (c) 2007, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD license.
# However, when used with the GPL version of PyQt the additional terms described in the PyQt GPL exception also apply

#
# Author: Riverbank Computing Limited
#------------------------------------------------------------------------------

""" Defines the various font editors and the font editor factory, for the
    PyQt user interface toolkit..
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from pyface.qt import QtCore, QtGui

from traitsui.editors.font_editor \
    import ToolkitEditorFactory as BaseToolkitEditorFactory

from editor_factory \
    import SimpleEditor as BaseSimpleEditor, \
    TextEditor as BaseTextEditor, \
    ReadonlyEditor as BaseReadonlyEditor

from editor \
    import Editor

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Standard font point sizes
PointSizes = [
   '8',  '9', '10', '11', '12', '14', '16', '18',
  '20', '22', '24', '26', '28', '36', '48', '72'
]

#---------------------------------------------------------------------------
#  The PyQtToolkitEditorFactory class.
#---------------------------------------------------------------------------
## We need to add qt4-specific methods to the editor factory, and so we create
## a subclass of the BaseToolkitEditorFactory.

class ToolkitEditorFactory(BaseToolkitEditorFactory):
    """ PyQt editor factory for font editors.
    """
    #---------------------------------------------------------------------------
    #  Returns a QFont object corresponding to a specified object's font trait:
    #---------------------------------------------------------------------------

    def to_qt4_font ( self, editor ):
        """ Returns a QFont object corresponding to a specified object's font
        trait.
        """
        return QtGui.QFont(editor.value)

    #---------------------------------------------------------------------------
    #  Gets the application equivalent of a QFont value:
    #---------------------------------------------------------------------------

    def from_qt4_font ( self, font ):
        """ Gets the application equivalent of a QFont value.
        """
        return font

    #---------------------------------------------------------------------------
    #  Returns the text representation of the specified object trait value:
    #---------------------------------------------------------------------------

    def str_font ( self, font ):
        """ Returns the text representation of the specified object trait value.
        """
        weight = { QtGui.QFont.Light: ' Light',
                   QtGui.QFont.Bold:  ' Bold'   }.get(font.weight(), '')
        style  = { QtGui.QFont.StyleOblique: ' Slant',
                   QtGui.QFont.StyleItalic:  ' Italic' }.get(font.style(), '')
        return '%s point %s%s%s' % (
               font.pointSize(), font.family(), style, weight )

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

    def popup_editor(self):
        """ Invokes the pop-up editor for an object trait.
        """
        fnt, ok = QtGui.QFontDialog.getFont(self.factory.to_qt4_font(self),
                                            self.control)

        if ok:
            self.value = self.factory.from_qt4_font(fnt)
            self.update_editor()

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

        * A text field containing the text representation of the font value
          (using that font if possible).
        * A combo box containing all available type face names.
        * A combo box containing the available type sizes.
    """
    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.control = QtGui.QWidget()
        layout = QtGui.QVBoxLayout(self.control)
        layout.setContentsMargins(0, 0, 0, 0)

        # Add the standard font control:
        self._font = font = QtGui.QLineEdit(self.str_value)
        QtCore.QObject.connect(font, QtCore.SIGNAL('editingFinished()'),
                self.update_object)
        layout.addWidget(font)

        # Add all of the font choice controls:
        layout2 = QtGui.QHBoxLayout()

        self._facename = control = QtGui.QFontComboBox()
        control.setEditable(False)
        QtCore.QObject.connect(control,
                QtCore.SIGNAL('currentFontChanged(QFont)'),
                self.update_object_parts)
        layout2.addWidget(control)

        self._point_size = control = QtGui.QComboBox()
        control.addItems(PointSizes)
        QtCore.QObject.connect(control,
                QtCore.SIGNAL('currentIndexChanged(int)'),
                self.update_object_parts)
        layout2.addWidget(control)

        # These don't have explicit controls.
        self._bold = self._italic = False

        layout.addLayout(layout2)

    #---------------------------------------------------------------------------
    #  Handles the user changing the contents of the font text control:
    #---------------------------------------------------------------------------

    def update_object (self):
        """ Handles the user changing the contents of the font text control.
        """
        self.value = unicode(self._font.text())
        self._set_font(self.factory.to_qt4_font(self))
        self.update_editor()

    #---------------------------------------------------------------------------
    #  Handles the user modifying one of the font components:
    #---------------------------------------------------------------------------

    def update_object_parts (self):
        """ Handles the user modifying one of the font components.
        """
        fnt = self._facename.currentFont()

        fnt.setBold(self._bold)
        fnt.setItalic(self._italic)

        psz = int(self._point_size.currentText())
        fnt.setPointSize(psz)

        self.value = self.factory.from_qt4_font(fnt)

        self._font.setText(self.str_value)
        self._set_font(fnt)

    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------

    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        font = self.factory.to_qt4_font( self )

        self._bold = font.bold()
        self._italic = font.italic()

        self._facename.setCurrentFont(font)

        try:
           idx = PointSizes.index(str(font.pointSize()))
        except ValueError:
           idx = PointSizes.index('9')

        self._point_size.setCurrentIndex(idx)

    #---------------------------------------------------------------------------
    #  Returns the text representation of a specified font value:
    #---------------------------------------------------------------------------

    def string_value ( self, font ):
        """ Returns the text representation of a specified font value.
        """
        return self.factory.str_font( font )

    #---------------------------------------------------------------------------
    #  Returns the editor's control for indicating error status:
    #---------------------------------------------------------------------------

    def get_error_control ( self ):
        """ Returns the editor's control for indicating error status.
        """
        return [ self._font, self._facename, self._point_size ]

    #-- Private Methods --------------------------------------------------------

    def _set_font ( self, font ):
        """ Sets the font used by the text control to the specified font.
        """
        font.setPointSize( min( 10, font.pointSize() ) )
        self._font.setFont( font )

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

    def update_object(self):
        """ Handles the user changing the contents of the edit control.
        """
        self.value = unicode(self.control.text())

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
    editor.control.setFont(editor.factory.to_qt4_font(editor))


# Define the names SimpleEditor, CustomEditor, TextEditor and ReadonlyEditor
# which are looked up by the editor factory for the font editor.
SimpleEditor = SimpleFontEditor
CustomEditor = CustomFontEditor
TextEditor = TextFontEditor
ReadonlyEditor = ReadonlyFontEditor
