# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Defines 'theme' related classes.
"""

from traits.api import HasPrivateTraits, Property, cached_property
from traits.etsconfig.api import ETSConfig

from .ui_traits import Image, HasBorder, HasMargin, Alignment


class Theme(HasPrivateTraits):

    # -- Public Traits --------------------------------------------------------

    #: The background image to use for the theme:
    image = Image

    #: The border inset:
    border = HasBorder

    #: The margin to use around the content:
    content = HasMargin

    #: The margin to use around the label:
    label = HasMargin

    #: The alignment to use for positioning the label:
    alignment = Alignment(cols=4)

    #: The color to use for content text (Wx only)
    content_color = Property()

    #: The color to use for label text (Wx only)
    label_color = Property()

    #: The image slice used to draw the theme (Wx only)
    image_slice = Property(observe="image")

    # -- Constructor ----------------------------------------------------------

    def __init__(self, image=None, **traits):
        """Initializes the object."""
        if image is not None:
            self.image = image

        super().__init__(**traits)

    # -- Property Implementations ---------------------------------------------

    def _get_content_color(self):
        if ETSConfig.toolkit == "wx":
            import wx

            if self._content_color is None:
                color = wx.BLACK
                islice = self.image_slice
                if islice is not None:
                    color = islice.content_color

                self._content_color = color

        return self._content_color

    def _set_content_color(self, color):
        self._content_color = color

    def _get_label_color(self):
        if ETSConfig.toolkit == "wx":
            import wx

            if self._label_color is None:
                color = wx.BLACK
                islice = self.image_slice
                if islice is not None:
                    color = islice.label_color

                self._label_color = color

        return self._label_color

    def _set_label_color(self, color):
        self._label_color = color

    @cached_property
    def _get_image_slice(self):
        if self.image is None:
            return None

        if ETSConfig.toolkit == "wx":
            from traitsui.wx.image_slice import image_slice_for

            return image_slice_for(self.image)


#: The default theme:
default_theme = Theme()
