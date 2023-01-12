# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Defines the various text editors for the wxPython user interface toolkit.
"""


import wx

from traits.api import TraitError

from traitsui.editors.text_editor import evaluate_trait

from .editor import Editor

from .editor_factory import ReadonlyEditor as BaseReadonlyEditor

from .constants import OKColor


# Readonly text editor with view state colors:
HoverColor = wx.LIGHT_GREY
DownColor = wx.WHITE


class SimpleEditor(Editor):
    """Simple style text editor, which displays a text field."""

    #: Flag for window styles:
    base_style = 0

    #: Background color when input is OK:
    ok_color = OKColor

    # -------------------------------------------------------------------------
    #  Trait definitions:
    # -------------------------------------------------------------------------

    #: Function used to evaluate textual user input:
    evaluate = evaluate_trait

    def init(self, parent):
        """Finishes initializing the editor by creating the underlying toolkit
        widget.
        """
        factory = self.factory
        style = self.base_style
        self.evaluate = factory.evaluate
        self.sync_value(factory.evaluate_name, "evaluate", "from")

        if (not factory.multi_line) or factory.password:
            style &= ~wx.TE_MULTILINE

        if factory.password:
            style |= wx.TE_PASSWORD

        multi_line = (style & wx.TE_MULTILINE) != 0
        if multi_line:
            self.scrollable = True

        if factory.enter_set and (not multi_line):
            control = wx.TextCtrl(
                parent, -1, self.str_value, style=style | wx.TE_PROCESS_ENTER
            )
            parent.Bind(
                wx.EVT_TEXT_ENTER, self.update_object, id=control.GetId()
            )
        else:
            control = wx.TextCtrl(parent, -1, self.str_value, style=style)

        control.Bind(wx.EVT_KILL_FOCUS, self.update_object)
        if control.IsSingleLine():
            control.SetHint(self.factory.placeholder)

        if factory.auto_set:
            parent.Bind(wx.EVT_TEXT, self.update_object, id=control.GetId())

        self.control = control
        self.set_error_state(False)
        self.set_tooltip()

    def update_object(self, event):
        """Handles the user entering input data in the edit control."""
        if isinstance(event, wx.FocusEvent):
            # Ensure that the base class' focus event handlers are run, some
            # built-in behavior may break on some platforms otherwise.
            event.Skip()

        if (not self._no_update) and (self.control is not None):
            try:
                self.value = self._get_user_value()

                if self._error is not None:
                    self._error = None
                    self.ui.errors -= 1

                self.set_error_state(False)

            except TraitError as excp:
                pass

    def update_editor(self):
        """Updates the editor when the object trait changes externally to the
        editor.
        """
        user_value = self._get_user_value()
        try:
            unequal = bool(user_value != self.value)
        except ValueError:
            # This might be a numpy array.
            unequal = True

        if unequal:
            self._no_update = True
            self.control.SetValue(self.str_value)
            self._no_update = False

        if self._error is not None:
            self._error = None
            self.ui.errors -= 1
            self.set_error_state(False)

    def _get_user_value(self):
        """Gets the actual value corresponding to what the user typed."""
        value = self.control.GetValue()
        try:
            value = self.evaluate(value)
        except:
            pass

        try:
            ret = self.factory.mapping.get(value, value)
        except TypeError:
            # The value is probably not hashable:
            ret = value

        return ret

    def error(self, excp):
        """Handles an error that occurs while setting the object's trait value."""
        if self._error is None:
            self._error = True
            self.ui.errors += 1

        self.set_error_state(True)

    def in_error_state(self):
        """Returns whether or not the editor is in an error state."""
        return self.invalid or self._error


class CustomEditor(SimpleEditor):
    """Custom style of text editor, which displays a multi-line text field."""

    #: Flag for window style. This value overrides the default.
    base_style = wx.TE_MULTILINE


class ReadonlyEditor(BaseReadonlyEditor):
    """Read-only style of text editor, which displays a read-only text field."""

    def init(self, parent):
        """Finishes initializing the editor by creating the underlying toolkit
        widget.
        """
        super().init(parent)

        if self.factory.view is not None:
            control = self.control
            control.Bind(wx.EVT_ENTER_WINDOW, self._enter_window)
            control.Bind(wx.EVT_LEAVE_WINDOW, self._leave_window)
            control.Bind(wx.EVT_LEFT_DOWN, self._left_down)
            control.Bind(wx.EVT_LEFT_UP, self._left_up)

    def update_editor(self):
        """Updates the editor when the object trait changes externally to the
        editor.
        """
        control = self.control
        new_value = self.str_value

        if hasattr(self.factory, "password") and self.factory.password:
            new_value = "*" * len(new_value)

        if (self.item.resizable is True) or (self.item.height != -1.0):
            if control.GetValue() != new_value:
                control.SetValue(new_value)
                control.SetInsertionPointEnd()

        elif control.GetLabel() != new_value:
            control.SetLabel(new_value)

    def dispose(self):
        """Disposes of the contents of an editor."""
        if self.factory.view is not None:
            control = self.control
            control.Unbind(wx.EVT_ENTER_WINDOW)
            control.Unbind(wx.EVT_LEAVE_WINDOW)
            control.Unbind(wx.EVT_LEFT_DOWN)
            control.Unbind(wx.EVT_LEFT_UP)

        super().dispose()

    # -- Private Methods ------------------------------------------------------

    def _set_color(self):
        control = self.control
        if not self._in_window:
            color = control.GetParent().GetBackgroundColour()
        elif self._down:
            color = DownColor
        else:
            color = HoverColor

        control.SetBackgroundColour(color)
        control.Refresh()

    # -- wxPython Event Handlers ----------------------------------------------

    def _enter_window(self, event):
        self._in_window = True
        self._set_color()

    def _leave_window(self, event):
        self._in_window = False
        self._set_color()

    def _left_down(self, event):
        self.control.CaptureMouse()
        self._down = True
        self._set_color()

    def _left_up(self, event):
        self._set_color()
        if not self._down:
            return

        self.control.ReleaseMouse()
        self._down = False

        if self._in_window:
            self.object.edit_traits(
                view=self.factory.view, parent=self.control
            )


TextEditor = SimpleEditor
