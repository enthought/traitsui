""" Implement the interface of AbstractTargetRegistry to support
dynamic checking on the target.
"""
import inspect

from traitsui.testing.tester._abstract_target_registry import (
    AbstractTargetRegistry,
)
from traitsui.testing.tester.exceptions import (
    InteractionNotSupported,
    LocationNotSupported,
)


class DynamicTargetRegistry(AbstractTargetRegistry):
    """ A registry to support targets with dynamic checks.

    Parameters
    ----------
    can_support : callable(target) -> bool
        A callable that return true if the given target is supported
        by the registry.
    interaction_to_handler : dict(type, callable)
        A dictionary mapping from interaction type to handler callables
    """

    def __init__(self, *, can_support, interaction_to_handler):
        self.can_support = can_support
        self.interaction_to_handler = interaction_to_handler

    def get_handler(self, target, interaction):
        """ Reimplemented AbstractTargetRegistry.get_handler """
        if interaction.__class__ not in self.get_interactions(target):
            raise InteractionNotSupported(
                target_class=target.__class__,
                interaction_class=interaction.__class__,
                supported=list(self.get_interactions(target)),
            )
        return self.interaction_to_handler[interaction.__class__]

    def get_interactions(self, target):
        """ Reimplemented AbstractTargetRegistry.get_interactions """
        if self.can_support(target):
            return set(self.interaction_to_handler)
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
