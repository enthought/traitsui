#  Copyright (c) 2005-2020, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#

import wx


def mouse_click_button(wrapper, interaction):
    """ Performs a mouce click on a wx button.

    Parameters
    ----------
    wrapper : UIWrapper
        The wrapper object wrapping the wx button.
    interaction : instance of traitsui.testing.tester.command.MouseClick
        interaction is unused here, but it is included so that the function
        matches the expected format for a handler.  Note this handler is
        intended to be used with an interaction_class of a MouseClick.
    """
    control = wrapper.target
    if not control.IsEnabled():
        return
    wx.MilliSleep(wrapper.delay)
    click_event = wx.CommandEvent(
        wx.wxEVT_COMMAND_BUTTON_CLICKED, control.GetId()
    )
    control.ProcessEvent(click_event)
