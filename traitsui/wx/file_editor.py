# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Defines file editors for the wxPython user interface toolkit.
"""

from os.path import abspath, split, splitext, isfile, exists

import wx

from pyface.api import FileDialog, OK
from traits.api import List, Str, Event, Any, observe, TraitError

from .text_editor import SimpleEditor as SimpleTextEditor

from .helper import TraitsUIPanel, PopupControl

# -------------------------------------------------------------------------
#  Trait definitions:
# -------------------------------------------------------------------------

# Wildcard filter:
filter_trait = List(Str)

# -------------------------------------------------------------------------
#  'SimpleEditor' class:
# -------------------------------------------------------------------------


class SimpleEditor(SimpleTextEditor):
    """Simple style of file editor, consisting of a text field and a **Browse**
    button that opens a file-selection dialog box. The user can also drag
    and drop a file onto this control.
    """

    #: The history control (used if the factory 'entries' > 0):
    history = Any()

    #: The popup file control (an Instance( PopupFile )):
    popup = Any()

    #: Wildcard filter to apply to the file dialog:
    filter = filter_trait

    def init(self, parent):
        """Finishes initializing the editor by creating the underlying toolkit
        widget.
        """
        self.control = panel = TraitsUIPanel(parent, -1)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        factory = self.factory

        if factory.entries > 0:
            from .history_control import HistoryControl

            self.history = HistoryControl(
                entries=factory.entries, auto_set=factory.auto_set
            )
            control = self.history.create_control(panel)
            pad = 3
            button = wx.Button(panel, -1, "...", size=wx.Size(28, -1))
        else:
            if factory.enter_set:
                control = wx.TextCtrl(panel, -1, "", style=wx.TE_PROCESS_ENTER)
                panel.Bind(
                    wx.EVT_TEXT_ENTER, self.update_object, id=control.GetId()
                )
            else:
                control = wx.TextCtrl(panel, -1, "")

            control.Bind(wx.EVT_KILL_FOCUS, self.update_object)

            if factory.auto_set:
                panel.Bind(wx.EVT_TEXT, self.update_object, id=control.GetId())

            bmp = wx.ArtProvider.GetBitmap(wx.ART_FOLDER_OPEN, size=(15, 15))
            button = wx.BitmapButton(panel, -1, bitmap=bmp)

            pad = 8

        self._file_name = control
        sizer.Add(control, 1, wx.EXPAND)
        sizer.Add(button, 0, wx.LEFT | wx.ALIGN_CENTER, pad)
        panel.Bind(wx.EVT_BUTTON, self.show_file_dialog, id=button.GetId())
        panel.SetDropTarget(FileDropTarget(self))
        panel.SetSizerAndFit(sizer)
        self._button = button

        self.set_tooltip(control)

        self.filter = factory.filter
        self.sync_value(factory.filter_name, "filter", "from", is_list=True)

    def dispose(self):
        """Disposes of the contents of an editor."""
        panel = self.control
        panel.Unbind(wx.EVT_BUTTON, id=self._button.GetId())
        self._button = None

        if self.history is not None:
            self.history.dispose()
            self.history = None
        else:
            control, self._file_name = self._file_name, None
            control.Unbind(wx.EVT_KILL_FOCUS)
            panel.Unbind(wx.EVT_TEXT_ENTER, id=control.GetId())
            panel.Unbind(wx.EVT_TEXT, id=control.GetId())

        super().dispose()

    @observe("history:value")
    def _history_value_changed(self, event):
        """Handles the history 'value' trait being changed."""
        value = event.new
        if not self._no_update:
            self._update(value)

    def update_object(self, event):
        """Handles the user changing the contents of the edit control."""
        if isinstance(event, wx.FocusEvent):
            event.Skip()
        self._update(self._file_name.GetValue())

    def update_editor(self):
        """Updates the editor when the object trait changes externally to the
        editor.
        """
        if self.history is not None:
            self._no_update = True
            self.history.value = self.str_value
            self._no_update = False
        else:
            self._file_name.SetValue(self.str_value)

    def show_file_dialog(self, event=None):
        """Displays the pop-up file dialog."""
        if self.history is not None:
            self.popup = self._create_file_popup()
        else:
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

    # -- Traits Event Handlers ------------------------------------------------

    @observe("popup:value")
    def _popup_value_changed(self, event):
        """Handles the popup value being changed."""
        file_name = event.new
        if self.factory.truncate_ext:
            file_name = splitext(file_name)[0]

        self.value = file_name
        self._no_update = True
        self.history.set_value(self.str_value)
        self._no_update = False

    @observe("popup:closed")
    def _popup_closed_changed(self, event):
        """Handles the popup control being closed."""
        self.popup = None

    # -- UI preference save/restore interface ---------------------------------

    def restore_prefs(self, prefs):
        """Restores any saved user preference information associated with the
        editor.
        """
        if self.history is not None:
            self.history.history = prefs.get("history", [])[
                : self.factory.entries
            ]

    def save_prefs(self):
        """Returns any user preference information associated with the editor."""
        if self.history is not None:
            return {"history": self.history.history[:]}

        return None

    # -- Private Methods ------------------------------------------------------

    def _create_file_dialog(self):
        """Creates the correct type of file dialog."""
        if len(self.factory.filter) > 0:
            wildcard = "|".join(self.factory.filter)
        else:
            wildcard = "All Files (*.*)|*.*"

        dlg = FileDialog(
            parent=self.get_control_widget(),
            default_path=self._file_name.GetValue(),
            action="save as" if self.factory.dialog_style == "save" else "open",
            wildcard=wildcard,
        )
        return dlg

    def _create_file_popup(self):
        """Creates the correct type of file popup."""
        return PopupFile(
            control=self.control,
            file_name=self.str_value,
            filter=self.factory.filter,
            height=300,
        )

    def _update(self, file_name):
        """Updates the editor value with a specified file name."""
        try:
            if self.factory.truncate_ext:
                file_name = splitext(file_name)[0]

            self.value = file_name
        except TraitError as excp:
            pass

    def _get_value(self):
        """Returns the current file name from the edit control."""
        if self.history is not None:
            return self.history.value

        return self._file_name.GetValue()


class CustomEditor(SimpleTextEditor):
    """Custom style of file editor, consisting of a file system tree view."""

    #: Is the file editor scrollable? This value overrides the default.
    scrollable = True

    #: Wildcard filter to apply to the file dialog:
    filter = filter_trait

    #: Event fired when the file system view should be rebuilt:
    reload = Event()

    #: Event fired when the user double-clicks a file:
    dclick = Event()

    def init(self, parent):
        """Finishes initializing the editor by creating the underlying toolkit
        widget.
        """
        style = self.get_style()
        factory = self.factory
        if (len(factory.filter) > 0) or (factory.filter_name != ""):
            style |= wx.DIRCTRL_SHOW_FILTERS

        self.control = wx.GenericDirCtrl(parent, style=style)
        self._tree = tree = self.control.GetTreeCtrl()
        id = tree.GetId()
        tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.update_object, id=id)
        tree.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self._on_dclick, id=id)
        tree.Bind(wx.EVT_TREE_ITEM_GETTOOLTIP, self._on_tooltip, id=id)

        self.filter = factory.filter
        self.sync_value(factory.filter_name, "filter", "from", is_list=True)
        self.sync_value(factory.reload_name, "reload", "from")
        self.sync_value(factory.dclick_name, "dclick", "to")

        self.set_tooltip()

    def dispose(self):
        """Disposes of the contents of an editor."""
        tree, self._tree = self._tree, None

        tree.Unbind(wx.EVT_TREE_SEL_CHANGED)
        tree.Unbind(wx.EVT_TREE_ITEM_ACTIVATED)

        super().dispose()

    def update_object(self, event):
        """Handles the user changing the contents of the edit control."""
        if self.control is not None:
            path = self.control.GetPath()
            if self.factory.allow_dir or isfile(path):
                if self.factory.truncate_ext:
                    path = splitext(path)[0]

                self.value = path

    def update_editor(self):
        """Updates the editor when the object trait changes externally to the
        editor.
        """
        if exists(self.str_value):
            self.control.SetPath(self.str_value)

    def get_style(self):
        """Returns the basic style to use for the control."""
        return wx.DIRCTRL_EDIT_LABELS

    def get_error_control(self):
        """Returns the editor's control for indicating error status."""
        return self._tree

    def _filter_changed(self):
        """Handles the 'filter' trait being changed."""
        self.control.SetFilter("|".join(self.filter[:]))

    def _on_dclick(self, event):
        """Handles the user double-clicking on a file name."""
        self.dclick = self.control.GetPath()

    def _on_tooltip(self, event):
        """Handles the user hovering on a file name for a tooltip."""
        text = self._tree.GetItemText(event.GetItem())
        event.SetToolTip(text)

    def _reload_changed(self):
        """Handles the 'reload' trait being changed."""
        self.control.ReCreateTree()


