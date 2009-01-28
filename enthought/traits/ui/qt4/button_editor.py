#------------------------------------------------------------------------------
# Copyright (c) 2007, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD license.
# However, when used with the GPL version of PyQt the additional terms described in the PyQt GPL exception also apply

#
# Author: Riverbank Computing Limited
#------------------------------------------------------------------------------

""" Defines the various button editors for the PyQt user interface toolkit.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from PyQt4 import QtCore, QtGui
    
from enthought.traits.api \
    import Unicode

# FIXME: ToolkitEditorFactory is a proxy class defined here just for backward
# compatibility. The class has been moved to the 
# enthought.traits.ui.editors.button_editor file.
from enthought.traits.ui.editors.button_editor \
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
    label = Unicode

    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        label = self.factory.label or self.item.get_label( self.ui )
        self.control = QtGui.QPushButton(self.string_value(label))
        self.sync_value( self.factory.label_value, 'label', 'from' )
        QtCore.QObject.connect(self.control, QtCore.SIGNAL('clicked()'),
                self.update_object )
        self.set_tooltip()

    #---------------------------------------------------------------------------
    #  Handles the 'label' trait being changed:
    #---------------------------------------------------------------------------

    def _label_changed ( self, label ):
        self.control.setText(self.string_value(label))

    #---------------------------------------------------------------------------
    #  Handles the user clicking the button by setting the value on the object:
    #---------------------------------------------------------------------------

    def update_object (self):
        """ Handles the user clicking the button by setting the factory value
            on the object.
        """
        self.value = self.factory.value

        # If there is an associated view, then display it:
        if (self.factory is not None) and (self.factory.view is not None):
            self.object.edit_traits( view   = self.factory.view,
                                     parent = self.control )

    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------

    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        pass

#-------------------------------------------------------------------------------
#  'CustomEditor' class:
#-------------------------------------------------------------------------------

class CustomEditor ( SimpleEditor ):
    """ Custom style editor for a button, which can contain an image.
    """

    # The mapping of button styles to Qt classes.
    _STYLE_MAP = {
        'checkbox': QtGui.QCheckBox,
        'radio':    QtGui.QRadioButton,
        'toolbar':  QtGui.QToolButton
    }

    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        # FIXME: We ignore orientation, width_padding and height_padding.

        factory = self.factory

        btype = self._STYLE_MAP.get(factory.style, QtGui.QPushButton)
        self.control = btype()
        self.control.setText(self.string_value(factory.label))

        if factory.image is not None:
            self.control.setIcon(factory.image.create_icon())

        QtCore.QObject.connect(self.control, QtCore.SIGNAL('clicked()'),
                self.update_object )
        self.set_tooltip()
