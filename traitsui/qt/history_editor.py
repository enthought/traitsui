# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Defines a text editor which displays a text field and maintains a history
    of previously entered values.
"""


from pyface.qt import QtGui, is_qt4, is_qt5

from .editor import Editor


class _HistoryEditor(Editor):
    """Simple style text editor, which displays a text field and maintains a
    history of previously entered values, the maximum number of which is
    specified by the 'entries' trait of the HistoryEditor factory.
    """

    # -------------------------------------------------------------------------
    #  'Editor' interface:
    # -------------------------------------------------------------------------

    def init(self, parent):
        """Finishes initializing the editor by creating the underlying toolkit
        widget.
        """
        self.control = control = QtGui.QComboBox()
        control.setEditable(True)
        control.setInsertPolicy(QtGui.QComboBox.InsertPolicy.InsertAtTop)

        if self.factory.entries > 0:
            control.model().rowsInserted.connect(self._truncate)

        if self.factory.auto_set:
            control.editTextChanged.connect(self.update_object)
        else:
            if is_qt4 or is_qt5:
                control.activated[str].connect(self.update_object)
            else:
                control.textActivated.connect(self.update_object)

        self.set_tooltip()

    def update_object(self, text):
        """Handles the user entering input data in the edit control."""
        if not self._no_update:
            self.value = str(text)

    def update_editor(self):
        """Updates the editor when the object trait changes externally to the
        editor.
        """
        self._no_update = True
        self.control.setEditText(self.str_value)
        self._no_update = False

    # -- UI preference save/restore interface ---------------------------------

    def restore_prefs(self, prefs):
        """Restores any saved user preference information associated with the
        editor.
        """
        history = prefs.get("history")
        if history:
            self._no_update = True
            self.control.addItems(history[: self.factory.entries])

            # Adding items sets the edit text, so we reset it afterwards:
            self.control.setEditText(self.str_value)

            self._no_update = False

    def save_prefs(self):
        """Returns any user preference information associated with the editor."""
        history = [
            str(self.control.itemText(index))
            for index in range(self.control.count())
        ]

        # If the view closed successfully, update the history with the current
        # editor value, as long it is different from the current object value:
        if self.ui.result:
            current = str(self.control.currentText())
            if current != self.str_value:
                history.insert(0, current)

        return {"history": history}

    # -------------------------------------------------------------------------
    #  '_HistoryEditor' private interface:
    # -------------------------------------------------------------------------

    def _truncate(self, parent, start, end):
        """Handle items being added to the combo box. If there are too many,
        remove items at the end.
        """
        diff = self.control.count() - self.factory.entries
        if diff > 0:
            for i in range(diff):
                self.control.removeItem(self.factory.entries)
