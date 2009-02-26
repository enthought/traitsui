#------------------------------------------------------------------------------
#
#  Copyright (c) 2005--2009, Enthought, Inc.
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
#  Date:   2/26/2009
#
#------------------------------------------------------------------------------
"""
A Traits UI editor that wraps a WX calendar panel.

Future Work
-----------
The class needs to be extend to provide the four basic editor types, 
Simple, Custom, Text, and ReadOnly.
"""
import datetime

import wx
import wx.calendar

from enthought.traits.ui.wx.editor import Editor

#-- SimpleEditor definition --------------------------------------------------- 
class SimpleEditor (Editor):
    """ 
    Simple Traits UI date editor.  Shows a text box, and a date-picker widget.
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
#-- end SimpleEditor definition ----------------------------------------------- 


CALENDAR_WIDTH = 208
LEFT_PADDING = 5
TOP_PADDING = 5
MONTH_PADDING = 5
SELECTED_FG = wx.Colour(255, 0, 0, 255)
INVISIBLE_HIGHLIGHT_FG = wx.Colour(0, 0, 0, 0)
INVISIBLE_HIGHLIGHT_BG = wx.Colour(0, 0, 0, 0)
#----------------------------------------------------------------------

class CalendarCtrl(wx.Panel):
    """
    WX panel for use by the CustomEditor.
    """
    
    def __init__(self, parent, ID):
        wx.Panel.__init__(self, parent, ID)
        
        self.date = wx.DateTime_Now()
        self.cal_ctrls = []
        self.selected_days = set([(2009,1,1), (2009,10,31), (2009,12,25)])

        #--------------------------------------------------------------
        # Left (oldest) month.
        #--------------------------------------------------------------
        pos = (LEFT_PADDING, TOP_PADDING)
        cal = self._make_calendar_widget(-2, pos)
        self.cal_ctrls.insert(0, cal)
                
        #--------------------------------------------------------------
        # Center (last) month.
        #--------------------------------------------------------------
        pos = (LEFT_PADDING + CALENDAR_WIDTH + MONTH_PADDING, TOP_PADDING)
        cal = self._make_calendar_widget(-1, pos)
        self.cal_ctrls.insert(0, cal)
        
        #--------------------------------------------------------------
        # Right (current) month.
        #--------------------------------------------------------------
        pos = (LEFT_PADDING + 2*CALENDAR_WIDTH + 2*MONTH_PADDING, TOP_PADDING)
        cal = self._make_calendar_widget(0, pos) 
        self.cal_ctrls.insert(0, cal)

        self.selected_list_changed()
        return
        

    def _make_calendar_widget(self, month_offset, position):
        """
        Add a calendar widget to the screen and hook up basic callbacks.
        """
        date = self.shift_datetime(self.date, month_offset)
        cal = wx.calendar.CalendarCtrl(self, 
            -1, 
            date, 
            pos = position,
            style = wx.calendar.CAL_SUNDAY_FIRST
                  | wx.calendar.CAL_SEQUENTIAL_MONTH_SELECTION
                  #| wx.calendar.CAL_SHOW_HOLIDAYS 
        )
        self.hide_highlight(cal)

        self.Bind(wx.calendar.EVT_CALENDAR, self.day_toggled, id=cal.GetId())
        self.Bind(wx.calendar.EVT_CALENDAR_SEL_CHANGED, 
                  self.highlight_changed, 
                  id=cal.GetId())

        # Set up control to sync the other calendar widgets:
        self.Bind(wx.calendar.EVT_CALENDAR_MONTH, self.month_changed, cal)
        self.Bind(wx.calendar.EVT_CALENDAR_YEAR, self.month_changed, cal)
        return cal


    def hide_highlight(self, calendar):
        """
        When the app changes the selected day, hide the highlight.
        """
        calendar.SetHighlightColours(INVISIBLE_HIGHLIGHT_FG, 
                                     INVISIBLE_HIGHLIGHT_BG)
        return

    
    def show_highlight(self, calendar):
        """
        Turn on the highlighting for when the user changes the selected day.
        """
        calendar.SetHighlightColours(SELECTED_FG, 
                                     INVISIBLE_HIGHLIGHT_BG)
        return


    def shift_datetime(self, old_date, months):
        """
        Create a new DateTime from *old_date* with an *offset* number of months.
        
        Parameters
        ----------
        old_date : DateTime
            The old DateTime to make a date copy of.  Does not copy time.
        months : int
            A signed int to add or subtract from the old date months.  Does
            not support jumping more than 12 months.
        """
        new_date = wx.DateTime()
        new_month = old_date.GetMonth() + months
        new_year = old_date.GetYear()
        if new_month < 0:
            new_month += 12
            new_year -= 1
        elif new_month > 11:
            new_month -= 12
            new_year += 1
                        
        # Should we always use 1 for the day in case of Feb?  Hidden highlight
        # can cause apparent unresponsiveness.
        new_date.Set(old_date.GetDay(), new_month, new_year)
        return new_date


    def selected_list_changed(self, evt=None):
        """ 
        Update the date colors of the days in the widgets.
        """
        for cal in self.cal_ctrls:
            cur_month = cal.GetDate().GetMonth() + 1
            cur_year = cal.GetDate().GetYear()
            for year, month, day in self.selected_days:
                if month == cur_month and year == cur_year:
                    attr = wx.calendar.CalendarDateAttr(
                        colText=SELECTED_FG,
                        # FIXME: A highlighted date doesn't show the border.
                        # So turn borders off for now.
                        #border=wx.calendar.CAL_BORDER_SQUARE,
                        #colBorder="blue"
                        )
                    cal.SetAttr(day, attr)
                else:
                    cal.ResetAttr(day)    
    
    
    #-------------------------------------------------------------------------- 
    # Event handlers
    #-------------------------------------------------------------------------- 
    
    def month_changed(self, evt=None):
        """ 
        Link the calendars together so if one changes, the all change.
        """
        cal_index = self.cal_ctrls.index(evt.GetEventObject())
        # Current month is already updated, just need to shift the others
        current_date = self.cal_ctrls[cal_index].GetDate() 
        for i, cal in enumerate(self.cal_ctrls):
            if i != cal_index:
                new_date = self.shift_datetime(current_date, cal_index - i)
                cal.SetDate(new_date)
            self.highlight_changed(None, cal)
        # Redraw the selected days.
        self.selected_list_changed()


    def highlight_changed(self, evt, cal=None):
        """
        We're hiding the default highlight to take on the selected date attr.
        """
        if cal == None:
            cal = evt.GetEventObject()
        date = cal.GetDate()
        highlight = (date.GetYear(), date.GetMonth()+1, date.GetDay())
        if highlight in self.selected_days: 
            self.show_highlight(cal)
        else:
            self.hide_highlight(cal)
        cal.Refresh()
        
        
    def day_toggled(self, evt):
        """
        When the user double-clicks on a date, toggle selection of that date.
        """
        cal = evt.GetEventObject()
        date = cal.GetDate()
        selection = (date.GetYear(), date.GetMonth()+1, date.GetDay())
        if selection in self.selected_days:
            self.selected_days.remove(selection)
        else:
            self.selected_days.add(selection)

        # Update all the selected calendar days.  Slightly inefficient.
        self.selected_list_changed()
        self.highlight_changed(evt)
#-- end CalendarCtrl --------------------------------------------------


class CustomEditor (SimpleEditor):
    """
    Show multiple months, and allow multi-select into a list.
    """
    
    def init ( self, parent ):
        """ 
        Finishes initializing the editor by creating the underlying widget.
        """
        calendar_ctrl = CalendarCtrl(parent, -1)
            
        self.control = calendar_ctrl
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
    pass
#-- end CustomEditor definition ----------------------------------------------- 


class TextEditor (SimpleEditor):
    # TODO: Write me.  Possibly use TextEditor as a model to show a string
    # representation of the date, and have enter-set do a date evaluation.
    pass
#-- end TextEditor definition ------------------------------------------------- 


class ReadonlyEditor (SimpleEditor):
    # TODO: Write me.  Possibly use TextEditor as a model to show a string
    # representation of the date that cannot be changed.
    pass
#-- end ReadonlyEditor definition --------------------------------------------- 

#-- eof ----------------------------------------------------------------------- 
