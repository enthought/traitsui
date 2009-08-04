#------------------------------------------------------------------------------
# Copyright (c) 2007, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD license.
# However, when used with the GPL version of PyQt the additional terms described in the PyQt GPL exception also apply

#
# Author: Riverbank Computing Limited
#------------------------------------------------------------------------------

""" Defines file editors for the PyQt user interface toolkit.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from os.path \
    import splitext, isfile, exists

from PyQt4 import QtCore, QtGui

from enthought.traits.api \
    import List, Event, Unicode, TraitError
    
# FIXME: ToolkitEditorFactory is a proxy class defined here just for backward
# compatibility. The class has been moved to the 
# enthought.traits.ui.editors.file_editor file.
from enthought.traits.ui.editors.file_editor \
    import ToolkitEditorFactory

from text_editor \
    import SimpleEditor as SimpleTextEditor

#-------------------------------------------------------------------------------
#  Trait definitions:
#-------------------------------------------------------------------------------

# Wildcard filter:
filter_trait = List(Unicode)

#-------------------------------------------------------------------------------
#  'SimpleEditor' class:
#-------------------------------------------------------------------------------

class SimpleEditor ( SimpleTextEditor ):
    """ Simple style of file editor, consisting of a text field and a **Browse**
        button that opens a file-selection dialog box. The user can also drag 
        and drop a file onto this control.
    """

    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.control = QtGui.QWidget()
        layout = QtGui.QHBoxLayout(self.control)
        layout.setMargin(0)

        self._file_name = control = QtGui.QLineEdit()
        layout.addWidget(control)

        if self.factory.auto_set:
            signal = QtCore.SIGNAL('textEdited(QString)')
        else:
            # Assume enter_set is set, or else the value will never get updated.
            signal = QtCore.SIGNAL('editingFinished()')
        QtCore.QObject.connect(control, signal, self.update_object)

        button = QtGui.QPushButton("Browse...")
        layout.addWidget(button)

        QtCore.QObject.connect(button, QtCore.SIGNAL('clicked()'), 
                               self.show_file_dialog)

        self.set_tooltip(control)

    #---------------------------------------------------------------------------
    #  Handles the user changing the contents of the edit control:
    #---------------------------------------------------------------------------

    def update_object(self):
        """ Handles the user changing the contents of the edit control.
        """
        self._update(unicode(self._file_name.text()))

    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------

    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the 
            editor.
        """
        self._file_name.setText(self.str_value)

    #---------------------------------------------------------------------------
    #  Displays the pop-up file dialog:
    #---------------------------------------------------------------------------

    def show_file_dialog(self):
        """ Displays the pop-up file dialog.
        """
        # We don't used the canned functions because we don't know how the
        # file name is to be used (ie. an existing one to be opened or a new
        # one to be created).
        dlg = self._create_file_dialog()

        if dlg.exec_() == QtGui.QDialog.Accepted:
            files = dlg.selectedFiles()

            if len(files) > 0:
                file_name = unicode(files[0])

                if self.factory.truncate_ext:
                    file_name = splitext(file_name)[0]

                self.value = file_name
                self.update_editor()

    #---------------------------------------------------------------------------
    #  Returns the editor's control for indicating error status:
    #---------------------------------------------------------------------------

    def get_error_control ( self ):
        """ Returns the editor's control for indicating error status.
        """
        return self._file_name

    #-- Private Methods --------------------------------------------------------

    def _create_file_dialog ( self ):
        """ Creates the correct type of file dialog.
        """
        dlg = QtGui.QFileDialog(self.control.parentWidget())
        dlg.selectFile(self._file_name.text())

        if len(self.factory.filter) > 0:
            dlg.setFilters(self.factory.filter)

        return dlg

    def _update ( self, file_name ):
        """ Updates the editor value with a specified file name.
        """
        try:
            if self.factory.truncate_ext:
                file_name = splitext( file_name )[0]

            self.value = file_name
        except TraitError, excp:
            pass

#-------------------------------------------------------------------------------
#  'CustomEditor' class:
#-------------------------------------------------------------------------------

class CustomEditor ( SimpleTextEditor ):
    """ Custom style of file editor, consisting of a file system tree view.
    """

    # Is the file editor scrollable? This value overrides the default.
    scrollable = True

    # Wildcard filter to apply to the file dialog:
    filter = filter_trait

    # Event fired when the file system view should be rebuilt:
    reload = Event

    # Event fired when the user double-clicks a file:
    dclick = Event

    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.control = _TreeView(self)

        self._model = model = QtGui.QDirModel()
        self.control.setModel(model)

        # Don't apply filters to directories and don't show "." and ".."
        model.setFilter(QtCore.QDir.AllDirs | QtCore.QDir.Files |
                        QtCore.QDir.Drives | QtCore.QDir.NoDotAndDotDot)

        # Show directories before files
        model.setSorting(QtCore.QDir.Name | QtCore.QDir.DirsFirst)

        # Hide the labels at the top and only show the column for the file name
        self.control.header().hide()
        for column in xrange(1, model.columnCount()):
            self.control.hideColumn(column)

        factory = self.factory
        self.filter = factory.filter
        self.sync_value(factory.filter_name, 'filter', 'from', is_list=True)
        self.sync_value(factory.reload_name, 'reload', 'from')
        self.sync_value(factory.dclick_name, 'dclick', 'to')

        self.set_tooltip()

    #---------------------------------------------------------------------------
    #  Handles the user changing the contents of the edit control:
    #---------------------------------------------------------------------------

    def update_object(self, idx):
        """ Handles the user changing the contents of the edit control.
        """
        if self.control is not None:
            path = unicode(self._model.filePath(idx))

            if self.factory.allow_dir or isfile(path):
                if self.factory.truncate_ext:
                    path = splitext( path )[0]

                self.value = path

    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------

    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the 
            editor.
        """
        if exists(self.str_value):
            index = self._model.index(self.str_value)
            self.control.expand(index)
            self.control.setCurrentIndex(index)

    #---------------------------------------------------------------------------
    #  Handles the 'filter' trait being changed:
    #---------------------------------------------------------------------------

    def _filter_changed ( self ):
        """ Handles the 'filter' trait being changed.
        """
        self._model.setNameFilters(self.filter)

    #---------------------------------------------------------------------------
    #  Handles the user double-clicking on a file name:
    #---------------------------------------------------------------------------

    def _on_dclick ( self, idx ):
        """ Handles the user double-clicking on a file name.
        """
        self.dclick = True

    #---------------------------------------------------------------------------
    #  Handles the 'reload' trait being changed:
    #---------------------------------------------------------------------------

    def _reload_changed ( self ):
        """ Handles the 'reload' trait being changed.
        """
        self._model.refresh()

#-------------------------------------------------------------------------------
#  '_TreeView' class:
#-------------------------------------------------------------------------------

class _TreeView(QtGui.QTreeView):
    """ This is an internal class needed because QAbstractItemView (for some
        strange reason) doesn't provide a signal when the current index
        changes.
    """

    def __init__(self, editor):

        QtGui.QTreeView.__init__(self)

        self.connect(self, QtCore.SIGNAL('doubleClicked(QModelIndex)'),
                editor._on_dclick)

        self._editor = editor

    def currentChanged(self, curr, prev):
        """ Reimplemented to tell the editor when the current index has
            changed.
        """

        QtGui.QTreeView.currentChanged(self, curr, prev)

        self._editor.update_object(curr)
