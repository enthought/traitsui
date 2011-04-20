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

""" Defines the various button editors for the wxPython user interface toolkit.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------


import wx

from traits.api \
    import Str

# FIXME: ToolkitEditorFactory is a proxy class defined here just for backward
# compatibility. The class has been moved to the
# traitsui.editors.button_editor file.
from traitsui.editors.button_editor \
    import ToolkitEditorFactory

from editor \
    import Editor

#-------------------------------------------------------------------------------
#  'SimpleEditor' class:
#-------------------------------------------------------------------------------

class SimpleEditor ( Editor ):
    """ Simple style editor for a button.
    """

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # The button label
    label = Str

    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        label = self.factory.label or self.item.get_label( self.ui )
        self.control = wx.Button( parent, -1, self.string_value( label ) )
        self.sync_value( self.factory.label_value, 'label', 'from' )
        wx.EVT_BUTTON( parent, self.control.GetId(), self.update_object )
        self.set_tooltip()

    #---------------------------------------------------------------------------
    #  Handles the 'label' trait being changed:
    #---------------------------------------------------------------------------

    def _label_changed ( self, label ):
        self.control.SetLabel( self.string_value( label ) )

    #---------------------------------------------------------------------------
    #  Handles the user clicking the button by setting the value on the object:
    #---------------------------------------------------------------------------

    def update_object ( self, event ):
        """ Handles the user clicking the button by setting the factory value
            on the object.
        """
        factory    = self.factory
        self.value = factory.value

        # If there is an associated view, then display it:
        if factory.view is not None:
            self.object.edit_traits( view   = factory.view,
                                     parent = self.control )

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
        wx.EVT_BUTTON( self.control.GetParent(), self.control.GetId(), None )

        super( SimpleEditor, self ).dispose()

#-------------------------------------------------------------------------------
#  'CustomEditor' class:
#-------------------------------------------------------------------------------

class CustomEditor ( SimpleEditor ):
    """ Custom style editor for a button, which can contain an image.
    """

    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        from pyface.image_button import ImageButton

        factory       = self.factory
        self._control = ImageButton(
            parent,
            label          = self.string_value( factory.label ),
            image          = factory.image,
            style          = factory.style,
            orientation    = factory.orientation,
            width_padding  = factory.width_padding,
            height_padding = factory.height_padding
        )
        self.control = self._control.control
        self._control.on_trait_change( self.update_object, 'clicked',
                                       dispatch = 'ui' )
        self.set_tooltip()

    #---------------------------------------------------------------------------
    #  Disposes of the contents of an editor:
    #---------------------------------------------------------------------------

    def dispose ( self ):
        """ Disposes of the contents of an editor.
        """
        self._control.on_trait_change( self.update_object, 'clicked',
                                       remove = True )

        super( CustomEditor, self ).dispose()

### EOF #######################################################################

