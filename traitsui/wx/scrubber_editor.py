# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Traits UI simple, scrubber-based integer or float value editor.
"""


import wx

from math import log10, pow

from traits.api import (
    Any,
    BaseRange,
    BaseEnum,
    Str,
    Float,
    TraitError,
    observe,
)

from traitsui.api import View, Item, EnumEditor

# FIXME: ScrubberEditor is a proxy class defined here just for backward
# compatibility (represents the editor factory for scrubber editors).
# The class has been moved to traitsui.editors.scrubber_editor
from traitsui.editors.scrubber_editor import ScrubberEditor

from traitsui.wx.editor import Editor

from pyface.timer.api import do_after

from .constants import ErrorColor

from .image_slice import paint_parent

from .helper import disconnect, disconnect_no_id, BufferDC


class _ScrubberEditor(Editor):
    """Traits UI simple, scrubber-based integer or float value editor."""

    #: The low end of the slider range:
    low = Any()

    #: The high end of the slider range:
    high = Any()

    #: The smallest allowed increment:
    increment = Float()

    #: The current text being displayed:
    text = Str()

    #: The mapping to use (only for Enum's):
    mapping = Any()

    # -- Class Variables ------------------------------------------------------

    text_styles = {
        "left": wx.TE_LEFT,
        "center": wx.TE_CENTRE,
        "right": wx.TE_RIGHT,
    }

    def init(self, parent):
        """Finishes initializing the editor by creating the underlying toolkit
        widget.
        """
        factory = self.factory

        # Establish the range of the slider:
        low_name = high_name = ""
        low, high = factory.low, factory.high
        if high <= low:
            low = high = None
            handler = self.object.trait(self.name).handler
            if isinstance(handler, BaseRange):
                low_name, high_name = handler._low_name, handler._high_name

                if low_name == "":
                    low = handler._low

                if high_name == "":
                    high = handler._high

            elif isinstance(handler, BaseEnum):
                if handler.name == "":
                    self.mapping = handler.values
                else:
                    self.sync_value(handler.name, "mapping", "from")

                low, high = 0, self.high

        # Create the control:
        self.control = control = wx.Window(
            parent,
            -1,
            size=wx.Size(50, 18),
            style=wx.FULL_REPAINT_ON_RESIZE | wx.TAB_TRAVERSAL,
        )

        # Set up the painting event handlers:
        control.Bind(wx.EVT_ERASE_BACKGROUND, self._erase_background)
        control.Bind(wx.EVT_PAINT, self._on_paint)
        control.Bind(wx.EVT_SET_FOCUS, self._set_focus)

        # Set up mouse event handlers:
        control.Bind(wx.EVT_LEAVE_WINDOW, self._leave_window)
        control.Bind(wx.EVT_ENTER_WINDOW, self._enter_window)
        control.Bind(wx.EVT_LEFT_DOWN, self._left_down)
        control.Bind(wx.EVT_LEFT_UP, self._left_up)
        control.Bind(wx.EVT_MOTION, self._motion)
        control.Bind(wx.EVT_MOUSEWHEEL, self._mouse_wheel)

        # Set up the control resize handler:
        control.Bind(wx.EVT_SIZE, self._resize)

        # Set the tooltip:
        self._can_set_tooltip = not self.set_tooltip()

        # Save the values we calculated:
        self.trait_set(low=low, high=high)
        self.sync_value(low_name, "low", "from")
        self.sync_value(high_name, "high", "from")

        # Force a reset (in case low = high = None, which won't cause a
        # notification to fire):
        self._reset_scrubber()

    def dispose(self):
        """Disposes of the contents of an editor."""
        # Remove all of the wx event handlers:
        disconnect_no_id(
            self.control,
            wx.EVT_ERASE_BACKGROUND,
            wx.EVT_PAINT,
            wx.EVT_SET_FOCUS,
            wx.EVT_LEAVE_WINDOW,
            wx.EVT_ENTER_WINDOW,
            wx.EVT_LEFT_DOWN,
            wx.EVT_LEFT_UP,
            wx.EVT_MOTION,
            wx.EVT_MOUSEWHEEL,
            wx.EVT_SIZE,
        )

        # Disconnect the pop-up text event handlers:
        self._disconnect_text()

        super().dispose()

    def update_editor(self):
        """Updates the editor when the object trait changes externally to the
        editor.
        """
        self.text = self.string_value(self.value)
        self._text_size = None
        self._refresh()

        self._enum_completed()

    def update_object(self, value):
        """Updates the object when the scrubber value changes."""
        if self.mapping is not None:
            value = self.mapping[int(value)]

        if value != self.value:
            try:
                self.value = value
                self.update_editor()
            except TraitError:
                value = int(value)
                if value != self.value:
                    self.value = value
                    self.update_editor()

    def error(self, excp):
        """Handles an error that occurs while setting the object's trait value."""
        pass

    # -- Trait Event Handlers -------------------------------------------------

    def _mapping_changed(self, mapping):
        """Handles the Enum mapping being changed."""
        self.high = len(mapping) - 1

    # -- Private Methods ------------------------------------------------------

    @observe("low, high")
    def _reset_scrubber(self, event=None):
        """Sets the the current tooltip."""
        low, high = self.low, self.high
        if self._can_set_tooltip:
            if self.mapping is not None:
                tooltip = "[%s]" % (", ".join(self.mapping))
                if len(tooltip) > 80:
                    tooltip = ""
            elif high is None:
                tooltip = ""
                if low is not None:
                    tooltip = "[%g..]" % low
            elif low is None:
                tooltip = "[..%g]" % high
            else:
                tooltip = "[%g..%g]" % (low, high)

            self.control.SetToolTip(tooltip)

        # Establish the slider increment:
        increment = self.factory.increment
        if increment <= 0.0:
            if (low is None) or (high is None) or isinstance(low, int):
                increment = 1.0
            else:
                increment = pow(10, round(log10((high - low) / 100.0)))

        self.increment = increment

        self.update_editor()

    def _get_text_bounds(self):
        """Get the window bounds of where the current text should be
        displayed.
        """
        tdx, tdy, descent, leading = self._get_text_size()
        wdx, wdy = self.control.GetClientSize()
        ty = ((wdy - (tdy - descent)) // 2) - 1
        alignment = self.factory.alignment
        if alignment == "left":
            tx = 0
        elif alignment == "center":
            tx = (wdx - tdx) // 2
        else:
            tx = wdx - tdx

        return (tx, ty, tdx, tdy)

    def _get_text_size(self):
        """Returns the text size information for the window."""
        if self._text_size is None:
            self._text_size = self.control.GetFullTextExtent(
                self.text.strip() or "M"
            )

        return self._text_size

    def _refresh(self):
        """Refreshes the contents of the control."""
        if self.control is not None:
            self.control.Refresh()

    def _set_scrubber_position(self, event, delta):
        """Calculates a new scrubber value for a specified mouse position
        change.
        """
        clicks = 3
        increment = self.increment
        if event.ShiftDown():
            increment *= 10.0
            clicks = 7
        elif event.ControlDown():
            increment /= 10.0

        value = self._value + (delta / clicks) * increment

        if self.low is not None:
            value = max(value, self.low)

        if self.high is not None:
            value = min(value, self.high)

        self.update_object(value)

    def _delayed_click(self):
        """Handle a delayed click response."""
        self._pending = False

    def _pop_up_editor(self):
        """Pop-up a text control to allow the user to enter a value using
        the keyboard.
        """
        self.control.SetCursor(wx.Cursor(wx.CURSOR_ARROW))

        if self.mapping is not None:
            self._pop_up_enum()
        else:
            self._pop_up_text()

    def _pop_up_enum(self):
        self._ui = self.object.edit_traits(
            view=View(
                Item(
                    self.name,
                    id="drop_down",
                    show_label=False,
                    padding=-4,
                    editor=EnumEditor(name="editor.mapping"),
                ),
                kind="subpanel",
            ),
            parent=self.control,
            context={"object": self.object, "editor": self},
        )

        dx, dy = self.control.GetSize()
        drop_down = self._ui.info.drop_down.control
        drop_down.SetSize(0, 0, dx, dy)
        drop_down.SetFocus()
        drop_down.Bind(wx.EVT_KILL_FOCUS, self._enum_completed)

    def _pop_up_text(self):
        control = self.control
        self._text = text = wx.TextCtrl(
            control,
            -1,
            str(self.value),
            size=control.GetSize(),
            style=self.text_styles[self.factory.alignment]
            | wx.TE_PROCESS_ENTER,
        )
        text.SetSelection(-1, -1)
        text.SetFocus()
        control.Bind(wx.EVT_TEXT_ENTER, self._text_completed, id=text.GetId())
        text.Bind(wx.EVT_ENTER_WINDOW, self._enter_text)
        text.Bind(wx.EVT_LEAVE_WINDOW, self._leave_text)
        text.Bind(wx.EVT_CHAR, self._key_entered)

    def _destroy_text(self):
        """Destroys the current text control."""
        self._ignore_focus = self._in_text_window

        self._disconnect_text()

        self.control.DestroyChildren()

        self._text = None

    def _disconnect_text(self):
        """Disconnects the event handlers for the pop up text editor."""
        if self._text is not None:
            disconnect(self._text, wx.EVT_TEXT_ENTER)
            disconnect_no_id(
                self._text,
                wx.EVT_KILL_FOCUS,
                wx.EVT_ENTER_WINDOW,
                wx.EVT_LEAVE_WINDOW,
                wx.EVT_CHAR,
            )

    def _init_value(self):
        """Initializes the current value when the user begins a drag or moves
        the mouse wheel.
        """
        if self.mapping is not None:
            try:
                self._value = list(self.mapping).index(self.value)
            except:
                self._value = 0
        else:
            self._value = self.value

    # --- wxPython Event Handlers ---------------------------------------------

    def _erase_background(self, event):
        """Do not erase the background here (do it in the 'on_paint' handler)."""
        pass

    def _on_paint(self, event):
        """Paint the background using the associated ImageSlice object."""
        control = self.control
        dc = BufferDC(control)

        # Draw the background:
        factory = self.factory
        color = factory.color_
        if self._x is not None:
            if factory.active_color_ is not None:
                color = factory.active_color_
        elif self._hover:
            if factory.hover_color_ is not None:
                color = factory.hover_color_

        if color is None:
            paint_parent(dc, control)
            brush = wx.TRANSPARENT_BRUSH
        else:
            brush = wx.Brush(color)

        color = factory.border_color_
        if color is not None:
            pen = wx.Pen(color)
        else:
            pen = wx.TRANSPARENT_PEN

        if (pen != wx.TRANSPARENT_PEN) or (brush != wx.TRANSPARENT_BRUSH):
            wdx, wdy = control.GetClientSize()
            dc.SetBrush(brush)
            dc.SetPen(pen)
            dc.DrawRectangle(0, 0, wdx, wdy)

        # Draw the current text value:
        dc.SetBackgroundMode(wx.TRANSPARENT)
        dc.SetTextForeground(factory.text_color_)
        dc.SetFont(control.GetFont())
        tx, ty, tdx, tdy = self._get_text_bounds()
        dc.DrawText(self.text, tx, ty)

        # Copy the buffer contents to the display:
        dc.copy()

    def _resize(self, event):
        """Handles the control being resized."""
        if self._text is not None:
            self._text.SetSize(self.control.GetSize())

    def _set_focus(self, event):
        """Handle the control getting the keyboard focus."""
        if (
            (not self._ignore_focus)
            and (self._x is None)
            and (self._text is None)
        ):
            self._pop_up_editor()
        event.Skip()

    def _enter_window(self, event):
        """Handles the mouse entering the window."""
        self._hover = True

        self.control.SetCursor(wx.Cursor(wx.CURSOR_HAND))

        if not self._ignore_focus:
            self._ignore_focus = True
            self.control.SetFocus()
        self._ignore_focus = False

        if self._x is not None:
            if self.factory.active_color_ != self.factory.color_:
                self.control.Refresh()
        elif self.factory.hover_color_ != self.factory.color_:
            self.control.Refresh()

    def _leave_window(self, event):
        """Handles the mouse leaving the window."""
        self._hover = False

        if self.factory.hover_color_ != self.factory.color_:
            self.control.Refresh()

    def _left_down(self, event):
        """Handles the left mouse being pressed."""
        self._x, self._y = event.GetX(), event.GetY()
        self._pending = True

        self._init_value()

        self.control.CaptureMouse()

        if self.factory.active_color_ != self.factory.hover_color_:
            self.control.Refresh()

        do_after(200, self._delayed_click)

    def _left_up(self, event):
        """Handles the left mouse button being released."""
        self.control.ReleaseMouse()
        if self._pending:
            self._pop_up_editor()

        self._x = self._y = self._value = self._pending = None

        if self._hover or (self.factory.active_color_ != self.factory.color_):
            self.control.Refresh()

    def _motion(self, event):
        """Handles the mouse moving."""
        if self._x is not None:
            x, y = event.GetX(), event.GetY()
            dx = x - self._x
            adx = abs(dx)
            dy = y - self._y
            ady = abs(dy)
            if self._pending:
                if (adx + ady) < 3:
                    return
                self._pending = False

            if adx > ady:
                delta = dx
            else:
                delta = -dy

            self._set_scrubber_position(event, delta)

    def _mouse_wheel(self, event):
        """Handles the mouse wheel moving."""
        if self._hover:
            self._init_value()
            clicks = 3
            if event.ShiftDown():
                clicks = 7
            delta = clicks * (
                event.GetWheelRotation() // event.GetWheelDelta()
            )
            self._set_scrubber_position(event, delta)

    def _update_value(self, event):
        """Updates the object value from the current text control value."""
        control = event.GetEventObject()
        try:
            self.update_object(float(control.GetValue()))

            return True

        except TraitError:
            control.SetBackgroundColour(ErrorColor)
            control.Refresh()

            return False

    def _enter_text(self, event):
        """Handles the mouse entering the pop-up text control."""
        self._in_text_window = True

    def _leave_text(self, event):
        """Handles the mouse leaving the pop-up text control."""
        self._in_text_window = False

    def _text_completed(self, event):
        """Handles the user pressing the 'Enter' key in the text control."""
        if isinstance(event, wx.FocusEvent):
            event.Skip()
        if self._update_value(event):
            self._destroy_text()

    def _enum_completed(self, event=None):
        """Handles the Enum drop-down control losing focus."""
        if self._ui is not None:
            self._ignore_focus = True
            disconnect_no_id(
                self._ui.info.drop_down.control, wx.EVT_KILL_FOCUS
            )
            self._ui.dispose()
            del self._ui

    def _key_entered(self, event):
        """Handles individual key strokes while the text control is active."""
        key_code = event.GetKeyCode()
        if key_code == wx.WXK_ESCAPE:
            self._destroy_text()
            return

        if key_code == wx.WXK_TAB:
            if self._update_value(event):
                if event.ShiftDown():
                    self.control.Navigate(0)
                else:
                    self.control.Navigate()
            return

        event.Skip()
