# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Defines the various button editors for the wxPython user interface toolkit.
"""


import wx

from pyface.ui_traits import Image
from traits.api import Str, observe

from .editor import Editor

# -------------------------------------------------------------------------
#  'SimpleEditor' class:
# -------------------------------------------------------------------------


class SimpleEditor(Editor):
    """Simple style editor for a button."""

    # -------------------------------------------------------------------------
    #  Trait definitions:
    # -------------------------------------------------------------------------

    #: The button label
    label = Str()

    def init(self, parent):
        """Finishes initializing the editor by creating the underlying toolkit
        widget.
        """
        label = self.factory.label or self.item.get_label(self.ui)
        self.control = wx.Button(parent, -1, self.string_value(label))
        self.sync_value(self.factory.label_value, "label", "from")
        self.control.Bind(wx.EVT_BUTTON, self.update_object)
        self.set_tooltip()

    def _label_changed(self, label):
        self.control.SetLabel(self.string_value(label))

    def update_object(self, event):
        """Handles the user clicking the button by setting the factory value
        on the object.
        """
        factory = self.factory
        self.value = factory.value

        # If there is an associated view, then display it:
        if factory.view is not None:
            self.object.edit_traits(view=factory.view, parent=self.control)

    def update_editor(self):
        """Updates the editor when the object trait changes externally to the
        editor.
        """
        pass

    def dispose(self):
        """Disposes of the contents of an editor."""
        self.control.Unbind(wx.EVT_BUTTON)
        super().dispose()


class CustomEditor(SimpleEditor):
    """Custom style editor for a button, which can contain an image."""

    #: The button image
    image = Image()

    def init(self, parent):
        """Finishes initializing the editor by creating the underlying toolkit
        widget.
        """
        from pyface.ui.wx.image_button import ImageButton

        factory = self.factory
        if self.factory.label:
            label = self.factory.label
        else:
            label = self.item.get_label(self.ui)

        self._control = ImageButton(
            parent,
            label=self.string_value(label),
            image=factory.image,
            style=factory.style,
            orientation=factory.orientation,
            width_padding=factory.width_padding,
            height_padding=factory.height_padding,
        )
        self.control = self._control.control
        self._control.on_trait_change(
            self.update_object, "clicked", dispatch="ui"
        )
        self.sync_value(self.factory.label_value, "label", "from")
        self.sync_value(self.factory.image_value, "image", "from")
        self.set_tooltip()

    def _label_changed(self, label):
        self._control.label = self.string_value(label)

    @observe("image")
    def _image_updated(self, event):
        image = event.new
        self._control.image = image

    def dispose(self):
        """Disposes of the contents of an editor."""
        self._control.on_trait_change(
            self.update_object, "clicked", remove=True
        )

        super().dispose()
