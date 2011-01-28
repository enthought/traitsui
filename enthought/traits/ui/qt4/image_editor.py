#-------------------------------------------------------------------------------
#
#  Copyright (c) 2009, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
#  Author: Evan Patterson
#  Date:   07/21/2009
#
#-------------------------------------------------------------------------------

""" Traits UI 'display only' image editor.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from enthought.qt import QtGui

from enthought.pyface.image_resource \
    import ImageResource

from enthought.traits.ui.ui_traits \
    import convert_bitmap

# FIXME: ImageEditor is a proxy class defined here just for backward
# compatibility. The class has been moved to the
# enthought.traits.ui.editors.image_editor file.
from enthought.traits.ui.editors.image_editor \
    import ImageEditor

from editor \
    import Editor

#-------------------------------------------------------------------------------
#  '_ImageEditor' class:
#-------------------------------------------------------------------------------

class _ImageEditor ( Editor ):
    """ Traits UI 'display only' image editor.
    """

    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        image = self.factory.image
        if image is None:
            image = self.value

        self.control = QtGui.QLabel()
        self.control.setPixmap( convert_bitmap( image ) )

        self.set_tooltip()

    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------

    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        if self.factory.image is None:
            value = self.value
            if isinstance( value, ImageResource ):
                self.control.setPixmap( convert_bitmap( value ) )
