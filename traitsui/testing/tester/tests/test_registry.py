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

from traitsui.testing.tester.target_registry import (
    TargetRegistry,
)
from traitsui.testing.tester.exceptions import (
    InteractionNotSupported,
    LocationNotSupported,
)


class TestInteractionRegistry(unittest.TestCase):

    def test_registry_empty(self):
        registry = TargetRegistry()
        with self.assertRaises(InteractionNotSupported) as exception_context:
            registry.get_handler(None, None)

        self.assertEqual(
            str(exception_context.exception),
            "No handler is found for target None with interaction None. "
            "Supported these: []",
        )

    def test_register_editor_with_action(self):
        registry = TargetRegistry()

        class SpecificEditor:
            pass

        class UserAction:
            pass

        def handler(wrapper, interaction):
            pass

        # when
        registry.register_interaction(
            target_class=SpecificEditor,
            interaction_class=UserAction,
            handler=handler,
        )

        # then
        actual = registry.get_handler(SpecificEditor, UserAction)
        self.assertIs(actual, handler)

    def test_action_not_supported_report_supported_action(self):
        # Test raise InteractionNotSupported contains information about what
        # actions are supported.

        class SpecificEditor:
            pass

        class SpecificEditor2:
            pass

        class UserAction:
            pass

        class UserAction2:
            pass

        class UserAction3:
            pass

        def handler(wrapper, interaction):
            pass

        registry = TargetRegistry()
        registry.register_interaction(SpecificEditor, UserAction, handler)
        registry.register_interaction(SpecificEditor2, UserAction2, handler)
        registry.register_interaction(SpecificEditor2, UserAction3, handler)

        with self.assertRaises(InteractionNotSupported) as exception_context:
            registry.get_handler(SpecificEditor2, None)

        self.assertIn(UserAction2, exception_context.exception.supported)
        self.assertIn(UserAction3, exception_context.exception.supported)
        self.assertNotIn(UserAction, exception_context.exception.supported)

    def test_error_conflict(self):
        # Test the same target + interaction type cannot be registered twice.

        class SpecificEditor:
            pass

        class UserAction:
            pass

        def handler(wrapper, interaction):
            pass

        registry = TargetRegistry()
        registry.register_interaction(SpecificEditor, UserAction, handler)

        with self.assertRaises(ValueError):
            registry.register_interaction(SpecificEditor, UserAction, handler)

    def test_error_get_interaction_doc(self):
        # The registry is empty
        registry = TargetRegistry()
        with self.assertRaises(InteractionNotSupported):
            registry.get_interaction_doc(float, int)

    def test_get_default_interaction_doc(self):

        class Action:
            """Some action."""
            pass

        def handler(wrapper, interaction):
            pass

        registry = TargetRegistry()
        registry.register_interaction(
            target_class=float,
            interaction_class=Action,
            handler=handler,
        )

        actual = registry.get_interaction_doc(
            target_class=float, interaction_class=Action,
        )
        self.assertEqual(actual, "Some action.")


class TestLocationRegistry(unittest.TestCase):

    def test_location_registry_empty(self):
        registry = TargetRegistry()
        with self.assertRaises(LocationNotSupported) as exception_context:
            registry.get_solver(None, None)

        self.assertEqual(exception_context.exception.supported, [])
        self.assertEqual(
            str(exception_context.exception),
            "Location None is not supported for None. Supported these: []",
        )

    def test_register_location(self):

        def solver(wrapper, location):
            return 1

        registry = TargetRegistry()
        registry.register_location(
            target_class=float, locator_class=str, solver=solver)

        self.assertIs(registry.get_solver(float, str), solver)

    def test_register_location_report_existing(self):

        def solver(wrapper, location):
            return 1

        registry = TargetRegistry()
        registry.register_location(
            target_class=float, locator_class=str, solver=solver)

        with self.assertRaises(LocationNotSupported) as exception_context:
            registry.get_solver(float, None)

        self.assertEqual(exception_context.exception.supported, [str])

    def test_get_location_help_default(self):

        class Locator:
            """ Some default documentation."""
            pass

        registry = TargetRegistry()
        registry.register_location(
            target_class=float,
            locator_class=Locator,
            solver=lambda w, l: 1,
        )

        help_text = registry.get_location_doc(
            target_class=float, locator_class=Locator,
        )
        self.assertEqual(help_text, "Some default documentation.")

    def test_error_get_interaction_doc(self):
        # The registry is empty
        registry = TargetRegistry()
        with self.assertRaises(LocationNotSupported):
            registry.get_location_doc(float, int)
