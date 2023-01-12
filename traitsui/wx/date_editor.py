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
A Traits UI editor that wraps a WX calendar panel.

Future Work
-----------
The class needs to be extend to provide the four basic editor types,
Simple, Custom, Text, and ReadOnly.
"""

import datetime
import logging

import wx
import wx.adv

from traitsui.wx.editor import Editor
from traitsui.wx.constants import WindowColor
from traitsui.wx.text_editor import ReadonlyEditor as TextReadonlyEditor


logger = logging.getLogger(__name__)


class SimpleEditor(Editor):
    """
    Simple Traits UI date editor.  Shows a text box, and a date-picker widget.
    """

    def init(self, parent):
        """
        Finishes initializing the editor by creating the underlying widget.
        """
        date_widget = wx.adv.DatePickerCtrl

        self.control = date_widget(
            parent,
            size=(120, -1),
            style=wx.adv.DP_DROPDOWN
            | wx.adv.DP_SHOWCENTURY
            | wx.adv.DP_ALLOWNONE,
        )
        self.control.Bind(wx.adv.EVT_DATE_CHANGED, self.day_selected)
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
                logger.exception(
                    "Invalid date: %d-%d-%d (y-m-d)", (year, month, day)
                )
                raise
        return

    def update_editor(self):
        """
        Updates the editor when the object trait changes externally to the
        editor.
        """
        if self.value:
            date = self.control.GetValue()
            # FIXME: A Trait assignment should support fixing an invalid
            # date in the widget.
            if date.IsValid():
                # Important: set the day before setting the month, otherwise wx may fail
                # to set the month.
                date.SetYear(self.value.year)
                date.SetDay(self.value.day)
                # wx 2.8.8 has 0-indexed months.
                date.SetMonth(self.value.month - 1)
                self.control.SetValue(date)
                self.control.Refresh()
        return


# ------------------------------------------------------------------------------
# --  Custom Editor
# ------------------------------------------------------------------------------

SELECTED_FG = wx.Colour(255, 0, 0)
UNAVAILABLE_FG = wx.Colour(192, 192, 192)
DRAG_HIGHLIGHT_FG = wx.Colour(255, 255, 255)
DRAG_HIGHLIGHT_BG = wx.Colour(128, 128, 255)
try:
    MOUSE_BOX_FILL = wx.Colour(0, 0, 255, 32)
    NORMAL_HIGHLIGHT_FG = wx.Colour(0, 0, 0, 0)
    NORMAL_HIGHLIGHT_BG = wx.Colour(255, 255, 255, 0)
# Alpha channel in wx.Colour does not exist prior to version 2.7.1.1
except TypeError:
    MOUSE_BOX_FILL = wx.Colour(0, 0, 255)
    NORMAL_HIGHLIGHT_FG = wx.Colour(0, 0, 0)
    NORMAL_HIGHLIGHT_BG = wx.Colour(255, 255, 255)


class wxMouseBoxCalendarCtrl(wx.adv.CalendarCtrl):
    """
    Subclass to add a mouse-over box-selection tool.

    Description
    -----------
    Add a Mouse drag-box highlight feature that can be used by the
    CustomEditor to detect user selections.  CalendarCtrl must be subclassed
    to get a device context to draw on top of the Calendar, otherwise the
    calendar widgets are always painted on top of the box during repaints.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.selecting = False
        self.box_selected = []
        self.sel_start = (0, 0)
        self.sel_end = (0, 0)
        self.Bind(wx.EVT_RIGHT_DOWN, self.start_select)
        self.Bind(wx.EVT_RIGHT_UP, self.end_select)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.end_select)
        self.Bind(wx.EVT_MOTION, self.on_select)
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.adv.EVT_CALENDAR_SEL_CHANGED, self.highlight_changed)

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
        for i in range(x1, x2, 15):
            for j in range(y1, y2, 15):
                grid.append(wx.Point(i, j))
            grid.append(wx.Point(i, y2))
        # Avoid jitter along the edge since the final points change.
        for j in range(y1, y2, 20):
            grid.append(wx.Point(x2, j))
        grid.append(wx.Point(x2, y2))

        selected_days = []
        for point in grid:
            (result, date, weekday) = self.HitTest(point)
            if result == wx.adv.CAL_HITTEST_DAY:
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
        if event:
            event.Skip()
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

    # -- event handlers --------------------------------------------------------
    def start_select(self, event):
        event.Skip()
        self.selecting = True
        self.box_selected = []
        self.sel_start = (event.m_x, event.m_y)
        self.sel_end = self.sel_start

    def end_select(self, event):
        event.Skip()
        self.selecting = False
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
        dc = wx.PaintDC(self)

        if not self.selecting:
            return

        x = self.sel_start[0]
        y = self.sel_start[1]
        w = self.sel_end[0] - x
        h = self.sel_end[1] - y

        gc = wx.GraphicsContext.Create(dc)
        pen = gc.CreatePen(wx.BLACK_PEN)
        gc.SetPen(pen)

        points = [(x, y), (x + w, y), (x + w, y + h), (x, y + h), (x, y)]

        gc.DrawLines(points)

        brush = gc.CreateBrush(wx.Brush(MOUSE_BOX_FILL))
        gc.SetBrush(brush)
        gc.DrawRectangle(x, y, w, h)


