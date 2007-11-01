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

""" Defines various directory editor and the directory editor factory for the 
wxPython user interface toolkit.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import wx

from os.path \
    import isdir

from file_editor \
    import ToolkitEditorFactory as EditorFactory,    \
           SimpleEditor         as SimpleFileEditor, \
           CustomEditor         as CustomFileEditor, \
           PopupFile

#-------------------------------------------------------------------------------
#  'ToolkitEditorFactory' class:
#-------------------------------------------------------------------------------

class ToolkitEditorFactory ( EditorFactory ):
    """ wxPython editor factory for directory editors.
    """
    
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
                               
class SimpleEditor ( SimpleFileEditor ):
    """ Simple style of editor for directories, which displays a text field
        and a **Browse** button that opens a directory-selection dialog box.
    """
    
    #---------------------------------------------------------------------------
    #  Creates the correct type of file dialog or popup:
    #---------------------------------------------------------------------------
           
    def create_file_dialog ( self ):
        """ Creates the correct type of file dialog.
        """
        dlg = wx.DirDialog( self.control, message = 'Select a Directory' )
        dlg.SetPath( self._filename.GetValue() )
        
        return dlg
        
    def _create_file_popup ( self ):
        """ Creates the correct type of file popup.
        """
        return PopupDirectory( control   = self.control,
                               file_name = self.str_value,
                               filter    = self.factory.filter,
                               height    = 300 )
        
#-------------------------------------------------------------------------------
#  'CustomEditor' class:
#-------------------------------------------------------------------------------
                               
class CustomEditor ( CustomFileEditor ):
    """ Custom style of editor for directories, which displays a tree view of
        the file system.
    """
        
    #---------------------------------------------------------------------------
    #  Returns the basic style to use for the control:
    #---------------------------------------------------------------------------
    
    def get_style ( self ):
        """ Returns the basic style to use for the control.
        """
        return (wx.DIRCTRL_DIR_ONLY | wx.DIRCTRL_EDIT_LABELS)

    #---------------------------------------------------------------------------
    #  Handles the user changing the contents of the edit control:
    #---------------------------------------------------------------------------
  
    def update_object ( self, event ):
        """ Handles the user changing the contents of the edit control.
        """
        if self.control is not None:
            path = self.control.GetPath()
            if isdir( path ):
                self.value = path
                
#-------------------------------------------------------------------------------
#  'PopupDirectory' class:
#-------------------------------------------------------------------------------

class PopupDirectory ( PopupFile ):
    
    def get_style ( self ):
        """ Returns the basic style to use for the popup.
        """
        return (wx.DIRCTRL_DIR_ONLY | wx.DIRCTRL_EDIT_LABELS)
        
    def is_valid ( self, path ):
        """ Returns whether or not the path is valid.
        """
        return isdir( path )

