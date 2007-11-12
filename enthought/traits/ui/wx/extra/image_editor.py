#-------------------------------------------------------------------------------
#
#  Traits UI 'display only' image editor.
#
#  Written by: David C. Morrill
#
#  Date: 06/05/2007
#
#  (c) Copyright 2007 by Enthought, Inc.
#
#-------------------------------------------------------------------------------

""" Traits UI 'display only' image editor.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------
    
from enthought.traits.api \
    import Instance
    
from enthought.traits.ui.ui_traits \
    import Image, convert_bitmap
    
from enthought.traits.ui.wx.editor \
    import Editor
    
from enthought.traits.ui.wx.basic_editor_factory \
    import BasicEditorFactory
    
from enthought.traits.ui.wx.image_control \
    import ImageControl

from enthought.pyface.image_resource \
    import ImageResource

#-------------------------------------------------------------------------------
#  '_ImageEditor' class:
#-------------------------------------------------------------------------------
                               
class _ImageEditor ( Editor ):
    """ Traits UI 'display only' image editor.
    """
        
    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------
        
    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        image = self.factory.image
        if image is None:
            image = self.value
            
        self.control = ImageControl( parent, convert_bitmap( image ), 
                                     padding = 0 )
            
        self.set_tooltip()
                        
    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------

    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        if self.factory.image is None:
            value = self.value
            if isinstance( value, ImageResource ):
                self.control.Bitmap( convert_bitmap( value ) )
                    
#-------------------------------------------------------------------------------
#  Create the editor factory object:
#-------------------------------------------------------------------------------

# wxPython editor factory for image editors:
class ImageEditor ( BasicEditorFactory ):
    
    # The editor class to be created:
    klass = _ImageEditor
    
    # The optional image resource to be displayed by the editor (if not
    # specified, the editor's object value is used as the ImageResource to
    # display):
    image = Image
    
