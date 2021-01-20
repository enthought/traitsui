# (C) Copyright 2004-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

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

    def _get_handler(self, target, interaction):
        """ Reimplemented AbstractTargetRegistry._get_handler """
        if interaction.__class__ not in self._get_interactions(target):
            raise InteractionNotSupported(
                target_class=target.__class__,
                interaction_class=interaction.__class__,
                supported=list(self._get_interactions(target)),
            )
        return self.interaction_to_handler[interaction.__class__]

    def _get_interactions(self, target):
        """ Reimplemented AbstractTargetRegistry._get_interactions """
        if self.can_support(target):
            return set(self.interaction_to_handler)
        return set()

    def _get_interaction_doc(self, target, interaction_class):
        """ Reimplemented AbstractTargetRegistry._get_interaction_doc """
        if interaction_class not in self._get_interactions(target):
            raise InteractionNotSupported(
                target_class=target.__class__,
                interaction_class=interaction_class,
                supported=list(self._get_interactions(target)),
            )
        return inspect.getdoc(interaction_class)

    def _get_solver(self, target, location):
        """ Reimplemented AbstractTargetRegistry._get_solver """
        raise LocationNotSupported(
            target_class=target.__class__,
            locator_class=location.__class__,
            supported=[],
        )

    def _get_locations(self, target):
        """ Reimplemented AbstractTargetRegistry._get_locations """
        return set()

    def _get_location_doc(self, target, locator_class):
        """ Reimplemented AbstractTargetRegistry._get_location_doc """
        raise LocationNotSupported(
            target_class=target.__class__,
            locator_class=locator_class,
            supported=[],
        )
