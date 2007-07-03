#-------------------------------------------------------------------------------
#
#  Traits UI themed button editor.
#
#  Written by: David C. Morrill
#
#  Date: 06/26/2007
#
#  (c) Copyright 2007 by Enthought, Inc.
#
#-------------------------------------------------------------------------------

""" Traits UI themed button editor.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import wx

from enthought.traits.api \
    import HasPrivateTraits, Instance, Str
    
from enthought.traits.ui.ui_traits \
    import Image, HasPadding, Padding, Position, Alignment, Spacing
    
from enthought.traits.ui.wx.editor \
    import Editor
    
from enthought.traits.ui.wx.basic_editor_factory \
    import BasicEditorFactory
    
from themed_control \
    import ThemedControl

#-------------------------------------------------------------------------------
#  '_ThemedButtonEditor' class:
#-------------------------------------------------------------------------------
                               
class _ThemedButtonEditor ( Editor ):
    """ Traits UI themed button editor.
    """
    
    # The ThemedControl used for the button:
    button = Instance( ThemedControl )
        
    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------
        
    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        # Create the button and its control:
        factory = self.factory
        label   = factory.label
        if (label == '') and (factory.image is None):
            label = self.item.label
            
        self.button = button = ThemedControl( **factory.get(
            'theme', 'image', 'position', 'spacing', 'padding' ) ).set(
            text       = label, 
            alignment  = 'center', 
            controller = self,
            min_size   = ( 80, 0 ) )
        self.control = button.create_control( parent )

        # Set the tooltip:
        self.set_tooltip()
                        
    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------

    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        pass
    
    #-- ThemedControl Event Handlers -------------------------------------------
    
    def normal_left_down ( self, x, y, event ):
        self.button.set( state  = 'down',
                         offset = ( 1, 1 ),
                         theme  = self.factory.down_theme or self.factory.theme)
        
    def normal_mouse_move ( self, x, y, event ):
        hover = self.factory.hover_theme
        if hover is not None:
            self.button.set( state = 'hover', theme = hover )
            self.control.CaptureMouse()
            
    def hover_left_down ( self, x, y, event ):
        self.control.ReleaseMouse()
        self.normal_left_down( x, y, event )
        
    def hover_mouse_move ( self, x, y, event ):
        if not self.button.in_control( x, y ):
            self.control.ReleaseMouse()
            self.button.set( state = 'normal', theme = self.factory.theme )
            
    def down_left_up ( self, x, y, event ):
        if self.button.in_control( x, y ):
            self.value = True
            
        self.button.set( state  = 'normal', 
                         offset = ( 0, 0 ), 
                         theme  = self.factory.theme )
        
    def down_mouse_move ( self, x, y, event ):
        theme = self.factory.down_theme or self.factory.theme
        is_in = self.button.in_control( x, y )
        if not is_in:
            theme = self.factory.theme
            
        self.button.set( offset = ( is_in, is_in ), theme = theme )
           
#-------------------------------------------------------------------------------
#  Create the editor factory object:
#-------------------------------------------------------------------------------

# wxPython editor factory for themed button editors:
class ThemedButtonEditor ( BasicEditorFactory ):
    
    # The editor class to be created:
    klass = _ThemedButtonEditor
    
    # The button label:
    label = Str
    
    # The basic theme for the button (i.e. the 'up' state):
    theme = Image( '@BG5' )
    
    # The optional 'down' state theme for the button:
    down_theme = Image( '@BE5' )
    
    # The optional 'hover' state theme for the button:
    hover_theme = Image( '@BG6' )
    
    # The optional image to display in the button:
    image = Image
    
    # The position of the image relative to the text:
    position = Position
    
    # The amount of space between the image and the text:
    spacing = Spacing
    
    # The amount of padding between the text/image and the border:
    padding = HasPadding( Padding( left = 4, right = 4, top = 2, bottom = 2 ) )
                 
