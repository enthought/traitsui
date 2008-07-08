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

""" Defines the base class for wxPython editors.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import wx

from enthought.traits.api \
    import HasTraits, Int, Instance, Str, Callable
    
from enthought.traits.ui.api \
    import Editor as UIEditor
    
from constants \
    import WindowColor, OKColor, ErrorColor

#-------------------------------------------------------------------------------
#  'Editor' class:
#-------------------------------------------------------------------------------

class Editor ( UIEditor ):
    """ Base class for wxPython editors for Traits-based UIs.
    """
    
    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------
    
    # Style for embedding control in a sizer:
    layout_style = Int( wx.EXPAND )
    
    # The maximum extra padding that should be allowed around the editor:
    border_size = Int( 4 )
    
    #---------------------------------------------------------------------------
    #  Handles the 'control' trait being set:
    #---------------------------------------------------------------------------
    
    def _control_changed ( self, control ):
        """ Handles the **control** trait being set.
        """
        if control is not None:
            control._editor = self
        
    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------
        
    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the 
            editor.
        """
        new_value = self.str_value
        if self.control.GetValue() != new_value:
            self.control.SetValue( new_value )

    #---------------------------------------------------------------------------
    #  Handles an error that occurs while setting the object's trait value:
    #---------------------------------------------------------------------------
 
    def error ( self, excp ):
        """ Handles an error that occurs while setting the object's trait value.
        """
        dlg = wx.MessageDialog( self.control, str( excp ),
                                self.description + ' value error',
                                wx.OK | wx.ICON_INFORMATION )
        dlg.ShowModal()
        dlg.Destroy()
       
    #---------------------------------------------------------------------------
    #  Sets the tooltip for a specified control:
    #---------------------------------------------------------------------------
        
    def set_tooltip ( self, control = None ):
        """ Sets the tooltip for a specified control.
        """
        desc = self.description
        if desc == '':
            desc = self.object.base_trait( self.name ).desc
            if desc is None:
                return False
                
            desc = 'Specifies ' + desc
            
        if control is None:
            control = self.control
            
        control.SetToolTipString( desc )
        
        return True
            
    #---------------------------------------------------------------------------
    #  Handles the 'enabled' state of the editor being changed:
    #---------------------------------------------------------------------------
            
    def _enabled_changed ( self, enabled ):
        """ Handles the **enabled** state of the editor being changed.
        """
        control = self.control
        if control is not None:
            control.Enable( enabled )
            control.Refresh()
            
    #---------------------------------------------------------------------------
    #  Handles the 'visible' state of the editor being changed:
    #---------------------------------------------------------------------------
            
    def _visible_changed ( self, visible ):
        """ Handles the **visible** state of the editor being changed.
        """
        if self.label_control is not None:
            self.label_control.Show( visible )
        self.control.Show( visible )
                
        sizer = self.control.GetContainingSizer()
        if sizer is not None:
            sizer.Layout()

        # Handle the case where the item whose visibility has changed is a 
        # notebook page:
        page      = self.control.GetParent()
        page_name = getattr( page, '_page_name', '' )
        if page_name != '':
            notebook = page.GetParent()
            for i in range( 0, notebook.GetPageCount() ):
                if notebook.GetPage( i ) is page:
                    break
            else:
                i = -1
                
            if visible:
                if i < 0:
                    notebook.AddPage( page, page_name )
                    
            elif i >= 0:
                notebook.RemovePage( i )
            
    #---------------------------------------------------------------------------
    #  Returns the editor's control for indicating error status:
    #---------------------------------------------------------------------------
    
    def get_error_control ( self ):
        """ Returns the editor's control for indicating error status.
        """
        return self.control
        
    #---------------------------------------------------------------------------
    #  Returns whether or not the editor is in an error state:
    #---------------------------------------------------------------------------
    
    def in_error_state ( self ):
        """ Returns whether or not the editor is in an error state.
        """
        return False
        
    #---------------------------------------------------------------------------
    #  Sets the editor's current error state:
    #---------------------------------------------------------------------------
    
    def set_error_state ( self, state = None, control = None ):
        """ Sets the editor's current error state.
        """
        if state is None:
            state = self.invalid
        state = state or self.in_error_state()
            
        if control is None:
            control = self.get_error_control()
            
        if not isinstance( control, list ):
            control = [ control ]
            
        for item in control:
            if state:
                color = ErrorColor
                if getattr( item, '_ok_color', None ) is None:
                    item._ok_color = item.GetBackgroundColour()
            else:
                color = getattr( item, '_ok_color', None )
                if color is None:
                    color = OKColor
                    if isinstance( item, wx.Panel ):
                        color = WindowColor
            
            item.SetBackgroundColour( color )
            item.Refresh()
            
    #---------------------------------------------------------------------------
    #  Handles the editor's invalid state changing:
    #---------------------------------------------------------------------------
    
    def _invalid_changed ( self, state ):
        """ Handles the editor's invalid state changing.
        """
        self.set_error_state()
                
