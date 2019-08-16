#------------------------------------------------------------------------------
#
#  Copyright (c) 2005, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
#  Author: David C. Morrill
#  Date:   10/21/2004
#
#------------------------------------------------------------------------------

""" Defines file editors for the wxPython user interface toolkit.
"""

#-------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------

from __future__ import absolute_import
import wx

from os.path \
    import abspath, split, splitext, isfile, exists

from traits.api \
    import List, Str, Event, Any, on_trait_change, TraitError

# FIXME: ToolkitEditorFactory is a proxy class defined here just for backward
# compatibility. The class has been moved to the
# traitsui.editors.file_editor file.
from traitsui.editors.file_editor \
    import ToolkitEditorFactory

from .text_editor \
    import SimpleEditor as SimpleTextEditor

from .helper \
    import TraitsUIPanel, PopupControl

#-------------------------------------------------------------------------
#  Trait definitions:
#-------------------------------------------------------------------------

# Wildcard filter:
filter_trait = List(Str)

#-------------------------------------------------------------------------
#  'SimpleEditor' class:
#-------------------------------------------------------------------------


class SimpleEditor(SimpleTextEditor):
    """ Simple style of file editor, consisting of a text field and a **Browse**
        button that opens a file-selection dialog box. The user can also drag
        and drop a file onto this control.
    """

    # The history control (used if the factory 'entries' > 0):
    history = Any

    # The popup file control (an Instance( PopupFile )):
    popup = Any

    #-------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #-------------------------------------------------------------------------

    def init(self, parent):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.control = panel = TraitsUIPanel(parent, -1)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        factory = self.factory

        if factory.entries > 0:
            from .history_control import HistoryControl

            self.history = HistoryControl(entries=factory.entries,
                                          auto_set=factory.auto_set)
            control = self.history.create_control(panel)
            pad = 3
            button = wx.Button(panel, -1, '...',
                               size=wx.Size(28, -1))
        else:
            if factory.enter_set:
                control = wx.TextCtrl(panel, -1, '',
                                      style=wx.TE_PROCESS_ENTER)
                wx.EVT_TEXT_ENTER(panel, control.GetId(), self.update_object)
            else:
                control = wx.TextCtrl(panel, -1, '')

            wx.EVT_KILL_FOCUS(control, self.update_object)

            if factory.auto_set:
                wx.EVT_TEXT(panel, control.GetId(), self.update_object)

            bmp = wx.ArtProvider.GetBitmap(wx.ART_FOLDER_OPEN,
                                           size=(15, 15))
            button = wx.BitmapButton(panel, -1, bitmap=bmp)

            pad = 8

        self._file_name = control
        sizer.Add(control, 1, wx.EXPAND | wx.ALIGN_CENTER)
        sizer.Add(button, 0, wx.LEFT | wx.ALIGN_CENTER, pad)
        wx.EVT_BUTTON(panel, button.GetId(), self.show_file_dialog)
        panel.SetDropTarget(FileDropTarget(self))
        panel.SetSizerAndFit(sizer)
        self._button = button

        self.set_tooltip(control)

    def dispose(self):
        """ Disposes of the contents of an editor.
        """
        panel = self.control
        panel.Bind(wx.EVT_BUTTON, None, id=self._button.GetId())
        self._button = None

        if self.history is not None:
            self.history.dispose()
            self.history = None
        else:
            factory = self.factory
            control, self._file_name = self._file_name, None
            control.Bind(wx.EVT_KILL_FOCUS, None)
            panel.Bind(wx.EVT_TEXT_ENTER, None, id=control.GetId())
            panel.Bind(wx.EVT_TEXT, None, id=control.GetId())

        super(SimpleEditor, self).dispose()

    #-------------------------------------------------------------------------
    #  Handles the history 'value' trait being changed:
    #-------------------------------------------------------------------------

    @on_trait_change('history:value')
    def _history_value_changed(self, value):
        """ Handles the history 'value' trait being changed.
        """
        if not self._no_update:
            self._update(value)

    #-------------------------------------------------------------------------
    #  Handles the user changing the contents of the edit control:
    #-------------------------------------------------------------------------

    def update_object(self, event):
        """ Handles the user changing the contents of the edit control.
        """
        if isinstance(event, wx.FocusEvent):
            event.Skip()
        self._update(self._file_name.GetValue())

    #-------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #-------------------------------------------------------------------------

    def update_editor(self):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        if self.history is not None:
            self._no_update = True
            self.history.value = self.str_value
            self._no_update = False
        else:
            self._file_name.SetValue(self.str_value)

    #-------------------------------------------------------------------------
    #  Displays the pop-up file dialog:
    #-------------------------------------------------------------------------

    def show_file_dialog(self, event):
        """ Displays the pop-up file dialog.
        """
        if self.history is not None:
            self.popup = self._create_file_popup()
        else:
            dlg = self._create_file_dialog()
            rc = (dlg.ShowModal() == wx.ID_OK)
            file_name = abspath(dlg.GetPath())
            dlg.Destroy()
            if rc:
                if self.factory.truncate_ext:
                    file_name = splitext(file_name)[0]

                self.value = file_name
                self.update_editor()

    #-------------------------------------------------------------------------
    #  Returns the editor's control for indicating error status:
    #-------------------------------------------------------------------------

    def get_error_control(self):
        """ Returns the editor's control for indicating error status.
        """
        return self._file_name

    #-- Traits Event Handlers ------------------------------------------------

    @on_trait_change('popup:value')
    def _popup_value_changed(self, file_name):
        """ Handles the popup value being changed.
        """
        if self.factory.truncate_ext:
            file_name = splitext(file_name)[0]

        self.value = file_name
        self._no_update = True
        self.history.set_value(self.str_value)
        self._no_update = False

    @on_trait_change('popup:closed')
    def _popup_closed_changed(self):
        """ Handles the popup control being closed.
        """
        self.popup = None

    #-- UI preference save/restore interface ---------------------------------

    def restore_prefs(self, prefs):
        """ Restores any saved user preference information associated with the
            editor.
        """
        if self.history is not None:
            self.history.history = \
                prefs.get('history', [])[: self.factory.entries]

    def save_prefs(self):
        """ Returns any user preference information associated with the editor.
        """
        if self.history is not None:
            return {'history': self.history.history[:]}

        return None

    #-- Private Methods ------------------------------------------------------

    def _create_file_dialog(self):
        """ Creates the correct type of file dialog.
        """
        if len(self.factory.filter) > 0:
            wildcard = '|'.join(self.factory.filter[:])
        else:
            wildcard = 'All Files (*.*)|*.*'

        if self.factory.dialog_style == 'save':
            style = wx.FD_SAVE
        elif self.factory.dialog_style == 'open':
            style = wx.FD_OPEN
        else:
            style = wx.FD_DEFAULT_STYLE

        directory, filename = split(self._get_value())

        dlg = wx.FileDialog(
            self.control,
            defaultDir=directory,
            defaultFile=filename,
            message='Select a File',
            wildcard=wildcard,
            style=style
        )

        return dlg

    def _create_file_popup(self):
        """ Creates the correct type of file popup.
        """
        return PopupFile(control=self.control,
                         file_name=self.str_value,
                         filter=self.factory.filter,
                         height=300)

    def _update(self, file_name):
        """ Updates the editor value with a specified file name.
        """
        try:
            if self.factory.truncate_ext:
                file_name = splitext(file_name)[0]

            self.value = file_name
        except TraitError as excp:
            pass

    def _get_value(self):
        """ Returns the current file name from the edit control.
        """
        if self.history is not None:
            return self.history.value

        return self._file_name.GetValue()

