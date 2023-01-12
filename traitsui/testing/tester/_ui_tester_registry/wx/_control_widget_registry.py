# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" This module provides a getter to obtain an AbstractTargetRegistry that can
support testing any target whose 'control' attribute refers to a wx.Window.
"""
import wx

from traitsui.testing.tester._dynamic_target_registry import (
    DynamicTargetRegistry,
)
from traitsui.testing.tester.query import IsEnabled, IsVisible


def _handle_is_enabled(wrapper, interaction):
    """Return true if the target's control is enabled.

    Parameters
    ----------
    wrapper : UIWrapper
        Wrapper on which the target's control should be a wx.Window
    interaction : IsEnabled
        Not currently used.
    """
    return wrapper._target.control.IsEnabled()


def _handle_is_visible(wrapper, interaction):
    """Return true if the target's control is visible.

    Parameters
    ----------
    wrapper : UIWrapper
        Wrapper on which the target's control should be a wx.Window
    interaction : IsVisible
        Not currently used.
    """
    return wrapper._target.control.IsShownOnScreen()


def _is_target_control_a_wx_window(target):
    """Return true if the target has a control that is an instance of
    wx.Window

    Parameters
    ----------
    target : any
        Any UI target

    Returns
    -------
    is_accepted : bool
    """
    return hasattr(target, "control") and isinstance(target.control, wx.Window)


def get_widget_registry():
    """Return a registry to support any target with an attribute 'control'
    that is an instance of wx.Window.

    Returns
    -------
    registry : DynamicTargetRegistry
        A registry that can be used with UIWrapper
    """
    return DynamicTargetRegistry(
        can_support=_is_target_control_a_wx_window,
        interaction_to_handler={
            IsEnabled: _handle_is_enabled,
            IsVisible: _handle_is_visible,
        },
    )
