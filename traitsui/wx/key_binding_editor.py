# -------------------------------------------------------------------------
#
#  Copyright (c) 2005, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
#  Author: David C. Morrill
#  Date:   05/20/2005
#
# -------------------------------------------------------------------------

""" Defines the key binding editor for use with the KeyBinding class. This is a
    specialized editor used to associate a particular key with a control (i.e.,
    the key binding editor).
"""


import wx

from traits.api import Bool, Event

# FIXME: ToolkitEditorFactory is a proxy class defined here just for backward
# compatibility. The class has been moved to the
# traitsui.editors.key_binding_editor file.
from traitsui.editors.key_binding_editor import (
    KeyBindingEditor as ToolkitEditorFactory,
)

from pyface.wx.dialog import confirmation

from .editor import Editor

from .key_event_to_name import key_event_to_name

# -------------------------------------------------------------------------
#  'KeyBindingEditor' class:
# -------------------------------------------------------------------------


class KeyBindingEditor(Editor):
    """ An editor for modifying bindings of keys to controls.
    """

    # -------------------------------------------------------------------------
    #  Trait definitions:
    # -------------------------------------------------------------------------

    #: Does the editor's control have focus currently?
    has_focus = Bool(False)

    #: Keyboard event
    key = Event()

    #: Clear field event
    clear = Event()

    def init(self, parent):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.control = KeyBindingCtrl(self, parent, size=wx.Size(160, 19))

    def update_object(self, event):
        """ Handles the user entering input data in the edit control.
        """
        try:
            self.value = value = key_event_to_name(event)
            self._binding.text = value
        except:
            pass

    def update_editor(self):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        self.control.Refresh()

    def update_focus(self, has_focus):
        """ Updates the current focus setting of the control.
        """
        if has_focus:
            self._binding.border_size = 1
            self.object.owner.focus_owner = self._binding

    def _key_changed(self, event):
        """ Handles a keyboard event.
        """
        binding = self.object
        key_name = key_event_to_name(event)
        cur_binding = binding.owner.key_binding_for(binding, key_name)
        if cur_binding is not None:
            if (
                confirmation(
                    None,
                    "'%s' has already been assigned to '%s'.\n"
                    "Do you wish to continue?"
                    % (key_name, cur_binding.description),
                    "Duplicate Key Definition",
                )
                == 5104
            ):
                return

        self.value = key_name

    def _clear_changed(self):
        """ Handles a clear field event.
        """
        self.value = ""


class KeyBindingCtrl(wx.Window):
    """ wxPython control for editing key bindings.
    """

    def __init__(
        self,
        editor,
        parent,
        wid=-1,
        pos=wx.DefaultPosition,
        size=wx.DefaultSize,
    ):

        super(KeyBindingCtrl, self).__init__(
            parent, wid, pos, size, style=wx.CLIP_CHILDREN | wx.WANTS_CHARS
        )
        # Save the reference to the controlling editor object:
        self.editor = editor

        # Indicate we don't have the focus right now:
        editor.has_focus = False

        # Set up the 'erase background' event handler:
        self.Bind(wx.EVT_ERASE_BACKGROUND, self._on_erase_background)

        # Set up the 'paint' event handler:
        self.Bind(wx.EVT_PAINT, self._paint)

        # Set up the focus change handlers:
        self.Bind(wx.EVT_SET_FOCUS, self._get_focus)
        self.Bind(wx.EVT_KILL_FOCUS, self._lose_focus)

        # Set up mouse event handlers:
        self.Bind(wx.EVT_LEFT_DOWN, self._set_focus)
        self.Bind(wx.EVT_LEFT_DCLICK, self._clear_contents)

        # Handle key events:
        self.Bind(wx.EVT_CHAR, self._on_char)

    def _on_char(self, event):
        """ Handle keyboard keys being pressed.
        """
        self.editor.key = event

    def _on_erase_background(self, event):
        pass

    def _paint(self, event):
        """ Updates the screen.
        """
        wdc = wx.PaintDC(self)
        dx, dy = self.GetSize()
        if self.editor.has_focus:
            wdc.SetPen(wx.Pen(wx.RED, 2))
            wdc.DrawRectangle(1, 1, dx - 1, dy - 1)
        else:
            wdc.SetPen(wx.Pen(wx.BLACK))
            wdc.DrawRectangle(0, 0, dx, dy)

        wdc.SetFont(self.GetFont())
        wdc.DrawText(self.editor.str_value, 5, 3)

    def _set_focus(self, event):
        """ Sets the keyboard focus to this window.
        """
        self.SetFocus()

    def _get_focus(self, event):
        """ Handles getting the focus.
        """
        self.editor.has_focus = True
        self.Refresh()

    def _lose_focus(self, event):
        """ Handles losing the focus.
        """
        self.editor.has_focus = False
        self.Refresh()

    def _clear_contents(self, event):
        """ Handles the user double clicking the control to clear its contents.
        """
        self.editor.clear = True
