# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

"""
A Traits UI editor that wraps a WX timer control.

Future Work
-----------
The only editor provided is an editable and constrained "XX:XX:XX XM" field.
At the minimum, a spinner should be provided so the time can be changed
without the need for a keyboard.  In addition we need to extend to provide
all four of the basic editor types, Simple, Custom, Text, and Readonly.
"""
import datetime

import wx.adv

from traitsui.wx.editor import Editor
from traitsui.wx.text_editor import ReadonlyEditor as TextReadonlyEditor


class SimpleEditor(Editor):
    """
    Traits UI time editor.
    """

    def init(self, parent):
        """
        Finishes initializing the editor by creating the underlying toolkit
        widget.
        """
        tctl = wx.adv.TimePickerCtrl(parent, -1, name="12 hour control")
        self.control = tctl
        self.control.Bind(wx.adv.EVT_TIME_CHANGED, self.time_updated)
        return

    def time_updated(self, event):
        """
        Event for when the wx time control is updated.
        """
        time = self.control.GetValue()
        hour = time.GetHour()
        minute = time.GetMinute()
        second = time.GetSecond()
        self.value = datetime.time(hour, minute, second)
        return

    def update_editor(self):
        """
        Updates the editor when the object trait changes externally to the
        editor.
        """
        if self.value:
            time = self.control.GetValue()
            time.SetHour(self.value.hour)
            time.SetMinute(self.value.minute)
            time.SetSecond(self.value.second)
            self.control.SetValue(time)
        return


# TODO: Write me.  Possibly use TextEditor as a model to show a string
# representation of the time, and have enter-set do a time evaluation.
class TextEditor(SimpleEditor):
    pass


# TODO: Write me.
class CustomEditor(SimpleEditor):
    pass


class ReadonlyEditor(TextReadonlyEditor):
    """Use a TextEditor for the view."""

    def _get_str_value(self):
        """Replace the default string value with our own time version."""
        if self.value is None:
            return self.factory.message
        else:
            return self.value.strftime(self.factory.strftime)
