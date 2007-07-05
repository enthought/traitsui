#-------------------------------------------------------------------------------
#
#  Written by: David C. Morrill
#
#  Date: 07/26/2006
#
#  (c) Copyright 2006 by Enthought, Inc.
#
#-------------------------------------------------------------------------------
""" Defines a completely empty editor, intended to be used as a spacer.
"""
#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import wx

from enthought.traits.ui.wx.editor \
    import Editor
    
from enthought.traits.ui.wx.basic_editor_factory \
    import BasicEditorFactory
    
from constants \
    import WindowColor
    
from image_slice \
    import paint_parent
                                      
#-------------------------------------------------------------------------------
#  'NullEditor' class:
#-------------------------------------------------------------------------------
                               
class NullEditor ( Editor ):
    """ A completely empty editor.
    """
    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------
        
    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.control = control = wx.Window( parent, -1 )
                            
        # Set up the painting event handlers:
        wx.EVT_ERASE_BACKGROUND( control, self._erase_background )
        wx.EVT_PAINT( control, self._on_paint )
                        
    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------

    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        pass
        
    #-- wxPython Event Handlers ------------------------------------------------
    
    def _erase_background ( self, event ):
        """ Do not erase the background here (do it in the 'on_paint' handler).
        """
        pass
           
    def _on_paint ( self, event ):
        """ Paint the background using the associated ImageSlice object.
        """
        control = self.control
        dc      = wx.PaintDC( control )
        
        # Repaint the parent's theme (if necessary):
        if paint_parent( dc, control, 0, 0 ) is None:
            
            # Otherwise, just paint the normal window background color:
            dx, dy = control.GetClientSizeTuple()
            dc.SetBrush( wx.Brush( WindowColor ) )
            dc.SetPen( wx.TRANSPARENT_PEN )
            dc.DrawRectangle( 0, 0, dx, dy )

#-------------------------------------------------------------------------------
#  Create the editor factory object:
#-------------------------------------------------------------------------------
                
ToolkitEditorFactory = BasicEditorFactory( klass = NullEditor )
                 
