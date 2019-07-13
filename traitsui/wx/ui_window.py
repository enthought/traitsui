#------------------------------------------------------------------------------
#
#  Copyright (c) 2008, Enthought, Inc.
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
#  Date:   08/23/2008
#
#------------------------------------------------------------------------------

""" A base class for creating custom Traits UI windows.
"""

#-------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------

from __future__ import absolute_import
import wx

from traits.api \
    import HasPrivateTraits, Instance, Property

from .helper \
    import init_wx_handlers, BufferDC

#-------------------------------------------------------------------------
#  'UIWindow' class:
#-------------------------------------------------------------------------


class UIWindow(HasPrivateTraits):
    """ A base class for creating custom Traits UI windows.
    """

    # The wx.Window associated with this custom window:
    control = Instance(wx.Window)

    # The initial size of the window:
    size = Instance(wx.Size, (-1, -1))

    # The current width of the window:
    width = Property

    # The current height of the window:
    height = Property

    #-- Public Methods -------------------------------------------------------

    def __init__(self, parent, **traits):
        """ Creates and initializes the window.
        """
        super(UIWindow, self).__init__(**traits)
        self.control = wx.Window(parent, -1,
                                 size=self.size,
                                 style=wx.FULL_REPAINT_ON_RESIZE)
        init_wx_handlers(self.control, self)

    def refresh(self, x=None, y=None, dx=None, dy=None):
        """ Refreshes the contents of the window.
        """
        if self.control is not None:
            if x is None:
                self.control.Refresh()
            else:
                self.control.Refresh(x, y, dx, dy)

    def capture(self):
        """ Capture the mouse.
        """
        self.control.CaptureMouse()

    def release(self):
        """ Release the mouse.
        """
        self.control.ReleaseMouse()

    #-- wxPython Event Handlers ----------------------------------------------

    def _erase_background(self, event):
        """ Never, ever, do anything in this handler.
        """
        pass

    def _paint(self, event):
        """ Paints the contents of the window.
        """
        dc = BufferDC(self.control)
        self._paint_dc(dc)
        dc.copy()

    def _paint_dc(self, dc):
        """ This method should be overridden by sub-classes to do the actual
            window painting.
        """
        pass

    #-- Property Implementations ---------------------------------------------

    def _get_width(self):
        return self.control.GetClientSize()[0]

    def _set_width(self, width):
        self.control.SetSize(width, self.height)

    def _get_height(self):
        return self.control.GetClientSize()[1]

    def _set_height(self, height):
        self.control.SetSize(self.width, height)
