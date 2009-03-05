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

MOUSE_BOX_FILL = wx.Colour(0, 0, 255, 32)

CALENDAR_WIDTH = 208
SELECTED_FG = wx.Colour(255, 0, 0, 255)
UNAVAILABLE_FG = wx.Colour(192, 192, 192, 255)
DRAG_HIGHLIGHT_FG = wx.Colour(255, 255, 255, 255)
DRAG_HIGHLIGHT_BG = wx.Colour(128, 128, 255, 255)
NORMAL_HIGHLIGHT_FG = wx.Colour(0, 0, 0, 0)
NORMAL_HIGHLIGHT_BG = wx.Colour(255, 255, 255, 0)

class wxMouseBoxCalendarCtrl(wx.calendar.CalendarCtrl):
    """
    Subclass to add a mouse-over box-selection tool.
    
    Description
    -----------
    Add a Mouse drag-box highlight feature that can be used by the 
    CustomEditor to detect user selections.  CalendarCtrl must be subclassed 
    to get a device context to draw on top of the Calendar.  Otherwise, the 
    calendar widgets are always painted on top of the box during repaints.
    """

    def __init__(self, *args, **kwargs):
        super(wxMouseBoxCalendarCtrl, self).__init__(*args, **kwargs)

        self.dc = None
        self.gc = None
        self.selecting = False
        self.box_selected = []
        self.sel_start = (0,0)
        self.sel_end = (0,0)
        self.Bind(wx.EVT_RIGHT_DOWN, self.start_select)
        self.Bind(wx.EVT_RIGHT_UP, self.end_select)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.end_select)
        self.Bind(wx.EVT_MOTION, self.on_select)
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.calendar.EVT_CALENDAR_SEL_CHANGED, self.highlight_changed)

 
    def boxed_days(self):
        """
        Compute the days that are under the box selection.
        
        Returns
        -------
        A list of wx.DateTime objects under the mouse box.
        """
        x1, y1 = self.sel_start
        x2, y2 = self.sel_end
        if x1 > x2:
            x1, x2 = x2, x1
        if y1 > y2:
            y1, y2 = y2, y1

        grid = []
        for i in range(x1, x2, 20):
            for j in range(y1, y2, 20):
                grid.append(wx.Point(i,j))
            # Avoid jitter along the edge since the final points change.
            grid.append(wx.Point(i, y2))
        for j in range(y1, y2, 20):
            grid.append(wx.Point(x2, j))
        grid.append(wx.Point(x2, y2))
        
        
        
        selected_days = []
        for point in grid:
            (result, date, weekday) = self.HitTest(point)
            if result == wx.calendar.CAL_HITTEST_DAY:
                if date not in selected_days:
                    selected_days.append(date)
                    
        return selected_days
 
 
    def highlight_changed(self, event=None):
        """
        Hide the default highlight to take on the selected date attr.
        
        Description
        -----------
        A feature of the wx CalendarCtrl is that there are selected days,
        that always are shown and the user can move around with left-click.  
        But it's confusing and misleading when there are multiple 
        CalendarCtrl objects linked in one editor.  So we hide the 
        highlights in this CalendarCtrl by making it mimic the attribute 
        of the selected day.

        Highlights apparently can't take on a border style, so to be truly
        invisible, normal days cannot have borders.
        """
        date = self.GetDate()
        
        attr = self.GetAttr(date.GetDay())
        if attr is None:
            bg_color = NORMAL_HIGHLIGHT_BG
            fg_color = NORMAL_HIGHLIGHT_FG
        else:
            bg_color = attr.GetBackgroundColour()
            fg_color = attr.GetTextColour()
        self.SetHighlightColours(fg_color, bg_color)
        self.Refresh()
        return
        

    #-- event handlers -------------------------------------------------------- 
    def start_select(self, event):
        event.Skip()
        self.selecting = True
        self.box_selected = []
        self.sel_start = (event.m_x, event.m_y)
        self.sel_end = self.sel_start
       
       
    def end_select(self, event):
        event.Skip()
        self.selecting = False
        
        if self.dc is not None:
            self.dc.Clear()
            self.Refresh()
 
 
    def on_select(self, event):
        event.Skip()
        if not self.selecting:
            return
 
        self.sel_end = (event.m_x, event.m_y)
        self.box_selected = self.boxed_days()
        self.Refresh()
 
 
    def on_paint(self, event):
        event.Skip()
        if self.dc is None:
            self.dc = wx.PaintDC(self)
 
        if not self.selecting:
            return
 
        x = self.sel_start[0]
        y = self.sel_start[1]
        w = self.sel_end[0] - x
        h = self.sel_end[1] - y
 
        gc = wx.GraphicsContext.Create(self.dc)
        pen = gc.CreatePen(wx.BLACK_PEN)
        gc.SetPen(pen)
 
        points = [(x,y), (x+w, y), (x+w,y+h), (x,y+h), (x,y)]
 
        gc.DrawLines(points)
 
        brush = gc.CreateBrush(wx.Brush(MOUSE_BOX_FILL))
        gc.SetBrush(brush)
        gc.DrawRectangle(x, y, w, h)