class MultiCalendarCtrl(wx.Panel):
    """
    WX panel containing calendar widgets for use by the CustomEditor.

    Description
    -----------
    Handles multi-selection of dates by special handling of the
    wxMouseBoxCalendarCtrl widget.  Doing single-select across multiple
    calendar widgets is also supported though most of the interesting
    functionality is then unused.
    """

    def __init__(
        self,
        parent,
        ID,
        editor,
        multi_select,
        shift_to_select,
        on_mixed_select,
        allow_future,
        months,
        padding,
        *args,
        **kwargs,
    ):
        super().__init__(parent, ID, *args, **kwargs)

        self.sizer = wx.BoxSizer()
        self.SetSizer(self.sizer)
        self.SetBackgroundColour(WindowColor)
        self.date = wx.DateTime.Now()
        self.today = self.date_from_datetime(self.date)

        # Object attributes
        self.multi_select = multi_select
        self.shift_to_select = shift_to_select
        self.on_mixed_select = on_mixed_select
        self.allow_future = allow_future
        self.editor = editor
        self.selected_days = editor.value
        self.months = months
        self.padding = padding
        self.cal_ctrls = []

        # State to remember when a user is doing a shift-click selection.
        self._first_date = None
        self._drag_select = []
        self._box_select = []

        # Set up the individual month frames.
        for i in range(-(self.months - 1), 1):
            cal = self._make_calendar_widget(i)
            self.cal_ctrls.insert(0, cal)
            if i != 0:
                self.sizer.AddSpacer(padding)

        # Initial painting
        self.selected_list_changed()
        return

    def date_from_datetime(self, dt):
        """
        Convert a wx DateTime object to a Python Date object.

        Parameters
        ----------
        dt : wx.DateTime
            A valid date to convert to a Python Date object
        """
        new_date = datetime.date(dt.GetYear(), dt.GetMonth() + 1, dt.GetDay())
        return new_date

    def datetime_from_date(self, date):
        """
        Convert a Python Date object to a wx DateTime object. Ignores time.

        Parameters
        ----------
        date : datetime.Date object
            A valid date to convert to a wx.DateTime object.  Since there
            is no time information in a Date object the defaults of DateTime
            are used.
        """
        dt = wx.DateTime()
        dt.SetYear(date.year)
        dt.SetMonth(date.month - 1)
        dt.SetDay(date.day)
        return dt

    def shift_datetime(self, old_date, months):
        """
        Create a new DateTime from *old_date* with an offset number of *months*.

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

        new_day = min(old_date.GetDay(), 28)
        new_date.Set(new_day, new_month, new_year)
        return new_date

    def selected_list_changed(self, evt=None):
        """Update the date colors of the days in the widgets."""
        for cal in self.cal_ctrls:
            cur_month = cal.GetDate().GetMonth() + 1
            cur_year = cal.GetDate().GetYear()
            selected_days = self.selected_days

            # When multi_select is False wrap in a list to pass the for-loop.
            if not self.multi_select:
                if selected_days is None:
                    selected_days = []
                else:
                    selected_days = [selected_days]

            # Reset all the days to the correct colors.
            for day in range(1, 32):
                try:
                    paint_day = datetime.date(cur_year, cur_month, day)
                    if not self.allow_future and paint_day > self.today:
                        attr = wx.adv.CalendarDateAttr(colText=UNAVAILABLE_FG)
                        cal.SetAttr(day, attr)
                    elif paint_day in selected_days:
                        attr = wx.adv.CalendarDateAttr(colText=SELECTED_FG)
                        cal.SetAttr(day, attr)
                    else:
                        cal.ResetAttr(day)
                except ValueError:
                    # Blindly creating Date objects sometimes produces invalid.
                    pass

            cal.highlight_changed()
        return

    def _make_calendar_widget(self, month_offset):
        """
        Add a calendar widget to the screen and hook up callbacks.

        Parameters
        ----------
        month_offset : int
            The number of months from today, that the calendar should
            start at.
        """
        date = self.shift_datetime(self.date, month_offset)
        panel = wx.Panel(self, -1)
        cal = wxMouseBoxCalendarCtrl(
            panel,
            -1,
            date,
            style=wx.adv.CAL_SUNDAY_FIRST
            | wx.adv.CAL_SEQUENTIAL_MONTH_SELECTION
            # | wx.adv.CAL_SHOW_HOLIDAYS
        )
        self.sizer.Add(panel)
        cal.highlight_changed()

        # Set up control to sync the other calendar widgets and coloring:
        cal.Bind(wx.adv.EVT_CALENDAR_MONTH, self.month_changed)
        cal.Bind(wx.adv.EVT_CALENDAR_YEAR, self.month_changed)

        cal.Bind(wx.EVT_LEFT_DOWN, self._left_down)

        if self.multi_select:
            cal.Bind(wx.EVT_LEFT_UP, self._left_up)
            cal.Bind(wx.EVT_RIGHT_UP, self._process_box_select)
            cal.Bind(wx.EVT_LEAVE_WINDOW, self._process_box_select)
            cal.Bind(wx.EVT_MOTION, self._mouse_drag)
            self.Bind(
                wx.adv.EVT_CALENDAR_WEEKDAY_CLICKED,
                self._weekday_clicked,
                cal,
            )
        return cal

    def unhighlight_days(self, days):
        """
        Turn off all highlights in all cals, but leave any selected color.

        Parameters
        ----------
        days : List(Date)
            The list of dates to add.  Possibly includes dates in the future.
        """
        for cal in self.cal_ctrls:
            c = cal.GetDate()
            for date in days:
                if date.year == c.GetYear() and date.month == c.GetMonth() + 1:

                    # Unselected days either need to revert to the
                    # unavailable color, or the default attribute color.
                    if not self.allow_future and (
                        (date.year, date.month, date.day)
                        > (self.today.year, self.today.month, self.today.day)
                    ):
                        attr = wx.adv.CalendarDateAttr(colText=UNAVAILABLE_FG)
                    else:
                        attr = wx.adv.CalendarDateAttr(
                            colText=NORMAL_HIGHLIGHT_FG,
                            colBack=NORMAL_HIGHLIGHT_BG,
                        )
                    if date in self.selected_days:
                        attr.SetTextColour(SELECTED_FG)
                    cal.SetAttr(date.day, attr)
            cal.highlight_changed()
        return

    def highlight_days(self, days):
        """
        Color the highlighted list of days across all calendars.

        Parameters
        ----------
        days : List(Date)
            The list of dates to add.  Possibly includes dates in the future.
        """
        for cal in self.cal_ctrls:
            c = cal.GetDate()
            for date in days:
                if date.year == c.GetYear() and date.month == c.GetMonth() + 1:
                    attr = wx.adv.CalendarDateAttr(
                        colText=DRAG_HIGHLIGHT_FG, colBack=DRAG_HIGHLIGHT_BG
                    )
                    cal.SetAttr(date.day, attr)
            cal.highlight_changed()
            cal.Refresh()

    def add_days_to_selection(self, days):
        """
        Add a list of days to the selection, using a specified style.

        Parameters
        ----------
        days : List(Date)
            The list of dates to add.  Possibly includes dates in the future.

        Description
        -----------
        When a user multi-selects entries and some of those entries are
        already selected and some are not, what should be the behavior for
        the seletion? Options::

            'toggle'     -- Toggle each day to it's opposite state.
            'on'         -- Always turn them on.
            'off'        -- Always turn them off.
            'max_change' -- Change all to same state, with most days changing.
                            For example 1 selected and 9 not, then they would
                            all get selected.
            'min_change' -- Change all to same state, with min days changing.
                            For example 1 selected and 9 not, then they would
                            all get unselected.
        """
        if not days:
            return
        style = self.on_mixed_select
        new_list = list(self.selected_days)

        if style == "toggle":
            for day in days:
                if self.allow_future or day <= self.today:
                    if day in new_list:
                        new_list.remove(day)
                    else:
                        new_list.append(day)

        else:
            already_selected = len([day for day in days if day in new_list])

            if style == "on" or already_selected == 0:
                add_items = True

            elif style == "off" or already_selected == len(days):
                add_items = False

            elif self.on_mixed_select == "max_change" and already_selected <= (
                len(days) / 2.0
            ):
                add_items = True

            elif self.on_mixed_select == "min_change" and already_selected > (
                len(days) / 2.0
            ):
                add_items = True

            else:
                # Cases where max_change is off or min_change off.
                add_items = False

            for day in days:
                # Skip if we don't allow future, and it's a future day.
                if self.allow_future or day <= self.today:
                    if add_items and day not in new_list:
                        new_list.append(day)
                    elif not add_items and day in new_list:
                        new_list.remove(day)

        self.selected_days = new_list
        # Link the list back to the model to make a Traits List change event.
        self.editor.value = new_list
        return

    def single_select_day(self, dt):
        """
        In non-multiselect switch the selection to a new date.

        Parameters
        ----------
        dt : wx.DateTime
            The newly selected date that should become the new calendar
            selection.

        Description
        -----------
        Only called when we're using  the single-select mode of the
        calendar widget, so we can assume that the selected_dates is
        a None or a Date singleton.
        """
        selection = self.date_from_datetime(dt)

        if dt.IsValid() and (self.allow_future or selection <= self.today):
            self.selected_days = selection
            self.selected_list_changed()
            # Modify the trait on the editor so that the events propagate.
            self.editor.value = self.selected_days
            return

    def _shift_drag_update(self, event):
        """Shift-drag in progress."""
        cal = event.GetEventObject()
        result, dt, weekday = cal.HitTest(event.GetPosition())

        self.unhighlight_days(self._drag_select)
        self._drag_select = []

        # Prepare for an abort, don't highlight new selections.
        if (
            self.shift_to_select and not event.ShiftDown()
        ) or result != wx.adv.CAL_HITTEST_DAY:

            cal.highlight_changed()
            for cal in self.cal_ctrls:
                cal.Refresh()
            return

        # Construct the list of selections.
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
        return

    # ------------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------------

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
        """A day on the weekday bar has been clicked.  Select all days."""
        evt.Skip()
        weekday = evt.GetWeekDay()
        cal = evt.GetEventObject()
        month = cal.GetDate().GetMonth() + 1
        year = cal.GetDate().GetYear()

        days = []
        # Messy math to compute the dates of each weekday in the month.
        # Python uses Monday=0, while wx uses Sunday=0.
        month_start_weekday = (datetime.date(year, month, 1).weekday() + 1) % 7
        weekday_offset = (weekday - month_start_weekday) % 7
        for day in range(weekday_offset, 31, 7):
            try:
                day = datetime.date(year, month, day + 1)
                if self.allow_future or day <= self.today:
                    days.append(day)
            except ValueError:
                pass
        self.add_days_to_selection(days)

        self.selected_list_changed()
        return

    def _left_down(self, event):
        """Handle user selection of days."""
        event.Skip()
        cal = event.GetEventObject()
        result, dt, weekday = cal.HitTest(event.GetPosition())

        if result == wx.adv.CAL_HITTEST_DAY and not self.multi_select:
            self.single_select_day(dt)
            return

        # Inter-month-drag selection.  A quick no-movement mouse-click is
        # equivalent to a multi-select of a single day.
        if (
            result == wx.adv.CAL_HITTEST_DAY
            and (not self.shift_to_select or event.ShiftDown())
            and not cal.selecting
        ):

            self._first_date = self.date_from_datetime(dt)
            self._drag_select = [self._first_date]
            # Start showing the highlight colors with a mouse_drag event.
            self._mouse_drag(event)

        return

    def _left_up(self, event):
        """Handle the end of a possible run-selection."""
        event.Skip()
        cal = event.GetEventObject()
        result, dt, weekday = cal.HitTest(event.GetPosition())

        # Complete a drag-select operation.
        if (
            result == wx.adv.CAL_HITTEST_DAY
            and (not self.shift_to_select or event.ShiftDown())
            and self._first_date
        ):

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
            self.unhighlight_days(newly_selected)

        # Reset a drag-select operation, even if it wasn't completed because
        # of a loss of focus or the Shift key prematurely released.
        self._first_date = None
        self._drag_select = []

        self.selected_list_changed()
        return

    def _mouse_drag(self, event):
        """Called when the mouse in being dragged within the main panel."""
        event.Skip()
        cal = event.GetEventObject()
        if not cal.selecting and self._first_date:
            self._shift_drag_update(event)
        if cal.selecting:
            self.unhighlight_days(self._box_select)
            self._box_select = [
                self.date_from_datetime(dt) for dt in cal.boxed_days()
            ]
            self.highlight_days(self._box_select)
        return

    def month_changed(self, evt=None):
        """
        Link the calendars together so if one changes, they all change.

        TODO: Maybe wx.adv.CAL_HITTEST_INCMONTH could be checked and
        the event skipped, rather than now where we undo the update after
        the event has gone through.
        """
        evt.Skip()
        cal_index = self.cal_ctrls.index(evt.GetEventObject())
        current_date = self.cal_ctrls[cal_index].GetDate()
        for i, cal in enumerate(self.cal_ctrls):
            # Current month is already updated, just need to shift the others
            if i != cal_index:
                new_date = self.shift_datetime(current_date, cal_index - i)
                cal.SetDate(new_date)
                cal.highlight_changed()

        # Back-up if we're not allowed to move into future months.
        if not self.allow_future:
            month = self.cal_ctrls[0].GetDate().GetMonth() + 1
            year = self.cal_ctrls[0].GetDate().GetYear()
            if (year, month) > (self.today.year, self.today.month):
                for i, cal in enumerate(self.cal_ctrls):
                    new_date = self.shift_datetime(wx.DateTime.Now(), -i)
                    cal.SetDate(new_date)
                    cal.highlight_changed()

        # Redraw the selected days.
        self.selected_list_changed()


class CustomEditor(Editor):
    """
    Show multiple months with MultiCalendarCtrl. Allow multi-select.

    Trait Listeners
    ---------------
    The wx editor directly modifies the *value* trait of the Editor, which
    is the named trait of the corresponding Item in your View.  Therefore
    you can listen for changes to the user's selection by directly listening
    to the item changed event.

    TODO
    ----
    Some more listeners need to be hooked up.  For example, in single-select
    mode, changing the value does not cause the calendar to update.  Also,
    the selection-add and remove is noisy, triggering an event for each
    addition rather than waiting until everything has been added and removed.

    Sample
    ------
    Example usage::

        class DateListPicker(HasTraits):
            calendar = List()
            traits_view = View(Item('calendar', editor=DateEditor(),
                                    style='custom', show_label=False))
    """

    # -- Editor interface ------------------------------------------------------

    def init(self, parent):
        """
        Finishes initializing the editor by creating the underlying widget.
        """
        if self.factory.multi_select and not isinstance(self.value, list):
            raise ValueError("Multi-select is True, but editing a non-list.")
        elif not self.factory.multi_select and isinstance(self.value, list):
            raise ValueError("Multi-select is False, but editing a list.")

        calendar_ctrl = MultiCalendarCtrl(
            parent,
            -1,
            self,
            self.factory.multi_select,
            self.factory.shift_to_select,
            self.factory.on_mixed_select,
            self.factory.allow_future,
            self.factory.months,
            self.factory.padding,
        )
        self.control = calendar_ctrl
        return

    def update_editor(self):
        """
        Updates the editor when the object trait changes externally to the
        editor.
        """
        self.control.selected_list_changed()
        return


# TODO: Write me.  Possibly use TextEditor as a model to show a string
# representation of the date, and have enter-set do a date evaluation.
class TextEditor(SimpleEditor):
    pass


class ReadonlyEditor(TextReadonlyEditor):
    """Use a TextEditor for the view."""

    def _get_str_value(self):
        """Replace the default string value with our own date verision."""
        if not self.value:
            return self.factory.message
        else:
            return self.value.strftime(self.factory.strftime)
