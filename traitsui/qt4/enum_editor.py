#------------------------------------------------------------------------------
# Copyright (c) 2008, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD license.
# However, when used with the GPL version of PyQt the additional terms
# described in the PyQt GPL exception also apply

#
# Author: Riverbank Computing Limited
#------------------------------------------------------------------------------

""" Defines the various editors and the editor factory for single-selection
    enumerations, for the PyQt user interface toolkit.
"""

#-------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------

from pyface.qt import QtCore, QtGui

from traits.api \
    import Bool, Property

# FIXME: ToolkitEditorFactory is a proxy class defined here just for backward
# compatibility. The class has been moved to the
# traitsui.editors.enum_editor file.
from traitsui.editors.enum_editor \
    import ToolkitEditorFactory

from editor \
    import Editor

from constants \
    import OKColor, ErrorColor

from traitsui.helper \
    import enum_values_changed
from functools import reduce


# default formatting function (would import from string, but not in Python 3)
capitalize = lambda s: s.capitalize()


#-------------------------------------------------------------------------
#  'BaseEditor' class:
#-------------------------------------------------------------------------

class BaseEditor(Editor):
    """ Base class for enumeration editors.
    """

    #-------------------------------------------------------------------------
    #  Trait definitions:
    #-------------------------------------------------------------------------

    # Current set of enumeration names:
    names = Property

    # Current mapping from names to values:
    mapping = Property

    # Current inverse mapping from values to names:
    inverse_mapping = Property

    #-------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #-------------------------------------------------------------------------

    def init(self, parent):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        factory = self.factory
        if factory.name != '':
            self._object, self._name, self._value = \
                self.parse_extended_name(factory.name)
            self.values_changed()
            self._object.on_trait_change(self._values_changed,
                                         ' ' + self._name, dispatch='ui')
        else:
            factory.on_trait_change(self.rebuild_editor, 'values_modified',
                                    dispatch='ui')

    #-------------------------------------------------------------------------
    #  Gets the current set of enumeration names:
    #-------------------------------------------------------------------------

    def _get_names(self):
        """ Gets the current set of enumeration names.
        """
        if self._object is None:
            return self.factory._names

        return self._names

    #-------------------------------------------------------------------------
    #  Gets the current mapping:
    #-------------------------------------------------------------------------

    def _get_mapping(self):
        """ Gets the current mapping.
        """
        if self._object is None:
            return self.factory._mapping

        return self._mapping

    #-------------------------------------------------------------------------
    #  Gets the current inverse mapping:
    #-------------------------------------------------------------------------

    def _get_inverse_mapping(self):
        """ Gets the current inverse mapping.
        """
        if self._object is None:
            return self.factory._inverse_mapping

        return self._inverse_mapping

    #-------------------------------------------------------------------------
    #  Rebuilds the contents of the editor whenever the original factory
    #  object's 'values' trait changes:
    #-------------------------------------------------------------------------

    def rebuild_editor(self):
        """ Rebuilds the contents of the editor whenever the original factory
            object's **values** trait changes.
        """
        raise NotImplementedError

    #-------------------------------------------------------------------------
    #  Recomputes the cached data based on the underlying enumeration model:
    #-------------------------------------------------------------------------

    def values_changed(self):
        """ Recomputes the cached data based on the underlying enumeration model.
        """
        self._names, self._mapping, self._inverse_mapping = \
            enum_values_changed(self._value(), self.string_value)

    #-------------------------------------------------------------------------
    #  Handles the underlying object model's enumeration set being changed:
    #-------------------------------------------------------------------------

    def _values_changed(self):
        """ Handles the underlying object model's enumeration set being changed.
        """
        self.values_changed()
        self.rebuild_editor()

    #-------------------------------------------------------------------------
    #  Disposes of the contents of an editor:
    #-------------------------------------------------------------------------

    def dispose(self):
        """ Disposes of the contents of an editor.
        """
        if self._object is not None:
            self._object.on_trait_change(self._values_changed,
                                         ' ' + self._name, remove=True)
        else:
            self.factory.on_trait_change(self.rebuild_editor,
                                         'values_modified', remove=True)

        super(BaseEditor, self).dispose()

#-------------------------------------------------------------------------
#  'SimpleEditor' class:
#-------------------------------------------------------------------------


