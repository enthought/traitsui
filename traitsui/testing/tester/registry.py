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


class InteractionRegistry:
    """ A registry for mapping from target type + interaction type to a specific
    implementation for simulating user interaction.

    The interaction type can be a subclass of any type. There are a few
    pre-defined interaction types in
    - ``traitsui.testing.tester.command``
    - ``traitsui.testing.tester.query``

    For example, to simulate clicking a button in TraitsUI's ButtonEditor, the
    implementation for Qt may look like this::

        def mouse_click_qt_button(wrapper, interaction):
            # wrapper is an instance of UIWrapper
            wrapper.target.control.click()

    The functon can then be registered with the target type and an interaction
    type::

        registry = InteractionRegistry()
        registry.register(
            target_class=traitsui.qt4.button_editor.SimpleEditor,
            interaction_class=traitsui.testing.tester.command.MouseClick,
            handler=mouse_click_qt_button,
        )

    Similarly, a wx implementation of clicking a button can be registered
    to the registry (the content of ``mouse_click_wx_button`` is not shown)::

        registry.register(
            target_class=traitsui.wx.button_editor.SimpleEditor,
            interaction_class=traitsui.testing.tester.command.MouseClick,
            handler=mouse_click_wx_button,
        )

    Then this registry can be used with the ``UITester`` and ``UIWrapper`` to
    support ``UIWrapper.perform`` and ``UIWrapper.inspect``.
    """

    def __init__(self):
        self._registry = _TargetToKeyRegistry(
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
        self._registry.register(
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
        return self._registry.get_value(
            target_class=target_class,
            key=interaction_class,
        )


class LocationRegistry:
    """ A registry for mapping from target type + locator type to a specific
    implementation for resolving a new target for furture user interactions
    (or further location resolutions).

    Used for supporting ``UIWrapper.locate``.

    The locator type can be any subclass of ``type``. There are predefined
    locators in ``traitsui.testing.tester.locator``.

    For example, suppose a UI target has a nested UI and a button. Both the
    nested UI and the button are UI targets that can be located in the
    container target.

    Suppose we have a locator type for the nested UI::

        class NestedUI:
            pass

    And there is an enum for the widget type::

        class WidgetType(Enum):
            button = "button"

    The solvers for these locators may look like this::

        def get_nested_ui(wrapper, _):
            return wrapper.target._nested_ui

        def get_widget_by_type(wrapper, location):
            if location == WidgetType.button:
                return wrapper.target._button
            raise ValueError("Other widget type not supported")

    The first argument is an instance of ``UIWrapper`` that wraps the container
    UI target, in this case, the UI target that holds a nested UI and a button.

    The second argument is an instance of the locator type.

    The solvers can then be registered for the container UI target::

        registry = LocationRegistry()
        registry.register(
            target_class=MyUIContainer,
            locator_class=NestedUI,
            solver=get_nested_ui,
        )
        registry.register(
            target_class=MyUIContainer,
            locator_class=WidgetType,
            solver=get_widget_by_type,
        )

    Then this registry can be used with the ``UITester`` and ``UIWrapper`` to
    support ``UIWrapper.locate``. If the nested UI has other locator solvers,
    then it would be possible to do chain location resolutions, like this::

        container.locate(NestedUI()).locate(Index(1))
    """

    def __init__(self):
        """ Initial registry is empty.
        """
        self._registry = _TargetToKeyRegistry(
            exception_maker=(
                lambda target_class, key, available_keys: LocationNotSupported(
                    target_class=target_class,
                    locator_class=key,
                    supported=available_keys,
                )
            ),
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
        self._registry.register(
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
        return self._registry.get_value(
            target_class=target_class,
            key=locator_class,
        )
