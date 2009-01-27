#------------------------------------------------------------------------------
# Copyright (c) 2007, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD license
# license.
#
# Author: Riverbank Computing Limited
#------------------------------------------------------------------------------

""" Defines the compound editor and the compound editor factory for the 
PyQt user interface toolkit.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from PyQt4 import QtGui
    
from enthought.traits.api \
    import Str
    
# FIXME: ToolkitEditorFactory is a proxy class defined here just for backward
# compatibility. The class has been moved to the 
# enthought.traits.ui.editors.compound_editor file.
from enthought.traits.ui.editors.compound_editor \
    import ToolkitEditorFactory

from editor \
    import Editor
    
#-------------------------------------------------------------------------------
#  'CompoundEditor' class:
#-------------------------------------------------------------------------------
                               
class CompoundEditor ( Editor ):
    """ Editor for compound traits, which displays editors for each of the
    combined traits, in the appropriate style.
    """
    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------
    
    # The kind of editor to create for each list item
    kind = Str  
        
    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------
        
    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        # The control is a vertical layout.
        self.control = QtGui.QVBoxLayout()

        # Add all of the component trait editors:
        self._editors = editors = []
        for factory in self.factory.editors:
            editor = getattr( factory, self.kind )( self.ui, self.object, 
                                       self.name, self.description, None )
            editor.prepare(self.control)

            if isinstance(editor.control, QtGui.QWidget):
                self.control.addWidget(editor.control)
            else:
                self.control.addLayout(editor.control)

            editors.append(editor)
        
    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------
        
    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the 
            editor.
        """
        pass
        
    #---------------------------------------------------------------------------
    #  Disposes of the contents of an editor:    
    #---------------------------------------------------------------------------
                
    def dispose ( self ):
        """ Disposes of the contents of an editor.
        """
        for editor in self._editors:
            editor.dispose()

        super( CompoundEditor, self ).dispose()

#-------------------------------------------------------------------------------
#  'SimpleEditor' class:
#-------------------------------------------------------------------------------

class SimpleEditor(CompoundEditor):

    # The kind of editor to create for each list item. This value overrides
    # the default.
    kind = 'simple_editor'

#-------------------------------------------------------------------------------
#  'CustomEditor' class:
#-------------------------------------------------------------------------------

class CustomEditor(CompoundEditor):

    # The kind of editor to create for each list item. This value overrides
    # the default.

    kind = 'custom_editor'
