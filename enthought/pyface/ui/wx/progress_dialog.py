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
#  Author: Enthought, Inc.
#
#------------------------------------------------------------------------------

""" A simple progress bar intended to run in the UI thread
"""

import wx
import time

# Enthought library imports
from enthought.traits.api import Instance, Enum, Int, Bool, Str, implements, Property

# Local imports
from widget import Widget
from enthought.pyface.i_progress_dialog import IProgressDialog, MProgressDialog
from window import Window

class ProgressBar(Widget):
    """ A simple progress bar dialog intended to run in the UI thread """

    parent = Instance(wx.Window)
    control = Instance(wx.Gauge)
    direction = Enum('horizontal', 'horizontal', 'vertical')

    def __init__(self, parent, minimum=0, maximum=100, direction='horizontal',
                 size=(200, -1)):
        """
        Constructs a progress bar which can be put into a panel, or optionaly,
        its own window

        """
        self._max = maximum
        self.parent = parent

        style = wx.GA_HORIZONTAL
        if direction == "vertical":
            style = wx.GA_VERTICAL

        self.control = wx.Gauge(parent, -1, maximum, style=style, size=size)

    def update(self, value):
        """
        Updates the progress bar to the desired value.

        """
        if self._max == 0:
            self.control.Pulse()
        else:
            self.control.SetValue(value)

        self.control.Update()

    def _show(self):
        # Show the parent
        self.parent.Show()

        # Show the toolkit-specific control in the parent
        self.control.Show()

