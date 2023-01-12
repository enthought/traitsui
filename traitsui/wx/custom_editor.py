# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Defines the wxPython implementation of the editor used to wrap a non-Traits
based custom control.
"""


import wx

from .editor import Editor

# -------------------------------------------------------------------------
#  'CustomEditor' class:
# -------------------------------------------------------------------------


class CustomEditor(Editor):
    """Wrapper for a custom editor control"""

    def init(self, parent):
        """Finishes initializing the editor by creating the underlying toolkit
        widget.
        """
        factory = self.factory.factory
        if factory is not None:
            self.control = factory(*((parent, self) + self.factory.args))
        if self.control is None:
            self.control = control = wx.StaticText(
                parent,
                -1,
                "An error occurred creating a custom editor.\n"
                "Please contact the developer.",
            )
            control.SetBackgroundColour(wx.RED)
            control.SetForegroundColour(wx.WHITE)
        self.set_tooltip()

    def update_editor(self):
        """Updates the editor when the object trait changes externally to the
        editor.
        """
        pass
