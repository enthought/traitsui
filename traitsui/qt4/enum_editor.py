# (C) Copyright 2009-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

# ------------------------------------------------------------------------------
# Copyright (c) 2008, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD license.
# However, when used with the GPL version of PyQt the additional terms
# described in the PyQt GPL exception also apply

#
# Author: Riverbank Computing Limited
# ------------------------------------------------------------------------------

""" Defines the various editors and the editor factory for single-selection
    enumerations, for the PyQt user interface toolkit.
"""

from functools import reduce


from pyface.qt import QtCore, QtGui, is_pyside

from traits.api import Bool, Property

from traitsui.helper import enum_values_changed
from .constants import OKColor, ErrorColor
from .editor import Editor

completion_mode_map = {
    "popup": QtGui.QCompleter.CompletionMode.PopupCompletion,
    "inline": QtGui.QCompleter.CompletionMode.InlineCompletion,
}


class BaseEditor(Editor):
    """Base class for enumeration editors."""

    #: Current set of enumeration names:
    names = Property()

    #: Current mapping from names to values:
    mapping = Property()

    #: Current inverse mapping from values to names:
    inverse_mapping = Property()

    # -------------------------------------------------------------------------
    #  BaseEditor Interface
    # -------------------------------------------------------------------------

    def values_changed(self):
        """Recomputes the cached data based on the underlying enumeration model
        or the values of the factory.
        """
        (
            self._names,
            self._mapping,
            self._inverse_mapping,
        ) = enum_values_changed(self._value(), self.string_value)

    def rebuild_editor(self):
        """Rebuilds the contents of the editor whenever the original factory
        object's **values** trait changes.

        This is not needed for the Qt backends.
        """
        raise NotImplementedError

    # -------------------------------------------------------------------------
    #  Editor Interface
    # -------------------------------------------------------------------------

    def init(self, parent):
        """Finishes initializing the editor by creating the underlying toolkit
        widget.
        """
        factory = self.factory
        if factory.name != "":
            self._object, self._name, self._value = self.parse_extended_name(
                factory.name
            )
            self.values_changed()
            self._object.observe(
                self._update_values_and_rebuild_editor,
                self._name + '.items',
                dispatch="ui",
            )
        else:
            self._value = lambda: self.factory.values
            self.values_changed()
            factory.observe(
                self._update_values_and_rebuild_editor, "values", dispatch="ui"
            )

    def dispose(self):
        """Disposes of the contents of an editor."""
        if self._object is not None:
            self._object.observe(
                self._update_values_and_rebuild_editor,
                self._name + '.items',
                remove=True,
                dispatch="ui",
            )
        else:
            self.factory.observe(
                self._update_values_and_rebuild_editor,
                "values",
                remove=True,
                dispatch="ui",
            )

        super().dispose()

    # -------------------------------------------------------------------------
    #  Private interface
    # -------------------------------------------------------------------------

    # Trait default handlers -------------------------------------------------

    def _get_names(self):
        """Gets the current set of enumeration names."""
        return self._names

    def _get_mapping(self):
        """Gets the current mapping."""
        return self._mapping

    def _get_inverse_mapping(self):
        """Gets the current inverse mapping."""
        return self._inverse_mapping

    # Trait change handlers --------------------------------------------------

    def _update_values_and_rebuild_editor(self, event):
        """Handles the underlying object model's enumeration set or factory's
        values being changed.
        """
        self.values_changed()
        self.rebuild_editor()


