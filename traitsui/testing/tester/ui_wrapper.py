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

    A UI target is an object which can be searched for nested UI targets,
    either as intermediate things (like editors or a table widget), or as a
    leaf widget which can be operated upon (e.g. a mouse click).

    For example, a ``UIWrapper`` may wrap an instance of traitsui.ui.UI in
    which more UI targets can be located. A ``UIWrapper`` may also wrap a
    leaf widget on which user interactions can be performed.

    For locating a nested UI target, the ``locate`` method is provided.
    For simulating user interactions such as a mouse click or visual
    inspection, the ``perform`` and ``inspect`` methods are provided.

    Attributes
    ----------
    target : any
        An object on which further UI target can be searched for, or can be
        a leaf target that can be operated on.
    delay : int, optional
        Time delay (in ms) in which actions by the wrapper are performed. Note
        it is propogated through to created child wrappers. The delay allows
        visual confirmation test code is working as desired. Defaults to 0.
    """

    def __init__(self, target, registries, delay=0):
        """ Initializer

        Parameters
        ----------
        target : any
            An object on which further UI target can be searched for, or can be
            a leaf target that can be operated on.
        registries : list of TargetRegistry
            Registries of interaction for different target, in the order
            of decreasing priority.
        """
        self.target = target
        self._registries = registries
        self.delay = delay

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
            registries=self._registries,
            delay=self.delay,
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
        for registry in self._registries:
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

        try_DefaultTarget = self._try_interaction_via_DefaultTarget(supported, interaction)
        if try_DefaultTarget:
            return try_DefaultTarget

        raise InteractionNotSupported(
            target_class=self.target.__class__,
            interaction_class=interaction.__class__,
            supported=supported,
        )

    def _try_interaction_via_DefaultTarget(self, supported, interaction):
        """ There may not be a handler registered for an interaction on
            the original target (which is represented by self). Instead, it
            may be registered for DefaultTarget.  To address this possibility,
            this method attempts to resolve from the current target to a
            DefaultTarget, and then sees if there is an appropriate handler
            that can perform the given interaction on DefaultTarget instead. If
            so, that handler will ultimately be called and this method returns
            the result. If not, any interactions for which there are handlers
            registered for DefaultTarget will be added to the list of supported
            interactiontypes.

        Parameters
        ----------
        supported : List
            A list of the interactions currently known to be supported for
            the wrapper object.  If no handler is found for the given
            interaction with DefaultTarget as the target_class, any handlers
            supported for DefaultTarget are added to the list. 
        interaction : instance of interaction type
            An object defining the interaction.

        Returns
        -------
        Any
            The output of the call to the appropriate handler (if found)
        None
            If no appropriate handler is found, the method returns None, and
            simply adds to the supported list if necessary. 
        """
        try:
            default_target = self.locate(locator.DefaultTarget())
        # If we can't solve from the current target to DefaultTarget this
        # interaction isn't supported, and there is nothing to add to supported
        except LocationNotSupported:
            pass
        else:
            # if we can locate a DefaultTarget try to perform the
            # interactation on it instead
            try:
                return default_target._perform_or_inspect(interaction)
            # if we can't add to supported
            except InteractionNotSupported as e:
                supported.extend(e.supported)


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
        for registry in self._registries:
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
