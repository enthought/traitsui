""" This module provides a getter to obtain an AbstractTargetRegistry that can
support testing any target whose 'control' attribute refers to a wx.Window.
"""
import wx

from traitsui.testing.tester._dynamic_target_registry import (
    DynamicTargetRegistry,
)
from traitsui.testing.tester.query import IsEnabled


def _handle_is_enabled(wrapper, interaction):
    """ Return true if the target's control is enabled.

    Parameters
    ----------
    wrapper : UIWrapper
        Wrapper on which the target's control should be a wx.Window
    interaction : IsEnabled
        Not currently used.
    """
    return wrapper._target.control.IsEnabled()


def _is_target_control_a_wx_window(target):
    """ Return true if the target has a control that is an instance of
    wx.Window

    Parameters
    ----------
    target : any
        Any UI target

    Returns
    -------
    is_accepted : bool
    """
    return (
        hasattr(target, "control")
        and isinstance(target.control, wx.Window)
    )


def get_widget_registry():
    """ Return a registry to support any target with an attribute 'control'
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
        }
    )
