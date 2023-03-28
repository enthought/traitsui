# (C) Copyright 2008-2023 Enthought, Inc., Austin, TX
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

""" Defines a subclass of the base PyQt color editor factory, for colors
that are represented as tuples of the form ( *red*, *green*, *blue* ), where
*red*, *green* and *blue* are floats in the range from 0.0 to 1.0.
"""


from pyface.qt import QtGui

from traits.trait_base import SequenceTypes

# Note: The ToolkitEditorFactory class imported from color_editor is a
# subclass of the abstract ToolkitEditorFactory class
# (in traitsui.api) with qt-specific methods defined.
# We need to override the implementations of the qt-specific methods here.
from .color_editor import ToolkitEditorFactory as BaseColorToolkitEditorFactory

# -------------------------------------------------------------------------
#  The PyQt4 ToolkitEditorFactory class.
# -------------------------------------------------------------------------


class ToolkitEditorFactory(BaseColorToolkitEditorFactory):
    """PyQt editor factory for color editors."""

    def to_qt_color(self, editor):
        """Gets the PyQt color equivalent of the object trait."""
        try:
            color = getattr(editor.object, editor.name + "_")
        except AttributeError:
            color = getattr(editor.object, editor.name)

        c = QtGui.QColor()
        c.setRgbF(color[0], color[1], color[2])

        return c

    def from_qt_color(self, color):
        """Gets the application equivalent of a PyQt value."""
        return (color.redF(), color.greenF(), color.blueF())

    def str_color(self, color):
        """Returns the text representation of a specified color value."""
        if type(color) in SequenceTypes:
            return "(%d,%d,%d)" % (
                int(color[0] * 255.0),
                int(color[1] * 255.0),
                int(color[2] * 255.0),
            )
        return color
