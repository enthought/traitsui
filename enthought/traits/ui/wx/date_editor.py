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

from enthought.traits.api import Int, Bool, List, on_trait_change
from enthought.traits.ui.wx.editor import Editor
from enthought.traits.ui.wx.constants import WindowColor


#------------------------------------------------------------------------------
#--  Simple Editor
#------------------------------------------------------------------------------

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


#------------------------------------------------------------------------------
#--  Custom Editor
#------------------------------------------------------------------------------

CALENDAR_WIDTH = 208
SELECTED_FG = wx.Colour(255, 0, 0, 255)
INVISIBLE_HIGHLIGHT_FG = wx.Colour(0, 0, 0, 0)
INVISIBLE_HIGHLIGHT_BG = wx.Colour(255, 255, 255, 0)

class CalendarCtrl(wx.Panel):
    """ 
    WX panel for use by the CustomEditor. 
    
    Description
    -----------
    Handles multi-select dates by special handling of the normal CalendarCtrl
    wx widget.  Doing single-select across multiple calendar widgets is also
    supported.
    """

    def __init__(self, parent, ID, selected, multi_select,
                 left_padding, top_padding, right_padding,
                 *args, **kwargs):
        wx.Panel.__init__(self, parent, ID, *args, **kwargs)

        self.SetBackgroundColour(WindowColor)

        self.date = wx.DateTime_Now()
        self.multi_select = multi_select
        self.selected_days = selected
        if not self.multi_select and not self.selected_days:
            self.selected_days = self.date_from_datetime(self.date)
        self.cal_ctrls = []
        self.left_padding = left_padding
        self.top_padding = top_padding
        self.month_padding = right_padding

        #--------------------------------------------------------------
        # Left (oldest) month.
        #--------------------------------------------------------------
        pos = (self.left_padding, self.top_padding)
        cal = self._make_calendar_widget(-2, pos)
        self.cal_ctrls.insert(0, cal)

        #--------------------------------------------------------------
        # Center (last) month.
        #--------------------------------------------------------------
        pos = (self.left_padding + CALENDAR_WIDTH + self.month_padding,
               self.top_padding)
        cal = self._make_calendar_widget(-1, pos)
        self.cal_ctrls.insert(0, cal)

        #--------------------------------------------------------------
        # Right (current) month.
        #--------------------------------------------------------------
        pos = (self.left_padding + 2*CALENDAR_WIDTH + 2*self.month_padding,
               self.top_padding)
        cal = self._make_calendar_widget(0, pos)
        self.cal_ctrls.insert(0, cal)

        self.selected_list_changed()
        for cal in self.cal_ctrls:
            self.highlight_changed(None, cal)
        return


    def date_from_datetime(self, dt):
        """
        Convert a wx DateTime object to a Python Date object.
        """
        new_date = datetime.date(dt.GetYear(), dt.GetMonth()+1, dt.GetDay())
        return new_date


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

        new_date.Set(old_date.GetDay(), new_month, new_year)
        return new_date


    def selected_list_changed(self, evt=None):
        """
        Update the date colors of the days in the widgets.
        """
        for cal in self.cal_ctrls:
            cur_month = cal.GetDate().GetMonth() + 1
            cur_year = cal.GetDate().GetYear()
            selected_days = self.selected_days

            # Wrap a singleton if necessary, to pass the for-loop.
            if not isinstance(selected_days, list):
                selected_days = [selected_days]

            for date_obj in selected_days:
                year, month, day = date_obj.timetuple()[:3]
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
        highlight = self.date_from_datetime(date)
        selected_days = self.selected_days

        # Wrap a singleton if necessary for the multi_select containment test.
        if not self.multi_select:
            selected_days = [selected_days]

        if highlight in selected_days:
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
        selection = self.date_from_datetime(date)
        if self.multi_select:
            if selection in self.selected_days:
                self.selected_days.remove(selection)
                cal.ResetAttr(date.GetDay())
            else:
                self.selected_days.append(selection)
        else:
            old_date = self.selected_days
            self.selected_days = selection
            for cal in self.cal_ctrls:
                if cal.GetDate().GetMonth()+1 == old_date.month:
                    cal.ResetAttr(old_date.day)
                    self.highlight_changed(evt, cal)

        # Update all the selected calendar days.  Slightly inefficient.
        self.selected_list_changed()
        self.highlight_changed(evt)
#-- end CalendarCtrl ----------------------------------------------------------


class CustomEditor(Editor):
    """
    Show multiple months using CalendarCtrl. Allow multi-select into a list.

    Trait Listeners
    ---------------
    The wx editor directly modifies the *value* trait of the Editor, which
    is the named trait of the corresponding Item in your View.  Therefore
    you can listen for changes to the user's selection by directly listening
    to the item changed event.

    Additional Work
    ---------------
    Written to support a specific need so not all features have been finished,

        1.  The custom editor has not been tested or used much with
            single-select, which should be the default for a normal Date.
        2.  The DateEditor Factory multi-select flag is not being propagated
            to this class.  (Or the padding flags for that matter.)  It has
            to be, for #1 to work.
        3.  More events could be generated.

    Sample
    ------
    Example usage::

        class DateListPicker(HasTraits):
            calendar = List
            traits_view = View(Item('calendar', editor=DateEditor(),
                                    style='custom', show_label=False))
    """

    # FIXME: The padding should be moved to the factory so it can be changed.
    # How much padding should be on the left of the editor.
    left_padding = Int(5)

    # How much padding should be on the top of the editor.
    top_padding = Int(5)

    # How much padding should be between the months.
    month_padding = Int(5)

    #-- Editor interface ------------------------------------------------------

    def init (self, parent):
        """
        Finishes initializing the editor by creating the underlying widget.
        """
        if self.factory.multi_select and not isinstance(self.value, list):
            raise ValueError('Multi-select is True, but editing a non-list.')
        elif not self.factory.multi_select and isinstance(self.value, list):
            raise ValueError('Multi-select is False, but editing a list.')
        
        calendar_ctrl = CalendarCtrl(parent,
                                     -1,
                                     self.value,
                                     self.factory.multi_select,
                                     self.left_padding,
                                     self.top_padding,
                                     self.month_padding)
        self.control = calendar_ctrl
        return


    def update_editor ( self ):
        """
        Updates the editor when the object trait changes externally to the
        editor.
        """
        self.control.selected_list_changed()
        return
#-- end CustomEditor definition -----------------------------------------------


#------------------------------------------------------------------------------
#--  Text Editor
#------------------------------------------------------------------------------
# TODO: Write me.  Possibly use TextEditor as a model to show a string
# representation of the date, and have enter-set do a date evaluation.
class TextEditor (SimpleEditor):
    pass
#-- end TextEditor definition -------------------------------------------------


#------------------------------------------------------------------------------
#--  Readonly Editor
#------------------------------------------------------------------------------
# TODO: Write me.  Possibly use TextEditor as a model to show a string
# representation of the date that cannot be changed.
class ReadonlyEditor (SimpleEditor):
    pass
#-- end ReadonlyEditor definition ---------------------------------------------

#-- eof -----------------------------------------------------------------------