class SimpleEditor(BaseEditor):
    """Simple style of enumeration editor, which displays a combo box."""

    # -------------------------------------------------------------------------
    #  Editor Interface
    # -------------------------------------------------------------------------

    def init(self, parent):
        """Finishes initializing the editor by creating the underlying toolkit
        widget.
        """
        super().init(parent)

        self.control = control = self.create_combo_box()
        self._add_items_to_combo_box()

        control.currentIndexChanged.connect(self.update_object)

        if self.factory.evaluate is not None:
            control.setEditable(True)
            control.completer().setCompletionMode(
                completion_mode_map[self.factory.completion_mode]
            )
            if self.factory.auto_set:
                control.editTextChanged.connect(self.update_text_object)
            else:
                control.lineEdit().editingFinished.connect(
                    self.update_autoset_text_object
                )
            control.setInsertPolicy(QtGui.QComboBox.InsertPolicy.NoInsert)

        self._no_enum_update = 0
        self.set_tooltip()

    def update_editor(self):
        """Updates the editor when the object trait changes externally to the
        editor.
        """
        if self._no_enum_update == 0:
            self._no_enum_update += 1
            if self.factory.evaluate is None:
                try:
                    index = self.names.index(self.inverse_mapping[self.value])
                    self.control.setCurrentIndex(index)
                except Exception:
                    self.control.setCurrentIndex(-1)
            else:
                try:
                    self.control.setEditText(self.str_value)
                except Exception:
                    self.control.setEditText("")
            self._no_enum_update -= 1

    def error(self, excp):
        """Handles an error that occurs while setting the object's trait value."""
        self._set_background(ErrorColor)

    def rebuild_editor(self):
        """Rebuilds the contents of the editor whenever the original factory
        object's **values** trait changes.
        """
        self.control.blockSignals(True)
        try:
            self.control.clear()
            self._add_items_to_combo_box()
        finally:
            self.control.blockSignals(False)

        self.update_editor()

    def set_size_policy(self, direction, resizable, springy, stretch):
        super().set_size_policy(direction, resizable, springy, stretch)

        if (direction == QtGui.QBoxLayout.Direction.LeftToRight and springy) or (
            direction != QtGui.QBoxLayout.Direction.LeftToRight and resizable
        ):
            self.control.setSizeAdjustPolicy(
                QtGui.QComboBox.SizeAdjustPolicy.AdjustToContentsOnFirstShow
            )

    # -------------------------------------------------------------------------
    #  Private interface
    # -------------------------------------------------------------------------

    def create_combo_box(self):
        """Returns the QComboBox used for the editor control."""
        control = QtGui.QComboBox()
        control.setSizeAdjustPolicy(QtGui.QComboBox.SizeAdjustPolicy.AdjustToContents)
        control.setSizePolicy(
            QtGui.QSizePolicy.Policy.Maximum, QtGui.QSizePolicy.Policy.Fixed
        )
        return control

    def _add_items_to_combo_box(self):
        for name in self.names:
            if self.factory.use_separator and name == self.factory.separator:
                self.control.insertSeparator(self.control.count())
            else:
                self.control.addItem(name)

    def _set_background(self, col):
        le = self.control.lineEdit()
        pal = QtGui.QPalette(le.palette())
        pal.setColor(QtGui.QPalette.ColorRole.Base, col)
        le.setPalette(pal)

    #  Signal handlers -------------------------------------------------------

    def update_object(self, index):
        """Handles the user selecting a new value from the combo box."""
        if self._no_enum_update == 0:
            self._no_enum_update += 1
            try:
                text = self.names[index]
                self.value = self.mapping[text]
            except Exception:
                from traitsui.api import raise_to_debug

                raise_to_debug()
            self._no_enum_update -= 1

    def update_text_object(self, text):
        """Handles the user typing text into the combo box text entry field."""
        if self._no_enum_update == 0:

            value = str(text)
            try:
                value = self.mapping[value]
            except Exception:
                try:
                    value = self.factory.evaluate(value)
                except Exception as excp:
                    self.error(excp)
                    return

            self._no_enum_update += 1
            try:
                self.value = value
            except Exception as excp:
                self._no_enum_update -= 1
                self.error(excp)
                return
            self._set_background(OKColor)
            self._no_enum_update -= 1

    def update_autoset_text_object(self):
        # Don't get the final text with the editingFinished signal
        if self.control is not None:
            text = self.control.lineEdit().text()
            return self.update_text_object(text)


