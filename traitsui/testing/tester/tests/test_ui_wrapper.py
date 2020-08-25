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
import unittest
from unittest import mock

from pyface.api import GUI

from traits.api import HasTraits, Int
from traits.testing.api import UnittestTools
from traitsui.tests._tools import (
    requires_toolkit,
    ToolkitName,
)
from traitsui.testing.tester.exceptions import (
    InteractionNotSupported,
    LocationNotSupported,
)
from traitsui.testing.tester.ui_wrapper import (
    UIWrapper,
)


def example_ui_wrapper(**kwargs):
    """ Return an instance of UIWrapper for testing purposes.

    Parameters
    ----------
    **kwargs
        Values to use instead of the default values.

    Returns
    -------
    wrapper: UIWrapper
    """
    values = dict(
        target=None,
        registries=[],
    )
    values.update(kwargs)
    return UIWrapper(**values)


class StubRegistry:

    def __init__(self, handler=None, solver=None):
        self.handler = handler
        self.solver = solver

    def get_handler(self, target_class, interaction_class):
        return self.handler

    def get_solver(self, target_class, locator_class):
        return self.solver


# Use of perform/inspect requires the GUI event loop
@requires_toolkit([ToolkitName.qt, ToolkitName.wx])
class TestUIWrapperInteractionRegistries(unittest.TestCase):
    """ Test the logic regarding the order of (interaction) registries.
    """

    def test_registry_priority(self):
        # If two registries have a handler for the same target and interaction
        # types, the first register is used.
        registry1 = StubRegistry(handler=lambda w, l: 1)
        registry2 = StubRegistry(handler=lambda w, l: 2)

        wrapper = example_ui_wrapper(
            registries=[registry2, registry1],
        )
        value = wrapper.inspect(None)

        self.assertEqual(value, 2)

        # reverse order
        wrapper = example_ui_wrapper(
            registries=[registry1, registry2]
        )
        value = wrapper.inspect(None)

        self.assertEqual(value, 1)

    def test_registry_selection(self):
        # If the first registry says it can't handle the interaction, the next
        # registry is tried.

        class EmptyRegistry:
            def get_handler(self, target_class, interaction_class):
                raise InteractionNotSupported(
                    target_class=None,
                    interaction_class=None,
                    supported=[],
                )

        registry1 = EmptyRegistry()
        registry2_handler = mock.Mock()
        registry2 = StubRegistry(handler=registry2_handler)

        wrapper = example_ui_wrapper(
            registries=[registry1, registry2],
        )
        wrapper.perform(None)

        self.assertEqual(registry2_handler.call_count, 1)

    def test_registry_all_declined(self):
        # If none of the registries can support an interaction, the
        # exception raised provide information on what actions are
        # supported.

        class EmptyRegistry1:

            def get_handler(self, target_class, interaction_class):
                raise InteractionNotSupported(
                    target_class=None,
                    interaction_class=None,
                    supported=[int],
                )

        class EmptyRegistry2:

            def get_handler(self, target_class, interaction_class):
                raise InteractionNotSupported(
                    target_class=None,
                    interaction_class=None,
                    supported=[float],
                )

        wrapper = example_ui_wrapper(
            registries=[EmptyRegistry1(), EmptyRegistry2()],
        )
        with self.assertRaises(InteractionNotSupported) as exception_context:
            wrapper.perform(None)

        self.assertCountEqual(
            exception_context.exception.supported,
            [int, float],
        )


class TestUIWrapperLocationRegistry(unittest.TestCase):
    """ Test the use of registries with locate. """

    def test_location_registry_priority(self):

        registry1 = StubRegistry(solver=lambda w, l: 1)
        registry2 = StubRegistry(solver=lambda w, l: 2)

        wrapper = example_ui_wrapper(
            registries=[registry2, registry1],
        )
        wrapper = wrapper.locate(None)

        self.assertEqual(wrapper.target, 2)

        # swap the order
        wrapper = example_ui_wrapper(
            registries=[registry1, registry2],
        )
        wrapper = wrapper.locate(None)

        self.assertEqual(wrapper.target, 1)

    def test_location_registry_selection(self):
        # If the first registry says it can't handle the interaction, the next
        # registry is tried.

        class EmptyRegistry:
            def get_solver(self, target_class, locator_class):
                raise LocationNotSupported(
                    target_class=None,
                    locator_class=None,
                    supported=[],
                )

        def solver2(wrapper, location):
            return 2

        registry1 = EmptyRegistry()
        registry2 = StubRegistry(solver=solver2)

        wrapper = example_ui_wrapper(
            registries=[registry1, registry2],
        )
        new_wrapper = wrapper.locate(None)

        self.assertEqual(new_wrapper.target, 2)
        self.assertEqual(
            new_wrapper._registries,
            wrapper._registries,
        )

    def test_registry_all_declined(self):
        # If none of the registries can support a location, the
        # exception raised provide information on what actions are
        # supported.

        class EmptyRegistry1:
            def get_solver(self, target_class, locator_class):
                raise LocationNotSupported(
                    target_class=None,
                    locator_class=None,
                    supported=[int],
                )

        class EmptyRegistry2:
            def get_solver(self, target_class, locator_class):
                raise LocationNotSupported(
                    target_class=None,
                    locator_class=None,
                    supported=[float],
                )

        wrapper = example_ui_wrapper(
            registries=[EmptyRegistry1(), EmptyRegistry2()],
        )
        with self.assertRaises(LocationNotSupported) as exception_context:
            wrapper.locate(None)

        self.assertCountEqual(
            exception_context.exception.supported,
            [int, float],
        )


class NumberHasTraits(HasTraits):
    number = Int()


@requires_toolkit([ToolkitName.qt, ToolkitName.wx])
class TestUIWrapperEventProcessed(unittest.TestCase, UnittestTools):
    """ Test GUI events are processed and exceptions from the GUI event
    loop are handled.
    """

    def test_event_processed(self):
        # Test GUI events are processed such that the trait is changed.
        gui = GUI()
        model = NumberHasTraits()

        def handler(wrapper, action):
            gui.set_trait_later(model, "number", 2)

        wrapper = example_ui_wrapper(
            registries=[StubRegistry(handler=handler)],
        )

        with self.assertTraitChanges(model, "number"):
            wrapper.perform(None)

    def test_event_processed_with_exception_captured(self):
        # Test exceptions in the GUI event loop are captured and then cause
        # the test to error.
        gui = GUI()

        def raise_error():
            raise ZeroDivisionError()

        def handler(wrapper, action):
            gui.invoke_later(raise_error)

        wrapper = example_ui_wrapper(
            registries=[StubRegistry(handler=handler)],
        )

        with self.assertRaises(RuntimeError), self.assertLogs("traitsui"):
            wrapper.perform(None)

    def test_exception_not_in_gui(self):
        # Exceptions from code executed outside of the event loop are
        # propagated as is.

        def handler(wrapper, action):
            raise ZeroDivisionError()

        wrapper = example_ui_wrapper(
            registries=[StubRegistry(handler=handler)],
        )

        with self.assertRaises(ZeroDivisionError):
            wrapper.perform(None)
