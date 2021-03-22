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
        """ Return a callable for handling an interaction for a given target.

        This is an implementation for an abstract method.

        Parameters
        ----------
        target : any
            The UI target being operated on.
        interaction : any
            Any interaction object.

        Returns
        -------
        handler : callable(UIWrapper, interaction) -> any
            The function to handle the given interaction on a target.

        Raises
        ------
        InteractionNotSupported
            If the given target and interaction types are not supported
            by this registry.
        """
        if interaction.__class__ not in self._get_interactions(target):
            raise InteractionNotSupported(
                target_class=target.__class__,
                interaction_class=interaction.__class__,
                supported=list(self._get_interactions(target)),
            )
        return self.interaction_to_handler[interaction.__class__]

    def _get_interactions(self, target):
        """ Returns all the interactions supported for the given target.

        This is an implementation for an abstract method.

        Parameters
        ----------
        target : any
            The UI target for which supported interactions are queried.

        Returns
        -------
        interaction_classes : set
            Supported interaction types for the given target type.
        """
        if self.can_support(target):
            return set(self.interaction_to_handler)
        return set()

    def _get_interaction_doc(self, target, interaction_class):
        """ Return the documentation for the given target and interaction type.

        This is an implementation for an abstract method.

        Parameters
        ----------
        target : any
            The UI target for which the interaction will be applied.
        interaction_class : subclass of type
            Any class.

        Returns
        -------
        doc : str

        Raises
        ------
        InteractionNotSupported
            If the given target and interaction types are not supported
            by this registry.
        """
        if interaction_class not in self._get_interactions(target):
            raise InteractionNotSupported(
                target_class=target.__class__,
                interaction_class=interaction_class,
                supported=list(self._get_interactions(target)),
            )
        return inspect.getdoc(interaction_class)

    def _get_solver(self, target, location):
        """ Return a callable registered for resolving a location for the
        given target and location.

        This is an implementation for an abstract method.

        Parameters
        ----------
        target : any
            The UI target being operated on.
        location : subclass of type
            The location to be resolved on the target.

        Raises
        ------
        LocationNotSupported
            If the given locator and target types are not supported.
        """
        raise LocationNotSupported(
            target_class=target.__class__,
            locator_class=location.__class__,
            supported=[],
        )

    def _get_locations(self, target):
        """ Returns all the location types supported for the given target.

        This is an implementation for an abstract method.

        Parameters
        ----------
        target : any
            The UI target for which supported location types are queried.

        Returns
        -------
        locators_classes : set
            Supported locator types for the given target type.
        """
        return set()

    def _get_location_doc(self, target, locator_class):
        """ Return the documentation for the given target and locator type.

        This is an implementation for an abstract method.

        Parameters
        ----------
        target : any
            The UI target being operated on.
        locator_class : subclass of type
            Any class.

        Returns
        -------
        doc : str

        Raises
        ------
        LocationNotSupported
            If the given locator and target types are not supported.
        """
        raise LocationNotSupported(
            target_class=target.__class__,
            locator_class=locator_class,
            supported=[],
        )
