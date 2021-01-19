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


class BaseDynamicRegistry(AbstractTargetRegistry):
    """ A registry to support targets with dynamic checks.

    Subclass should populate the _INTERACTION_TO_HANDLER mapping
    and implement _is_target_accepted method.
    """

    #: A dictionary mapping from interaction type to handler callable
    #: Subclass should propulate this mapping.
    _INTERACTION_TO_HANDLER = {}

    def _is_target_accepted(self, target):
        """ Return true if the target is accepted by the registry.
        Subclass must implement this method.

        Parameters
        ----------
        target : any
            Any UI target

        Returns
        -------
        is_accepted : bool
        """
        raise NotImplementedError("_is_target_accepted must be implemented.")

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
