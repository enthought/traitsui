# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Custom exceptions for UITester and UIWrapper.
"""


class TesterError(Exception):
    """Custom exception for UITester/UIWrapper."""

    pass


class Disabled(TesterError):
    """Raised when a simulation fails because the widget is disabled."""

    pass


class InteractionNotSupported(TesterError):
    """Raised when an interaction is not supported by a wrapper.

    Parameters
    ----------
    target_class : subclass of type
        The type of a UI target being operated on.
    interaction_class : subclass of type
        Any class for the interaction.
    supported : list of types
        List of supported interaction types.
    """

    def __init__(self, target_class, interaction_class, supported):
        self.target_class = target_class
        self.interaction_class = interaction_class
        self.supported = supported

    def __str__(self):
        return (
            "No handler is found for target {!r} with interaction {!r}. "
            "Supported these: {!r}".format(
                self.target_class, self.interaction_class, self.supported
            )
        )


class LocationNotSupported(TesterError):
    """Raised when attempt to resolve a location on a UI fails
    because the location type is not supported.
    """

    def __init__(self, target_class, locator_class, supported):
        self.target_class = target_class
        self.locator_class = locator_class
        self.supported = supported

    def __str__(self):
        return (
            "Location {!r} is not supported for {!r}. "
            "Supported these: {!r}".format(
                self.locator_class, self.target_class, self.supported
            )
        )
