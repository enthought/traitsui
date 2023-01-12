# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import io
import textwrap
import unittest
from unittest import mock

from pyface.api import GUI

from traits.api import HasTraits, Int
from traits.testing.api import UnittestTools
from traitsui.tests._tools import (
    process_cascade_events,
    requires_toolkit,
    ToolkitName,
)
from traitsui.testing.tester._abstract_target_registry import (
    AbstractTargetRegistry,
)
from traitsui.testing.tester.exceptions import (
    InteractionNotSupported,
    LocationNotSupported,
)
from traitsui.testing.tester.target_registry import (
    TargetRegistry,
)
from traitsui.testing.tester.ui_wrapper import (
    UIWrapper,
)


def example_ui_wrapper(**kwargs):
    """Return an instance of UIWrapper for testing purposes.

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


class StubRegistry(AbstractTargetRegistry):
    """A stub implementation of the AbstractTargetRegistry for testing"""

    def __init__(
        self,
        handler=None,
        solver=None,
        supported_interaction_classes=(),
        supported_locator_classes=(),
        interaction_doc="",
        location_doc="",
    ):
        self.handler = handler
        self.solver = solver
        self.supported_interaction_classes = supported_interaction_classes
        self.supported_locator_classes = supported_locator_classes
        self.interaction_doc = interaction_doc
        self.location_doc = location_doc

    def _get_handler(self, target, interaction):
        if interaction.__class__ not in self.supported_interaction_classes:
            raise InteractionNotSupported(
                target_class=target.__class__,
                interaction_class=interaction.__class__,
                supported=list(self.supported_interaction_classes),
            )
        return self.handler

    def _get_interactions(self, target):
        return set(self.supported_interaction_classes)

    def _get_interaction_doc(self, target, interaction_class):
        return self.interaction_doc

    def _get_solver(self, target, location):
        if location.__class__ not in self.supported_locator_classes:
            raise LocationNotSupported(
                target_class=target.__class__,
                locator_class=location.__class__,
                supported=list(self.supported_locator_classes),
            )
        return self.solver

    def _get_locations(self, target):
        return set(self.supported_locator_classes)

    def _get_location_doc(self, target, locator_class):
        return self.location_doc


# Use of perform/inspect requires the GUI event loop
@requires_toolkit([ToolkitName.qt, ToolkitName.wx])
class TestUIWrapperInteractionRegistries(unittest.TestCase):
    """Test the logic regarding the order of (interaction) registries."""

    def test_registry_priority(self):
        # If two registries have a handler for the same target and interaction
        # types, the first register is used.
        registry1 = StubRegistry(
            handler=lambda w, l: 1,
            supported_interaction_classes=[str],
        )
        registry2 = StubRegistry(
            handler=lambda w, l: 2,
            supported_interaction_classes=[str],
        )

        wrapper = example_ui_wrapper(
            registries=[registry2, registry1],
        )
        value = wrapper.inspect("some string")

        self.assertEqual(value, 2)

        # reverse order
        wrapper = example_ui_wrapper(registries=[registry1, registry2])
        value = wrapper.inspect("some other string")

        self.assertEqual(value, 1)

    def test_registry_selection(self):
        # If the first registry says it can't handle the interaction, the next
        # registry is tried.

        registry1 = StubRegistry()
        registry2_handler = mock.Mock()
        registry2 = StubRegistry(
            handler=registry2_handler,
            supported_interaction_classes=[int],
        )

        wrapper = example_ui_wrapper(
            registries=[registry1, registry2],
        )
        wrapper.perform(123)

        self.assertEqual(registry2_handler.call_count, 1)

    def test_registry_all_declined(self):
        # If none of the registries can support an interaction, the
        # exception raised provide information on what actions are
        # supported.

        wrapper = example_ui_wrapper(
            registries=[
                StubRegistry(supported_interaction_classes=[int]),
                StubRegistry(supported_interaction_classes=[float]),
            ],
        )
        with self.assertRaises(InteractionNotSupported) as exception_context:
            wrapper.perform(None)

        self.assertCountEqual(
            exception_context.exception.supported,
            [int, float],
        )


# Use of locate requires the GUI event loop
@requires_toolkit([ToolkitName.qt, ToolkitName.wx])
class TestUIWrapperLocationRegistry(unittest.TestCase):
    """Test the use of registries with locate."""

    def test_location_registry_priority(self):
        registry1 = StubRegistry(
            solver=lambda w, l: 1,
            supported_locator_classes=[str],
        )
        registry2 = StubRegistry(
            solver=lambda w, l: 2,
            supported_locator_classes=[str],
        )

        wrapper = example_ui_wrapper(
            registries=[registry2, registry1],
        )
        new_wrapper = wrapper.locate("some string")

        self.assertEqual(new_wrapper._target, 2)

        # swap the order
        wrapper = example_ui_wrapper(
            registries=[registry1, registry2],
        )
        new_wrapper = wrapper.locate("some other string")

        self.assertEqual(new_wrapper._target, 1)

    def test_location_registry_selection(self):
        # If the first registry says it can't handle the interaction, the next
        # registry is tried.

        def solver2(wrapper, location):
            return 2

        registry1 = StubRegistry()
        registry2 = StubRegistry(
            solver=solver2,
            supported_locator_classes=[str],
        )

        wrapper = example_ui_wrapper(
            registries=[registry1, registry2],
        )
        new_wrapper = wrapper.locate("some string")

        self.assertEqual(new_wrapper._target, 2)
        self.assertEqual(
            new_wrapper._registries,
            wrapper._registries,
        )

    def test_registry_all_declined(self):
        # If none of the registries can support a location, the
        # exception raised provide information on what actions are
        # supported.

        wrapper = example_ui_wrapper(
            registries=[
                StubRegistry(supported_locator_classes=[int]),
                StubRegistry(supported_locator_classes=[float]),
            ],
        )
        with self.assertRaises(LocationNotSupported) as exception_context:
            wrapper.locate(None)

        self.assertCountEqual(
            exception_context.exception.supported,
            [int, float],
        )


class TestUIWrapperHelp(unittest.TestCase):
    """Test calling UIWrapper.help"""

    def test_help_message(self):
        class Action:
            """Say hello.
            Say bye.
            """

            pass

        class Locator:
            """Return anything you like.
            Good day!
            """

            pass

        registry1 = TargetRegistry()
        registry1.register_interaction(
            target_class=str,
            interaction_class=Action,
            handler=mock.Mock(),
        )
        registry2 = TargetRegistry()
        registry2.register_location(
            target_class=str,
            locator_class=Locator,
            solver=mock.Mock(),
        )

        wrapper = example_ui_wrapper(
            target="dummy", registries=[registry1, registry2]
        )

        # when
        stream = io.StringIO()
        with mock.patch("sys.stdout", stream):
            wrapper.help()

        # then
        self.assertEqual(
            stream.getvalue(),
            textwrap.dedent(
                f"""\
                Interactions
                ------------
                {Action!r}
                    Say hello.
                    Say bye.

                Locations
                ---------
                {Locator!r}
                    Return anything you like.
                    Good day!

            """
            ),
        )

    def test_help_message_priority_interactions(self):
        # The first registry in the list has the highest priority
        # The last registry in the list has the least priority

        high_priority_registry = StubRegistry(
            supported_locator_classes=[str],
            supported_interaction_classes=[float],
            interaction_doc="Interaction: I get a higher priority.",
            location_doc="Location: I get a higher priority.",
        )

        low_priority_registry = StubRegistry(
            supported_locator_classes=[str],
            supported_interaction_classes=[float],
            interaction_doc="Interaction: I get a lower priority.",
            location_doc="Location: I get a lower priority.",
        )

        # Put higher priority registry first.
        wrapper = example_ui_wrapper(
            target="dummy",
            registries=[high_priority_registry, low_priority_registry],
        )

        # when
        stream = io.StringIO()
        with mock.patch("sys.stdout", stream):
            wrapper.help()

        # then
        self.assertEqual(
            stream.getvalue(),
            textwrap.dedent(
                f"""\
                Interactions
                ------------
                {float!r}
                    Interaction: I get a higher priority.

                Locations
                ---------
                {str!r}
                    Location: I get a higher priority.

            """
            ),
        )

    def test_help_message_nothing_is_supported(self):
        registry = TargetRegistry()
        wrapper = example_ui_wrapper(registries=[registry])

        # when
        stream = io.StringIO()
        with mock.patch("sys.stdout", stream):
            wrapper.help()

        # then
        self.assertEqual(
            stream.getvalue(),
            textwrap.dedent(
                """\
                Interactions
                ------------
                No interactions are supported.

                Locations
                ---------
                No locations are supported.

            """
            ),
        )


class NumberHasTraits(HasTraits):
    number = Int()


@requires_toolkit([ToolkitName.qt, ToolkitName.wx])
class TestUIWrapperEventProcessed(unittest.TestCase, UnittestTools):
    """Test GUI events are processed and exceptions from the GUI event
    loop are handled.
    """

    def test_event_processed(self):
        # Test GUI events are processed such that the trait is changed.
        gui = GUI()
        model = NumberHasTraits()

        def handler(wrapper, action):
            gui.set_trait_later(model, "number", 2)

        wrapper = example_ui_wrapper(
            registries=[
                StubRegistry(
                    handler=handler,
                    supported_interaction_classes=[float],
                ),
            ],
        )

        with self.assertTraitChanges(model, "number"):
            wrapper.perform(2.123)

    def test_event_processed_prior_to_resolving_location(self):
        # Test GUI events are processed prior to resolving location
        gui = GUI()
        model = NumberHasTraits()
        gui.set_trait_later(model, "number", 2)

        def solver(wrapper, location):
            return model.number

        wrapper = example_ui_wrapper(
            registries=[
                StubRegistry(
                    solver=solver,
                    supported_locator_classes=[float],
                )
            ],
        )

        new_wrapper = wrapper.locate(4.567)
        self.assertEqual(new_wrapper._target, 2)

    def test_event_processed_with_exception_captured(self):
        # Test exceptions in the GUI event loop are captured and then cause
        # the test to error.
        gui = GUI()

        def raise_error():
            raise ZeroDivisionError()

        def handler(wrapper, action):
            gui.invoke_later(raise_error)

        wrapper = example_ui_wrapper(
            registries=[
                StubRegistry(
                    handler=handler,
                    supported_interaction_classes=[float],
                ),
            ],
        )
        with self.assertRaises(RuntimeError), self.assertLogs("traitsui"):
            wrapper.perform(1.234)

    def test_exception_not_in_gui(self):
        # Exceptions from code executed outside of the event loop are
        # propagated as is.

        def handler(wrapper, action):
            raise ZeroDivisionError()

        wrapper = example_ui_wrapper(
            registries=[
                StubRegistry(
                    handler=handler,
                    supported_interaction_classes=[float],
                ),
            ],
        )

        with self.assertRaises(ZeroDivisionError):
            wrapper.perform(9.99)

    def test_perform_event_processed_optional(self):
        # Allow event processing to be switched off.
        gui = GUI()
        side_effect = mock.Mock()

        def handler(wrapper, action):
            gui.invoke_later(side_effect)

        wrapper = example_ui_wrapper(
            registries=[
                StubRegistry(
                    handler=handler,
                    supported_interaction_classes=[float],
                ),
            ],
            auto_process_events=False,
        )

        # With auto_process_events set to False, events are not automatically
        # processed.
        wrapper.perform(12.345)
        self.addCleanup(process_cascade_events)

        self.assertEqual(side_effect.call_count, 0)

    def test_locate_event_processed_optional(self):
        # Allow event processing to be switched off.
        gui = GUI()
        side_effect = mock.Mock()
        gui.invoke_later(side_effect)
        self.addCleanup(process_cascade_events)

        def solver(wrapper, location):
            return 1

        wrapper = example_ui_wrapper(
            registries=[
                StubRegistry(
                    solver=solver,
                    supported_locator_classes=[float],
                ),
            ],
            auto_process_events=False,
        )

        # With auto_process_events set to False, events are not automatically
        # processed.
        new_wrapper = wrapper.locate(1.234)

        self.assertEqual(side_effect.call_count, 0)
        self.assertFalse(new_wrapper._auto_process_events)