#-- end wxMouseBoxCalendarCtrl ------------------------------------------------ 


class MultiCalendarCtrl(wx.Panel):
    """ 
    WX panel containing calendar widgets for use by the CustomEditor. 
    
    Description
    -----------
    Handles multi-select dates by special handling of the 
    wxMouseBoxCalendarCtrl widget.  Doing single-select across multiple 
    calendar widgets is also supported.
    """

    def __init__(self, parent, ID, selected, multi_select, allow_future,
                 months, padding, *args, **kwargs):
        wx.Panel.__init__(self, parent, ID, *args, **kwargs)

        self.sizer = wx.BoxSizer()
        self.SetSizer(self.sizer)
        self.SetBackgroundColour(WindowColor)
        self.date = wx.DateTime_Now()
        self.today = self.date_from_datetime(self.date)
        
        # Object attributes
        self.multi_select = multi_select
        self.allow_future = allow_future
        self.selected_days = selected
        if not self.multi_select and not self.selected_days:
            self.selected_days = self.today
        self.months = months
        self.padding = padding
        self.cal_ctrls = []
        
        # State to remember when a user is doing a shift-click selection.
        self._first_date = None
        self._drag_select = []
        self._box_select = []

        # Set up the individual month frames.
        for i in range(-(self.months-1), 1):
            cal = self._make_calendar_widget(i)
            self.cal_ctrls.insert(0, cal)
            if i != 0:
                self.sizer.AddSpacer(wx.Size(padding, padding))

        # Initial painting
        self.selected_list_changed()
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
            cal.highlight_changed()
        return

    
    def _make_calendar_widget(self, month_offset):
        """
        Add a calendar widget to the screen and hook up callbacks.
        """
        date = self.shift_datetime(self.date, month_offset)
        panel = wx.Panel(self, -1)
        cal = wxMouseBoxCalendarCtrl(panel,
            -1,
            date,
            style = wx.calendar.CAL_SUNDAY_FIRST
                  | wx.calendar.CAL_SEQUENTIAL_MONTH_SELECTION
                  #| wx.calendar.CAL_SHOW_HOLIDAYS
        )
        self.sizer.Add(panel)
        cal.highlight_changed()
        
        # Set up control to sync the other calendar widgets and coloring:
        self.Bind(wx.calendar.EVT_CALENDAR, self.day_toggled, id=cal.GetId())
        self.Bind(wx.calendar.EVT_CALENDAR_MONTH, self.month_changed, cal)
        self.Bind(wx.calendar.EVT_CALENDAR_YEAR, self.month_changed, cal)
        self.Bind(wx.calendar.EVT_CALENDAR_WEEKDAY_CLICKED, 
                  self._weekday_clicked, cal)

        # Events not handled by the wx CalendarCtrl.
        wx.EVT_LEFT_DOWN(cal, self._left_down)
        wx.EVT_LEFT_UP(cal, self._left_up)
        wx.EVT_RIGHT_UP(cal, self._process_box_select)
        wx.EVT_LEAVE_WINDOW(cal, self._process_box_select)
        wx.EVT_MOTION(cal, self._mouse_drag)
        return cal


        
    def unhighlight_days(self, days):
        """
        Turn off all highlights in all cals, but leave any selected color.
        """
        for cal in self.cal_ctrls:
            c = cal.GetDate()
            for date in days:
                if date.year == c.GetYear() and date.month == c.GetMonth()+1:
                    
                    # Unselected days either need to revert to the 
                    # unavailable color, or the default attribute color.
                    if (not self.allow_future and 
                       ((date.year, date.month, date.day) > 
                       (self.today.year, self.today.month, self.today.day))):
                        attr = wx.calendar.CalendarDateAttr(colText=UNAVAILABLE_FG)
                    else:
                        attr = wx.calendar.CalendarDateAttr(
                            colText=NORMAL_HIGHLIGHT_FG,
                            colBack=NORMAL_HIGHLIGHT_BG)
                    if date in self.selected_days:
                        attr.SetTextColour(SELECTED_FG)
                    cal.SetAttr(date.day, attr)
            cal.highlight_changed()
        return


    def highlight_days(self, days):
        """
        Color the highlighted list of days across all calendars.
        """
        for cal in self.cal_ctrls:
            c = cal.GetDate()
            for date in days:
                if date.year == c.GetYear() and date.month == c.GetMonth()+1:
                    attr = wx.calendar.CalendarDateAttr(
                            colText=DRAG_HIGHLIGHT_FG,
                            colBack=DRAG_HIGHLIGHT_BG
                            )
                    cal.SetAttr(date.day, attr)
            cal.highlight_changed()
            cal.Refresh()


    def add_days_to_selection(self, days):
        """
        Add a list of days to the selection, using various rules.
        """
        if days:
            # Do we want to add or remove them? 
            add_items = days[0] not in self.selected_days
    
            for day in days:
                # Skip if we don't allow future, and it's a future day.
                if self.allow_future or day <= self.today:
                    if add_items and day not in self.selected_days:
                        self.selected_days.append(day)
                    elif not add_items and day in self.selected_days:
                        self.selected_days.remove(day)

    #------------------------------------------------------------------------
    # Event handlers
    #------------------------------------------------------------------------

    def _process_box_select(self, event):
        """
        Possibly move the calendar box-selected days into our selected days.
        """
        event.Skip()
        self.unhighlight_days(self._box_select)
        
        if not event.Leaving():
            self.add_days_to_selection(self._box_select)
            self.selected_list_changed()
            
        self._box_select = []


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
        return
    

    def _left_down(self, event):
        """ Handle user selection of days. """
        event.Skip()
        cal = event.GetEventObject()
        result, dt, weekday = cal.HitTest(event.GetPosition())
        
        # Ctrl-click selection
        if result == wx.calendar.CAL_HITTEST_DAY and event.CmdDown():
            self.day_toggled(event, dt)
            
        # Inter-month-drag selection
        if (result == wx.calendar.CAL_HITTEST_DAY 
            and event.ShiftDown()
            and not cal.selecting):
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
            
            last_date = self.date_from_datetime(dt)
            if last_date <= self._first_date:
                first, last = last_date, self._first_date
            else:
                first, last = self._first_date, last_date
            
            newly_selected = []
            while first <= last:
                newly_selected.append(first)
                first = first + datetime.timedelta(1)
            self.add_days_to_selection(newly_selected)
        
        # Reset a drag-select operation, even if it wasn't completed.    
        self._first_date = None
        self._drag_select = []

        self.selected_list_changed()
        return
       
        
    def _shift_drag_update(self, event):
        """ Shift-drag in progress. """
        cal = event.GetEventObject()
        result, dt, weekday = cal.HitTest(event.GetPosition())

        self.unhighlight_days(self._drag_select)

        self._drag_select = [] 
        # Prepare for an abort, don't highlight new selections.
        if not event.ShiftDown() or result != wx.calendar.CAL_HITTEST_DAY:
            cal.highlight_changed()
            for cal in self.cal_ctrls:
                cal.Refresh()
            return
            
        # Make a list of selections.
        last_date = self.date_from_datetime(dt)
        if last_date <= self._first_date:
            first, last = last_date, self._first_date
        else:
            first, last = self._first_date, last_date
        while first <= last:
            if self.allow_future or first <= self.today:
                self._drag_select.append(first)
            first = first + datetime.timedelta(1)

        self.highlight_days(self._drag_select)


    def _mouse_drag(self, event):
        """ Called when the mouse in being dragged within the calendars. """
        event.Skip()
        cal = event.GetEventObject()
        if not cal.selecting and self._first_date:
            self._shift_drag_update(event)
        if cal.selecting:
            self.unhighlight_days(self._box_select)
            self._box_select = [self.date_from_datetime(dt)
                                for dt in cal.boxed_days()]
            self.highlight_days(self._box_select)
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
                cal.highlight_changed()
        
        # Back-up if we're not allowed to move into future months.
        if not self.allow_future:
            month = self.cal_ctrls[0].GetDate().GetMonth()+1
            year = self.cal_ctrls[0].GetDate().GetYear()
            if (year, month) > (self.today.year, self.today.month):
                for i, cal in enumerate(self.cal_ctrls):
                    new_date = self.shift_datetime(wx.DateTime_Now(), -i)
                    cal.SetDate(new_date)
                    cal.highlight_changed()
            
        # Redraw the selected days.
        self.selected_list_changed()


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
                    cal.highlight_changed()

        # Update all the selected calendar days.  Slightly inefficient.
        self.selected_list_changed()
#-- end CalendarCtrl ----------------------------------------------------------


class CustomEditor(Editor):
    """
    Show multiple months with MultiCalendarCtrl. Allow multi-select.

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

    #-- Editor interface ------------------------------------------------------

    def init (self, parent):
        """
        Finishes initializing the editor by creating the underlying widget.
        """
        if self.factory.multi_select and not isinstance(self.value, list):
            raise ValueError('Multi-select is True, but editing a non-list.')
        elif not self.factory.multi_select and isinstance(self.value, list):
            raise ValueError('Multi-select is False, but editing a list.')
        
        calendar_ctrl = MultiCalendarCtrl(parent,
                                          -1,
                                          self.value,
                                          self.factory.multi_select,
                                          self.factory.allow_future,
                                          self.factory.months,
                                          self.factory.padding)
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
