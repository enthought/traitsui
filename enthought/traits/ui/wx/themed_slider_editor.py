#-------------------------------------------------------------------------------
#
#  Traits UI simple, themed slider-based interger or float value editor.
#
#  Written by: David C. Morrill
#
#  Date: 06/22/2007
#
#  (c) Copyright 2007 by Enthought, Inc.
#
#-------------------------------------------------------------------------------

""" Traits UI simple, themed slider-based interger or float value editor.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from enthought.traits.api \
    import Enum, Range, Float, Bool, Color, TraitError
    
from enthought.traits.ui.wx.editor \
    import Editor
    
from enthought.traits.ui.wx.basic_editor_factory \
    import BasicEditorFactory
    
from image_slice \
    import ImageSlider

#-------------------------------------------------------------------------------
#  '_ThemedSliderEditor' class:
#-------------------------------------------------------------------------------
                               
class _ThemedSliderEditor ( Editor ):
    """ Traits UI simple, themed slider-based interger or float value editor.
    """
        
    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------
        
    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        factory = self.factory
        
        low, high = factory.low, factory.high
        if high <= low:
            low = high = None
            range      = self.object.trait( self.name ).handler
            if isinstance( range, Range ):
                low, high = range._low, range._high
            if low is None:
                if high is None:
                    high = 1.0
                low = high - 1.0
            elif high is None:
                high = low + 1.0
                
        increment = factory.increment
        if isinstance( low, int ) and (increment <= 0.0):
            increment = 1.0
                
        self._slider = ImageSlider( low          = low,
                                    high         = high,
                                    increment    = increment,
                                    show_value   = factory.show_value,
                                    alignment    = factory.alignment,
                                    slider_color = factory.slider_color,
                                    bg_color     = factory.bg_color,
                                    tip_color    = factory.tip_color,
                                    text_color   = factory.text_color )
                                    
        self._slider.on_trait_change( self.update_object, 'value' )

        self.control = self._slider.create_control( parent )
        self.set_tooltip()
                        
    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------

    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        self._slider.value = self.value
                        
    #---------------------------------------------------------------------------
    #  Updates the object when the control slider value changes:
    #---------------------------------------------------------------------------
        
    def update_object ( self, value ):
        """ Updates the object when the control slider value changes.
        """
        try:
            self.value = value
        except TraitError:
            self.value = int( value )

    #---------------------------------------------------------------------------
    #  Handles an error that occurs while setting the object's trait value:
    #---------------------------------------------------------------------------
 
    def error ( self, excp ):
        """ Handles an error that occurs while setting the object's trait value.
        """
        pass
        
    #---------------------------------------------------------------------------
    #  Disposes of the contents of an editor:    
    #---------------------------------------------------------------------------
                
    def dispose ( self ):
        """ Disposes of the contents of an editor.
        """
        super( _ThemedSliderEditor, self ).dispose()
        
        self._slider.on_trait_change( self.update_object, 'value', 
                                      remove = True )
                    
#-------------------------------------------------------------------------------
#  Create the editor factory object:
#-------------------------------------------------------------------------------

# wxPython editor factory for themed slider editors:
class ThemedSliderEditor ( BasicEditorFactory ):
    
    # The editor class to be created:
    klass = _ThemedSliderEditor
    
    # The low end of the slider range:
    low = Float
    
    # The high end of the slider range:
    high = Float
    
    # The smallest allowed increment:
    increment = Float
    
    # Should the current value be displayed as text?
    show_value = Bool( True )
    
    # The alignment of the text within the slider:
    alignment = Enum( 'center', 'left', 'right' )
    
    # The color to use for the slider bar:
    slider_color = Color( 0xC0C0C0 )
    
    # The background color for the slider:
    bg_color = Color( 'white' )
    
    # The color of the slider tip:
    tip_color = Color( 0xFF7300 )
    
    # The color to use for the value text:
    text_color = Color( 'black' )
                 
