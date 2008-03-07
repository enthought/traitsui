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

# Standard library imports.
from logging import DEBUG

# Major package imports.
import wx

# Enthought library imports.
from enthought.traits.api import Any, Bool, Font, implements, Instance, Int
from enthought.traits.api import Tuple, Unicode

# Private Enthought library imports.
# FIXME v3: This should be moved out of pyface.
from enthought.pyface.util.font_helper import new_font_like

# Local imports.
from enthought.pyface.i_splash_screen import ISplashScreen, MSplashScreen
from enthought.pyface.image_resource import ImageResource
from window import Window


class SplashScreen(MSplashScreen, Window):
    """ The toolkit specific implementation of a SplashScreen.  See the
    ISplashScreen interface for the API documentation.
    """

    implements(ISplashScreen)

    #### 'ISplashScreen' interface ############################################

    image = Instance(ImageResource, ImageResource('splash'))

    log_level = Int(DEBUG)

    show_log_messages = Bool(True)

    text = Unicode

    text_color = Any

    text_font = Any

    text_location  = Tuple(5, 5)

    ###########################################################################
    # Protected 'IWidget' interface.
    ###########################################################################

    def _create_control(self, parent):
        # Get the splash screen image.
        image = self.image.create_image()

        splash_screen = wx.SplashScreen(
            # The bitmap to display on the splash screen.
            image.ConvertToBitmap(),
            # Splash Style.
            wx.SPLASH_NO_TIMEOUT | wx.SPLASH_CENTRE_ON_SCREEN,
            # Timeout in milliseconds (we don't currently timeout!).
            0,
            # The parent of the splash screen.
            parent,
            # wx Id.
            -1,
            # Window style.
            style = wx.SIMPLE_BORDER | wx.FRAME_NO_TASKBAR
        )

        # By default we create a font slightly bigger and slightly more italic
        # than the normal system font ;^)  The font is used inside the event
        # handler for 'EVT_PAINT'.
        self._wx_default_text_font = new_font_like(
            wx.NORMAL_FONT,
            point_size = wx.NORMAL_FONT.GetPointSize() + 1,
            style      = wx.ITALIC
        )

        # This allows us to write status text on the splash screen.
        wx.EVT_PAINT(splash_screen, self._on_paint)

        return splash_screen

    ###########################################################################
    # Private interface.
    ###########################################################################

    def _text_changed(self):
        """ Called when the splash screen text has been changed. """

        # Passing 'False' to 'Refresh' means "do not erase the background".
        self.control.Refresh(False)
        self.control.Update()
        wx.Yield()

    def _on_paint(self, event):
        """ Called when the splash window is being repainted. """

        if self.control is not None:
            # Get the window that the splash image is drawn in.
            window = self.control.GetSplashWindow()

            dc = wx.PaintDC(window)

            if self.text_font is None:
                text_font = self._wx_default_text_font
            else:
                text_font = self.text_font

            dc.SetFont(text_font)

            if self.text_color is None:
                text_color = 'black'
            else:
                text_color = self.text_color

            dc.SetTextForeground(text_color)

            x, y = self.text_location
            dc.DrawText(self.text, x, y)

        # Let the normal wx paint handling do its stuff.
        event.Skip()

#### EOF ######################################################################
