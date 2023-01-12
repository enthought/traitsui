# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Define the registry object responsible for collecting and reporting
implementations for testing various GUI elements.
"""

import inspect


from traitsui.testing.tester._abstract_target_registry import (
    AbstractTargetRegistry,
)
from traitsui.testing.tester.exceptions import (
    InteractionNotSupported,
    LocationNotSupported,
)


class _TargetToKeyRegistry:
    """Perform the mapping from target to a key to a callable.

    Internally this is a dict(type, dict(type, callable)), but expose a few
    methods for better error reporting.
    """

    def __init__(self, exception_maker):
        """Initializer

        Parameters
        ----------
        exception_maker : callable(target_class, key, available_keys)
            A callable that return an exception for when no values are referred
            to by a given pair of target_class and key.
        """
        self._target_to_key_to_value = {}
        self.exception_maker = exception_maker

    def register(self, target_class, key, value):
        action_to_handler = self._target_to_key_to_value.setdefault(
            target_class, {}
        )
        if key in action_to_handler:
            raise ValueError(
                "A value for target {!r} and key {!r} already "
                "exists.".format(target_class, key)
            )
        action_to_handler[key] = value

    def get_value(self, target_class, key):
        action_to_handler = self._target_to_key_to_value.get(target_class, [])
        if key not in action_to_handler:
            raise self.exception_maker(
                target_class=target_class,
                key=key,
                available_keys=list(action_to_handler),
            )
        return action_to_handler[key]

    def get_keys(self, target_class):
        """Return all the keys for the given target.

        Parameters
        ----------
        target_class : subclass of type
            The type of a UI target being operated on.

        Returns
        -------
        keys : set
        """
        return set(self._target_to_key_to_value.get(target_class, []))


class TargetRegistry(AbstractTargetRegistry):
    """An object for registering interaction and location resolution logic
    for different UI target types.

    ``register_interaction`` supports extending ``UIWrapper.perform`` and
    ``UIWrapper.inspect`` for a given UI target type and interaction type.

    ``register_location`` supports extending ``UIWrapper.locate`` for a given
    UI target type and location type.

    See :ref:`testing-how-extension-works` in the User Manual for further
    details.
    """

    def __init__(self):
        self._interaction_registry = _TargetToKeyRegistry(
            exception_maker=(
                lambda target_class, key, available_keys: (
                    InteractionNotSupported(
                        target_class=target_class,
                        interaction_class=key,
                        supported=available_keys,
                    )
                )
            ),
        )
        self._location_registry = _TargetToKeyRegistry(
            exception_maker=(
                lambda target_class, key, available_keys: LocationNotSupported(
                    target_class=target_class,
                    locator_class=key,
                    supported=available_keys,
                )
            ),
        )

    def register_interaction(self, target_class, interaction_class, handler):
        """Register a handler for a given target type and interaction type.

        Parameters
        ----------
        target_class : subclass of type
            The type of a UI target being operated on.
        interaction_class : subclass of type
            Any class.
        handler : callable(UIWrapper, interaction) -> any
            The function to handle the particular interaction on a target.
            ``interaction`` should be an instance of ``interaction_class``.

        Raises
        ------
        ValueError
            If a handler has already be registered for the same target type
            and interaction class.
        """
        self._interaction_registry.register(
            target_class=target_class,
            key=interaction_class,
            value=handler,
        )

    def _get_handler(self, target, interaction):
        """Return a callable for handling an interaction for a given target.

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
        return self._interaction_registry.get_value(
            target_class=target.__class__,
            key=interaction.__class__,
        )

    def _get_interactions(self, target):
        """Returns all the interactions supported for the given target.

        Parameters
        ----------
        target : any
            The UI target for which supported interactions are queried.

        Returns
        -------
        interaction_classes : set
            Supported interaction types for the given target type.
        """
        return self._interaction_registry.get_keys(
            target_class=target.__class__
        )

    def _get_interaction_doc(self, target, interaction_class):
        """Return the documentation for the given target and interaction type.

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
        self._interaction_registry.get_value(
            target_class=target.__class__,
            key=interaction_class,
        )
        # This maybe configurable in the future via register_interaction
        return inspect.getdoc(interaction_class)

    def register_location(self, target_class, locator_class, solver):
        """Register a solver for resolving the next UI target for the given
        target type and locator type.

        Parameters
        ----------
        target_class : subclass of type
            The type of a UI target being operated on.
        locator_class : subclass of type
            Any class.
        solver : callable(UIWrapper, location) -> any
            A callable for resolving a location into a new target.
            The location argument will be an instance of locator_class.

        Raises
        ------
        ValueError
            If a solver has already been registered for the given target
            type and locator type.
        """
        self._location_registry.register(
            target_class=target_class,
            key=locator_class,
            value=solver,
        )

    def _get_solver(self, target, location):
        """Return a callable registered for resolving a location for the
        given target and location.

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
        return self._location_registry.get_value(
            target_class=target.__class__,
            key=location.__class__,
        )

    def _get_locations(self, target):
        """Returns all the location types supported for the given target.

        Parameters
        ----------
        target : any
            The UI target for which supported location types are queried.

        Returns
        -------
        locators_classes : set
            Supported locator types for the given target type.
        """
        return self._location_registry.get_keys(target_class=target.__class__)

    def _get_location_doc(self, target, locator_class):
        """Return the documentation for the given target and locator type.

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
        self._location_registry.get_value(
            target_class=target.__class__,
            key=locator_class,
        )
        # This maybe configurable in the future via register_location
        return inspect.getdoc(locator_class)
