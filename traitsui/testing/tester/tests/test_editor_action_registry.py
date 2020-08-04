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

from traitsui.editor import Editor
from traitsui.testing.tester.editor_action_registry import EditorActionRegistry
from traitsui.testing.tester.exceptions import ActionNotSupported


class TestEditorActionRegistry(unittest.TestCase):

    def test_registry_empty(self):
        registry = EditorActionRegistry()
        with self.assertRaises(ActionNotSupported) as exception_context:
            registry.get_handler(None, None)

        self.assertEqual(
            str(exception_context.exception),
            "No handler is found for editor None with action None. "
            "Supported these: []",
        )

    def test_register_editor_with_action(self):
        registry = EditorActionRegistry()

        class SpecificEditor(Editor):
            pass

        class UserAction:
            pass

        def handler(interactor, action):
            pass

        # when
        registry.register(SpecificEditor, UserAction, handler)

        # then
        actual = registry.get_handler(SpecificEditor, UserAction)
        self.assertIs(actual, handler)

    def test_action_not_supported_report_supported_action(self):
        # Test raise ActionNotSupported contains information about what
        # actions are supported.

        class SpecificEditor(Editor):
            pass

        class SpecificEditor2(Editor):
            pass

        class UserAction:
            pass

        class UserAction2:
            pass

        class UserAction3:
            pass

        def handler(interactor, action):
            pass

        registry = EditorActionRegistry()
        registry.register(SpecificEditor, UserAction, handler)
        registry.register(SpecificEditor2, UserAction2, handler)
        registry.register(SpecificEditor2, UserAction3, handler)

        with self.assertRaises(ActionNotSupported) as exception_context:
            registry.get_handler(SpecificEditor2, None)

        self.assertIn(UserAction2, exception_context.exception.supported)
        self.assertIn(UserAction3, exception_context.exception.supported)
        self.assertNotIn(UserAction, exception_context.exception.supported)

    def test_error_conflict(self):
        # Test the same editor + action type cannot be registered twice.

        class SpecificEditor(Editor):
            pass

        class UserAction:
            pass

        def handler(interactor, action):
            pass

        registry = EditorActionRegistry()
        registry.register(SpecificEditor, UserAction, handler)

        with self.assertRaises(ValueError):
            registry.register(SpecificEditor, UserAction, handler)
