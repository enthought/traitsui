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
#  Author: Judah De Paula
#  Date:   10/7/2008
#
#------------------------------------------------------------------------------
"""
A Traits UI editor that wraps a WX calendar panel.

Future Work
-----------
The only editor provided is a DatePickerCtrl.  The class needs to be extend 
to provide the four basic editor types, Simple, Custom, Text, and ReadOnly.
"""
import datetime

import wx

from enthought.traits.ui.wx.editor import Editor
from enthought.traits.ui.wx.basic_editor_factory import BasicEditorFactory



#-- _DateEditor definition ---------------------------------------------------- 
class _DateEditor (Editor):
    """ 
    Traits UI date editor.
    """
    
    def init ( self, parent ):
        """ 
        Finishes initializing the editor by creating the underlying widget.
        """
        # MS-Win's DatePickerCtrl comes with a check-box we don't want.
        # GenericDatePickerCtrl was exposed in wxPython version 2.8.8 only.
        if 'wxMSW' in wx.PlatformInfo and wx.__version__ > '2.8.8':
            date_widget = wx.GenericDatePickerCtrl
        else:
            # Linux / OS-X / windows 
            date_widget = wx.DatePickerCtrl
            
        self.control = date_widget(parent, 
                                   size=(120,-1),
                                   style = wx.DP_DROPDOWN
                                         | wx.DP_SHOWCENTURY
                                         | wx.DP_ALLOWNONE)
        self.control.Bind(wx.EVT_DATE_CHANGED, self.day_selected)
        return


    def day_selected(self, event):
        """
        Event for when calendar is selected, update/create date string.
        """
        date = event.GetDate()
        # WX sometimes has year == 0 temporarily when doing state changes.
        if date.IsValid() and date.GetYear() != 0:
            year = date.GetYear()
            # wx 2.8.8 has 0-indexed months.
            month = date.GetMonth() + 1  
            day = date.GetDay()
            try:
                self.value = datetime.date(year, month, day)
            except ValueError:
                print 'Invalid date:', year, month, day
                raise
                
        return


    def update_editor ( self ):
        """
        Updates the editor when the object trait changes externally to the
        editor.
        """
        if self.value:
            date = self.control.GetValue()
            # FIXME: A Trait assignment should support fixing an invalid 
            # date in the widget.
            if date.IsValid():
                date.SetYear(self.value.year)
                # wx 2.8.8 has 0-indexed months.
                date.SetMonth(self.value.month - 1) 
                date.SetDay(self.value.day)
                self.control.SetValue(date)
                self.control.Refresh()
        return
#-- end _DateEditor definition ------------------------------------------------ 

#-- eof ----------------------------------------------------------------------- 
