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
    import Instance, Str, on_trait_change

from enthought.traits.ui.api \
    import Theme
    
from enthought.traits.ui.ui_traits \
    import ATheme, AView, Image, Margins, Position, Spacing
    
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
            label = self.item.get_label( self.ui )
            
        self.button = button = ThemedControl( **factory.get(
            'theme', 'image', 'position', 'spacing' ) ).set(
            text              = label, 
            controller        = self,
            default_alignment = 'center',
            min_size          = ( 80, 0 ) )
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
    
    #-- Trait Event Handlers ---------------------------------------------------
    
    @on_trait_change( 'button.enabled' )
    def _on_enabled_changed ( self ):
        """ Handles the button 'enabled' state changing.
        """
        if self.button.enabled:
            self.button.set( state  = 'normal', 
                             offset = ( 0, 0 ),
                             theme  = self.factory.theme )
        else:
            self.button.set( state  = 'disabled', 
                             offset = ( 0, 0 ),
                             theme  = self.factory.disabled_theme or 
                                      self.factory.theme )
    
    #-- ThemedControl Event Handlers -------------------------------------------
    
    def normal_left_down ( self, x, y, event ):
        if self.control.IsEnabled():
            self.button.set( state  = 'down',
                             offset = ( 1, 1 ),
                             theme  = self.factory.down_theme or 
                                      self.factory.theme )
        
    def normal_motion ( self, x, y, event ):
        hover = self.factory.hover_theme
        if self.control.IsEnabled() and (hover is not None):
            self.button.set( state = 'hover', theme = hover )
            self.control.CaptureMouse()
            
    def hover_left_down ( self, x, y, event ):
        self.control.ReleaseMouse()
        self.normal_left_down( x, y, event )
        
    def hover_motion ( self, x, y, event ):
        if not self.button.in_control( x, y ):
            self.control.ReleaseMouse()
            self.button.set( state = 'normal', theme = self.factory.theme )
            
    def down_left_up ( self, x, y, event ):
        if self.button.in_control( x, y ):
            self.value = True
            
            # If there is an associated view, display it:
            if self.factory.view is not None:
                self.object.edit_traits( view   = self.factory.view,
                                         parent = self.control )
            
        self.button.set( state  = 'normal', 
                         offset = ( 0, 0 ), 
                         theme  = self.factory.theme )
        
    def down_motion ( self, x, y, event ):
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
    theme = ATheme( '@BG5' )
    
    # The optional 'down' state theme for the button:
    down_theme = ATheme( '@BE5' )
    
    # The optional 'hover' state theme for the button:
    hover_theme = ATheme( '@BG6' )
    
    # The optional 'disabled' state theme for the button:
    disabled_theme = ATheme( '@GG3' )
    
    # The optional image to display in the button:
    image = Image
    
    # The position of the image relative to the text:
    position = Position
    
    # The amount of space between the image and the text:
    spacing = Spacing
    
    # The optional view to display when the button is clicked:
    view = AView
                 
