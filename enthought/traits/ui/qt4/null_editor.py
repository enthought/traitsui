#-------------------------------------------------------------------------------
#
#  Copyright (c) 2006, Enthought, Inc.
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
#  Date:   07/26/2006
#
#-------------------------------------------------------------------------------

""" Defines a completely empty editor, intended to be used as a spacer.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from PyQt4 import QtGui

# FIXME: ToolkitEditorFactory is a proxy class defined here just for backward
# compatibility. The class has been moved to the 
# enthought.traits.ui.editors.null_editor file.
from enthought.traits.ui.editors.null_editor \
    import NullEditor as ToolkitEditorFactory

from editor \
    import Editor

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
        self.control = QtGui.QWidget()

        # Since NullEditors are used exclusively for the purpose of layout
        # adjustment, make them fill available space:
        self.control.setSizePolicy( QtGui.QSizePolicy.Expanding,
                                    QtGui.QSizePolicy.Expanding )
                        
    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------

    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        pass
