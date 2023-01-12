# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Defines a subclass of the base wxPython color editor factory, for colors
    that are represented as tuples of the form ( *red*, *green*, *blue* ),
    where *red*, *green* and *blue* are floats in the range from 0.0 to 1.0.
"""


import wx

from traits.trait_base import SequenceTypes

# Note: The ToolkitEditorFactory class imported from color_editor is the
# abstract ToolkitEditorFactory class (in traitsui.api) along with
# wx-specific methods added via a category. We need to override the
# implementations of the wx-specific methods here.
from .color_editor import ToolkitEditorFactory as BaseColorToolkitEditorFactory

# ---------------------------------------------------------------------------
#  The wxPython ToolkitEditorFactory class.
# ---------------------------------------------------------------------------


class ToolkitEditorFactory(BaseColorToolkitEditorFactory):
    """wxPython editor factory for color editors."""

    def to_wx_color(self, editor, color=None):
        """Gets the wxPython color equivalent of the object trait."""
        if color is None:
            try:
                color = getattr(editor.object, editor.name + "_")
            except AttributeError:
                color = getattr(editor.object, editor.name)
        if isinstance(color, tuple):
            return wx.Colour(
                int(color[0] * 255.0),
                int(color[1] * 255.0),
                int(color[2] * 255.0),
            )
        return color

    def from_wx_color(self, color):
        """Gets the application equivalent of a wxPython value."""
        return (
            color.Red() / 255.0,
            color.Green() / 255.0,
            color.Blue() / 255.0,
        )

    def str_color(self, color):
        """Returns the text representation of a specified color value."""
        if type(color) in SequenceTypes:
            return "(%d,%d,%d)" % (
                int(color[0] * 255.0),
                int(color[1] * 255.0),
                int(color[2] * 255.0),
            )
        return super().str_color(color)
