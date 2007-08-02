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

""" Defines file editors and the file editor factoryfor the wxPython user 
    interface toolkit.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import wx

from os.path \
    import abspath, splitext, isfile
    
from enthought.traits.api \
    import List, Str, Event, Bool
    
from enthought.traits.ui.api \
    import View, Group
    
from text_editor \
    import ToolkitEditorFactory as EditorFactory, \
           SimpleEditor         as SimpleTextEditor
           
from helper \
    import traits_ui_panel

#-------------------------------------------------------------------------------
#  Trait definitions:
#-------------------------------------------------------------------------------

# Wildcard filter:
filter_trait = List( Str )

#-------------------------------------------------------------------------------
#  'ToolkitEditorFactory' class:
#-------------------------------------------------------------------------------

class ToolkitEditorFactory ( EditorFactory ):
    """ wxPython editor factory for file editors.
    """
    
    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------
    
    # Wildcard filter to apply to the file dialog:
    filter = filter_trait
    
    # Optional extended trait name of the trait containing the list of filters:
    filter_name = Str
    
    # Should file extension be truncated?
    truncate_ext = Bool( False )
    
    # Is user input set on every keystroke? (Overrides the default) ('simple' 
    # style only):
    auto_set = False      
    
    # Is user input set when the Enter key is pressed? (Overrides the default)
    # ('simple' style only):
    enter_set = True
    
    # Optional extended trait name used to notify the editor when the file 
    # system view should be reloaded ('custom' style only):
    reload_name = Str
    
    #---------------------------------------------------------------------------
    #  Traits view definition:  
    #---------------------------------------------------------------------------
    
    traits_view = View( [ [ '<options>',
                        'truncate_ext{Automatically truncate file extension?}',
                        '|options:[Options]>' ],
                          [ 'filter', '|[Wildcard filters]<>' ] ] )
    
    extras = Group()
    
    #---------------------------------------------------------------------------
    #  'Editor' factory methods:
    #---------------------------------------------------------------------------
    
    def simple_editor ( self, ui, object, name, description, parent ):
        return SimpleEditor( parent,
                             factory     = self, 
                             ui          = ui, 
                             object      = object, 
                             name        = name, 
                             description = description ) 
    
    def custom_editor ( self, ui, object, name, description, parent ):
        return CustomEditor( parent,
                             factory     = self, 
                             ui          = ui, 
                             object      = object, 
                             name        = name, 
                             description = description ) 
                                      
#-------------------------------------------------------------------------------
#  'SimpleEditor' class:
#-------------------------------------------------------------------------------
                               
class SimpleEditor ( SimpleTextEditor ):
    """ Simple style of file editor, consisting of a text field and a **Browse**
        button that opens a file-selection dialog box. The user can also drag 
        and drop a file onto this control.
    """
    
    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------
        
    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.control = panel = traits_ui_panel( parent, -1 )
        sizer        = wx.BoxSizer( wx.HORIZONTAL )
        
        if self.factory.enter_set:
            control = wx.TextCtrl( panel, -1, '', style = wx.TE_PROCESS_ENTER )
            wx.EVT_TEXT_ENTER( panel, control.GetId(), self.update_object )
        else:
            control = wx.TextCtrl( panel, -1, '' )
            
        self._filename = control
        wx.EVT_KILL_FOCUS( control, self.update_object )
        
        if self.factory.auto_set:
            wx.EVT_TEXT( panel, control.GetId(), self.update_object )
            
        sizer.Add( control, 1, wx.EXPAND | wx.ALIGN_CENTER )
        button = wx.Button( panel, -1, 'Browse...' )
        sizer.Add( button, 0, wx.LEFT | wx.ALIGN_CENTER, 8 )
        wx.EVT_BUTTON( panel, button.GetId(), self.show_file_dialog )
        panel.SetDropTarget( FileDropTarget( self ) )
        panel.SetSizerAndFit( sizer )

    #---------------------------------------------------------------------------
    #  Handles the user changing the contents of the edit control:
    #---------------------------------------------------------------------------
  
    def update_object ( self, event ):
        """ Handles the user changing the contents of the edit control.
        """
        try:
            filename = self._filename.GetValue()
            if self.factory.truncate_ext:
                filename = splitext( filename )[0]
                
            self.value = filename
        except TraitError, excp:
            pass
        
    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------
        
    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the 
            editor.
        """
        self._filename.SetValue( self.str_value )
       
    #---------------------------------------------------------------------------
    #  Displays the pop-up file dialog:
    #---------------------------------------------------------------------------
 
    def show_file_dialog ( self, event ):
        """ Displays the pop-up file dialog.
        """
        dlg      = self.create_file_dialog()
        rc       = (dlg.ShowModal() == wx.ID_OK)
        filename = abspath( dlg.GetPath() )
        dlg.Destroy()
        if rc:
            if self.factory.truncate_ext:
                filename = splitext( filename )[0]
                
            self.value = filename
            self.update_editor()

    #---------------------------------------------------------------------------
    #  Creates the correct type of file dialog:
    #---------------------------------------------------------------------------
           
    def create_file_dialog ( self ):
        """ Creates the correct type of file dialog.
        """
        dlg = wx.FileDialog( self.control, message = 'Select a File' )
        dlg.SetFilename( self._filename.GetValue() )
        if len( self.factory.filter ) > 0:
            dlg.SetWildcard( '|'.join( self.factory.filter[:] ) )
            
        return dlg
                                      
