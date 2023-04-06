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

""" Defines the key binding editor for use with the KeyBinding class. This is a
specialized editor used to associate a particular key with a control (i.e., the
key binding editor).
"""


from pyface.qt import QtCore, QtGui

from pyface.api import YES, confirm
from traits.api import Bool, Event

from .editor import Editor

from .key_event_to_name import key_event_to_name


class KeyBindingEditor(Editor):
    """An editor for modifying bindings of keys to controls."""

    # -------------------------------------------------------------------------
    #  Trait definitions:
    # -------------------------------------------------------------------------

    #: Does the editor's control have focus currently?
    has_focus = Bool(False)

    #: Keyboard event
    key = Event()

    #: Clear field event
    clear = Event()

    def init(self, parent):
        """Finishes initializing the editor by creating the underlying toolkit
        widget.
        """
        self.control = KeyBindingCtrl(self)

    def update_editor(self):
        """Updates the editor when the object trait changes externally to the
        editor.
        """
        self.control.setText(self.value)

    def _key_changed(self, event):
        """Handles a keyboard event."""
        binding = self.object
        key_name = key_event_to_name(event)
        cur_binding = self.ui.parent.handler.key_binding_for(binding, key_name)
        if cur_binding is not None:
            result = confirm(
                parent=self.control,
                message=(
                    f"{key_name!r} has already been assigned to "
                    f"'{cur_binding.description}'.\n"
                    "Do you wish to continue?"
                ),
                title="Duplicate Key Definition",
            )
            if result != YES:
                return

        self.value = key_name
        # Need to manually update editor because the update to the value
        # won't get transferred to toolkit object due to loopback protection.
        self.update_editor()

    def _clear_changed(self):
        """Handles a clear field event."""
        self.value = ""
        # Need to manually update editor because the update to the value
        # won't get transferred to toolkit object due to loopback protection.
        self.update_editor()


class KeyBindingCtrl(QtGui.QLineEdit):
    """PyQt control for editing key bindings."""

    def __init__(self, editor, parent=None):
        super().__init__(parent)

        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
        self.setMinimumWidth(160)
        self.setMaximumWidth(160)
        self.setReadOnly(True)

        # Save the reference to the controlling editor object:
        self.editor = editor

        # Indicate we don't have the focus right now:
        editor.has_focus = False

    def keyPressEvent(self, event):
        """Handle keyboard keys being pressed."""
        # Ignore presses of the control and shift keys.
        if event.key() not in (QtCore.Qt.Key.Key_Control, QtCore.Qt.Key.Key_Shift):
            self.editor.key = event

    def paintEvent(self, event):
        """Updates the screen."""
        super().paintEvent(event)

        if self.editor.has_focus:
            w = self.width()
            h = self.height()
            p = QtGui.QPainter(self)

            p.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, True)
            pen = QtGui.QPen(QtGui.QColor("tomato"))
            pen.setWidth(2)
            p.setPen(pen)
            p.drawRect(1, 1, w - 2, h - 2)

            p.end()

    def focusInEvent(self, event):
        """Handles getting the focus."""
        self.editor.has_focus = True
        self.update()

    def focusOutEvent(self, event):
        """Handles losing the focus."""
        self.editor.has_focus = False
        self.update()

    def mouseDoubleClickEvent(self, event):
        """Handles the user double clicking the control to clear its contents."""
        self.editor.clear = True