class SimpleEditor(BaseEditor):
    """ Simple style of enumeration editor, which displays a combo box.
    """

    #-------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #-------------------------------------------------------------------------

    def init(self, parent):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        super(SimpleEditor, self).init(parent)

        self.control = control = self.create_combo_box()
        control.addItems(self.names)

        control.currentIndexChanged[str].connect(self.update_object)

        if self.factory.evaluate is not None:
            control.setEditable(True)
            if self.factory.auto_set:
                control.editTextChanged.connect(self.update_text_object)
            else:
                control.lineEdit().editingFinished.connect(
                    self.update_autoset_text_object)
            control.setInsertPolicy(QtGui.QComboBox.NoInsert)

        self._no_enum_update = 0
        self.set_tooltip()

    #-------------------------------------------------------------------------
    #  Returns the QComboBox used for the editor control:
    #-------------------------------------------------------------------------

    def create_combo_box(self):
        """ Returns the QComboBox used for the editor control.
        """
        control = QtGui.QComboBox()
        control.setSizeAdjustPolicy(QtGui.QComboBox.AdjustToContents)
        control.setSizePolicy(QtGui.QSizePolicy.Maximum,
                              QtGui.QSizePolicy.Fixed)
        return control

    #-------------------------------------------------------------------------
    #  Adjust size policy to behave properly in group
    #-------------------------------------------------------------------------

    def set_size_policy(self, direction, resizable, springy, stretch):
        super(
            SimpleEditor,
            self).set_size_policy(
            direction,
            resizable,
            springy,
            stretch)

        if ((direction == QtGui.QBoxLayout.LeftToRight and springy) or
                (direction != QtGui.QBoxLayout.LeftToRight and resizable)):
            self.control.setSizeAdjustPolicy(
                QtGui.QComboBox.AdjustToContentsOnFirstShow)

    #-------------------------------------------------------------------------
    #  Handles the user selecting a new value from the combo box:
    #-------------------------------------------------------------------------

    def update_object(self, text):
        """ Handles the user selecting a new value from the combo box.
        """
        if self._no_enum_update == 0:
            self._no_enum_update += 1
            try:
                self.value = self.mapping[unicode(text)]
            except:
                from traitsui.api import raise_to_debug
                raise_to_debug()
            self._no_enum_update -= 1

    #-------------------------------------------------------------------------
    #  Handles the user typing text into the combo box text entry field:
    #-------------------------------------------------------------------------

    def update_text_object(self, text):
        """ Handles the user typing text into the combo box text entry field.
        """
        if self._no_enum_update == 0:
            value = unicode(text)
            try:
                value = self.mapping[value]
            except:
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

    #-------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #-------------------------------------------------------------------------

    def update_editor(self):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        if self._no_enum_update == 0:
            self._no_enum_update += 1
            if self.factory.evaluate is None:
                try:
                    index = self.names.index(self.inverse_mapping[self.value])
                    self.control.setCurrentIndex(index)
                except:
                    self.control.setCurrentIndex(-1)
            else:
                try:
                    self.control.setEditText(self.str_value)
                except:
                    self.control.setEditText('')
            self._no_enum_update -= 1

    #-------------------------------------------------------------------------
    #  Handles an error that occurs while setting the object's trait value:
    #-------------------------------------------------------------------------

    def error(self, excp):
        """ Handles an error that occurs while setting the object's trait value.
        """
        self._set_background(ErrorColor)

    #-------------------------------------------------------------------------
    #  Sets the background color of the QLineEdit of the QComboBox.
    #-------------------------------------------------------------------------

    def _set_background(self, col):
        le = self.control.lineEdit()
        pal = QtGui.QPalette(le.palette())
        pal.setColor(QtGui.QPalette.Base, col)
        le.setPalette(pal)

    #-------------------------------------------------------------------------
    #  Rebuilds the contents of the editor whenever the original factory
    #  object's 'values' trait changes:
    #-------------------------------------------------------------------------

    def rebuild_editor(self):
        """ Rebuilds the contents of the editor whenever the original factory
            object's **values** trait changes.
        """
        self.control.blockSignals(True)
        self.control.clear()
        self.control.addItems(self.names)
        self.control.blockSignals(False)

        self.update_editor()