#-------------------------------------------------------------------------------
#  'CustomEditor' class:
#-------------------------------------------------------------------------------
                               
class CustomEditor ( SimpleTextEditor ):
    """ Custom style of file editor, consisting of a file system tree view.
    """

    # Is the file editor scrollable? This value overrides the default.
    scrollable = True
    
    # Wildcard filter to apply to the file dialog:
    filter = filter_trait
    
    # Event fired when the file system view should be rebuilt:
    reload = Event
    
    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------
        
    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        style   = self.get_style()
        factory = self.factory
        if (len( factory.filter ) > 0) or (factory.filter_name != ''):
            style |= wx.DIRCTRL_SHOW_FILTERS
            
        self.control = wx.GenericDirCtrl( parent, style = style )
        self._tree   = tree = self.control.GetTreeCtrl()
        wx.EVT_TREE_SEL_CHANGED( tree, tree.GetId(), self.update_object )
        
        self.filter = factory.filter
        self.sync_value( factory.filter_name, 'filter', 'from', is_list = True )
        self.sync_value( factory.reload_name, 'reload', 'from' )
        
        self.set_tooltip()

    #---------------------------------------------------------------------------
    #  Handles the user changing the contents of the edit control:
    #---------------------------------------------------------------------------
  
    def update_object ( self, event ):
        """ Handles the user changing the contents of the edit control.
        """
        if self.control is not None:
            path = self.control.GetPath()
            if isfile( path ):
                if self.factory.truncate_ext:
                    path = splitext( path )[0]
                    
                self.value = path
        
    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------
        
    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the 
            editor.
        """
        self.control.SetPath( self.str_value )
        
    #---------------------------------------------------------------------------
    #  Returns the basic style to use for the control:
    #---------------------------------------------------------------------------
    
    def get_style ( self ):
        """ Returns the basic style to use for the control.
        """
        return wx.DIRCTRL_EDIT_LABELS
        
    #---------------------------------------------------------------------------
    #  Handles the 'filter' trait being changed:
    #---------------------------------------------------------------------------
    
    def _filter_changed ( self ):
        """ Handles the 'filter' trait being changed.
        """
        self.control.SetFilter( '|'.join( self.filter[:] ) )
        
    #---------------------------------------------------------------------------
    #  Handles the 'reload' trait being changed:
    #---------------------------------------------------------------------------
    
    def _reload_changed ( self ):
        """ Handles the 'reload' trait being changed.
        """
        self.control.ReCreateTree()

#-------------------------------------------------------------------------------
#  'FileDropTarget' class:  
#-------------------------------------------------------------------------------
                
class FileDropTarget ( wx.FileDropTarget ):
    """ A target for a drag and drop operation, which accepts a file.
    """
    def __init__ ( self, editor ):
        wx.FileDropTarget.__init__( self )
        self.editor = editor

    def OnDropFiles ( self, x, y, filenames ):
        self.editor.value = filenames[-1]
        self.editor.update_editor()
        
        return True
        
