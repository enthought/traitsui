# (C) Copyright 2008-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

# Copyright (c) 2007, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD license.
# However, when used with the GPL version of PyQt the additional terms
# described in the PyQt GPL exception also apply
#
# Author: Riverbank Computing Limited

""" Defines various directory editor for the PyQt user interface toolkit.
"""

from pyface.api import DirectoryDialog

from .file_editor import (
    SimpleEditor as SimpleFileEditor,
    CustomEditor as CustomFileEditor,
)


class SimpleEditor(SimpleFileEditor):
    """Simple style of editor for directories, which displays a text field
    and a **Browse** button that opens a directory-selection dialog box.
    """

    def _create_file_dialog(self):
        """Creates the correct type of file dialog."""

        dlg = DirectoryDialog(
            parent=self.get_control_widget(),
            default_path=self._file_name.text(),
        )
        return dlg


class CustomEditor(CustomFileEditor):
    """Custom style of editor for directories, which displays a tree view of
    the file system.
    """

    def init(self, parent):
        super().init(parent)
        self._model.setNameFilterDisables(True)
        self._model.setNameFilters([""])

    def update_object(self, idx):
        """Handles the user changing the contents of the edit control."""
        if self.control is not None:
            if self._model.isDir(idx):
                self.value = str(self._model.filePath(idx))

    # Trait change handlers --------------------------------------------------

    def _filter_changed(self):
        """Handles the 'filter' trait being changed."""
        # name filters don't apply to directories
        pass
