#  Copyright (c) 2005-2020, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#

from contextlib import contextmanager

from traitsui.testing.tester.exceptions import (
    InteractionNotSupported,
    LocationNotSupported,
)
from traitsui.testing.tester import locator
from traitsui.tests._tools import (
    process_cascade_events as _process_cascade_events,
    reraise_exceptions as _reraise_exceptions,
)


class UIWrapper:
    """
    An ``UIWrapper`` has the following responsibilities:

    (1) Wraps a UI target.
    (2) Search for a nested UI target within the wrapped UI target.
    (3) Perform user interaction on the UI target, e.g. mouse click.

    For example, a ``UIWrapper`` may wrap an instance of traitsui.ui.UI in
    which more UI targets can be located. A ``UIWrapper`` may also wrap a
    leaf widget on which user interactoins. It may also wrap a UI target
    somewhere in between in the hierarchy of GUI components.

    For locating a nested UI target, the ``locate`` method is provided.
    For simulating user interactions such as a mouse click or visual
    inspection, the ``perform`` and ``inspect`` methods are provided.

    Attributes
    ----------
    target : any
        An object on which further UI target can be searched for, or can be
        a leaf target that can be operated on.
    """

    def __init__(self, target, interaction_registries, location_registries):
        """ Initializer

        Parameters
        ----------
        target : any
            An object on which further UI target can be searched for, or can be
            a leaf target that can be operated on.
        interaction_registries : list of InteractionRegistry
            Registries of interaction for different target, in the order
            of decreasing priority.
        location_registries : list of LocationRegistry
            Registries for resolving nested UI targets, in the order
            of decreasing priority.
        """
        self.target = target
        self._interaction_registries = interaction_registries
        self._location_registries = location_registries

    def locate(self, location):
        """ Attempt to resolve the given location and return a new
        UIWrapper.

        Parameters
        ----------
        location : Location

        Raises
        ------
        LocationNotSupported
            If the given location is not supported.
        """
        return UIWrapper(
            target=self._get_next_target(location),
            interaction_registries=self._interaction_registries,
            location_registries=self._location_registries,
        )

    def find_by_name(self, name):
        """ Find a target inside the current target using a name.

        Parameters
        ----------
        name : str
            A single name for retreiving a target on a UI.

        Returns
        -------
        wrapper : UIWrapper
        """
        return self.locate(locator.TargetByName(name=name))

    def perform(self, interaction):
        """ Perform a user interaction that causes side effects.

        Parameters
        ----------
        interaction : object
            An interaction instance that defines the user interaction.
            See ``traitsui.testing.tester.command`` module for builtin
            query objects.
            e.g. ``traitsui.testing.tester.command.MouseClick``
        """
        self._perform_or_inspect(interaction)

    def inspect(self, interaction):
        """ Return a value or values for inspection.

        Parameters
        ----------
        interaction : object
            An interaction instance that defines the inspection.
            See ``traitsui.testing.tester.query`` module for builtin
            query objects.
            e.g. ``traitsui.testing.tester.query.DisplayedText``
        """
        return self._perform_or_inspect(interaction)

    def _perform_or_inspect(self, interaction):
        """ Perform a user interaction or a user inspection.

        Parameters
        ----------
        interaction : instance of interaction type
            An object defining the interaction.

        Returns
        -------
        value : any

        Raises
        ------
        InteractionNotSupported
            If the given interaction does not have a corresponding
            implementation for the wrapped UI target.
        """
        interaction_class = interaction.__class__
        supported = []
        for registry in self._interaction_registries:
            try:
                handler = registry.get_handler(
                    target_class=self.target.__class__,
                    interaction_class=interaction_class,
                )
            except InteractionNotSupported as e:
                supported.extend(e.supported)
                continue
            else:
                with _event_processed():
                    return handler(self, interaction)

        raise InteractionNotSupported(
            target_class=self.target.__class__,
            interaction_class=interaction.__class__,
            supported=supported,
        )

    def _get_next_target(self, location):
        """ Return the next UI target from the given location.

        Parameters
        ----------
        location : instance of locator type
            A location for resolving the next target.

        Returns
        -------
        new_target : any

        Raises
        ------
        LocationNotSupport
            If no solver are provided for resolving the given location in the
            wrapped UI target.
        """
        supported = set()
        for registry in self._location_registries:
            try:
                handler = registry.get_solver(
                    self.target.__class__,
                    location.__class__,
                )
            except LocationNotSupported as e:
                supported |= set(e.supported)
            else:
                return handler(self, location)

        raise LocationNotSupported(
            target_class=self.target.__class__,
            locator_class=location.__class__,
            supported=list(supported),
        )


@contextmanager
def _event_processed():
    """ Context manager to ensure GUI events are processed upon entering
    and exiting the context.
    """
    with _reraise_exceptions():
        _process_cascade_events()
        try:
            yield
        finally:
            _process_cascade_events()
