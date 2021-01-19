""" Implement the interface of AbstractTargetRegistry to support
testing any target whose 'control' attribute refers to a QWidget.
"""
from pyface.qt import QtGui

from traitsui.testing.tester._base_dynamic_registry import (
    BaseDynamicRegistry,
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


class QtControlWidgetRegistry(BaseDynamicRegistry):
    """ A registry to support any target with an attribute 'control' that is
    an instance of QWidget.
    """

    # Mapping from interaction type to handler callable
    _INTERACTION_TO_HANDLER = {
        IsEnabled: _handle_is_enabled,
    }

    def _is_target_accepted(self, target):
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
