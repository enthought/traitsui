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

from pyface.qt import QtCore, QtGui

from traits.api import Unicode, List, Str, on_trait_change

# FIXME: ToolkitEditorFactory is a proxy class defined here just for backward
# compatibility. The class has been moved to the
# traitsui.editors.button_editor file.
from traitsui.editors.button_editor \
    import ToolkitEditorFactory

from editor import Editor

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

    # The list of items in a drop-down menu, if any
    #menu_items = List

    # The selected item in the drop-down menu.
    selected_item = Str

    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        label = self.factory.label or self.item.get_label(self.ui)

        if self.factory.values_trait:
            self.control = QtGui.QToolButton()
            self.control.toolButtonStyle = QtCore.Qt.ToolButtonTextOnly
            self.control.setText(self.string_value(label))
            self.object.on_trait_change(self._update_menu, self.factory.values_trait)
            self.object.on_trait_change(self._update_menu, self.factory.values_trait + "_items")
            self._menu = QtGui.QMenu()
            self._update_menu()
            self.control.setMenu(self._menu)

        else:
            self.control = QtGui.QPushButton(self.string_value(label))
            self._menu = None
            self.control.setAutoDefault(False)

        self.sync_value(self.factory.label_value, 'label', 'from')
        self.control.clicked.connect(self.update_object)
        self.set_tooltip()


    def _label_changed(self, label):
        self.control.setText(self.string_value(label))

    def _update_menu(self):
        self._menu.blockSignals(True)
        self._menu.clear()
        for item in getattr(self.object, self.factory.values_trait):
            action = self._menu.addAction(item)
            action.triggered.connect(lambda event, name=item: self._menu_selected(name))
        self.selected_item = ""
        self._menu.blockSignals(False)

    def _menu_selected(self, item_name):
        self.selected_item = item_name
        self.label = item_name

    def update_object(self):
        """ Handles the user clicking the button by setting the factory value
            on the object.
        """
        if self.selected_item != "":
            self.value = self.selected_item
        else:
            self.value = self.factory.value

        # If there is an associated view, then display it:
        if (self.factory is not None) and (self.factory.view is not None):
            self.object.edit_traits( view   = self.factory.view,
                                     parent = self.control )

    def update_editor(self):
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
