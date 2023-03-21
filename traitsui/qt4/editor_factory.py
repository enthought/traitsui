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

""" Defines the base PyQt classes the various styles of editors used in a
Traits-based user interface.
"""


from pyface.qt import QtCore, QtGui

from traits.api import TraitError

from .editor import Editor


class SimpleEditor(Editor):
    """Base class for simple style editors, which displays a text field
    containing the text representation of the object trait value. Clicking in
    the text field displays an editor-specific dialog box for changing the
    value.
    """

    def init(self, parent):
        """Finishes initializing the editor by creating the underlying toolkit
        widget.
        """
        self.control = _SimpleField(self)
        self.set_tooltip()

    # -------------------------------------------------------------------------
    #  Invokes the pop-up editor for an object trait:
    #
    #  (Normally overridden in a subclass)
    # -------------------------------------------------------------------------

    def popup_editor(self):
        """Invokes the pop-up editor for an object trait."""
        pass


class TextEditor(Editor):
    """Base class for text style editors, which displays an editable text
    field, containing a text representation of the object trait value.
    """

    def init(self, parent):
        """Finishes initializing the editor by creating the underlying toolkit
        widget.
        """
        self.control = QtGui.QLineEdit(self.str_value)
        self.control.editingFinished.connect(self.update_object)
        self.set_tooltip()

    def dispose(self):
        """Disposes of the contents of an editor."""
        if self.control is not None:
            self.control.editingFinished.disconnect(self.update_object)
        super().dispose()

    def update_object(self):
        """Handles the user changing the contents of the edit control."""
        if self.control is None:
            return
        try:
            self.value = str(self.control.text())
        except TraitError as excp:
            pass


class ReadonlyEditor(Editor):
    """Base class for read-only style editors, which displays a read-only text
    field, containing a text representation of the object trait value.
    """

    # -------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    # -------------------------------------------------------------------------

    text_alignment_map = {
        "left": QtCore.Qt.AlignmentFlag.AlignLeft,
        "right": QtCore.Qt.AlignmentFlag.AlignRight,
        "just": QtCore.Qt.AlignmentFlag.AlignJustify,
        "top": QtCore.Qt.AlignmentFlag.AlignLeft,
        "bottom": QtCore.Qt.AlignmentFlag.AlignBottom,
        "vcenter": QtCore.Qt.AlignmentFlag.AlignVCenter,
        "hcenter": QtCore.Qt.AlignmentFlag.AlignHCenter,
        "center": QtCore.Qt.AlignmentFlag.AlignVCenter | QtCore.Qt.AlignmentFlag.AlignHCenter,
    }

    def init(self, parent):
        """Finishes initializing the editor by creating the underlying toolkit
        widget.
        """
        self.control = QtGui.QLabel(self.str_value)

        if self.item.resizable is True or self.item.height != -1.0:
            self.control.setWordWrap(True)

        alignment = None
        for item in self.factory.text_alignment.split(","):
            item_alignment = self.text_alignment_map.get(item, None)
            if item_alignment:
                if alignment:
                    alignment = alignment | item_alignment
                else:
                    alignment = item_alignment

        if alignment:
            self.control.setAlignment(alignment)

        self.set_tooltip()

    def update_editor(self):
        """Updates the editor when the object trait changes externally to the
        editor.
        """
        self.control.setText(self.str_value)


class _SimpleField(QtGui.QLineEdit):
    def __init__(self, editor):
        QtGui.QLineEdit.__init__(self, editor.str_value)

        self.setReadOnly(True)
        self._editor = editor

    def mouseReleaseEvent(self, e):
        QtGui.QLineEdit.mouseReleaseEvent(self, e)

        if e.button() == QtCore.Qt.MouseButton.LeftButton:
            self._editor.popup_editor()
