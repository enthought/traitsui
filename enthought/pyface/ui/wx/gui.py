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
import logging
import sys

# Major package imports.
import wx

# Enthought library imports.
from enthought.traits.api import Bool, HasTraits, implements, Unicode

# Local imports.
from enthought.pyface.i_gui import IGUI, MGUI


# Logging.
logger = logging.getLogger(__name__)


class GUI(MGUI, HasTraits):

    implements(IGUI)

    #### 'GUI' interface ######################################################

    busy = Bool(False)

    started = Bool(False)

    state_location = Unicode

    ###########################################################################
    # 'object' interface.
    ###########################################################################

    def __init__(self, splash_screen=None):
        # Display the (optional) splash screen.
        self._splash_screen = splash_screen

        if self._splash_screen is not None:
            self._splash_screen.open()

        return

    ###########################################################################
    # 'GUI' class interface.
    ###########################################################################

    def invoke_after(cls, millisecs, callable, *args, **kw):
        wx.FutureCall(millisecs, callable, *args, **kw)

        return

    invoke_after = classmethod(invoke_after)

    def invoke_later(cls, callable, *args, **kw):
        wx.CallAfter(callable, *args, **kw)

        return

    invoke_later = classmethod(invoke_later)

    def set_trait_after(cls, millisecs, obj, trait_name, new):
        wx.FutureCall(millisecs, setattr, obj, trait_name, new)

        return

    set_trait_after = classmethod(set_trait_after)

    def set_trait_later(cls, obj, trait_name, new):
        wx.CallAfter(setattr, obj, trait_name, new)

        return

    set_trait_later = classmethod(set_trait_later)

    def process_events(allow_user_events=True):
        if allow_user_events:
            wx.GetApp().Yield(True)
        else:
            wx.SafeYield()

        return

    process_events = staticmethod(process_events)

    def set_busy(busy=True):
        if busy:
            GUI._cursor = wx.BusyCursor()
        else:
            GUI._cursor = None

    set_busy = staticmethod(set_busy)

    ###########################################################################
    # 'GUI' interface.
    ###########################################################################

    def start_event_loop(self):
        """ Start the GUI event loop. """

        if self._splash_screen is not None:
            self._splash_screen.close()

        # Make sure that we only set the 'started' trait after the main loop
        # has really started.
        self.set_trait_after(10, self, "started", True)

        # A hack to force menus to appear for applications run on Mac OS X.
        if sys.platform == 'darwin':
            def _mac_os_x_hack():
                f = wx.Frame(None, -1)
                f.Show(True)
                f.Close()
            self.invoke_later(_mac_os_x_hack)

        logger.debug("---------- starting GUI event loop ----------")
        wx.GetApp().MainLoop()

        self.started = False

        return

    def stop_event_loop(self):
        """ Stop the GUI event loop. """

        logger.debug("---------- stopping GUI event loop ----------")
        wx.GetApp().ExitMainLoop()

        return

    ###########################################################################
    # Trait handlers.
    ###########################################################################

    def _state_location_default(self):
        """ The default state location handler. """

        return self._default_state_location()

    def _busy_changed(self, new):
        """ The busy trait change handler. """

        if new:
            self._wx_cursor = wx.BusyCursor()
        else:
            del self._wx_cursor

        return

#### EOF ######################################################################
