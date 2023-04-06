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

""" Defines the various Boolean editors for the PyQt user interface toolkit.
"""


from pyface.qt import QtCore, QtGui

from .editor import Editor

# This needs to be imported in here for use by the editor factory for boolean
# editors (declared in traitsui). The editor factory's text_editor
# method will use the TextEditor in the ui.
from .text_editor import SimpleEditor as TextEditor

from .constants import ReadonlyColor


class SimpleEditor(Editor):
    """Simple style of editor for Boolean values, which displays a check box."""

    def init(self, parent):
        """Finishes initializing the editor by creating the underlying toolkit
        widget.
        """
        self.control = QtGui.QCheckBox()
        self.control.stateChanged.connect(self.update_object)
        self.set_tooltip()

    def dispose(self):
        if self.control is not None:
            self.control.stateChanged.disconnect(self.update_object)
        super().dispose()

    def update_object(self, state):
        """Handles the user clicking the checkbox."""
        self.value = bool(state)

    def update_editor(self):
        """Updates the editor when the object trait changes externally to the
        editor.
        """
        if self.value:
            self.control.setCheckState(QtCore.Qt.CheckState.Checked)
        else:
            self.control.setCheckState(QtCore.Qt.CheckState.Unchecked)


class ReadonlyEditor(Editor):
    """Read-only style of editor for Boolean values, which displays static text
    of either "True" or "False".
    """

    def init(self, parent):
        """Finishes initializing the editor by creating the underlying toolkit
        widget.
        """
        self.control = QtGui.QLineEdit()
        self.control.setReadOnly(True)

        pal = QtGui.QPalette(self.control.palette())
        pal.setColor(QtGui.QPalette.ColorRole.Base, ReadonlyColor)
        self.control.setPalette(pal)

    # -------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #
    #  (Should normally be overridden in a subclass)
    # -------------------------------------------------------------------------

    def update_editor(self):
        """Updates the editor when the object trait changes externally to the
        editor.
        """
        if self.value:
            self.control.setText("True")
        else:
            self.control.setText("False")
