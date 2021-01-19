""" This module provides a getter to obtain an AbstractTargetRegistry that can
support testing any target whose 'control' attribute refers to a QWidget.
"""
from pyface.qt import QtGui

from traitsui.testing.tester._dynamic_target_registry import (
    DynamicTargetRegistry,
)
from traitsui.testing.tester.query import IsEnabled


def _handle_is_enabled(wrapper, interaction):
    """ Return true if the target's control is enabled.

    Parameters
    ----------
    wrapper : UIWrapper
        Wrapper on which the target's control should be a QWidget
    interaction : IsEnabled
        Not currently used.
    """
    return wrapper._target.control.isEnabled()


def _is_target_control_a_qt_widget(target):
    """ Return true if the target is accepted by the registry.

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
        and isinstance(target.control, QtGui.QWidget)
    )


def get_widget_registry():
    """ Return a registry to support any target with an attribute 'control'
    that is an instance of QWidget.

    Returns
    -------
    registry : DynamicTargetRegistry
        A registry that can be used with UIWrapper
    """
    return DynamicTargetRegistry(
        can_support=_is_target_control_a_qt_widget,
        interaction_to_handler={
            IsEnabled: _handle_is_enabled,
        }
    )
