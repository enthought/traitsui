#------------------------------------------------------------------------------
# Copyright (c) 2007, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD license
# license.
#
# Author: Riverbank Computing Limited
#------------------------------------------------------------------------------

""" Defines various directory editor for the PyQt user interface toolkit.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from PyQt4 import QtGui
    
# FIXME: ToolkitEditorFactory is a proxy class defined here just for backward
# compatibility. The class has been moved to the 
# enthought.traits.ui.editors.custom_editor file.
from enthought.traits.ui.editors.directory_editor \
    import ToolkitEditorFactory

from file_editor \
    import SimpleEditor as SimpleFileEditor, \
           CustomEditor as CustomFileEditor

#-------------------------------------------------------------------------------
#  'SimpleEditor' class:
#-------------------------------------------------------------------------------
                               
class SimpleEditor ( SimpleFileEditor ):
    """ Simple style of editor for directories, which displays a text field
        and a **Browse** button that opens a directory-selection dialog box.
    """
    
    #---------------------------------------------------------------------------
    #  Creates the correct type of file dialog:
    #---------------------------------------------------------------------------
           
    def _create_file_dialog ( self ):
        """ Creates the correct type of file dialog.
        """
        dlg = QtGui.QFileDialog(self.control.parentWidget())
        dlg.selectFile(self._file_name.text())
        dlg.setFileMode(QtGui.QFileDialog.Directory)

        return dlg
        
#-------------------------------------------------------------------------------
#  'CustomEditor' class:
#-------------------------------------------------------------------------------
                               
class CustomEditor ( CustomFileEditor ):
    """ Custom style of editor for directories, which displays a tree view of
        the file system.
    """

    #---------------------------------------------------------------------------
    #  Handles the user changing the contents of the edit control:
    #---------------------------------------------------------------------------
  
    def update_object(self, idx):
        """ Handles the user changing the contents of the edit control.
        """
        if self._model.isDir(idx):
            self.value = unicode(self._model.filePath(idx))
