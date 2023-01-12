# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Defines the various Boolean editors for the wxPython user interface toolkit.
"""


import wx

from .editor import Editor

# This needs to be imported in here for use by the editor factory for boolean
# editors (declared in traitsui). The editor factory's text_editor
# method will use the TextEditor in the ui.
from .text_editor import SimpleEditor as TextEditor

from .constants import ReadonlyColor


class SimpleEditor(Editor):
    """Simple style of editor for Boolean values, which displays a check box."""

    def init(self, parent):
        """Finishes initializing the editor by creating the underlying toolkit
        widget.
        """
        self.control = wx.CheckBox(parent, -1, "")
        self.control.Bind(wx.EVT_CHECKBOX, self.update_object)
        self.set_tooltip()

    def dispose(self):
        self.control.Unbind(wx.EVT_CHECKBOX)

    def update_object(self, event):
        """Handles the user clicking the checkbox."""
        self.value = self.control.GetValue() != 0

    def update_editor(self):
        """Updates the editor when the object trait changes externally to the
        editor.
        """
        self.control.SetValue(self.value)


class ReadonlyEditor(Editor):
    """Read-only style of editor for Boolean values, which displays static text
    of either "True" or "False".
    """

    def init(self, parent):
        """Finishes initializing the editor by creating the underlying toolkit
        widget.
        """
        self.control = wx.TextCtrl(parent, -1, "", style=wx.TE_READONLY)
        self.control.SetBackgroundColour(ReadonlyColor)

    # -------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #
    #  (Should normally be overridden in a subclass)
    # -------------------------------------------------------------------------

    def update_editor(self):
        """Updates the editor when the object trait changes externally to the
        editor.
        """
        if self.value:
            self.control.SetValue("True")
        else:
            self.control.SetValue("False")
