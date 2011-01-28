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
#  Author: Enthought, Inc.
#
#------------------------------------------------------------------------------

""" Enthought pyface package component
"""

# Major package imports.
import wx

# Enthought library imports.
from enthought.traits.api import implements, Instance, Int, Unicode

# Local imports.
from enthought.pyface.i_heading_text import IHeadingText, MHeadingText
from enthought.pyface.image_resource import ImageResource
from enthought.pyface.util.font_helper import new_font_like
from widget import Widget


class HeadingText(MHeadingText, Widget):
    """ The toolkit specific implementation of a HeadingText.  See the
    IHeadingText interface for the API documentation.
    """

    implements(IHeadingText)

    #### 'IHeadingText' interface #############################################

    level = Int(1)

    text = Unicode('Default')

    image = Instance(ImageResource, ImageResource('heading_level_1'))

    ###########################################################################
    # 'object' interface.
    ###########################################################################

    def __init__(self, parent, **traits):
        """ Creates the panel. """

        # Base class constructor.
        super(HeadingText, self).__init__(**traits)

        # Create the toolkit-specific control that represents the widget.
        self.control = self._create_control(parent)

        return

    ###########################################################################
    # Private interface.
    ###########################################################################

    def _create_control(self, parent):
        """ Create the toolkit-specific control that represents the widget. """

        # The background image (it is tiled).
        image = self.image.create_image()
        self._bmp = image.ConvertToBitmap()

        sizer = wx.BoxSizer(wx.VERTICAL)
        panel = wx.Panel(parent, -1, style=wx.CLIP_CHILDREN | wx.SIMPLE_BORDER)
        panel.SetSizer(sizer)
        panel.SetAutoLayout(True)

        # Create a suitable font.
        self._font = new_font_like(wx.NORMAL_FONT, family=wx.SWISS)

        width, height = self._get_preferred_size(self.text, self._font)
        panel.SetMinSize((width, height))

        wx.EVT_PAINT(panel, self._on_paint_background)
        wx.EVT_ERASE_BACKGROUND(panel, self._on_erase_background)

        return panel

    def _get_preferred_size(self, text, font):
        """ Calculates the preferred size of the widget. """

        dc = wx.ScreenDC()

        dc.SetFont(font)
        width, height = dc.GetTextExtent(text)

        return (width + 10, height + 10)

    def _tile_background_image(self, dc, width, height):
        """ Tiles the background image. """

        w = self._bmp.GetWidth()
        h = self._bmp.GetHeight()

        x = 0
        while x < width:
            y = 0
            while y < height:
                dc.DrawBitmap(self._bmp, x, y)
                y = y + h

            x = x + w

        return

    #### Trait event handlers #################################################

    def _text_changed(self, new):
        """ Called when the text is changed. """

        if self.control is not None:
            self.control.Refresh()

        return

    #### wx event handlers ####################################################

    def _on_paint_background(self, event):
        """ Called when the background of the panel is painted. """

        dc = wx.PaintDC(self.control)
        size = self.control.GetClientSize()

        # Tile the background image.
        self._tile_background_image(dc, size.width, size.height)

        # Render the text.
        dc.SetFont(self._font)
        dc.DrawText(self.text, 5, 4)

        return

    def _on_erase_background(self, event):
        """ Called when the background of the panel is erased. """

        dc = event.GetDC()
        size = self.control.GetClientSize()

        # Tile the background image.
        self._tile_background_image(dc, size.width, size.height)

        # Render the text.
        dc.SetFont(self._font)
        dc.DrawText(self.text, 5, 4)

        return

#### EOF ######################################################################
