# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Interface of a registry depended on by the UIWrapper.

This module is currently labelled as for internal use, but it can be made
public when there is an external need.
"""

import abc


class AbstractTargetRegistry(abc.ABC):
    """Abstract base class which defines the registry interface expected
    by :class:`~traitsui.testing.tester.ui_wrapper.UIWrapper`.
    """

    @abc.abstractmethod
    def _get_handler(self, target, interaction):
        """Return a callable for handling an interaction for a given target.

        This is a protected method expected to be implemented by a subclass.

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

    @abc.abstractmethod
    def _get_interactions(self, target):
        """Returns all the interactions supported for the given target.

        This is a protected method expected to be implemented by a subclass.

        Parameters
        ----------
        target : any
            The UI target for which supported interactions are queried.

        Returns
        -------
        interaction_classes : set
            Supported interaction types for the given target type.
        """

    @abc.abstractmethod
    def _get_interaction_doc(self, target, interaction_class):
        """Return the documentation for the given target and interaction type.

        This is a protected method expected to be implemented by a subclass.

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

    @abc.abstractmethod
    def _get_solver(self, target, location):
        """Return a callable registered for resolving a location for the
        given target and location.

        This is a protected method expected to be implemented by a subclass.

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

    @abc.abstractmethod
    def _get_locations(self, target):
        """Returns all the location types supported for the given target.

        This is a protected method expected to be implemented by a subclass.

        Parameters
        ----------
        target : any
            The UI target for which supported location types are queried.

        Returns
        -------
        locators_classes : set
            Supported locator types for the given target type.
        """

    @abc.abstractmethod
    def _get_location_doc(self, target, locator_class):
        """Return the documentation for the given target and locator type.

        This is a protected method expected to be implemented by a subclass.

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
