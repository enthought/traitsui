#------------------------------------------------------------------------------
# Copyright (c) 2007, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD license.
# However, when used with the GPL version of PyQt the additional terms
# described in the PyQt GPL exception also apply

#
# Author: Riverbank Computing Limited
#------------------------------------------------------------------------------

""" Defines the various editors for multi-selection enumerations, for the PyQt
user interface toolkit.
"""

#-------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------

from __future__ import absolute_import, division

import logging

from pyface.qt import QtCore, QtGui

from traits.api \
    import List, Unicode, TraitError

# FIXME: ToolkitEditorFactory is a proxy class defined here just for backward
# compatibility. The class has been moved to the
# traitsui.editors.check_list_editor file.
from traitsui.editors.check_list_editor \
    import ToolkitEditorFactory

from .editor_factory \
    import TextEditor as BaseTextEditor

from .editor \
    import EditorWithList
import six


logger = logging.getLogger(__name__)


# default formatting function (would import from string, but not in Python 3)
capitalize = lambda s: s.capitalize()


#-------------------------------------------------------------------------
#  'SimpleEditor' class:
#-------------------------------------------------------------------------

class SimpleEditor(EditorWithList):
    """ Simple style of editor for checklists, which displays a combo box.
    """

    #-------------------------------------------------------------------------
    #  Trait definitions:
    #-------------------------------------------------------------------------

    # Checklist item names
    names = List(Unicode)

    # Checklist item values
    values = List

    #-------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #-------------------------------------------------------------------------

    def init(self, parent):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.create_control(parent)
        super(SimpleEditor, self).init(parent)

    #-------------------------------------------------------------------------
    #  Creates the initial editor control:
    #-------------------------------------------------------------------------

    def create_control(self, parent):
        """ Creates the initial editor control.
        """
        self.control = QtGui.QComboBox()
        self.control.activated[int].connect(self.update_object)

    #-------------------------------------------------------------------------
    #  Handles the list of legal check list values being updated:
    #-------------------------------------------------------------------------

    def list_updated(self, values):
        """ Handles updates to the list of legal checklist values.
        """
        sv = self.string_value
        if (len(values) > 0) and isinstance(values[0], six.string_types):
            values = [(x, sv(x, capitalize)) for x in values]
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
                    logger.warn('Unable to remove non-current value [%s] from '
                                'values %s', cur_value[i], values)
        if modified:
            if isinstance(self.value, six.string_types):
                cur_value = ','.join(cur_value)
            self.value = cur_value

        self.rebuild_editor()

    #-------------------------------------------------------------------------
    #  Rebuilds the editor after its definition is modified:
    #-------------------------------------------------------------------------

    def rebuild_editor(self):
        """ Rebuilds the editor after its definition is modified.
        """
        control = self.control
        control.clear()
        for name in self.names:
            control.addItem(name)
        self.update_editor()

    #-------------------------------------------------------------------------
    #  Handles the user selecting a new value from the combo box:
    #-------------------------------------------------------------------------

    def update_object(self, index):
        """ Handles the user selecting a new value from the combo box.
        """
        value = self.values[index]
        if not isinstance(self.value, six.string_types):
            value = [value]
        self.value = value

    #-------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #-------------------------------------------------------------------------

    def update_editor(self):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        try:
            self.control.setCurrentIndex(
                self.values.index(parse_value(self.value)[0]))
        except:
            pass

#-------------------------------------------------------------------------
#  'CustomEditor' class:
#-------------------------------------------------------------------------


class CustomEditor(SimpleEditor):
    """ Custom style of editor for checklists, which displays a set of check
        boxes.
    """

    #-------------------------------------------------------------------------
    #  Creates the initial editor control:
    #-------------------------------------------------------------------------

    def create_control(self, parent):
        """ Creates the initial editor control.
        """
        self.control = QtGui.QWidget()
        layout = QtGui.QGridLayout(self.control)
        layout.setContentsMargins(0, 0, 0, 0)

        self._mapper = QtCore.QSignalMapper()
        self._mapper.mapped[six.text_type].connect(self.update_object)

    #-------------------------------------------------------------------------
    #  Rebuilds the editor after its definition is modified:
    #-------------------------------------------------------------------------

    def rebuild_editor(self):
        """ Rebuilds the editor after its definition is modified.
        """
        # Clear any existing content:
        self.clear_layout()

        cur_value = parse_value(self.value)

        # Create a sizer to manage the radio buttons:
        labels = self.names
        values = self.values
        n = len(labels)
        cols = self.factory.cols
        rows = (n + cols - 1) // cols
        incr = [n // cols] * cols
        rem = n % cols
        for i in range(cols):
            incr[i] += (rem > i)
        incr[-1] = -sum(incr[:-1]) + 1

        # Add the set of all possible choices:
        layout = self.control.layout()
        index = 0
        for i in range(rows):
            for j in range(cols):
                if n > 0:
                    cb = QtGui.QCheckBox(labels[index])
                    cb.value = values[index]

                    if cb.value in cur_value:
                        cb.setCheckState(QtCore.Qt.Checked)
                    else:
                        cb.setCheckState(QtCore.Qt.Unchecked)

                    cb.clicked.connect(self._mapper.map)
                    self._mapper.setMapping(cb, labels[index])

                    layout.addWidget(cb, i, j)

                    index += incr[j]
                    n -= 1

    #-------------------------------------------------------------------------
    #  Handles the user clicking one of the 'custom' check boxes:
    #-------------------------------------------------------------------------

    def update_object(self, label):
        """ Handles the user clicking one of the custom check boxes.
        """
        cb = self._mapper.mapping(label)
        cur_value = parse_value(self.value)
        if cb.checkState() == QtCore.Qt.Checked:
            cur_value.append(cb.value)
        elif cb.value in cur_value:
            cur_value.remove(cb.value)

        if isinstance(self.value, six.string_types):
            cur_value = ','.join(cur_value)

        self.value = cur_value

    #-------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #-------------------------------------------------------------------------

    def update_editor(self):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        new_values = parse_value(self.value)
        for cb in self.control.findChildren(QtGui.QCheckBox, None):
            if cb.value in new_values:
                cb.setCheckState(QtCore.Qt.Checked)
            else:
                cb.setCheckState(QtCore.Qt.Unchecked)

#-------------------------------------------------------------------------
#  'TextEditor' class:
#-------------------------------------------------------------------------


class TextEditor(BaseTextEditor):
    """ Text style of editor for checklists, which displays a text field.
    """

    #-------------------------------------------------------------------------
    #  Handles the user changing the contents of the edit control:
    #-------------------------------------------------------------------------

    def update_object(self, event=None):
        """ Handles the user changing the contents of the edit control.
        """
        try:
            value = six.text_type(self.control.text())
            value = eval(value)
        except:
            pass
        try:
            self.value = value
        except TraitError as excp:
            pass

#-------------------------------------------------------------------------
#  Parse a value into a list:
#-------------------------------------------------------------------------


def parse_value(value):
    """ Parses a value into a list.
    """
    if value is None:
        return []
    if not isinstance(value, six.string_types):
        return value[:]
    return [x.strip() for x in value.split(',')]
