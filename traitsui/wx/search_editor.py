#-------------------------------------------------------------------------------
#
#  Copyright (c) 2009, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
#  Author: Evan Patterson
#  Date:   06/25/09
#
#-------------------------------------------------------------------------------

# System library imports
import wx

# Local imports
from editor import Editor


class SearchEditor(Editor):

    def init(self, parent):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """

        style = 0
        if self.factory.enter_set:
            style = wx.TE_PROCESS_ENTER
        self.control = wx.SearchCtrl(parent, -1, value=self.value, style=style)

        self.control.SetDescriptiveText(self.factory.text)
        self.control.ShowSearchButton(self.factory.search_button)
        self.control.ShowCancelButton(self.factory.cancel_button)

        if self.factory.auto_set:
            wx.EVT_TEXT(parent, self.control.GetId(), self.update_object)

        if self.factory.enter_set:
            wx.EVT_TEXT_ENTER(parent, self.control.GetId(), self.update_object)

        wx.EVT_SEARCHCTRL_SEARCH_BTN(parent, self.control.GetId(),
                                     self.update_object)
        wx.EVT_SEARCHCTRL_CANCEL_BTN(parent, self.control.GetId(),
                                     self.clear_text)

    def update_object(self, event):
        """ Handles the user entering input data in the edit control.
        """

        if not self._no_update:
            self.value = self.control.GetValue()
            if self.factory.search_event_trait != '':
                setattr(self.object, self.factory.search_event_trait, True)

    def clear_text(self, event):
        """ Handles the user pressing the cancel search button.
        """

        if not self._no_update:
            self.control.SetValue("")
            self.value = ""
            if self.factory.search_event_trait != '':
                setattr(self.object, self.factory.search_event_trait, True)

    def update_editor(self):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """

        if self.control.GetValue() != self.value:
            self._no_update = True
            self.control.SetValue(self.str_value)
            self._no_update = False