#-------------------------------------------------------------------------
#  'CustomEditor' class:
#-------------------------------------------------------------------------


class CustomEditor(SimpleTextEditor):
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

    #-------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #-------------------------------------------------------------------------

    def init(self, parent):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        style = self.get_style()
        factory = self.factory
        if (len(factory.filter) > 0) or (factory.filter_name != ''):
            style |= wx.DIRCTRL_SHOW_FILTERS

        self.control = wx.GenericDirCtrl(parent, style=style)
        self._tree = tree = self.control.GetTreeCtrl()
        id = tree.GetId()
        wx.EVT_TREE_SEL_CHANGED(tree, id, self.update_object)
        wx.EVT_TREE_ITEM_ACTIVATED(tree, id, self._on_dclick)
        wx.EVT_TREE_ITEM_GETTOOLTIP(tree, id, self._on_tooltip)

        self.filter = factory.filter
        self.sync_value(factory.filter_name, 'filter', 'from', is_list=True)
        self.sync_value(factory.reload_name, 'reload', 'from')
        self.sync_value(factory.dclick_name, 'dclick', 'to')

        self.set_tooltip()

    def dispose(self):
        """ Disposes of the contents of an editor.
        """
        tree, self._tree = self._tree, None
        id = tree.GetId()

        wx.EVT_TREE_SEL_CHANGED(tree, id, None)
        wx.EVT_TREE_ITEM_ACTIVATED(tree, id, None)

        super(CustomEditor, self).dispose()

    #-------------------------------------------------------------------------
    #  Handles the user changing the contents of the edit control:
    #-------------------------------------------------------------------------

    def update_object(self, event):
        """ Handles the user changing the contents of the edit control.
        """
        if self.control is not None:
            path = self.control.GetPath()
            if self.factory.allow_dir or isfile(path):
                if self.factory.truncate_ext:
                    path = splitext(path)[0]

                self.value = path

    #-------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #-------------------------------------------------------------------------

    def update_editor(self):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        if exists(self.str_value):
            self.control.SetPath(self.str_value)

    #-------------------------------------------------------------------------
    #  Returns the basic style to use for the control:
    #-------------------------------------------------------------------------

    def get_style(self):
        """ Returns the basic style to use for the control.
        """
        return wx.DIRCTRL_EDIT_LABELS

    #-------------------------------------------------------------------------
    #  Returns the editor's control for indicating error status:
    #-------------------------------------------------------------------------

    def get_error_control(self):
        """ Returns the editor's control for indicating error status.
        """
        return self._tree

    #-------------------------------------------------------------------------
    #  Handles the 'filter' trait being changed:
    #-------------------------------------------------------------------------

    def _filter_changed(self):
        """ Handles the 'filter' trait being changed.
        """
        self.control.SetFilter('|'.join(self.filter[:]))

    #-------------------------------------------------------------------------
    #  Handles the user double-clicking on a file name:
    #-------------------------------------------------------------------------

    def _on_dclick(self, event):
        """ Handles the user double-clicking on a file name.
        """
        self.dclick = self.control.GetPath()

    #-------------------------------------------------------------------------
    #  Handles the user hovering on a file name for a tooltip:
    #-------------------------------------------------------------------------

    def _on_tooltip(self, event):
        """ Handles the user hovering on a file name for a tooltip.
        """
        text = self._tree.GetItemText(event.GetItem())
        event.SetToolTip(text)

    #-------------------------------------------------------------------------
    #  Handles the 'reload' trait being changed:
    #-------------------------------------------------------------------------

    def _reload_changed(self):
        """ Handles the 'reload' trait being changed.
        """
        self.control.ReCreateTree()

