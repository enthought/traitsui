""" Implement the interface of AbstractTargetRegistry to support
testing any target whose 'control' attribute refers to a QWidget.
"""
import inspect

from pyface.qt import QtGui

from traitsui.testing.tester._abstract_target_registry import (
    AbstractTargetRegistry,
)
from traitsui.testing.tester.exceptions import (
    InteractionNotSupported,
    LocationNotSupported,
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


class QtControlWidgetRegistry(AbstractTargetRegistry):
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

    def get_handler(self, target, interaction):
        """ Reimplemented AbstractTargetRegistry.get_handler """
        if interaction.__class__ not in self.get_interactions(target):
            raise InteractionNotSupported(
                target_class=target.__class__,
                interaction_class=interaction.__class__,
                supported=list(self.get_interactions(target)),
            )
        return self._INTERACTION_TO_HANDLER[interaction.__class__]

    def get_interactions(self, target):
        """ Reimplemented AbstractTargetRegistry.get_interactions """
        if self._is_target_accepted(target):
            return set(self._INTERACTION_TO_HANDLER)
        return set()

    def get_interaction_doc(self, target, interaction_class):
        """ Reimplemented AbstractTargetRegistry.get_interaction_doc """
        if interaction_class not in self.get_interactions(target):
            raise InteractionNotSupported(
                target_class=target.__class__,
                interaction_class=interaction_class,
                supported=list(self.get_interactions(target)),
            )
        return inspect.getdoc(interaction_class)

    def get_solver(self, target, location):
        """ Reimplemented AbstractTargetRegistry.get_solver """
        raise LocationNotSupported(
            target_class=target.__class__,
            locator_class=location.__class__,
            supported=[],
        )

    def get_locations(self, target):
        """ Reimplemented AbstractTargetRegistry.get_locations """
        return set()

    def get_location_doc(self, target, locator_class):
        """ Reimplemented AbstractTargetRegistry.get_location_doc """
        raise LocationNotSupported(
            target_class=target.__class__,
            locator_class=locator_class,
            supported=[],
        )
