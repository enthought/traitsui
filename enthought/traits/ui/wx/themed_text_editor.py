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

from enthought.traits.api \
    import Enum, Instance
    
from enthought.traits.ui.wx.editor \
    import Editor
    
from enthought.traits.ui.wx.basic_editor_factory \
    import BasicEditorFactory
    
from enthought.traits.ui.ui_traits \
    import Image

from enthought.pyface.image_resource \
    import ImageResource
    
from image_slice \
    import ImageText

#-------------------------------------------------------------------------------
#  '_ThemedTextEditor' class:
#-------------------------------------------------------------------------------
                               
class _ThemedTextEditor ( Editor ):
    """ Traits UI simple, read-only single line text editor with a themed
        (i.e. image background).
    """
        
    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------
        
    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.control = ImageText( parent, self.factory.theme, 
                                  alignment = self.factory.alignment ) 
        self.set_tooltip()
                        
    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------

    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        self.control.SetLabel( self.str_value )
                    
#-------------------------------------------------------------------------------
#  Create the editor factory object:
#-------------------------------------------------------------------------------

# wxPython editor factory for themed text editors:
class ThemedTextEditor ( BasicEditorFactory ):
    
    # The editor class to be created:
    klass = _ThemedTextEditor
    
    # The background theme image to display:
    theme = Image
    
    # The alignment of the text within the control:
    alignment = Enum( 'left', 'right', 'center' )
                 
