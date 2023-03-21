# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import wx

from traits.api import Instance, Int, Str
from traitsui.wx.editor import Editor
from pyface.ui.wx.progress_dialog import ProgressDialog


class _ProgressDialog(ProgressDialog):
    def close(self):
        """Overwritten to disable closing."""
        pass


class SimpleEditor(Editor):
    """
    Show a progress bar with all the optional goodies

    """

    progress = Instance(ProgressDialog)

    # The message to be displayed along side the progress guage
    message = Str()

    # The starting value
    min = Int()

    # The ending value
    max = Int()

    # -- Editor interface ------------------------------------------------------

    def init(self, parent):
        """Finishes initializing the editor by creating the underlying toolkit
        widget.
        """
        self.control = self.create_control(parent)
        factory = self.factory
        self.min = factory.min
        self.max = factory.max
        self.message = factory.message
        self.sync_value(factory.min_name, "min", "from")
        self.sync_value(factory.max_name, "max", "from")
        self.sync_value(factory.message_name, "message", "from")
        self.set_tooltip()

    def create_control(self, parent):
        """
        Finishes initializing the editor by creating the underlying widget.
        """

        self.progress = ProgressDialog(
            title=self.factory.title,
            message=self.factory.message,
            min=self.factory.min,
            max=self.factory.max,
            can_cancel=self.factory.can_cancel,
            show_time=self.factory.show_time,
            show_percent=self.factory.show_percent,
        )

        panel = wx.Panel(parent, -1)

        sizer = wx.BoxSizer(wx.VERTICAL)
        panel.SetSizer(sizer)
        panel.SetAutoLayout(True)
        panel.SetBackgroundColour(wx.NullColour)

        self.progress.dialog_size = wx.Size()

        # The 'guts' of the dialog.
        self.progress._create_message(panel, sizer)
        self.progress._create_gauge(panel, sizer)
        self.progress._create_percent(panel, sizer)
        self.progress._create_timer(panel, sizer)
        self.progress._create_buttons(panel, sizer)

        panel.SetClientSize(self.progress.dialog_size)

        panel.CentreOnParent()

        self.control = panel
        return self.control

    def update_editor(self):
        """
        Updates the editor when the object trait changes externally to the
        editor.
        """
        self.progress.min = self.min
        self.progress.max = self.max
        self.progress.change_message(self.message)
        self.progress.update(self.value)

    def _min_changed(self):
        self.update_editor()

    def _max_changed(self):
        self.update_editor()

    def _message_changed(self):
        self.update_editor()
