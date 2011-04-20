#-------------------------------------------------------------------------------
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
#  Date:   05/18/2005
#
#-------------------------------------------------------------------------------

""" Provides a simple function for scheduling some code to run at some time in
    the future (assumes application is wxPython based).
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import wx

#-------------------------------------------------------------------------------
#  'DoLaterTimer' class:
#-------------------------------------------------------------------------------

class DoLaterTimer ( wx.Timer ):

    # List of currently active timers:
    active_timers = []

    #---------------------------------------------------------------------------
    #  Initializes the object:
    #---------------------------------------------------------------------------

    def __init__ ( self, interval, callable, args, kw_args ):
        global active_timers
        wx.Timer.__init__( self )
        for timer in self.active_timers:
            if ((timer.callable == callable) and
                (timer.args     == args)     and
                (timer.kw_args  == kw_args)):
                timer.Start( interval, True )
                return
        self.active_timers.append( self )
        self.callable = callable
        self.args     = args
        self.kw_args  = kw_args
        self.Start( interval, True )

    #---------------------------------------------------------------------------
    #  Handles the timer pop event:
    #---------------------------------------------------------------------------

    def Notify ( self ):
        global active_timers

        self.active_timers.remove( self )
        self.callable( *self.args, **self.kw_args )