#-------------------------------------------------------------------------------
#  'EditorWithList' class:  
#-------------------------------------------------------------------------------
                          
class EditorWithList ( Editor ):
    """ Editor for an object that contains a list.
    """
    #---------------------------------------------------------------------------
    #  Trait definitions:  
    #---------------------------------------------------------------------------
    
    # Object containing the list being monitored
    list_object = Instance( HasTraits )
    
    # Name of the monitored trait
    list_name = Str
    
    # Function used to evaluate the current list object value:
    list_value = Callable
    
    #---------------------------------------------------------------------------
    #  Initializes the object:  
    #---------------------------------------------------------------------------
        
    def init ( self, parent ):
        """ Initializes the object.
        """
        factory = self.factory
        name    = factory.name
        if name != '':
            self.list_object, self.list_name, self.list_value = \
                self.parse_extended_name( name ) 
        else:
            self.list_object, self.list_name = factory, 'values'
            self.list_value = lambda: factory.values
            
        self.list_object.on_trait_change( self._list_updated, 
                                          self.list_name, dispatch = 'ui' )
        
        self._list_updated()
        
    #---------------------------------------------------------------------------
    #  Disconnects the listeners set up by the constructor:  
    #---------------------------------------------------------------------------
                
    def dispose ( self ):
        """ Disconnects the listeners set up by the constructor.
        """
        self.list_object.on_trait_change( self._list_updated, 
                                          self.list_name, remove = True )
                                          
        super( EditorWithList, self ).dispose()
            
    #---------------------------------------------------------------------------
    #  Handles the monitored trait being updated:  
    #---------------------------------------------------------------------------
                        
    def _list_updated ( self ):
        """ Handles the monitored trait being updated.
        """
        self.list_updated( self.list_value() )
        
    #---------------------------------------------------------------------------
    #  Handles the monitored list being updated:  
    #---------------------------------------------------------------------------
                
    def list_updated ( self, values ):
        """ Handles the monitored list being updated.
        """
        raise NotImplementedError
        
#-------------------------------------------------------------------------------
#  'EditorFromView' class:  
#-------------------------------------------------------------------------------

class EditorFromView ( Editor ):
    """ An editor generated from a View object.
    """
    
    #---------------------------------------------------------------------------
    #  Initializes the object:  
    #---------------------------------------------------------------------------
        
    def init ( self, parent ):
        """ Initializes the object.
        """
        self._ui = ui = self.init_ui( parent )
        if ui.history is None:
            ui.history = self.ui.history
            
        self.control = ui.control

    #---------------------------------------------------------------------------
    #  Creates and returns the traits UI defined by this editor:
    #  (Must be overridden by a subclass):
    #---------------------------------------------------------------------------

    def init_ui ( self, parent ):
        """ Creates and returns the traits UI defined by this editor.
            (Must be overridden by a subclass).
        """
        raise NotImplementedError
        
    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------
        
    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the 
            editor.
        """
        # Normally nothing needs to be done here, since it should all be handled
        # by the editor's internally created traits UI:
        pass
        
    #---------------------------------------------------------------------------
    #  Dispose of the editor:
    #---------------------------------------------------------------------------
                
    def dispose ( self ):
        """ Disposes of the editor.
        """
        self._ui.dispose()
        
        super( EditorFromView, self ).dispose()

