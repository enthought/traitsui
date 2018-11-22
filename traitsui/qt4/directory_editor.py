# Copyright (c) 2007, Riverbank Computing Limited
# Copyright (c) 2018, Enthought, Inc
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD license.
# However, when used with the GPL version of PyQt the additional terms
# described in the PyQt GPL exception also apply
#
# Author: Riverbank Computing Limited

""" Defines various directory editor for the PyQt user interface toolkit.
"""

from __future__ import absolute_import
from pyface.qt import QtGui

# FIXME: ToolkitEditorFactory is a proxy class defined here just for backward
# compatibility. The class has been moved to the
# traitsui.editors.custom_editor file.
from traitsui.editors.directory_editor import ToolkitEditorFactory

from .file_editor import (
    SimpleEditor as SimpleFileEditor, CustomEditor as CustomFileEditor
)
import six


class SimpleEditor(SimpleFileEditor):
    """ Simple style of editor for directories, which displays a text field
        and a **Browse** button that opens a directory-selection dialog box.
    """

    def _create_file_dialog(self):
        """ Creates the correct type of file dialog.
        """
        dlg = QtGui.QFileDialog(self.control)
        dlg.selectFile(self._file_name.text())
        dlg.setFileMode(QtGui.QFileDialog.Directory)
        dlg.setOptions(QtGui.QFileDialog.ShowDirsOnly)

        return dlg


class CustomEditor(CustomFileEditor):
    """ Custom style of editor for directories, which displays a tree view of
        the file system.
    """

    def init(self, parent):
        super(CustomEditor, self).init(parent)
        self._model.setNameFilterDisables(True)
        self._model.setNameFilters([''])

    def update_object(self, idx):
        """ Handles the user changing the contents of the edit control.
        """
        if self.control is not None:
            if self._model.isDir(idx):
                self.value = six.text_type(self._model.filePath(idx))

    # Trait change handlers --------------------------------------------------

    def _filter_changed(self):
        """ Handles the 'filter' trait being changed.
        """
        # name filters don't apply to directories
        pass
