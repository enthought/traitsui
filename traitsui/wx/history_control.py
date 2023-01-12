# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Defines the a text entry field (actually a combo-box) with a drop-down list
    of values previously entered into the control.
"""


import wx

from traits.api import HasPrivateTraits, Instance, Str, List, Int, Bool

from pyface.timer.api import do_later

from .constants import OKColor, ErrorColor

# -------------------------------------------------------------------------
#  'HistoryControl' class:
# -------------------------------------------------------------------------


class HistoryControl(HasPrivateTraits):

    #: The UI control:
    control = Instance(wx.Window)

    #: The current value of the control:
    value = Str()

    #: Should 'value' be updated on every keystroke?
    auto_set = Bool(False)

    #: The current history of the control:
    history = List(Str)

    #: The maximum number of history entries allowed:
    entries = Int(10)

    #: Is the current value valid?
    error = Bool(False)

    # -- Public Methods -------------------------------------------------------

    def create_control(self, parent):
        """Creates the control."""
        self.control = control = wx.ComboBox(
            parent,
            -1,
            self.value,
            wx.Point(0, 0),
            wx.Size(-1, -1),
            self.history,
            style=wx.CB_DROPDOWN,
        )
        parent.Bind(wx.EVT_COMBOBOX, self._update_value, id=control.GetId())
        control.Bind(wx.EVT_KILL_FOCUS, self._kill_focus)
        parent.Bind(
            wx.EVT_TEXT_ENTER, self._update_text_value, id=control.GetId()
        )
        if self.auto_set:
            parent.Bind(
                wx.EVT_TEXT, self._update_value_only, id=control.GetId()
            )

        return control

    def dispose(self):
        """Disposes of the control at the end of its life cycle."""
        control, self.control = self.control, None
        parent = control.GetParent()
        parent.Bind(wx.EVT_COMBOBOX, None, id=control.GetId())
        parent.Bind(wx.EVT_TEXT_ENTER, None, id=control.GetId())
        control.Unbind(wx.EVT_KILL_FOCUS)

    def set_value(self, value):
        """Sets the specified value and adds it to the history."""
        self._update(value)

    # -- Traits Event Handlers ------------------------------------------------

    def _value_changed(self, value):
        """Handles the 'value' trait being changed."""
        if not self._no_update:
            control = self.control
            if control is not None:
                control.SetValue(value)
                self._restore = False

    def _history_changed(self):
        """Handles the 'history' being changed."""
        if not self._no_update:
            if self._first_time is None:
                self._first_time = False
                if (self.value == "") and (len(self.history) > 0):
                    self.value = self.history[0]

            self._load_history(select=False)

    def _error_changed(self, error):
        """Handles the 'error' trait being changed."""
        if error:
            self.control.SetBackgroundColour(ErrorColor)
        else:
            self.control.SetBackgroundColour(OKColor)

        self.control.Refresh()

    # -- Wx Event Handlers ----------------------------------------------------

    def _update_value(self, event):
        """Handles the user selecting something from the drop-down list of the
        combobox.
        """
        self._update(event.GetString())

    def _update_value_only(self, event):
        """Handles the user typing into the text field in 'auto_set' mode."""
        self._no_update = True
        self.value = event.GetString()
        self._no_update = False

    def _update_text_value(self, event, select=True):
        """Handles the user typing something into the text field of the
        combobox.
        """
        if not self._no_update:
            self._update(self.control.GetValue(), select)

    def _kill_focus(self, event):
        """Handles the combobox losing focus."""
        self._update_text_value(event, False)
        event.Skip()

    # -- Private Methods ------------------------------------------------------

    def _update(self, value, select=True):
        """Updates the value and history list based on a specified value."""
        self._no_update = True

        if value.strip() != "":
            history = self.history
            if (len(history) == 0) or (value != history[0]):
                if value in history:
                    history.remove(value)
                history.insert(0, value)
                del history[self.entries :]
                self._load_history(value, select)

        self.value = value

        self._no_update = False

    def _load_history(self, restore=None, select=True):
        """Loads the current history list into the control."""
        control = self.control
        control.Freeze()

        if restore is None:
            restore = control.GetValue()

        control.Clear()
        for value in self.history:
            control.Append(value)

        self._restore = True
        do_later(self._thaw_value, restore, select)

    def _thaw_value(self, restore, select):
        """Restores the value of the combobox control."""
        control = self.control
        if control is not None:
            if self._restore:
                control.SetValue(restore)

                if select:
                    control.SetTextSelection(0, len(restore))

            control.Thaw()
