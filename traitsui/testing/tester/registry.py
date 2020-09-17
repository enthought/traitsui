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

from traitsui.testing.tester.exceptions import (
    InteractionNotSupported,
    LocationNotSupported,
)


class _TargetToKeyRegistry:
    """ Perform the mapping from target to a key to a callable.

    Internally this is a dict(type, dict(type, callable)), but expose a few
    methods for better error reporting.
    """

    def __init__(self, exception_maker):
        """ Initializer

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


class TargetRegistry:
    """ An object for registering interaction and location resolution logic
    for different UI target types.

    Registering interaction handler (register_handler)
    --------------------------------------------------
    The interaction type can be a subclass of any type. There are a few
    pre-defined interaction types in
    - ``traitsui.testing.tester.command``
    - ``traitsui.testing.tester.query``

    For example, to simulate clicking a button in TraitsUI's ButtonEditor, the
    implementation for Qt may look like this::

        def mouse_click_qt_button(wrapper, interaction):
            # wrapper is an instance of UIWrapper
            wrapper.target.control.click()

    The function can then be registered with the target type and an interaction
    type::

        registry = TargetRegistry()
        registry.register_handler(
            target_class=traitsui.qt4.button_editor.SimpleEditor,
            interaction_class=traitsui.testing.tester.command.MouseClick,
            handler=mouse_click_qt_button,
        )

    Similarly, a wx implementation of clicking a button can be registered
    to the registry (the content of ``mouse_click_wx_button`` is not shown)::

        registry.register_handler(
            target_class=traitsui.wx.button_editor.SimpleEditor,
            interaction_class=traitsui.testing.tester.command.MouseClick,
            handler=mouse_click_wx_button,
        )

    Then this registry can be used with the ``UITester`` and ``UIWrapper`` to
    support ``UIWrapper.perform`` and ``UIWrapper.inspect``.

    Registering location solver (register_solver)
    ---------------------------------------------

    Resolving a location on a UI target is logically similar to making a query
    for a nested UI target. This query is separated out to support the
    ``UIWrapper.locate`` method independently of the query method
    ``UIWrapper.inspect``.

    The locator type can be any subclass of ``type``. There are predefined
    locators in ``traitsui.testing.tester.locator``.

    For example, suppose a UI target called ``MyUIContainer`` has some buttons,
    and the objective of a test is to click a specific button with a given
    label. We will therefore need to locate the button with the given label
    before a mouse click can be performed.

    The test code we wanted to achieve looks like this::

        button_wrapper = container.locate(Button("OK"))

    Where we want to ``button_wrapper`` to be an instance of``UIWrapper``
    wrapping a button.

    The ``Button`` is a new locator type::

        class Button:
            ''' Locator for locating a push button by label.'''
            def __init__(self, label):
                self.label = label

    Say ``MyUIContainer`` is keeping tracking of the buttons by name in an
    dictionary called ``_buttons``::

        def get_button(wrapper, location):
            return wrapper.target._buttons[location.label]

    The solvers can then be registered for the container UI target::

        registry = TargetRegistry()
        registry.register_solver(
            target_class=MyUIContainer,
            locator_class=Button,
            solver=get_button,
        )

    When the solver is registered this way, the ``wrapper`` argument will be
    an instance of ``UIWrapper`` whose ``target`` attribute is an instance of
    ``MyUIContainer``, and ``location`` will be an instance of ``Button``, as
    is provided via ``UIWrapper.locate``.
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

    def register_handler(self, target_class, interaction_class, handler):
        """ Register a handler for a given target type and interaction type.

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

    def get_handler(self, target_class, interaction_class):
        """ Return a callable for handling an interaction for a given target
        type.

        Parameters
        ----------
        target_class : subclass of type
            The type of a UI target being operated on.
        interaction_class : subclass of type
            Any class.

        Returns
        -------
        handler : callable(UIWrapper, interaction) -> any
            The function to handle the particular interaction on a target.
            ``interaction`` should be an instance of ``interaction_class``.
        """
        return self._interaction_registry.get_value(
            target_class=target_class,
            key=interaction_class,
        )

    def register_solver(self, target_class, locator_class, solver):
        """ Register a solver for resolving the next UI target for the given
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

    def get_solver(self, target_class, locator_class):
        """ Return a callable registered for resolving a location for the
        given target type and locator type.

        Parameters
        ----------
        target_class : subclass of type
            The type of a UI target being operated on.
        locator_class : subclass of type
            Any class.

        Raises
        ------
        LocationNotSupported
        """
        return self._location_registry.get_value(
            target_class=target_class,
            key=locator_class,
        )