class PopupFile(PopupControl):

    #: The initially specified file name:
    file_name = Str()

    #: The file name filter to support:
    filter = filter_trait

    #: Override of PopupControl trait to make the popup resizable:
    resizable = True

    # -- PopupControl Method Overrides ----------------------------------------

    def create_control(self, parent):
        """Creates the file control and gets it ready for use."""
        style = self.get_style()
        if len(self.filter) > 0:
            style |= wx.DIRCTRL_SHOW_FILTERS

        self._files = files = wx.GenericDirCtrl(
            parent, style=style, filter="|".join(self.filter)
        )
        files.SetPath(self.file_name)
        self._tree = tree = files.GetTreeCtrl()
        tree.Bind(wx.EVT_TREE_SEL_CHANGED, self._select_file, id=tree.GetId())

    def dispose(self):
        self._tree.Unbind(wx.EVT_TREE_SEL_CHANGED)
        self._tree = self._files = None

    def get_style(self):
        """Returns the base style for this type of popup."""
        return wx.DIRCTRL_EDIT_LABELS

    def is_valid(self, path):
        """Returns whether or not the path is valid."""
        return isfile(path)

    # -- Private Methods ------------------------------------------------------

    def _select_file(self, event):
        """Handles a file being selected in the file control."""
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
        if (
            (path != abspath(self.file_name))
            and (path[-1:] not in ("/\\"))
            and self.is_valid(path)
        ):
            self.value = path


class FileDropTarget(wx.FileDropTarget):
    """A target for a drag and drop operation, which accepts a file."""

    def __init__(self, editor):
        wx.FileDropTarget.__init__(self)
        self.editor = editor

    def OnDropFiles(self, x, y, file_names):
        self.editor.value = file_names[-1]
        self.editor.update_editor()

        return True
