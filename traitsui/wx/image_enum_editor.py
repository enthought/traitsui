# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Defines the various image enumeration editors for the wxPython user interface toolkit.
"""


import wx

from traits.api import Any

from .editor import Editor

from .enum_editor import BaseEditor as BaseEnumEditor

from .helper import bitmap_cache, position_window, TraitsUIPanel

from .constants import WindowColor

from .image_control import ImageControl

from traitsui.wx import toolkit

# -------------------------------------------------------------------------
#  'ReadonlyEditor' class:
# -------------------------------------------------------------------------


class ReadonlyEditor(Editor):
    """Read-only style of image enumeration editor, which displays a single
    ImageControl, representing the object trait's value.
    """

    def init(self, parent):
        """Finishes initializing the editor by creating the underlying toolkit
        widget.
        """
        self.control = ImageControl(
            parent,
            bitmap_cache(
                "%s%s%s"
                % (self.factory.prefix, self.str_value, self.factory.suffix),
                False,
                self.factory._image_path,
            ),
        )

    def update_editor(self):
        """Updates the editor when the object trait changes externally to the
        editor.
        """
        self.control.Bitmap(
            bitmap_cache(
                "%s%s%s"
                % (self.factory.prefix, self.str_value, self.factory.suffix),
                False,
                self.factory._image_path,
            )
        )


class SimpleEditor(ReadonlyEditor):
    """Simple style of image enumeration editor, which displays an
    ImageControl, representing the object trait's value. Clicking an image
    displays a dialog box for selecting an image corresponding to a different
    value.
    """

    def init(self, parent):
        """Finishes initializing the editor by creating the underlying toolkit
        widget.
        """
        super().init(parent)
        self.control.Selected(True)
        self.control.Handler(self.popup_editor)
        self.set_tooltip()

    def popup_editor(self, control):
        """Handles the user clicking the ImageControl to display the pop-up
        dialog.
        """
        ImageEnumDialog(self)


class CustomEditor(BaseEnumEditor):
    """Custom style of image enumeration editor, which displays a grid of
    ImageControls. The user can click an image to select the corresponding
    value.
    """

    # -------------------------------------------------------------------------
    #  Trait definitions:
    # -------------------------------------------------------------------------

    update_handler = Any  # Callback to call when any button clicked

    def init(self, parent):
        """Finishes initializing the editor by creating the underlying toolkit
        widget.
        """
        super().init(parent)

        # Create the panel to hold the ImageControl buttons:
        self.control = TraitsUIPanel(parent, -1)
        self._create_image_grid()

    def rebuild_editor(self):
        # Clear any existing content:
        self.control.SetSizer(None)
        toolkit.destroy_children(self.control)

        self._create_image_grid()

    def _create_image_grid(self):
        """Populates a specified window with a grid of image buttons."""
        panel = self.control

        # Create the main sizer:
        if self.factory.cols > 1:
            sizer = wx.GridSizer(0, self.factory.cols, 0, 0)
        else:
            sizer = wx.BoxSizer(wx.VERTICAL)

        # Add the set of all possible choices:
        factory = self.factory
        cur_value = self.value
        for name in self.names:
            value = self.mapping[name]
            control = ImageControl(
                panel,
                bitmap_cache(
                    "%s%s%s" % (factory.prefix, name, factory.suffix),
                    False,
                    factory._image_path,
                ),
                value == cur_value,
                self.update_object,
            )
            control.value = value
            sizer.Add(control, 0, wx.ALL, 2)
            self.set_tooltip(control)

        # Finish setting up the control layout:
        panel.SetSizerAndFit(sizer)

    def update_object(self, control):
        """Handles the user clicking on an ImageControl to set an object value."""
        self.value = control.value
        if self.update_handler is not None:
            self.update_handler()

    def update_editor(self):
        """Updates the editor when the object trait changes externally to the
        editor.
        """
        value = self.value
        for control in self.control.GetChildren():
            control.Selected(value == control.value)


class ImageEnumDialog(wx.Frame):
    """Dialog box for selecting an ImageControl"""

    def __init__(self, editor):
        """Initializes the object."""
        wx.Frame.__init__(self, editor.control, -1, "", style=wx.SIMPLE_BORDER)
        self.SetBackgroundColour(WindowColor)
        self.Bind(wx.EVT_ACTIVATE, self._on_close_dialog)
        self._closed = False

        dlg_editor = CustomEditor(
            self,
            factory=editor.factory,
            ui=editor.ui,
            object=editor.object,
            name=editor.name,
            description=editor.description,
            update_handler=self._close_dialog,
        )

        dlg_editor.init(self)

        # Wrap the dialog around the image button panel:
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(dlg_editor.control)
        sizer.Fit(self)

        # Position the dialog:
        position_window(self, parent=editor.control)
        self.Show()

    def _on_close_dialog(self, event):
        """Closes the dialog."""
        if not event.GetActive():
            self._close_dialog()

    def _close_dialog(self):
        """Closes the dialog."""
        if not self._closed:
            self._closed = True
            self.Destroy()
