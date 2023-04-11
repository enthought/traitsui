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

""" Defines file editors for the PyQt user interface toolkit.
"""

from os.path import abspath, splitext, isfile, exists

from pyface.qt import QtCore, QtGui, is_qt4
from pyface.api import FileDialog, OK
from traits.api import Any, Callable, List, Event, File, Str, TraitError, Tuple

from .editor import Editor
from .text_editor import SimpleEditor as SimpleTextEditor
from .helper import IconButton


# Wildcard filter:
filter_trait = List(Str)


class SimpleEditor(SimpleTextEditor):
    """Simple style of file editor, consisting of a text field and a **Browse**
    button that opens a file-selection dialog box. The user can also drag
    and drop a file onto this control.
    """

    #: List of tuple(signal, slot) to be removed in dispose.
    #: First item in the tuple is the Qt signal, the second item is the event
    #: handler.
    _connections_to_remove = List(Tuple(Any(), Callable()))

    #: Wildcard filter to apply to the file dialog:
    filter = filter_trait

    def init(self, parent):
        """Finishes initializing the editor by creating the underlying toolkit
        widget.
        """
        self.control = QtGui.QWidget()
        layout = QtGui.QHBoxLayout(self.control)
        layout.setContentsMargins(0, 0, 0, 0)

        self._file_name = control = QtGui.QLineEdit()
        layout.addWidget(control)

        if self.factory.auto_set:
            control.textEdited.connect(self.update_object)
            self._connections_to_remove.append(
                (control.textEdited, self.update_object)
            )
        else:
            # Assume enter_set is set, or else the value will never get
            # updated.
            control.editingFinished.connect(self.update_object)
            self._connections_to_remove.append(
                (control.editingFinished, self.update_object)
            )

        button = IconButton(QtGui.QStyle.StandardPixmap.SP_DirIcon, self.show_file_dialog)
        layout.addWidget(button)

        self.set_tooltip(control)

        self.filter = self.factory.filter
        self.sync_value(self.factory.filter_name, "filter", "from", is_list=True)

    def dispose(self):
        """Disposes of the contents of an editor."""
        while self._connections_to_remove:
            signal, handler = self._connections_to_remove.pop()
            signal.disconnect(handler)

        # IconButton.clicked signal should be disconnected here.
        # (enthought/traitsui#888)

        # skip the dispose from TextEditor (enthought/traitsui#884)
        Editor.dispose(self)

    def update_object(self):
        """Handles the user changing the contents of the edit control."""
        if self.control is not None:
            file_name = str(self._file_name.text())
            try:
                if self.factory.truncate_ext:
                    file_name = splitext(file_name)[0]

                self.value = file_name
            except TraitError as excp:
                self._file_name.setText(self.value)

    def update_editor(self):
        """Updates the editor when the object trait changes externally to the
        editor.
        """
        self._file_name.setText(self.str_value)

    def show_file_dialog(self):
        """Displays the pop-up file dialog."""
        # We don't used the canned functions because we don't know how the
        # file name is to be used (ie. an existing one to be opened or a new
        # one to be created).
        dlg = self._create_file_dialog()
        dlg.open()

        if dlg.return_code == OK:
            if self.factory.truncate_ext:
                self.value = splitext(dlg.path)[0]
            else:
                self.value = dlg.path
            self.update_editor()

    def get_error_control(self):
        """Returns the editor's control for indicating error status."""
        return self._file_name

    # -- Private Methods ------------------------------------------------------

    def _create_file_dialog(self):
        """Creates the correct type of file dialog."""
        wildcard = " ".join(self.factory.filter)
        dlg = FileDialog(
            parent=self.get_control_widget(),
            default_path=self._file_name.text(),
            action="save as" if self.factory.dialog_style == "save" else "open",
            wildcard=wildcard,
        )
        return dlg


