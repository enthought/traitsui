# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Defines the various color editors for the Wx user interface toolkit.
"""


import sys

import wx
import wx.adv

from traits.api import List, TraitError
from traitsui.editors.color_editor import (
    ToolkitEditorFactory as BaseToolkitEditorFactory,
)

from .editor_factory import SimpleEditor as BaseSimpleEditor
from .editor_factory import ReadonlyEditor as BaseReadonlyEditor
from .editor_factory import TextEditor as BaseTextEditor

from .color_trait import w3c_color_database
from .helper import TraitsUIPanel


ColorTypes = (wx.Colour,)


# ---------------------------------------------------------------------------
#  The Wx ToolkitEditorFactory class.
# ---------------------------------------------------------------------------


class ToolkitEditorFactory(BaseToolkitEditorFactory):
    """Wx editor factory for color editors."""

    def to_wx_color(self, editor, color=None):
        """Gets the wxPython color equivalent of the object trait."""
        if color is None:
            if self.mapped:
                color = getattr(editor.object, editor.name + "_")
            else:
                color = getattr(editor.object, editor.name)

        if isinstance(color, tuple):
            color = wx.Colour(*[int(round(c * 255.0)) for c in color])
        return color

    def from_wx_color(self, color):
        """Gets the application equivalent of a wxPython value."""
        return color.Red(), color.Green(), color.Blue()

    def str_color(self, color):
        """Returns the text representation of a specified color value."""
        if isinstance(color, ColorTypes):
            alpha = color.Alpha()
            if alpha == 255:
                return "rgb(%d,%d,%d)" % (
                    color.Red(),
                    color.Green(),
                    color.Blue(),
                )

            return "rgba(%d,%d,%d,%d)" % (
                color.Red(),
                color.Green(),
                color.Blue(),
                alpha,
            )

        return str(color)


# ------------------------------------------------------------------------------
#  'ColorComboBox' class:
# ------------------------------------------------------------------------------


class ColorComboBox(wx.adv.OwnerDrawnComboBox):
    def OnDrawItem(self, dc, rect, item, flags):

        r = wx.Rect(rect.x, rect.y, rect.width, rect.height)
        r.Deflate(3, 0)
        swatch_size = r.height - 2

        color_name = self.GetString(item)

        dc.DrawText(
            color_name, r.x + 3, r.y + (r.height - dc.GetCharHeight()) // 2
        )

        if color_name == "custom":
            swatch = wx.Rect(
                r.x + r.width - swatch_size, r.y + 1, swatch_size, swatch_size
            )
            dc.GradientFillLinear(
                swatch, wx.Colour(255, 255, 0), wx.Colour(0, 0, 255)
            )
        else:
            color = w3c_color_database.Find(color_name)

            brush = wx.Brush(color)
            dc.SetBrush(brush)
            dc.DrawRectangle(
                r.x + r.width - swatch_size, r.y + 1, swatch_size, swatch_size
            )


# ------------------------------------------------------------------------------
#  'SimpleColorEditor' class:
# ------------------------------------------------------------------------------


class SimpleColorEditor(BaseSimpleEditor):
    """Simple style of color editor, which displays a text field whose
    background color is the color value. Selecting the text field displays
    a dialog box for selecting a new color value.
    """

    # --------------------------------------------------------------------------
    #  Invokes the pop-up editor for an object trait:
    # --------------------------------------------------------------------------

    choices = List()

    def _choices_default(self):
        """by default, uses the W3C 16 color names."""
        return [
            "aqua",
            "black",
            "blue",
            "fuchsia",
            "gray",
            "green",
            "lime",
            "maroon",
            "navy",
            "olive",
            "purple",
            "red",
            "silver",
            "teal",
            "white",
            "yellow",
            "custom",
        ]

    def init(self, parent):
        """
        Finishes initializing the editor by creating the underlying widget.
        """
        current_color = self.factory.to_wx_color(self)
        current_color_name = current_color.GetAsString()

        self.control = ColorComboBox(
            parent,
            -1,
            current_color_name,
            wx.Point(0, 0),
            wx.Size(40, -1),
            self.choices,
            style=wx.CB_READONLY,
        )

        self.control.Bind(wx.EVT_COMBOBOX, self.color_selected)

    def dispose(self):
        if self.control is not None:
            self.control.Unbind(wx.EVT_COMBOBOX, handler=self.color_selected)
        super().dispose()

    def update_editor(self):
        """Updates the editor when the object trait changes externally to the
        editor.
        """
        current_color = self.factory.to_wx_color(self)
        self.control.SetValue(self.string_value(current_color))

    def color_selected(self, event):
        """
        Event for when color is selected
        """

        color_name = self.choices[event.Selection]

        if color_name == "custom":
            color_dialog = wx.ColourDialog(self.control)
            result = color_dialog.ShowModal()
            if result == wx.ID_CANCEL:
                return

            color = color_dialog.GetColourData().GetColour()
            self.value = self.factory.from_wx_color(color)
        else:
            try:
                color = w3c_color_database.Find(color_name)
                self.value = self.factory.from_wx_color(color)
            except ValueError:
                pass

        return

    def string_value(self, color):
        """Returns the text representation of a specified color value."""
        color_name = w3c_color_database.FindName(color)
        if color_name != "":
            return color_name

        return color.GetAsString()


# ------------------------------------------------------------------------------
#  'CustomColorEditor' class:
# ------------------------------------------------------------------------------


class CustomColorEditor(BaseSimpleEditor):
    """Simple style of color editor, which displays a text field whose
    background color is the color value. Selecting the text field displays
    a dialog box for selecting a new color value.
    """

    def init(self, parent):
        """
        Finishes initializing the editor by creating the underlying widget.
        """
        self.control = self._panel = parent = TraitsUIPanel(parent, -1)
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        # 'text_control' is the text display of the color.
        text_control = wx.TextCtrl(
            parent, -1, self.str_value, style=wx.TE_PROCESS_ENTER
        )
        text_control.Bind(wx.EVT_KILL_FOCUS, self.update_object)
        parent.Bind(
            wx.EVT_TEXT_ENTER, self.update_object, id=text_control.GetId()
        )

        # 'button_control' shows the 'Edit' button.
        button_control = wx.Button(parent, label="Edit", style=wx.BU_EXACTFIT)
        button_control.Bind(
            wx.EVT_BUTTON, self.open_color_dialog, id=button_control.GetId()
        )

        sizer.Add(text_control, wx.ALIGN_LEFT)
        sizer.AddSpacer(8)
        sizer.Add(button_control, wx.ALIGN_RIGHT)
        self.control.SetSizer(sizer)

        self._text_control = text_control
        self._button_control = button_control

        self.set_tooltip()

        return

    def update_object(self, event):
        """Handles the user changing the contents of the edit control."""
        if not isinstance(event, wx._core.CommandEvent):
            event.Skip()
            return
        try:
            # The TextCtrl object was saved as self._text_control in init().
            value = self._text_control.GetValue()
            self.value = w3c_color_database.Find(value)
            self.set_color()
        except TraitError:
            pass

    def set_color(self):
        # The CustomColorEditor uses this method instead of the global
        # set_color function.
        color = self.factory.to_wx_color(self)
        self._text_control.SetBackgroundColour(color)
        self.control.SetBackgroundColour(color)
        self._text_control.SetValue(self.string_value(color))

    def update_editor(self):
        """Updates the editor when the object trait changes externally to the
        editor.
        """
        self.set_color()

    def open_color_dialog(self, event):
        """Opens the color dialog and sets the value upon return"""
        color_data = wx.ColourData()
        color_data.SetColour(self.value)

        color_dialog = wx.ColourDialog(self.control, color_data)
        result = color_dialog.ShowModal()
        if result == wx.ID_CANCEL:
            return

        color = color_dialog.GetColourData().GetColour()
        self.value = color
        self.set_color()

    def color_selected(self, event):
        """
        Event for when color is selected
        """
        color = event.GetColour()
        try:
            self.value = self.factory.from_wx_color(color)
        except ValueError:
            pass

        return

    def string_value(self, color):
        """Returns the text representation of a specified color value."""
        color_name = w3c_color_database.FindName(color)
        if color_name != "":
            return color_name

        return self.factory.str_color(color)


# ------------------------------------------------------------------------------
#  'ReadonlyColorEditor' class:
# ------------------------------------------------------------------------------


class ReadonlyColorEditor(BaseReadonlyEditor):
    """Read-only style of color editor, which displays a read-only text field
    whose background color is the color value.
    """

    def init(self, parent):
        """Finishes initializing the editor by creating the underlying toolkit
        widget.
        """
        self.control = wx.TextCtrl(parent, style=wx.TE_READONLY)

    def update_editor(self):
        """Updates the editor when the object trait changes externally to the
        editor.
        """
        # super().update_editor()
        self.control.SetValue(self.string_value(self.value))
        set_color(self)

    def string_value(self, color):
        """Returns the text representation of a specified color value."""
        color_name = w3c_color_database.FindName(color)
        if color_name != "":
            return color_name

        return self.factory.str_color(color)


# ------------------------------------------------------------------------------
#  'ReadonlyColorEditor' class:
# ------------------------------------------------------------------------------


class TextColorEditor(BaseTextEditor):
    """Text style of color editor, which displays a text field
    whose background color is the color value.
    """

    def update_editor(self):
        """Updates the editor when the object trait changes externally to the
        editor.
        """
        self.control.SetValue(self.string_value(self.value))
        set_color(self)

    def update_object(self, event):
        """Handles the user changing the contents of the edit control."""
        if not isinstance(event, wx._core.CommandEvent):
            return
        try:
            self.value = w3c_color_database.Find(self.control.GetValue())
            set_color(self)
        except TraitError:
            pass

    def string_value(self, color):
        """Returns the text representation of a specified color value."""
        color_name = w3c_color_database.FindName(color)
        if color_name != "":
            return color_name

        return self.factory.str_color(color)


# ------------------------------------------------------------------------------
#   Sets the color of the specified editor's color control:
# ------------------------------------------------------------------------------


def set_color(editor):
    """Sets the color of the specified color control."""
    color = editor.factory.to_wx_color(editor)
    editor.control.SetBackgroundColour(color)


# Define the SimpleEditor, CustomEditor, etc. classes which are used by the
# editor factory for the color editor.
SimpleEditor = SimpleColorEditor
CustomEditor = CustomColorEditor
TextEditor = TextColorEditor
ReadonlyEditor = ReadonlyColorEditor