#-------------------------------------------------------------------------
#  'RadioEditor' class:
#-------------------------------------------------------------------------


class RadioEditor(BaseEditor):
    """ Enumeration editor, used for the "custom" style, that displays radio
        buttons.
    """

    # Is the button layout row-major or column-major?
    row_major = Bool(False)

    #-------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #-------------------------------------------------------------------------

    def init(self, parent):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        super(RadioEditor, self).init(parent)

        self.control = QtGui.QWidget()
        layout = QtGui.QGridLayout(self.control)
        layout.setContentsMargins(0, 0, 0, 0)

        self._mapper = QtCore.QSignalMapper()
        self._mapper.mapped.connect(self.update_object)

        self.rebuild_editor()

    #-------------------------------------------------------------------------
    #  Handles the user clicking one of the 'custom' radio buttons:
    #-------------------------------------------------------------------------

    def update_object(self, index):
        """ Handles the user clicking one of the custom radio buttons.
        """
        try:
            self.value = self.mapping[self.names[index]]
        except:
            pass

    #-------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #-------------------------------------------------------------------------

    def update_editor(self):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        layout = self.control.layout()
        value = self.value
        for i in range(layout.count()):
            rb = layout.itemAt(i).widget()
            rb.setChecked(rb.value == value)

    #-------------------------------------------------------------------------
    #  Rebuilds the contents of the editor whenever the original factory
    #  object's 'values' trait changes:
    #-------------------------------------------------------------------------

    def rebuild_editor(self):
        """ Rebuilds the contents of the editor whenever the original factory
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
        if self.row_major:
            incr = [1] * cols
        else:
            incr = [n // cols] * cols
            rem = n % cols
            for i in range(cols):
                incr[i] += (rem > i)
            incr[-1] = -(reduce(lambda x, y: x + y, incr[:-1], 0) - 1)

        # Add the set of all possible choices:
        layout = self.control.layout()
        index = 0
        for i in range(rows):
            for j in range(cols):
                if n > 0:
                    name = names[index]
                    rb = self.create_button(name)
                    rb.value = mapping[name]

                    rb.setChecked(name == cur_name)

                    rb.clicked.connect(self._mapper.map)
                    self._mapper.setMapping(rb, index)

                    self.set_tooltip(rb)
                    layout.addWidget(rb, i, j)

                    index += int(round(incr[j]))
                    n -= 1

    #-------------------------------------------------------------------------
    #  Returns the QAbstractButton used for the radio button:
    #-------------------------------------------------------------------------

    def create_button(self, name):
        """ Returns the QAbstractButton used for the radio button.
        """
        label = self.string_value(name, capitalize)
        return QtGui.QRadioButton(label)

#-------------------------------------------------------------------------
#  'ListEditor' class:
#-------------------------------------------------------------------------


class ListEditor(BaseEditor):
    """ Enumeration editor, used for the "custom" style, that displays a list
        box.
    """
    #-------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #-------------------------------------------------------------------------

    def init(self, parent):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        super(ListEditor, self).init(parent)

        self.control = QtGui.QListWidget()
        self.control.currentTextChanged.connect(self.update_object)

        self.rebuild_editor()
        self.set_tooltip()

    #-------------------------------------------------------------------------
    #  Handles the user selecting a list box item:
    #-------------------------------------------------------------------------

    def update_object(self, text):
        """ Handles the user selecting a list box item.
        """
        value = unicode(text)
        try:
            value = self.mapping[value]
        except:
            try:
                value = self.factory.evaluate(value)
            except:
                pass
        try:
            self.value = value
        except:
            pass

    #-------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #-------------------------------------------------------------------------

    def update_editor(self):
        """ Updates the editor when the object trait changes externally to the
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
        except:
            pass

    #-------------------------------------------------------------------------
    #  Rebuilds the contents of the editor whenever the original factory
    #  object's 'values' trait changes:
    #-------------------------------------------------------------------------

    def rebuild_editor(self):
        """ Rebuilds the contents of the editor whenever the original factory
            object's **values** trait changes.
        """

        self.control.blockSignals(True)
        self.control.clear()
        for name in self.names:
            self.control.addItem(name)
        self.control.blockSignals(False)

        self.update_editor()
