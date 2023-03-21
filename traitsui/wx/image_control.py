# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Defines a wxPython ImageControl widget that is used by various trait
    editors to display trait values iconically.
"""


import wx


class ImageControl(wx.Window):
    """A wxPython control that displays an image, which can be selected or
    unselected by mouse clicks.
    """

    #: Pens used to draw the 'selection' marker:
    _selectedPenDark = wx.Pen(
        wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DSHADOW), 1, wx.SOLID
    )

    _selectedPenLight = wx.Pen(
        wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DHIGHLIGHT), 1, wx.SOLID
    )

    def __init__(
        self, parent, bitmap, selected=None, handler=None, padding=10
    ):
        """Initializes the object."""
        if bitmap is not None:
            size = wx.Size(
                bitmap.GetWidth() + padding, bitmap.GetHeight() + padding
            )
        else:
            size = wx.Size(32 + padding, 32 + padding)

        wx.Window.__init__(self, parent, -1, size=size,)
        self._bitmap = bitmap
        self._selected = selected
        self._handler = handler
        self._mouse_over = False
        self._button_down = False

        # Set up the 'paint' event handler:
        self.Bind(wx.EVT_PAINT, self._on_paint)

        # Set up mouse event handlers:
        self.Bind(wx.EVT_LEFT_DOWN, self._on_left_down)
        self.Bind(wx.EVT_LEFT_UP, self._on_left_up)
        self.Bind(wx.EVT_ENTER_WINDOW, self._on_enter)
        self.Bind(wx.EVT_LEAVE_WINDOW, self._on_leave)

    def Selected(self, selected=None):
        """Gets or sets the selection state of the image."""
        if selected is not None:
            selected = selected != 0
            if selected != self._selected:
                if selected:
                    for control in self.GetParent().GetChildren():
                        if (
                            isinstance(control, ImageControl)
                            and control.Selected()
                        ):
                            control.Selected(False)
                            break

                self._selected = selected
                self.Refresh()

        return self._selected

    def Bitmap(self, bitmap=None):
        """Gets or sets the bitmap image."""
        if bitmap is not None:
            if bitmap != self._bitmap:
                self._bitmap = bitmap
                self.Refresh()
        else:
            self._bitmap = None

        return self._bitmap

    def Handler(self, handler=None):
        """Gets or sets the click handler."""
        if handler is not None:
            if handler != self._handler:
                self._handler = handler
                self.Refresh()

        return self._handler

    def _on_enter(self, event=None):
        """Handles the mouse entering the control."""
        if self._selected is not None:
            self._mouse_over = True
            self.Refresh()

    def _on_leave(self, event=None):
        """Handles the mouse leaving the control."""
        if self._mouse_over:
            self._mouse_over = False
            self.Refresh()

    def _on_left_down(self, event=None):
        """Handles the user pressing the mouse button."""
        if self._selected is not None:
            self.CaptureMouse()
            self._button_down = True
            self.Refresh()

    def _on_left_up(self, event=None):
        """Handles the user clicking the control."""
        need_refresh = self._button_down
        if need_refresh:
            self.ReleaseMouse()
            self._button_down = False

        if self._selected is not None:
            wdx, wdy = self.GetClientSize()
            x = event.GetX()
            y = event.GetY()
            if (0 <= x < wdx) and (0 <= y < wdy):
                if self._selected != -1:
                    self.Selected(True)
                elif need_refresh:
                    self.Refresh()
                if self._handler is not None:
                    wx.CallAfter(self._handler, self)
                return

        if need_refresh:
            self.Refresh()

    def _on_paint(self, event=None):
        """Handles the control being re-painted."""
        wdc = wx.PaintDC(self)
        wdx, wdy = self.GetClientSize()
        bitmap = self._bitmap
        if bitmap is None:
            return
        bdx = bitmap.GetWidth()
        bdy = bitmap.GetHeight()
        wdc.DrawBitmap(bitmap, (wdx - bdx) // 2, (wdy - bdy) // 2, True)

        pens = [self._selectedPenLight, self._selectedPenDark]
        bd = self._button_down

        if self._mouse_over:
            wdc.SetBrush(wx.TRANSPARENT_BRUSH)
            wdc.SetPen(pens[bd])
            wdc.DrawLine(0, 0, wdx, 0)
            wdc.DrawLine(0, 1, 0, wdy)
            wdc.SetPen(pens[1 - bd])
            wdc.DrawLine(wdx - 1, 1, wdx - 1, wdy)
            wdc.DrawLine(1, wdy - 1, wdx - 1, wdy - 1)

        if self._selected is True:
            wdc.SetBrush(wx.TRANSPARENT_BRUSH)
            wdc.SetPen(pens[bd])
            wdc.DrawLine(1, 1, wdx - 1, 1)
            wdc.DrawLine(1, 1, 1, wdy - 1)
            wdc.DrawLine(2, 2, wdx - 2, 2)
            wdc.DrawLine(2, 2, 2, wdy - 2)
            wdc.SetPen(pens[1 - bd])
            wdc.DrawLine(wdx - 2, 2, wdx - 2, wdy - 1)
            wdc.DrawLine(2, wdy - 2, wdx - 2, wdy - 2)
            wdc.DrawLine(wdx - 3, 3, wdx - 3, wdy - 2)
            wdc.DrawLine(3, wdy - 3, wdx - 3, wdy - 3)
