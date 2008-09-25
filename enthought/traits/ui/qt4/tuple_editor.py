#------------------------------------------------------------------------------
# Copyright (c) 2007, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the GPL v2
# license.
#
# Author: Riverbank Computing Limited
#------------------------------------------------------------------------------

""" Defines the tuple editor for the PyQt user interface toolkit.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

     
# FIXME: ToolkitEditorFactory is a proxy class defined here just for backward
# compatibility. The class has been moved to the 
# enthought.traits.ui.editors.tuple_editor file.
from enthought.traits.ui.editors.tuple_editor \
    import SimpleEditor as BaseSimpleEditor, ToolkitEditorFactory
    
from editor \
    import Editor
    
#-------------------------------------------------------------------------------
#  'SimpleEditor' class:
#-------------------------------------------------------------------------------
                               
class SimpleEditor ( BaseSimpleEditor, Editor ):
    """ Simple style of editor for tuples.
    
    The editor displays an editor for each of the fields in the tuple, based on
    the type of each field. 
    """
    pass
