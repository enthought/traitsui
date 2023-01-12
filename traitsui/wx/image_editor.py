# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Traits UI 'display only' image editor.
"""


from pyface.image_resource import ImageResource

from traitsui.ui_traits import convert_bitmap

# FIXME: ImageEditor is a proxy class defined here just for backward
# compatibility. The class has been moved to the
# traitsui.editors.image_editor file.
from traitsui.editors.image_editor import ImageEditor

from .editor import Editor

from .image_control import ImageControl

# -------------------------------------------------------------------------
#  '_ImageEditor' class:
# -------------------------------------------------------------------------


class _ImageEditor(Editor):
    """Traits UI 'display only' image editor."""

    def init(self, parent):
        """Finishes initializing the editor by creating the underlying toolkit
        widget.
        """
        image = self.factory.image
        if image is None:
            image = self.value
        if image is not None:
            bitmap = convert_bitmap(image)
        else:
            bitmap = None

        self.control = ImageControl(parent, bitmap, padding=0)

        self.set_tooltip()

    def update_editor(self):
        """Updates the editor when the object trait changes externally to the
        editor.
        """
        if self.factory.image is None:
            value = self.value
            if value is not None:
                bitmap = convert_bitmap(value)
            else:
                bitmap = None
            self.control.Bitmap(bitmap)
