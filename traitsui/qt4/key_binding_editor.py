# (C) Copyright 2008-2021 Enthought, Inc., Austin, TX
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

from traits.api import Bool, Event

from .editor import Editor

from .key_event_to_name import key_event_to_name


class KeyBindingEditor(Editor):
    """ An editor for modifying bindings of keys to controls.
    """

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
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.control = KeyBindingCtrl(self)

    def update_object(self, event):
        """ Handles the user entering input data in the edit control.
        """
        try:
            self.value = value = key_event_to_name(event)
            self._binding.text = value
        except:
            pass

    def update_editor(self):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        self.control.setText(self.value)

    def update_focus(self, has_focus):
        """ Updates the current focus setting of the control.
        """
        if has_focus:
            self._binding.border_size = 1
            self.object.owner.focus_owner = self._binding

    def _key_changed(self, event):
        """ Handles a keyboard event.
        """
        binding = self.object
        key_name = key_event_to_name(event)
        cur_binding = binding.owner.key_binding_for(binding, key_name)
        if cur_binding is not None:
            if (
                QtGui.QMessageBox.question(
                    self.control,
                    "Duplicate Key Definition",
                    "'%s' has already been assigned to '%s'.\n"
                    "Do you wish to continue?"
                    % (key_name, cur_binding.description),
                    QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                    QtGui.QMessageBox.No,
                )
                != QtGui.QMessageBox.Yes
            ):
                return

        self.value = key_name

    def _clear_changed(self):
        """ Handles a clear field event.
        """
        self.value = ""


class KeyBindingCtrl(QtGui.QLabel):
    """ PyQt control for editing key bindings.
    """

    def __init__(self, editor, parent=None):
        super().__init__(parent)

        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setIndent(4)
        self.setMinimumWidth(160)

        pal = QtGui.QPalette(self.palette())
        pal.setColor(QtGui.QPalette.Window, QtCore.Qt.white)
        self.setPalette(pal)
        self.setAutoFillBackground(True)

        # Save the reference to the controlling editor object:
        self.editor = editor

        # Indicate we don't have the focus right now:
        editor.has_focus = False

    def keyPressEvent(self, event):
        """ Handle keyboard keys being pressed.
        """
        # Ignore presses of the control and shift keys.
        if event.key() not in (QtCore.Qt.Key_Control, QtCore.Qt.Key_Shift):
            self.editor.key = event

    def paintEvent(self, event):
        """ Updates the screen.
        """
        QtGui.QLabel.paintEvent(self, event)

        w = self.width()
        h = self.height()
        p = QtGui.QPainter(self)

        if self.editor.has_focus:
            p.setRenderHint(QtGui.QPainter.Antialiasing, True)
            pen = QtGui.QPen(QtGui.QColor("tomato"))
            pen.setWidth(2)
            p.setPen(pen)
            p.drawRect(1, 1, w - 2, h - 2)
        else:
            p.setPen(self.palette().color(QtGui.QPalette.Mid))
            p.drawRect(0, 0, w - 1, h - 1)

        p.end()

    def focusInEvent(self, event):
        """ Handles getting the focus.
        """
        self.editor.has_focus = True
        self.update()

    def focusOutEvent(self, event):
        """ Handles losing the focus.
        """
        self.editor.has_focus = False
        self.update()

    def mouseDoubleClickEvent(self, event):
        """ Handles the user double clicking the control to clear its contents.
        """
        self.editor.clear = True
