#------------------------------------------------------------------------------
#
#  Copyright (c) 2005, Enthought, Inc.
#  All rights reserved.
#  
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#  Thanks for using Enthought open source!
#  
#  Author: David C. Morrill
#  Date:   10/21/2004
#
#------------------------------------------------------------------------------

""" Defines the a text entry field (actually a combo-box) with a drop-down list
    of values previously entered into the control.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import wx

from enthought.traits.api \
    import HasPrivateTraits, Instance, Str, List, Int, Bool

from enthought.pyface.timer.api \
    import do_later
    
from constants \
    import OKColor, ErrorColor
    
#-------------------------------------------------------------------------------
#  'HistoryControl' class:
#-------------------------------------------------------------------------------

class HistoryControl ( HasPrivateTraits ):

    # The UI control:
    control = Instance( wx.Window )
    
    # The current value of the control:
    value = Str
    
    # The currently history of the control:
    history = List( Str )
    
    # The maximum number of history entries allowed:
    entries = Int( 10 )
    
    # Is the current value valid?
    error = Bool( False )
    
    #-- Public Methods ---------------------------------------------------------
    
    def create_control ( self, parent ):
        """ Creates the control.
        """
        self.control = control = wx.ComboBox( parent, -1, self.value,
                                          wx.Point( 0, 0 ), wx.Size( -1, -1 ), 
                                          self.history, style = wx.CB_DROPDOWN )
        wx.EVT_COMBOBOX( parent, control.GetId(), self._update_value )
        wx.EVT_TEXT_ENTER( parent, control.GetId(), 
                           self._update_text_value )
        wx.EVT_KILL_FOCUS( control, self._kill_focus )
        
        return control

    #-- Traits Event Handlers --------------------------------------------------
    
    def _value_changed ( self, value ):
        """ Handles the 'value' trait being changed.
        """
        if not self._no_update:
            self._update( value )
            #self.control.SetValue( value )
            
    def _history_changed ( self ):
        """ Handles the 'history' being changed.
        """
        if not self._no_update:
            self._load_history()
            
    def _error_changed ( self, error ):
        """ Handles the 'error' trait being changed.
        """
        if error:
            self.control.SetBackgroundColour( ErrorColor )
        else:
            self.control.SetBackgroundColour( OKColor )
           
        self.control.Refresh()
            
    #-- Wx Event Handlers ------------------------------------------------------
    
    def _update_value ( self, event ):
        """ Handles the user selecting something from the drop-down list of the
            combobox.
        """
        self._update( event.GetString() )
        
    def _update_text_value ( self, event, select = True ):
        """ Handles the user typing something into the text field of the
            combobox.
        """
        if not self._no_update:
            value = self.control.GetValue()
            if value != self.value:
                self._update( value, select )
        
    def _kill_focus ( self, event ):
        """ Handles the combobox losing focus.
        """
        self._update_text_value( event, False )
        event.Skip()
        
    #-- Private Methods --------------------------------------------------------

    def _update ( self, value, select = True ):
        """ Updates the value and history list based on a specified value.
        """
        self._no_update = True
        
        if value.strip() != '':
            history = self.history
            if value in history:
                history.remove( value )
            history.insert( 0, value )
            del history[ self.entries: ]
            self._load_history( value, select )
          
        self.value = value
        
        self._no_update = False
        
    def _load_history ( self, restore = None, select = True ):
        """ Loads the current history list into the control.
        """
        control = self.control
        control.Freeze()
        
        if restore is None:
            restore = control.GetValue()
            
        control.Clear()
        for value in self.history:
            control.Append( value )
           
        do_later( self._thaw_value, restore, select )
        
    def _thaw_value ( self, restore, select ):
        """ Restores the value of the combobox control.
        """
        self.control.SetValue( restore )
        
        if select:
            self.control.SetMark( 0, len( restore ) )
            
        self.control.Thaw()
        
