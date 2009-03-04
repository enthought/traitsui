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
UNAVAILABLE_FG = wx.Colour(192, 192, 192, 255)
DRAG_HIGHLIGHT_FG = wx.Colour(255, 255, 255, 255)
DRAG_HIGHLIGHT_BG = wx.Colour(128, 128, 255, 255)
NORMAL_HIGHLIGHT_FG = wx.Colour(0, 0, 0, 0)
NORMAL_HIGHLIGHT_BG = wx.Colour(255, 255, 255, 0)

class CalendarCtrl(wx.Panel):
    """ 
    WX panel for use by the CustomEditor. 
    
    Description
    -----------
    Handles multi-select dates by special handling of the normal CalendarCtrl
    wx widget.  Doing single-select across multiple calendar widgets is also
    supported.
    """

    def __init__(self, parent, ID, selected, multi_select, allow_future,
                 left_padding, top_padding, right_padding,
                 *args, **kwargs):
        wx.Panel.__init__(self, parent, ID, *args, **kwargs)

        self.SetBackgroundColour(WindowColor)
        self.date = wx.DateTime_Now()
        self.today = self.date_from_datetime(self.date)
        
        # Object attributes
        self.multi_select = multi_select
        self.allow_future = allow_future
        self.selected_days = selected
        if not self.multi_select and not self.selected_days:
            self.selected_days = self.today
        self.cal_ctrls = []
        
        # State to remember when a user is doing a shift-click selection.
        self._first_date = None
        self._drag_select = []

        # Layout
        self.left_padding = left_padding
        self.top_padding = top_padding
        self.month_padding = right_padding

        # TODO: Hard-coded three-month window, but all the update functions
        #       loop over self.cal_ctrls so it should be straightforward
        #       to make the number of months a parameter in the constructor. 
        #       Perhaps start using spacers at the same time.
        
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

        #--------------------------------------------------------------
        # Initial painting
        #--------------------------------------------------------------
        self.selected_list_changed()
        self.highlight_changed()
        return

    
    def date_from_datetime(self, dt):
        """
        Convert a wx DateTime object to a Python Date object.
        """
        new_date = datetime.date(dt.GetYear(), dt.GetMonth()+1, dt.GetDay())
        return new_date


    def datetime_from_date(self, date):
        """
        Convert a Python Date object to a wx DateTime object. Ignores time.
        """
        dt = wx.DateTime()
        dt.SetYear(date.year)
        dt.SetMonth(date.month-1)
        dt.SetDay(date.day)
        return dt


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
        """ Update the date colors of the days in the widgets. """
        for cal in self.cal_ctrls:
            cur_month = cal.GetDate().GetMonth() + 1
            cur_year = cal.GetDate().GetYear()
            selected_days = self.selected_days

            # Gray out future days if they're unselectable.
            if not self.allow_future:                
                for day in range(1,32):
                    if (cur_year, cur_month, day) > \
                       (self.today.year, self.today.month, self.today.day):
                        attr = wx.calendar.CalendarDateAttr(colText=UNAVAILABLE_FG)
                        cal.SetAttr(day, attr)
                    else:
                        cal.ResetAttr(day)

            # When not multi_select, wrap the singleton to pass the for-loop.
            if not isinstance(selected_days, list):
                selected_days = [selected_days]

            for date_obj in selected_days:
                year, month, day = date_obj.timetuple()[:3]
                if month == cur_month and year == cur_year:
                    attr = wx.calendar.CalendarDateAttr(
                        colText=SELECTED_FG,
                        # FIXME: A highlighted date doesn't show the border.
                        # So we can't use borders for now.
                        #border=wx.calendar.CAL_BORDER_SQUARE,
                        #colBorder="blue"
                        )
                    cal.SetAttr(day, attr)
                else:
                    # Unselected days either need to revert to the 
                    # unavailable color, or the default attribute color.
                    if (not self.allow_future and 
                       ((cur_year, cur_month, day) > 
                       (self.today.year, self.today.month, self.today.day))):
                        attr = wx.calendar.CalendarDateAttr(colText=UNAVAILABLE_FG)
                        cal.SetAttr(day, attr)
                    else:
                        cal.ResetAttr(day)

    
    def _make_calendar_widget(self, month_offset, position):
        """
        Add a calendar widget to the screen and hook up callbacks.
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
        self.highlight_changed(cal=cal)
        
        # Set up control to sync the other calendar widgets and coloring:
        self.Bind(wx.calendar.EVT_CALENDAR, self.day_toggled, id=cal.GetId())
        self.Bind(wx.calendar.EVT_CALENDAR_MONTH, self.month_changed, cal)
        self.Bind(wx.calendar.EVT_CALENDAR_YEAR, self.month_changed, cal)
        self.Bind(wx.calendar.EVT_CALENDAR_WEEKDAY_CLICKED, 
                  self._weekday_clicked, cal)
        self.Bind(wx.calendar.EVT_CALENDAR_SEL_CHANGED,
                  self.highlight_changed,
                  id=cal.GetId())

        # Direct mouse events not handled by the wx CalendarCtrl.
        wx.EVT_LEFT_DOWN(cal, self._left_down)
        wx.EVT_LEFT_UP(cal, self._left_up)
        wx.EVT_MOTION(cal, self._mouse_drag)
        return cal

    def _month_start_weekday(self, date):
        """ Return the dayofweek (in WX format, sun=0) of a dt """
        pass

    #------------------------------------------------------------------------
    # Event handlers
    #------------------------------------------------------------------------

    def _weekday_clicked(self, evt):
        """ A day on the weekday bar has been clicked.  Select all days. """
        weekday = evt.GetWeekDay()
        cal = evt.GetEventObject()
        month = cal.GetDate().GetMonth()+1
        year = cal.GetDate().GetYear()

        days = []
        # Messy math to compute the dates of each weekday in the month.
        # Python uses Monday=0, while wx uses Sunday=0. 
        month_start_weekday = (datetime.date(year, month, 1).weekday()+1) %7
        weekday_offset = (weekday - month_start_weekday) % 7
        for day in range(weekday_offset, 31, 7):
            try:
                day = datetime.date(year, month, day+1)
                if self.allow_future or day <= self.today:
                    days.append(day)
            except ValueError:
                pass
        
        # Try to be clever and toggle the most days all the same way.
        selected = len([day for day in days if day in self.selected_days])
        add_items = selected <= (len(days) / 2.0)
        for day in days:
            if self.allow_future or day <= self.today:
                if add_items and day not in self.selected_days:
                    self.selected_days.append(day)
                elif not add_items and day in self.selected_days:
                    self.selected_days.remove(day)

        self.selected_list_changed()
        self.highlight_changed()
        return
    

    def _left_down(self, event):
        """ Handle user selection of days. """
        event.Skip()
        cal = event.GetEventObject()
        result, dt, weekday = cal.HitTest(event.GetPosition())
        
        # Ctrl-click selection
        if result == wx.calendar.CAL_HITTEST_DAY and event.CmdDown():
            self.day_toggled(event, dt)
            
        # Shift-click selection
        if result == wx.calendar.CAL_HITTEST_DAY and event.ShiftDown():
            # Remember that the user started a multiselect.
            self._first_date = self.date_from_datetime(dt)
            self._drag_select = [self._first_date]
            # Start showing the highlight colors with a mouse_drag event.
            self._mouse_drag(event)
        return
    
    
    def _left_up(self, event):
        """ Handle the end of a possible run-selection. """
        event.Skip()
        cal = event.GetEventObject()
        result, dt, weekday = cal.HitTest(event.GetPosition())
        
        # Complete a drag-select operation.
        if (result == wx.calendar.CAL_HITTEST_DAY and event.ShiftDown()
            and self._first_date):
            
            # Do we want to add or remove them? 
            add_items = self._first_date not in self.selected_days
            last_date = self.date_from_datetime(dt)
            if last_date <= self._first_date:
                first, last = last_date, self._first_date
            else:
                first, last = self._first_date, last_date
            
            while first <= last:
                # Skip if we don't allaw future, and it's a future day.
                if self.allow_future or first <= self.today:
                    if add_items and first not in self.selected_days:
                        self.selected_days.append(first)
                    elif not add_items and first in self.selected_days:
                        self.selected_days.remove(first)
                first = first + datetime.timedelta(1)
        
        # Reset a drag-select operation, even if it wasn't completed.    
        self._first_date = None
        self._drag_select = []

        self.selected_list_changed()
        self.highlight_changed()
        return
       
        
    def _shift_drag_update(self, event):
        """ Shift-drag in progress. """
        cal = event.GetEventObject()
        result, dt, weekday = cal.HitTest(event.GetPosition())

        #if result == wx.calendar.CAL_HITTEST_DAY and event.ShiftDown()

        # Always unset the old values before deciding to repaint new ones.
        for cal in self.cal_ctrls:
            c = cal.GetDate()
            for date in self._drag_select:
                if date.year == c.GetYear() and date.month == c.GetMonth()+1:
                    attr = wx.calendar.CalendarDateAttr(
                            colText=NORMAL_HIGHLIGHT_FG,
                            colBack=NORMAL_HIGHLIGHT_BG)
                    if date in self.selected_days:
                        attr.SetTextColour(SELECTED_FG)
                    cal.SetAttr(date.day, attr)

        self._drag_select = [] 
        # Prepare for an abort, don't highlight new selections.
        if not event.ShiftDown() or result != wx.calendar.CAL_HITTEST_DAY:
            self.highlight_changed()
            for cal in self.cal_ctrls:
                cal.Refresh()
            return
            
        # Make a fresh list of selections.
        last_date = self.date_from_datetime(dt)
        if last_date <= self._first_date:
            first, last = last_date, self._first_date
        else:
            first, last = self._first_date, last_date
        
        while first <= last:
            if self.allow_future or first <= self.today:
                self._drag_select.append(first)
            first = first + datetime.timedelta(1)

        # Color the selected list of days.
        for cal in self.cal_ctrls:
            c = cal.GetDate()
            for date in self._drag_select:
                if date.year == c.GetYear() and date.month == c.GetMonth()+1:
                    attr = wx.calendar.CalendarDateAttr(
                            colText=DRAG_HIGHLIGHT_FG,
                            colBack=DRAG_HIGHLIGHT_BG
                            )
                    cal.SetAttr(date.day, attr)
            self.highlight_changed(cal=cal)
            cal.Refresh()


    def _mouse_drag(self, event):
        """ Called when the mouse in being dragged within the calendars. """
        event.Skip()
        if self._first_date:
            self._shift_drag_update(event)
        return
        

    def month_changed(self, evt=None):
        """
        Link the calendars together so if one changes, they all change.
        
        TODO: Maybe wx.calendar.CAL_HITTEST_INCMONTH could be checked and
        the event skipped, rather than now where we undo the update after 
        the event has gone through.
        """
         
        cal_index = self.cal_ctrls.index(evt.GetEventObject())
        # Current month is already updated, just need to shift the others
        current_date = self.cal_ctrls[cal_index].GetDate()
        for i, cal in enumerate(self.cal_ctrls):
            if i != cal_index:
                new_date = self.shift_datetime(current_date, cal_index - i)
                cal.SetDate(new_date)
        
        # Back-up if we're not allowed to move into future months.
        if not self.allow_future:
            month = self.cal_ctrls[0].GetDate().GetMonth()+1
            year = self.cal_ctrls[0].GetDate().GetYear()
            if (year, month) > (self.today.year, self.today.month):
                for i, cal in enumerate(self.cal_ctrls):
                    new_date = self.shift_datetime(wx.DateTime_Now(), -i)
                    cal.SetDate(new_date)
            
        # Redraw the selected days.
        self.highlight_changed()
        self.selected_list_changed()


    def highlight_changed(self, evt=None, cal=None):
        """
        Hide the default highlight to take on the selected date attr.
        
        Parameters
        ----------
        evt : wx Event
            The default calling parameter for a wx event.
        cal : wx.calendar.CalendarCtrl
            If calling directly, then a calendar can be provided instead 
            without needing an event.  If neither are provided, then the
            master cal_ctrls object attribute is used.
        
        Description
        -----------
        A feature of the wx CalendarCtrl is that there are selected days,
        that always are shown and the user can move around with left-click.  
        But it's confusing and misleading when there are multiple 
        CalendarCtrl objects linked in this editor.  So we hide the 
        highlights in each CalendarCtrl by making it mimic the attribute 
        of the selected day.
        """
        if evt is None and cal is None:
            cals = self.cal_ctrls
        elif cal == None:
            cals = [evt.GetEventObject()]
        else:
            cals = [cal]
        
        for cal in cals:
            date = cal.GetDate()
            highlight = self.date_from_datetime(date)
            
            attr = cal.GetAttr(highlight.day)
            if attr is None:
                bg_color = NORMAL_HIGHLIGHT_BG
                fg_color = NORMAL_HIGHLIGHT_FG
            else:
                bg_color = attr.GetBackgroundColour()
                fg_color = attr.GetTextColour()
            cal.SetHighlightColours(fg_color, bg_color)
            cal.Refresh()
        return


    def day_toggled(self, evt, dt=None):
        """
        When the user double-clicks on a date, toggle selection of that date.
        """
        cal = evt.GetEventObject()
        if dt == None:
            dt = cal.GetDate()
        selection = self.date_from_datetime(dt)
        # If selecting future dates is disabled, then short-circuit a toggle.
        if not self.allow_future and selection > self.today:
            return

        if self.multi_select:
            if selection in self.selected_days:
                self.selected_days.remove(selection)
                cal.ResetAttr(selection.day)
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
        2.  More events could be generated.

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
                                     self.factory.allow_future,
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
