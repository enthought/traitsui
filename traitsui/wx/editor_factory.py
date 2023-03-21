# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Defines the base wxPython EditorFactory class and classes the various
    styles of editors used in a Traits-based user interface.
"""


import warnings

import wx

from traits.api import TraitError, Any, Bool, Event, Str

from .editor import Editor

from .constants import WindowColor


class SimpleEditor(Editor):
    """Base class for simple style editors, which displays a text field
    containing the text representation of the object trait value. Clicking
    in the text field displays an editor-specific dialog box for changing
    the value.
    """

    #: Has the left mouse button been pressed:
    left_down = Bool(False)

    def init(self, parent):
        """Finishes initializing the editor by creating the underlying toolkit
        widget.
        """
        self.control = self.create_control(parent)
        self.control.Bind(wx.EVT_LEFT_DOWN, self._enable_popup_editor)
        self.control.Bind(wx.EVT_LEFT_UP, self._show_popup_editor)
        self.set_tooltip()

    def create_control(self, parent):
        """Creates the control to use for the simple editor."""
        return wx.TextCtrl(parent, -1, self.str_value, style=wx.TE_READONLY)

    # -------------------------------------------------------------------------
    #  Invokes the pop-up editor for an object trait:
    #
    #  (Normally overridden in a subclass)
    # -------------------------------------------------------------------------

    def popup_editor(self, event):
        """Invokes the pop-up editor for an object trait."""
        pass

    def _enable_popup_editor(self, event):
        """Mark the left mouse button as being pressed currently."""
        self.left_down = True

    def _show_popup_editor(self, event):
        """Display the popup editor if the left mouse button was pressed
        previously.
        """
        if self.left_down:
            self.left_down = False
            self.popup_editor(event)


class TextEditor(Editor):
    """Base class for text style editors, which displays an editable text
    field, containing a text representation of the object trait value.
    """

    def init(self, parent):
        """Finishes initializing the editor by creating the underlying toolkit
        widget.
        """
        self.control = wx.TextCtrl(
            parent, -1, self.str_value, style=wx.TE_PROCESS_ENTER
        )
        self.control.Bind(wx.EVT_KILL_FOCUS, self.update_object)
        parent.Bind(
            wx.EVT_TEXT_ENTER, self.update_object, id=self.control.GetId()
        )
        self.set_tooltip()

    def dispose(self):
        """Disposes of the contents of an editor."""
        if self.control is not None:  # just in-case
            parent = self.control.GetParent()
            parent.Unbind(
                wx.EVT_TEXT_ENTER,
                handler=self.update_object,
                id=self.control.GetId(),
            )
            self.control.Unbind(wx.EVT_KILL_FOCUS, handler=self.update_object)
        super().dispose()

    def update_object(self, event):
        """Handles the user changing the contents of the edit control."""
        if isinstance(event, wx.FocusEvent):
            event.Skip()
        try:
            self.value = self.control.GetValue()
        except TraitError as excp:
            pass


class ReadonlyEditor(Editor):
    """Base class for read-only style editors, which displays a read-only text
    field, containing a text representation of the object trait value.
    """

    # -------------------------------------------------------------------------
    #  Trait definitions:
    # -------------------------------------------------------------------------

    # layout_style = 0  # Style for imbedding control in a sizer (override)

    def init(self, parent):
        """Finishes initializing the editor by creating the underlying toolkit
        widget.
        """
        if (self.item.resizable is True) or (self.item.height != -1.0):
            self.control = wx.TextCtrl(
                parent,
                -1,
                self.str_value,
                style=wx.NO_BORDER | wx.TE_MULTILINE | wx.TE_READONLY,
            )
            self.control.SetBackgroundColour(WindowColor)
        else:
            self.control = wx.StaticText(
                parent, -1, self.str_value, style=wx.ALIGN_LEFT
            )
            self.layout_style = 0

        self.set_tooltip()

    def update_editor(self):
        """Updates the editor when the object trait changes externally to the
        editor.
        """
        new_value = self.str_value
        if (self.item.resizable is True) or (self.item.height != -1.0):
            if self.control.GetValue() != new_value:
                self.control.SetValue(new_value)
        elif self.control.GetLabel() != new_value:
            self.control.SetLabel(new_value)