class RadioEditor(BaseEditor):
    """Enumeration editor, used for the "custom" style, that displays radio
    buttons.
    """

    #: Is the button layout row-major or column-major?
    row_major = Bool(False)

    # -------------------------------------------------------------------------
    #  Editor Interface
    # -------------------------------------------------------------------------

    def init(self, parent):
        """Finishes initializing the editor by creating the underlying toolkit
        widget.
        """
        super().init(parent)

        self.control = QtGui.QWidget()
        layout = QtGui.QGridLayout(self.control)
        layout.setContentsMargins(0, 0, 0, 0)

        self._mapper = QtCore.QSignalMapper()
        if is_pyside and QtCore.__version_info__ >= (5, 15):
            self._mapper.mappedInt.connect(self.update_object)
        else:
            self._mapper.mapped.connect(self.update_object)

        self.rebuild_editor()

    def update_editor(self):
        """Updates the editor when the object trait changes externally to the
        editor.
        """
        layout = self.control.layout()
        value = self.value
        for i in range(layout.count()):
            rb = layout.itemAt(i).widget()
            rb.setChecked(rb.value == value)

    def rebuild_editor(self):
        """Rebuilds the contents of the editor whenever the original factory
        object's **values** trait changes.
        """
        # Clear any existing content:
        self.clear_layout()

        # Get the current trait value:
        cur_name = self.str_value

        # Create a sizer to manage the radio buttons:
        names = self.names
        mapping = self.mapping
        n = len(names)
        cols = self.factory.cols
        rows = (n + cols - 1) // cols
        # incr will keep track of how to increment index so that as we traverse
        # the grid in row major order, the elements are added to appear in
        # the correct order
        if self.row_major:
            incr = [1] * cols
        else:
            incr = [n // cols] * cols
            rem = n % cols
            for i in range(cols):
                incr[i] += rem > i
            incr[-1] = -(reduce(lambda x, y: x + y, incr[:-1], 0) - 1)
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
                    name = names[index]
                    rb = self.create_button(name)
                    rb.value = mapping[name]

                    rb.setChecked(name == cur_name)

                    # The connection type is set to workaround Qt5 + MacOSX
                    # issue with event dispatching. See enthought/traitsui#1308
                    rb.clicked.connect(
                        self._mapper.map, type=QtCore.Qt.ConnectionType.QueuedConnection
                    )
                    self._mapper.setMapping(rb, index)

                    self.set_tooltip(rb)
                    layout.addWidget(rb, i, j)

                    index += int(round(incr[j]))
                    n -= 1

    # -------------------------------------------------------------------------
    #  Private interface
    # -------------------------------------------------------------------------

    def create_button(self, name):
        """Returns the QAbstractButton used for the radio button."""
        label = self.string_value(name, str.capitalize)
        return QtGui.QRadioButton(label)

    #  Signal handlers -------------------------------------------------------

    def update_object(self, index):
        """Handles the user clicking one of the custom radio buttons."""
        try:
            self.value = self.mapping[self.names[index]]
        except Exception:
            pass


class ListEditor(BaseEditor):
    """Enumeration editor, used for the "custom" style, that displays a list
    box.
    """

    # -------------------------------------------------------------------------
    #  Editor Interface
    # -------------------------------------------------------------------------

    def init(self, parent):
        """Finishes initializing the editor by creating the underlying toolkit
        widget.
        """
        super().init(parent)

        self.control = QtGui.QListWidget()
        self.control.currentTextChanged.connect(self.update_object)

        self.rebuild_editor()
        self.set_tooltip()

    def update_editor(self):
        """Updates the editor when the object trait changes externally to the
        editor.
        """
        control = self.control
        try:
            value = self.inverse_mapping[self.value]

            for row in range(control.count()):
                itm = control.item(row)

                if itm.text() == value:
                    control.setCurrentItem(itm)
                    control.scrollToItem(itm)
                    break
        except Exception:
            pass

    def rebuild_editor(self):
        """Rebuilds the contents of the editor whenever the original factory
        object's **values** trait changes.
        """

        self.control.blockSignals(True)
        self.control.clear()
        for name in self.names:
            self.control.addItem(name)
        self.control.blockSignals(False)

        self.update_editor()

    # -------------------------------------------------------------------------
    #  Private interface
    # -------------------------------------------------------------------------

    #  Signal handlers -------------------------------------------------------

    def update_object(self, text):
        """Handles the user selecting a list box item."""
        value = str(text)
        try:
            value = self.mapping[value]
        except Exception:
            try:
                value = self.factory.evaluate(value)
            except Exception:
                pass
        try:
            self.value = value
        except Exception:
            pass