class ProgressDialog(MProgressDialog, Window):
    """ A simple progress dialog window which allows itself to be updated """

    progress_bar = Instance(ProgressBar)
    title = Str
    message = Property()
    min = Int
    max = Int
    margin = Int(5)
    can_cancel = Bool(False)
    show_time = Bool(False)
    show_percent = Bool(False)
    _user_cancelled = Bool(False)
    _message_text = Str()

    dialog_size = Instance(wx.Size)

    # Label for the 'cancel' button
    cancel_button_label = Str('Cancel')

    def __init__(self, *args, **kw):
        if 'message' in kw:
            self._message_text = kw.pop('message')

        super(ProgressDialog, self).__init__( *args, **kw)

    def open(self):
        super(ProgressDialog, self).open()
        self._start_time = time.time()
        wx.Yield()

    def close(self):
        if self.progress_bar is not None:
            self.progress_bar.destroy()
            self.progress_bar = None

        if self._message_control is not None:
            self._message_control = None

        super(ProgressDialog, self).close()

    def change_message(self, value):
        self._message_text = value
        if self._message_control is not None:
            self._message_control.SetLabel(value)
            self._message_control.Update()
            self.control.GetSizer().Layout()

    def update(self, value):
        """
        updates the progress bar to the desired value. If the value is >=
        the maximum and the progress bar is not contained in another panel
        the parent window will be closed

        """

        if self.progress_bar is None:
            # the developer is trying to update a progress bar which is already
            # done. Allow it, but do nothing
            return (False, False)

        self.progress_bar.update(value)

        if self.max > 0:
            percent = (float(value) - self.min)/(self.max - self.min)

            if self.show_time and (percent != 0):
                current_time = time.time()
                elapsed = current_time - self._start_time
                estimated = elapsed/percent
                remaining = estimated - elapsed

                self._set_time_label(elapsed,
                                 self._elapsed_control)
                self._set_time_label(estimated,
                                 self._estimated_control)
                self._set_time_label(remaining,
                                 self._remaining_control)

            if self.show_percent:
                self._percent_control = "%3f" % ((percent * 100) % 1)

            if value >= self.max or self._user_cancelled:
                self.close()
        else:
            if self._user_cancelled:
                self.close()

        wx.Yield()

        return (not self._user_cancelled, False)

    def _on_cancel(self, event):
        self._user_cancelled = True
        self.close()

    def _on_close(self, event):
        self._user_cancelled = True
        return self.close()

    def _set_time_label(self, value, control):
        hours = value / 3600
        minutes = (value % 3600) / 60
        seconds = value % 60
        label = "%1u:%02u:%02u" % (hours, minutes, seconds)

        control.SetLabel(control.GetLabel()[:-7] + label)

    def _get_message(self):
        return self._message_text

    def _create_buttons(self, dialog, parent_sizer):
        """ Creates the buttons. """

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._cancel = None

        if self.can_cancel == True:

            # 'Cancel' button.
            self._cancel = cancel = wx.Button(dialog, wx.ID_CANCEL,
                                              self.cancel_button_label)
            wx.EVT_BUTTON(dialog, wx.ID_CANCEL, self._on_cancel)
            sizer.Add(cancel, 0, wx.LEFT, 10)

            button_size = cancel.GetSize()
            self.dialog_size.x = max(self.dialog_size.x, button_size.x + 2*self.margin)
            self.dialog_size.y += button_size.y + 2*self.margin

            parent_sizer.Add(sizer, 0, wx.ALIGN_RIGHT | wx.ALL, self.margin)
        return

    def _create_label(self, dialog, parent_sizer, text):
        local_sizer = wx.BoxSizer()
        dummy = wx.StaticText(dialog, -1, text)
        label = wx.StaticText(dialog, -1, "unknown")

        local_sizer.Add(dummy, 1, wx.ALIGN_LEFT)
        local_sizer.Add(label, 1, wx.ALIGN_LEFT | wx.ALIGN_RIGHT, self.margin)
        parent_sizer.Add(local_sizer, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, self.margin)

        return label

    def _create_gauge(self, dialog, parent_sizer):
        self.progress_bar = ProgressBar(dialog, self.min, self.max)
        parent_sizer.Add(self.progress_bar.control, 0, wx.CENTER | wx.ALL, self.margin)

        horiz_spacer = 50

        progress_bar_size = self.progress_bar.control.GetSize()
        self.dialog_size.x = max(self.dialog_size.x, progress_bar_size.x + 2*self.margin + horiz_spacer)
        self.dialog_size.y += progress_bar_size.y + 2*self.margin

        return

    def _create_message(self, dialog, parent_sizer):
        self._message_control = wx.StaticText(dialog, -1, self.message)
        parent_sizer.Add(self._message_control, 0, wx.LEFT | wx.TOP, self.margin)

        msg_control_size = self._message_control.GetSize()
        self.dialog_size.x = max(self.dialog_size.x, msg_control_size.x + 2*self.margin)
        self.dialog_size.y += msg_control_size.y + 2*self.margin

        return

    def _create_percent(self, dialog, parent_sizer):
        if not self.show_percent:
            return

        raise NotImplementedError


    def _create_timer(self, dialog, parent_sizer):
        if not self.show_time:
            return

        self._elapsed_control = self._create_label(dialog, parent_sizer, "Elapsed time : ")
        self._estimated_control = self._create_label(dialog, parent_sizer, "Estimated time : ")
        self._remaining_control = self._create_label(dialog, parent_sizer, "Remaining time : ")

        elapsed_size = self._elapsed_control.GetSize()
        estimated_size = self._estimated_control.GetSize()
        remaining_size = self._remaining_control.GetSize()

        timer_size = wx.Size()
        timer_size.x = max(elapsed_size.x, estimated_size.x, remaining_size.x)
        timer_size.y = elapsed_size.y + estimated_size.y + remaining_size.y

        self.dialog_size.x = max(self.dialog_size.x, timer_size.x + 2*self.margin)
        self.dialog_size.y += timer_size.y + 2*self.margin

        return

    def _create_control(self, parent):
        """ Creates the window contents.

        This method is intended to be overridden if necessary.  By default we
        just create an empty panel.

        """
        style = wx.DEFAULT_FRAME_STYLE | wx.FRAME_NO_WINDOW_MENU | wx.CLIP_CHILDREN

        dialog = wx.Frame(parent, -1, self.title, style=style, size=self.size,
                pos=self.position)

        sizer = wx.BoxSizer(wx.VERTICAL)
        dialog.SetSizer(sizer)
        dialog.SetAutoLayout(True)
        dialog.SetBackgroundColour(wx.NullColor)

        self.dialog_size = wx.Size()

        # The 'guts' of the dialog.
        self._create_message(dialog, sizer)
        self._create_gauge(dialog, sizer)
        self._create_percent(dialog, sizer)
        self._create_timer(dialog, sizer)
        self._create_buttons(dialog, sizer)

        dialog.SetClientSize(self.dialog_size)

        dialog.CentreOnParent()

        return dialog
