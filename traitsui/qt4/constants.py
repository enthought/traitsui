# (C) Copyright 2008-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

# ------------------------------------------------------------------------------
# Copyright (c) 2007, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD license.
# However, when used with the GPL version of PyQt the additional terms
# described in the PyQt GPL exception also apply

#
# Author: Riverbank Computing Limited
# ------------------------------------------------------------------------------

""" Defines constants used by the PyQt implementation of the various text
editors and text editor factories.
"""


from pyface.qt import QtGui

from pyface.api import SystemMetrics

_palette = QtGui.QApplication.palette()

# Default dialog title
DefaultTitle = "Edit properties"

# Color of valid input
OKColor = _palette.color(QtGui.QPalette.Base)

# Color to highlight input errors
ErrorColor = QtGui.QColor(255, 192, 192)

# Color for background of read-only fields
ReadonlyColor = QtGui.QColor(244, 243, 238)

# Color for background of fields where objects can be dropped
DropColor = QtGui.QColor(215, 242, 255)

# Color for an editable field
EditableColor = _palette.color(QtGui.QPalette.Base)

# Color for background of windows (like dialog background color)
WindowColor = _palette.color(QtGui.QPalette.Window)

del _palette

#: Screen width
screen_dx = SystemMetrics().screen_width

#: Screen height
screen_dy = SystemMetrics().screen_height
