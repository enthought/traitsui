#------------------------------------------------------------------------------
#
#  Copyright (c) 2005, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
#  Author: David C. Morrill
#  Date:   10/21/2004
#
#------------------------------------------------------------------------------

""" Defines the various image enumeration editors for the wxPython user interface toolkit.
"""

#-------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------

from __future__ import absolute_import
import wx

from traits.api \
    import Any

# FIXME: ToolkitEditorFactory is a proxy class defined here just for backward
# compatibility. The class has been moved to the
# traitsui.editors.image_enum_editor file.
from traitsui.editors.image_enum_editor \
    import ToolkitEditorFactory

from .editor \
    import Editor

from .helper \
    import bitmap_cache, position_window, TraitsUIPanel

from .constants \
    import WindowColor

from .image_control \
    import ImageControl

#-------------------------------------------------------------------------
#  'ReadonlyEditor' class:
#-------------------------------------------------------------------------


class ReadonlyEditor(Editor):
    """ Read-only style of image enumeration editor, which displays a single
    ImageControl, representing the object trait's value.
    """
    #-------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #-------------------------------------------------------------------------

    def init(self, parent):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.control = ImageControl(
            parent,
            bitmap_cache(
                '%s%s%s' %
                (self.factory.prefix,
                 self.str_value,
                 self.factory.suffix),
                False,
                self.factory._image_path))

    #-------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #-------------------------------------------------------------------------

    def update_editor(self):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        self.control.Bitmap(
            bitmap_cache(
                '%s%s%s' %
                (self.factory.prefix,
                 self.str_value,
                 self.factory.suffix),
                False,
                self.factory._image_path))

#-------------------------------------------------------------------------
#  'SimpleEditor' class:
#-------------------------------------------------------------------------


class SimpleEditor(ReadonlyEditor):
    """ Simple style of image enumeration editor, which displays an
    ImageControl, representing the object trait's value. Clicking an image
    displays a dialog box for selecting an image corresponding to a different
    value.
    """
    #-------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #-------------------------------------------------------------------------

    def init(self, parent):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        super(SimpleEditor, self).init(parent)
        self.control.Selected(True)
        self.control.Handler(self.popup_editor)
        self.set_tooltip()

    #-------------------------------------------------------------------------
    #  Handles the user clicking the ImageControl to display the pop-up dialog:
    #-------------------------------------------------------------------------

    def popup_editor(self, control):
        """ Handles the user clicking the ImageControl to display the pop-up
            dialog.
        """
        ImageEnumDialog(self)

#-------------------------------------------------------------------------
#  'CustomEditor' class:
#-------------------------------------------------------------------------


class CustomEditor(Editor):
    """ Custom style of image enumeration editor, which displays a grid of
    ImageControls. The user can click an image to select the corresponding
    value.
    """
    #-------------------------------------------------------------------------
    #  Trait definitions:
    #-------------------------------------------------------------------------

    update_handler = Any  # Callback to call when any button clicked

    #-------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #-------------------------------------------------------------------------

    def init(self, parent):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self._create_image_grid(parent)

    #-------------------------------------------------------------------------
    #  Populates a specified window with a grid of image buttons:
    #-------------------------------------------------------------------------

    def _create_image_grid(self, parent):
        """ Populates a specified window with a grid of image buttons.
        """
        # Create the panel to hold the ImageControl buttons:
        self.control = panel = TraitsUIPanel(parent, -1)

        # Create the main sizer:
        if self.factory.cols > 1:
            sizer = wx.GridSizer(0, self.factory.cols, 0, 0)
        else:
            sizer = wx.BoxSizer(wx.VERTICAL)

        # Add the set of all possible choices:
        factory = self.factory
        mapping = factory._mapping
        cur_value = self.value
        for name in self.factory._names:
            value = mapping[name]
            control = ImageControl(
                panel,
                bitmap_cache(
                    '%s%s%s' %
                    (factory.prefix,
                     name,
                     factory.suffix),
                    False,
                    factory._image_path),
                value == cur_value,
                self.update_object)
            control.value = value
            sizer.Add(control, 0, wx.ALL, 2)
            self.set_tooltip(control)

        # Finish setting up the control layout:
        panel.SetSizerAndFit(sizer)

    #-------------------------------------------------------------------------
    #  Handles the user clicking on an ImageControl to set an object value:
    #-------------------------------------------------------------------------

    def update_object(self, control):
        """ Handles the user clicking on an ImageControl to set an object value.
        """
        self.value = control.value
        if self.update_handler is not None:
            self.update_handler()

    #-------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #-------------------------------------------------------------------------

    def update_editor(self):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        value = self.value
        for control in self.control.GetChildren():
            control.Selected(value == control.value)

#-------------------------------------------------------------------------
#  'ImageEnumDialog' class:
#-------------------------------------------------------------------------


class ImageEnumDialog(wx.Frame):
    """ Dialog box for selecting an ImageControl
    """
    #-------------------------------------------------------------------------
    #  Initializes the object:
    #-------------------------------------------------------------------------

    def __init__(self, editor):
        """ Initializes the object.
        """
        wx.Frame.__init__(self, editor.control, -1, '',
                          style=wx.SIMPLE_BORDER)
        self.SetBackgroundColour(WindowColor)
        wx.EVT_ACTIVATE(self, self._on_close_dialog)
        self._closed = False

        dlg_editor = CustomEditor(self,
                                  factory=editor.factory,
                                  ui=editor.ui,
                                  object=editor.object,
                                  name=editor.name,
                                  description=editor.description,
                                  update_handler=self._close_dialog)

        dlg_editor.init(self)

        # Wrap the dialog around the image button panel:
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(dlg_editor.control)
        sizer.Fit(self)

        # Position the dialog:
        position_window(self, parent=editor.control)
        self.Show()

    #-------------------------------------------------------------------------
    #  Closes the dialog:
    #-------------------------------------------------------------------------

    def _on_close_dialog(self, event):
        """ Closes the dialog.
        """
        if not event.GetActive():
            self._close_dialog()

    #-------------------------------------------------------------------------
    #  Closes the dialog:
    #-------------------------------------------------------------------------

    def _close_dialog(self):
        """ Closes the dialog.
        """
        if not self._closed:
            self._closed = True
            self.Destroy()

### EOF #######################################################################
