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

""" Defines the various text editors for the PyQt user interface toolkit.
"""

from pyface.qt import QtCore, QtGui

from traits.api import Any, Callable, List, TraitError, Tuple

from traitsui.editors.text_editor import evaluate_trait

from .editor import Editor

from .editor_factory import ReadonlyEditor as BaseReadonlyEditor

from .constants import OKColor


class SimpleEditor(Editor):
    """Simple style text editor, which displays a text field."""

    #: Flag for window styles:
    base_style = QtGui.QLineEdit

    #: Background color when input is OK:
    ok_color = OKColor

    # -------------------------------------------------------------------------
    #  Trait definitions:
    # -------------------------------------------------------------------------

    #: Function used to evaluate textual user input:
    evaluate = evaluate_trait

    # -- private trait definitions ------------------------------------------

    #: A list of tuple(Qt signal, slot) connected which need to be disconnected
    #: in dispose.
    _connections_to_remove = List(Tuple(Any, Callable))

    def init(self, parent):
        """Finishes initializing the editor by creating the underlying toolkit
        widget.
        """
        factory = self.factory
        wtype = self.base_style
        self.evaluate = factory.evaluate
        self.sync_value(factory.evaluate_name, "evaluate", "from")

        if not factory.multi_line or factory.is_grid_cell or factory.password:
            wtype = QtGui.QLineEdit

        multi_line = wtype is not QtGui.QLineEdit
        if multi_line:
            self.scrollable = True

        control = wtype(self.str_value)

        if factory.read_only:
            control.setReadOnly(True)

        if factory.password:
            control.setEchoMode(QtGui.QLineEdit.EchoMode.Password)

        if wtype == QtGui.QTextEdit:
            control.textChanged.connect(self.update_object)
            self._connections_to_remove.append(
                (control.textChanged, self.update_object)
            )
        else:
            # QLineEdit
            if factory.auto_set and not factory.is_grid_cell:
                control.textEdited.connect(self.update_object)
                self._connections_to_remove.append(
                    (control.textEdited, self.update_object)
                )
            else:
                control.editingFinished.connect(self.update_object)
                self._connections_to_remove.append(
                    (control.editingFinished, self.update_object)
                )

        placeholder = self.factory.placeholder

        if wtype is not QtGui.QTextEdit or QtCore.__version_info__ >= (5, 2):
            # setPlaceholderText is introduced to QTextEdit since Qt 5.2
            control.setPlaceholderText(placeholder)

        if wtype is not QtGui.QTextEdit and QtCore.__version_info__ >= (5, 2):
            # setClearButtonEnabled is introduced to QLineEdit since Qt 5.2
            control.setClearButtonEnabled(self.factory.cancel_button)

        self.control = control
        # default horizontal policy is Expand, set this to Minimum
        if not (self.item.resizable) and not self.item.springy:
            policy = self.control.sizePolicy()
            policy.setHorizontalPolicy(QtGui.QSizePolicy.Policy.Minimum)
            self.control.setSizePolicy(policy)
        self.set_error_state(False)
        self.set_tooltip()

    def dispose(self):
        """Disposes of the contents of an editor."""
        while self._connections_to_remove:
            signal, handler = self._connections_to_remove.pop()
            signal.disconnect(handler)

        super().dispose()

    def update_object(self):
        """Handles the user entering input data in the edit control."""
        if (not self._no_update) and (self.control is not None):
            try:
                self.value = self._get_user_value()

                if self._error is not None:
                    self._error = None
                    self.ui.errors -= 1

                self.set_error_state(False)

            except TraitError as excp:
                pass

    def update_editor(self):
        """Updates the editor when the object trait changes externally to the
        editor.
        """
        user_value = self._get_user_value()
        try:
            unequal = bool(user_value != self.value)
        except ValueError:
            # This might be a numpy array.
            unequal = True

        if unequal:
            self._no_update = True
            self.control.setText(self.str_value)
            self._no_update = False

        if self._error is not None:
            self._error = None
            self.ui.errors -= 1
            self.set_error_state(False)

    def _get_user_value(self):
        """Gets the actual value corresponding to what the user typed."""
        try:
            value = self.control.text()
        except AttributeError:
            value = self.control.toPlainText()

        value = str(value)

        try:
            value = self.evaluate(value)
        except:
            pass

        try:
            ret = self.factory.mapping.get(value, value)
        except TypeError:
            # The value is probably not hashable.
            ret = value

        return ret

    def error(self, excp):
        """Handles an error that occurs while setting the object's trait value."""
        if self._error is None:
            self._error = True
            self.ui.errors += 1

        self.set_error_state(True)

    def in_error_state(self):
        """Returns whether or not the editor is in an error state."""
        return self.invalid or self._error


class CustomEditor(SimpleEditor):
    """Custom style of text editor, which displays a multi-line text field."""

    #: FIXME: The wx version exposes a wx constant.
    #: Flag for window style. This value overrides the default.
    base_style = QtGui.QTextEdit


class ReadonlyEditor(BaseReadonlyEditor):
    """Read-only style of text editor, which displays a read-only text field."""

    def init(self, parent):
        super().init(parent)

        if self.factory.readonly_allow_selection:
            flags = (
                self.control.textInteractionFlags()
                | QtCore.Qt.TextInteractionFlag.TextSelectableByMouse
            )
            self.control.setTextInteractionFlags(flags)

    def update_editor(self):
        """Updates the editor when the object trait changes externally to the
        editor.
        """
        new_value = self.str_value

        if self.factory.password:
            new_value = "*" * len(new_value)

        self.control.setText(new_value)


# -------------------------------------------------------------------------
#  'TextEditor' class:
# -------------------------------------------------------------------------

# Same as SimpleEditor for a text editor.
TextEditor = SimpleEditor
