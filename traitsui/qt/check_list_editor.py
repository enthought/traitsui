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

""" Defines the various editors for multi-selection enumerations, for the PyQt
user interface toolkit.
"""


import logging

from pyface.qt import QtCore, QtGui, is_pyside

from traits.api import Any, Callable, List, Str, TraitError, Tuple

from .editor_factory import TextEditor as BaseTextEditor

from .editor import EditorWithList


logger = logging.getLogger(__name__)

# -------------------------------------------------------------------------
#  'SimpleEditor' class:
# -------------------------------------------------------------------------


class SimpleEditor(EditorWithList):
    """Simple style of editor for checklists, which displays a combo box."""

    # -------------------------------------------------------------------------
    #  Trait definitions:
    # -------------------------------------------------------------------------

    #: Checklist item names
    names = List(Str)

    #: Checklist item values
    values = List()

    def init(self, parent):
        """Finishes initializing the editor by creating the underlying toolkit
        widget.
        """
        self.create_control(parent)
        super().init(parent)

    def create_control(self, parent):
        """Creates the initial editor control."""
        self.control = QtGui.QComboBox()
        self.control.activated[int].connect(self.update_object)

    def dispose(self):
        """Disposes of the contents of an editor."""
        if self.control is not None:
            self.control.activated[int].disconnect(self.update_object)

        super().dispose()

    def list_updated(self, values):
        """Handles updates to the list of legal checklist values."""
        sv = self.string_value
        if (len(values) > 0) and isinstance(values[0], str):
            values = [(x, sv(x, str.capitalize)) for x in values]
        self.values = valid_values = [x[0] for x in values]
        self.names = [x[1] for x in values]

        # Make sure the current value is still legal:
        modified = False
        cur_value = parse_value(self.value)
        for i in range(len(cur_value) - 1, -1, -1):
            if cur_value[i] not in valid_values:
                try:
                    del cur_value[i]
                    modified = True
                except TypeError as e:
                    logger.warning(
                        "Unable to remove non-current value [%s] from "
                        "values %s",
                        cur_value[i],
                        values,
                    )
        if modified:
            if isinstance(self.value, str):
                cur_value = ",".join(cur_value)
            self.value = cur_value

        self.rebuild_editor()

    def rebuild_editor(self):
        """Rebuilds the editor after its definition is modified."""
        control = self.control
        control.clear()
        for name in self.names:
            control.addItem(name)
        self.update_editor()

    def update_object(self, index):
        """Handles the user selecting a new value from the combo box."""
        value = self.values[index]
        if not isinstance(self.value, str):
            value = [value]
        self.value = value

    def update_editor(self):
        """Updates the editor when the object trait changes externally to the
        editor.
        """
        try:
            self.control.setCurrentIndex(
                self.values.index(parse_value(self.value)[0])
            )
        except:
            pass


class CustomEditor(SimpleEditor):
    """Custom style of editor for checklists, which displays a set of check
    boxes.
    """

    #: List of tuple(signal, slot) to be disconnected while rebuilding the
    #: editor.
    _connections_to_rebuild = List(Tuple(Any, Callable))

    def init(self, parent):
        """Finishes initializing the editor by creating the underlying toolkit
        widget.
        """
        self.create_control(parent)
        EditorWithList.init(self, parent)

    def create_control(self, parent):
        """Creates the initial editor control."""
        self.control = QtGui.QWidget()
        layout = QtGui.QGridLayout(self.control)
        layout.setContentsMargins(0, 0, 0, 0)

        self._mapper = QtCore.QSignalMapper()
        if is_pyside and QtCore.__version_info__ >= (5, 15):
            self._mapper.mappedString.connect(self.update_object)
        else:
            self._mapper.mapped[str].connect(self.update_object)

    def dispose(self):
        """Disposes of the contents of an editor."""
        while self._connections_to_rebuild:
            signal, handler = self._connections_to_rebuild.pop()
            signal.disconnect(handler)

        # signal from create_control
        if self._mapper is not None:
            if is_pyside and QtCore.__version_info__ >= (5, 15):
                self._mapper.mappedString.disconnect(self.update_object)
            else:
                self._mapper.mapped[str].disconnect(self.update_object)
            self._mapper = None

        # enthought/traitsui#884
        EditorWithList.dispose(self)

    def rebuild_editor(self):
        """Rebuilds the editor after its definition is modified."""
        while self._connections_to_rebuild:
            signal, handler = self._connections_to_rebuild.pop()
            signal.disconnect(handler)

        # Clear any existing content:
        self.clear_layout()

        cur_value = parse_value(self.value)

        # Create a sizer to manage the radio buttons:
        labels = self.names
        values = self.values
        n = len(labels)
        cols = self.factory.cols
        rows = (n + cols - 1) // cols
        # incr will keep track of how to increment index so that as we traverse
        # the grid in row major order, the elements are added to appear in
        # column major order
        incr = [n // cols] * cols
        rem = n % cols
        for i in range(cols):
            incr[i] += rem > i
        incr[-1] = -sum(incr[:-1]) + 1
        # e.g for a gird:
        # 0 2 4
        # 1 3 5
        # incr should be [2, 2, -3]

        # Add the set of all possible choices:
        layout = self.control.layout()
        index = 0
        # populate the layout in row_major order
        for i in range(rows):
            for j in range(cols):
                if n > 0:
                    cb = QtGui.QCheckBox(labels[index])
                    cb.value = values[index]

                    if cb.value in cur_value:
                        cb.setCheckState(QtCore.Qt.CheckState.Checked)
                    else:
                        cb.setCheckState(QtCore.Qt.CheckState.Unchecked)

                    cb.clicked.connect(self._mapper.map)
                    self._connections_to_rebuild.append(
                        (cb.clicked, self._mapper.map)
                    )
                    self._mapper.setMapping(cb, labels[index])

                    layout.addWidget(cb, i, j)

                    index += incr[j]
                    n -= 1

    def update_object(self, label):
        """Handles the user clicking one of the custom check boxes."""
        cb = self._mapper.mapping(label)
        cur_value = parse_value(self.value)
        if cb.checkState() == QtCore.Qt.CheckState.Checked:
            cur_value.append(cb.value)
        elif cb.value in cur_value:
            cur_value.remove(cb.value)

        if isinstance(self.value, str):
            cur_value = ",".join(cur_value)

        self.value = cur_value

    def update_editor(self):
        """Updates the editor when the object trait changes externally to the
        editor.
        """
        new_values = parse_value(self.value)
        for cb in self.control.findChildren(QtGui.QCheckBox, None):
            if cb.value in new_values:
                cb.setCheckState(QtCore.Qt.CheckState.Checked)
            else:
                cb.setCheckState(QtCore.Qt.CheckState.Unchecked)


class TextEditor(BaseTextEditor):
    """Text style of editor for checklists, which displays a text field."""

    def update_object(self, event=None):
        """Handles the user changing the contents of the edit control."""
        try:
            value = str(self.control.text())
            value = eval(value)
        except:
            pass
        try:
            self.value = value
        except TraitError as excp:
            pass


# -------------------------------------------------------------------------
#  Parse a value into a list:
# -------------------------------------------------------------------------


def parse_value(value):
    """Parses a value into a list."""
    if value is None:
        return []
    if not isinstance(value, str):
        return value[:]
    return [x.strip() for x in value.split(",")]
