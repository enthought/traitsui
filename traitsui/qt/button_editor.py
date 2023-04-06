# (C) Copyright 2008-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

# ------------------------------------------------------------------------------
# Copyright (c) 2007, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD license.
# However, when used with the GPL version of PyQt the additional terms
# described in the PyQt GPL exception also apply

#
# Author: Riverbank Computing Limited
# ------------------------------------------------------------------------------

""" Defines the various button editors for the PyQt user interface toolkit.
"""


from pyface.qt import QtCore, QtGui
from pyface.api import Image

from traits.api import List, Str, observe, on_trait_change

from .editor import Editor


class SimpleEditor(Editor):
    """Simple style editor for a button."""

    # -------------------------------------------------------------------------
    #  Trait definitions:
    # -------------------------------------------------------------------------

    #: The button label
    label = Str()

    #: The list of items in a drop-down menu, if any
    # menu_items = List()

    #: The selected item in the drop-down menu.
    selected_item = Str()

    def init(self, parent):
        """Finishes initializing the editor by creating the underlying toolkit
        widget.
        """
        label = self.factory.label or self.item.get_label(self.ui)

        if self.factory.values_trait:
            self.control = QtGui.QToolButton()
            self.control.toolButtonStyle = QtCore.Qt.ToolButtonStyle.ToolButtonTextOnly
            self.control.setText(self.string_value(label))
            self.object.observe(
                self._update_menu, self.factory.values_trait + ".items"
            )
            self._menu = QtGui.QMenu()
            self._update_menu()
            self.control.setMenu(self._menu)

        else:
            self.control = QtGui.QPushButton(self.string_value(label))
            self._menu = None
            self.control.setAutoDefault(False)

        self.sync_value(self.factory.label_value, "label", "from")

        # The connection type is set to workaround Qt5 + MacOSX issue with
        # event dispatching. Without the type set to QueuedConnection, other
        # widgets may not repaint properly in response to a button click.
        # See enthought/traitsui#1308
        self.control.clicked.connect(
            self.update_object,
            type=QtCore.Qt.ConnectionType.QueuedConnection,
        )
        self.set_tooltip()

    def dispose(self):
        """Disposes of the contents of an editor."""

        if self.factory.values_trait:
            self.object.observe(
                self._update_menu,
                self.factory.values_trait + ".items",
                remove=True,
            )

        if self.control is not None:
            self.control.clicked.disconnect(self.update_object)
        super().dispose()

    def _label_changed(self, label):
        self.control.setText(self.string_value(label))

    def _update_menu(self, event=None):
        self._menu.blockSignals(True)
        self._menu.clear()
        for item in getattr(self.object, self.factory.values_trait):
            action = self._menu.addAction(item)
            action.triggered.connect(
                lambda event, name=item: self._menu_selected(name)
            )
        self.selected_item = ""
        self._menu.blockSignals(False)

    def _menu_selected(self, item_name):
        self.selected_item = item_name
        self.label = item_name

    def update_object(self):
        """Handles the user clicking the button by setting the factory value
        on the object.
        """
        if self.control is None:
            return
        if self.selected_item != "":
            self.value = self.selected_item
        else:
            self.value = self.factory.value

        # If there is an associated view, then display it:
        if (self.factory is not None) and (self.factory.view is not None):
            self.object.edit_traits(
                view=self.factory.view, parent=self.control
            )

    def update_editor(self):
        """Updates the editor when the object trait changes externally to the
        editor.
        """
        pass


class CustomEditor(SimpleEditor):
    """Custom style editor for a button, which can contain an image."""

    #: The button image
    image = Image()

    #: The mapping of button styles to Qt classes.
    _STYLE_MAP = {
        "checkbox": QtGui.QCheckBox,
        "radio": QtGui.QRadioButton,
        "toolbar": QtGui.QToolButton,
    }

    def init(self, parent):
        """Finishes initializing the editor by creating the underlying toolkit
        widget.
        """
        # FIXME: We ignore orientation, width_padding and height_padding.

        factory = self.factory
        if factory.label:
            label = factory.label
        else:
            label = self.item.get_label(self.ui)
        btype = self._STYLE_MAP.get(factory.style, QtGui.QPushButton)
        self.control = btype()
        self.control.setText(self.string_value(label))

        if factory.image is not None:
            self.control.setIcon(factory.image.create_icon())

        self.sync_value(self.factory.label_value, "label", "from")
        self.sync_value(self.factory.image_value, "image", "from")
        self.control.clicked.connect(self.update_object)
        self.set_tooltip()

    @observe("image")
    def _image_updated(self, event):
        image = event.new
        self.control.setIcon(image.create_icon())

    def dispose(self):
        """Disposes of the contents of an editor."""
        if self.control is not None:
            self.control.clicked.disconnect(self.update_object)

        # FIXME: Maybe better to let this class subclass Editor directly
        # enthought/traitsui#884
        Editor.dispose(self)