class CustomEditor(SimpleTextEditor):
    """Custom style of file editor, consisting of a file system tree view."""

    #: Is the file editor scrollable? This value overrides the default.
    scrollable = True

    #: Wildcard filter to apply to the file dialog:
    filter = filter_trait

    #: The root path of the file tree view.
    root_path = File()

    #: Event fired when the file system view should be rebuilt:
    reload = Event()

    #: Event fired when the user double-clicks a file:
    dclick = Event()

    def init(self, parent):
        """Finishes initializing the editor by creating the underlying toolkit
        widget.
        """
        control = _TreeView(self)
        control.doubleClicked.connect(self._on_dclick)

        self._model = model = QtGui.QFileSystemModel()

        current_path = abspath(self.str_value)

        # Don't apply filters to directories and don't show "." and ".."
        model.setFilter(
            QtCore.QDir.Filter.AllDirs
            | QtCore.QDir.Filter.Files
            | QtCore.QDir.Filter.Drives
            | QtCore.QDir.Filter.NoDotAndDotDot
        )

        # Hide filtered out files instead of only disabling them
        self._model.setNameFilterDisables(False)

        # Show the user's home directory by default.
        model.setRootPath(QtCore.QDir.homePath())

        control.setModel(model)
        control.setRootIndex(model.index(QtCore.QDir.homePath()))

        self.control = control

        # set the current item
        if current_path:
            index = model.index(current_path)
            control.expand(index)
            control.setCurrentIndex(index)

        # Hide the labels at the top and only show the column for the file name
        self.control.header().hide()
        for column in range(1, model.columnCount()):
            self.control.hideColumn(column)

        factory = self.factory
        self.filter = factory.filter
        self.root_path = factory.root_path
        self.sync_value(factory.filter_name, "filter", "from", is_list=True)
        self.sync_value(factory.root_path_name, "root_path", "from")
        self.sync_value(factory.reload_name, "reload", "from")
        self.sync_value(factory.dclick_name, "dclick", "to")

        self.set_tooltip()

        # This is needed to enable horizontal scrollbar.
        header = self.control.header()
        if is_qt4:
            header.setResizeMode(0, QtGui.QHeaderView.ResizeMode.ResizeToContents)
        else:
            header.setSectionResizeMode(0, QtGui.QHeaderView.ResizeMode.ResizeToContents)
        header.setStretchLastSection(False)

    def dispose(self):
        """Disposes of the contents of an editor."""
        self._model.beginResetModel()
        self._model.endResetModel()

        if self.control is not None:
            self.control.doubleClicked.disconnect(self._on_dclick)

        # Skip dispose from simple text editor (enthought/traitsui#884)
        Editor.dispose(self)

    def update_object(self, idx):
        """Handles the user changing the contents of the edit control."""
        if self.control is not None:
            path = str(self._model.filePath(idx))

            if self.factory.allow_dir or isfile(path):
                if self.factory.truncate_ext:
                    path = splitext(path)[0]

                self.value = path

    def update_editor(self):
        """Updates the editor when the object trait changes externally to the
        editor.
        """
        if exists(self.str_value):
            index = self._model.index(abspath(self.str_value))
            self.control.expand(index)
            self.control.setCurrentIndex(index)

    # -- Private Methods ------------------------------------------------------

    def _on_dclick(self, idx):
        """Handles the user double-clicking on a file name."""
        self.dclick = str(self._model.filePath(idx))

    # Trait change handlers --------------------------------------------------

    def _filter_changed(self):
        """Handles the 'filter' trait being changed."""
        self._model.setNameFilters(self.filter)

    def _root_path_changed(self):
        """Handles the 'root_path' trait being changed."""
        path = self.root_path
        if not path:
            path = QtCore.QDir.homePath()
        self._model.setRootPath(path)
        self.control.setRootIndex(self._model.index(path))

    def _reload_changed(self):
        """Handles the 'reload' trait being changed."""
        self._model.refresh()


class _TreeView(QtGui.QTreeView):
    """This is an internal class needed because QAbstractItemView doesn't
    provide a signal for when the current index changes.
    """

    def __init__(self, editor):
        super().__init__()
        self._editor = editor

    def event(self, event):
        if event.type() == QtCore.QEvent.Type.ToolTip:
            index = self.indexAt(event.pos())
            if index and index.isValid():
                QtGui.QToolTip.showText(event.globalPos(), index.data(), self)
            else:
                QtGui.QToolTip.hideText()
                event.ignore()

            return True

        return super().event(event)

    def keyPressEvent(self, keyevent):
        key = keyevent.key()
        if key == QtCore.Qt.Key.Key_Return or key == QtCore.Qt.Key.Key_Enter:
            self._editor._on_dclick(self.selectedIndexes()[0])
            keyevent.accept()
        QtGui.QTreeView.keyPressEvent(self, keyevent)

    def currentChanged(self, current, previous):
        """Reimplemented to tell the editor when the current index has changed."""
        super().currentChanged(current, previous)
        self._editor.update_object(current)