#-------------------------------------------------------------------------
#  'PopupFile' class:
#-------------------------------------------------------------------------


class PopupFile(PopupControl):

    # The initially specified file name:
    file_name = Str

    # The file name filter to support:
    filter = filter_trait

    # Override of PopupControl trait to make the popup resizable:
    resizable = True

    #-- PopupControl Method Overrides ----------------------------------------

    def create_control(self, parent):
        """ Creates the file control and gets it ready for use.
        """
        style = self.get_style()
        if len(self.filter) > 0:
            style |= wx.DIRCTRL_SHOW_FILTERS

        self._files = files = wx.GenericDirCtrl(parent, style=style,
                                                filter='|'.join(self.filter))
        files.SetPath(self.file_name)
        self._tree = tree = files.GetTreeCtrl()
        wx.EVT_TREE_SEL_CHANGED(tree, tree.GetId(), self._select_file)

    def dispose(self):
        wx.EVT_TREE_SEL_CHANGED(self._tree, self._tree.GetId(), None)
        self._tree = self._files = None

    def get_style(self):
        """ Returns the base style for this type of popup.
        """
        return wx.DIRCTRL_EDIT_LABELS

    def is_valid(self, path):
        """ Returns whether or not the path is valid.
        """
        return isfile(path)

    #-- Private Methods ------------------------------------------------------

    def _select_file(self, event):
        """ Handles a file being selected in the file control.
        """
        path = self._files.GetPath()

        # We have to make sure the selected path is different than the original
        # path because when a filter is changed we get called with the currently
        # selected path, even though no file was actually selected by the user.
        # So we only count it if it is a different path.
        #
        # We also check the last character of the path, because under Windows
        # we get a call when the filter is changed for each drive letter. If the
        # drive is not available, it can take the 'isfile' call a long time to
        # time out, so we attempt to ignore them by doing a quick test to see
        # if it could be a valid file name, and ignore it if it is not:
        if ((path != abspath(self.file_name)) and
            (path[-1:] not in ('/\\')) and
                self.is_valid(path)):
            self.value = path

#-------------------------------------------------------------------------
#  'FileDropTarget' class:
#-------------------------------------------------------------------------


class FileDropTarget(wx.FileDropTarget):
    """ A target for a drag and drop operation, which accepts a file.
    """

    def __init__(self, editor):
        wx.FileDropTarget.__init__(self)
        self.editor = editor

    def OnDropFiles(self, x, y, file_names):
        self.editor.value = file_names[-1]
        self.editor.update_editor()

        return True

### EOF #######################################################################
