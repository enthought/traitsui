# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Defines constants used by the wxPython implementation of the various text
    editors and text editor factories.
"""

import sys

import wx

from pyface.api import SystemMetrics

#: Define platform and wx version constants:
is_mac = sys.platform == "darwin"
is_dark = wx.SystemSettings.GetAppearance().IsDark()

#: Default dialog title
DefaultTitle = "Edit properties"

#: Color of valid input
OKColor = wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW)

#: Color to highlight input errors
if is_dark:
    ErrorColor = wx.Colour(0xcf, 0x66, 0x79)
else:
    ErrorColor = wx.Colour(255, 192, 192)


#: Color for background of read-only fields
if is_dark:
    ReadonlyColor = wx.Colour(22, 22, 24)
else:
    ReadonlyColor = wx.Colour(244, 243, 238)

#: Color for background of fields where objects can be dropped
if is_dark:
    DropColor = wx.Colour(94, 131, 167)
else:
    DropColor = wx.Colour(215, 242, 255)

#: Color for an editable field
EditableColor = OKColor

#: Color for background of windows (like dialog background color)
if is_mac:
    WindowColor = wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW)
else:
    WindowColor = wx.SystemSettings.GetColour(wx.SYS_COLOUR_MENUBAR)

#: Default colour for table foreground
if is_dark:
    TableCellColor = wx.WHITE
else:
    TableCellColor = wx.BLACK

#: Default colour for table background
TableCellBackgroundColor = OKColor

#: Default colour for table background
TableReadOnlyBackgroundColor = ReadonlyColor

#: Default colour for table background
TableLabelColor = TableCellColor

#: Default colour for table background
TableLabelBackgroundColor = WindowColor

#: Default foreground colour for table selection
TableSelectionTextColor = TableCellColor

#: Default background colour for table selection
TableSelectionBackgroundColor = wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHT)

#: Standard width of an image bitmap
standard_bitmap_width = 120

#: Width of a scrollbar
scrollbar_dx = wx.SystemSettings.GetMetric(wx.SYS_VSCROLL_X)

#: Screen width
screen_dx = SystemMetrics().screen_width

#: Screen height
screen_dy = SystemMetrics().screen_height
