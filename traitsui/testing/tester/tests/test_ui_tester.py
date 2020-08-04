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
from traits.api import (
    Button, Instance, HasTraits, Str,
)
from traits.testing.api import UnittestTools
from traitsui.api import Item, ModelView, View
from traitsui.tests._tools import (
    is_qt,
    is_wx,
    requires_toolkit,
    ToolkitName,
)
from traitsui.testing.tester import command, query
from traitsui.testing.tester.abstract_registry import AbstractRegistry
from traitsui.testing.tester.editor_action_registry import EditorActionRegistry
from traitsui.testing.tester.exceptions import (
    ActionNotSupported,
    EditorNotFound,
)
from traitsui.testing.tester.ui_tester import UITester, UserInteractor


class Order(HasTraits):

    submit_button = Button()

    submit_label = Str("Submit")


class Model(HasTraits):

    order = Instance(Order, ())


class SimpleApplication(ModelView):

    model = Instance(Model)


class TestUITesterCreateUI(unittest.TestCase):
    """ Test UITester.create_ui
    """

    def test_ui_disposed(self):
        tester = UITester()
        order = Order()
        view = View(Item("submit_button"))
        with tester.create_ui(order, dict(view=view)) as ui:
            pass
        self.assertTrue(ui.destroyed)


def get_registry_for_nested_ui():
    """ Return an instance of EditorActionRegistry to support
    ``inspect(query.NestedUI)``.
    """

    def get_nested_ui_in_custom_editor(interactor, action):
        return interactor.editor._ui

    registry = EditorActionRegistry()

    if is_qt():
        from traitsui.qt4.instance_editor import (
            CustomEditor as CustomInstanceEditor
        )
        registry.register(
            editor_class=CustomInstanceEditor,
            action_class=query.NestedUI,
            handler=get_nested_ui_in_custom_editor,
        )

    if is_wx():
        from traitsui.wx.instance_editor import (
            CustomEditor as CustomInstanceEditor
        )
        registry.register(
            editor_class=CustomInstanceEditor,
            action_class=query.NestedUI,
            handler=get_nested_ui_in_custom_editor,
        )
    return registry


@requires_toolkit([ToolkitName.qt, ToolkitName.wx])
class TestUITesterFindEditor(unittest.TestCase):
    """ Test logic for finding an editor."""

    def test_interactor_found_if_editor_found(self):
        tester = UITester()
        view = View(Item("submit_button"))
        with tester.create_ui(Order(), dict(view=view)) as ui:
            interactor = tester.find_by_name(ui, "submit_button")
            self.assertIsInstance(interactor, UserInteractor)

            expected, = ui.get_editors("submit_button")
            self.assertEqual(interactor.editor, expected)

    def test_no_editors_found(self):
        # The view does not have "submit_n_events"
        tester = UITester()
        view = View(Item("submit_button"))
        with tester.create_ui(Order(), dict(view=view)) as ui:
            with self.assertRaises(EditorNotFound) as exception_context:
                tester.find_by_name(ui, "submit_n_events")

        self.assertIn(
            "No editors can be found", str(exception_context.exception),
        )

    def test_multiple_editors_found(self):
        # There may be more than one editor with the same name.
        # find_by_name cannot be used in this case.
        tester = UITester()
        view = View(Item("submit_button"), Item("submit_button"))
        with tester.create_ui(Order(), dict(view=view)) as ui:
            with self.assertRaises(ValueError) as exception_context:
                tester.find_by_name(ui, "submit_button")

        self.assertIn(
            "Found multiple editors", str(exception_context.exception),
        )

    def test_find_by_name_in_nested(self):
        # Test finding an editor nested in an UI of another editor.
        # This requires the NestedUI action to have been implemented.
        order = Order()
        view = View(Item("model.order", style="custom"))
        app = SimpleApplication(model=Model(order=order))
        tester = UITester([get_registry_for_nested_ui()])
        with tester.create_ui(app, dict(view=view)) as ui:
            interactor = (
                tester.find_by_name(ui, "order").find_by_name("submit_label")
            )
            self.assertEqual(interactor.editor.name, "submit_label")
            self.assertEqual(interactor.editor.object, order)


class StubRegistry(AbstractRegistry):

    def __init__(self, get_handler):
        self._get_handler = get_handler

    def get_handler(self, editor_class, action_class):
        return self._get_handler()


class TestUITesterManageRegistry(unittest.TestCase):
    """ Test the logic regarding the order of registries.
    """

    def test_registries_copy(self):
        registries = [StubRegistry(None), StubRegistry(None)]
        tester = UITester(registries)

        # when
        registries.append(StubRegistry(None))

        # then
        # tester is unaffected.
        self.assertEqual(len(tester._registries), 2)

    def test_registry_priority(self):
        # If two registries have a handler for the same editor and action
        # types, the first registry has priority.

        handler1 = mock.Mock()
        handler2 = mock.Mock()
        registry1 = StubRegistry(get_handler=lambda: handler1)
        registry2 = StubRegistry(get_handler=lambda: handler2)

        model = Order()
        tester = UITester([registry2, registry1])
        with tester.create_ui(model) as ui:
            interactor = tester.find_by_name(ui, "submit_label")
            interactor.perform(None)

        self.assertEqual(handler2.call_count, 1)
        self.assertEqual(handler1.call_count, 0)

        # reverse order
        handler1.reset_mock()
        handler2.reset_mock()
        tester = UITester([registry1, registry2])
        with tester.create_ui(model) as ui:
            interactor = tester.find_by_name(ui, "submit_label")
            interactor.perform(None)

        self.assertEqual(handler1.call_count, 1)
        self.assertEqual(handler2.call_count, 0)

    def test_registry_selection(self):
        # If the first registry says it can't handle the action, the next
        # registry is tried.

        def registry1_get_handler():
            raise ActionNotSupported(
                editor_class=None,
                action_class=None,
                supported=[],
            )

        registry1 = StubRegistry(get_handler=registry1_get_handler)
        registry2_handler = mock.Mock()
        registry2 = StubRegistry(get_handler=lambda: registry2_handler)

        model = Order()
        tester = UITester([registry1, registry2])
        with tester.create_ui(model) as ui:
            interactor = tester.find_by_name(ui, "submit_label")
            interactor.perform(None)

        self.assertEqual(registry2_handler.call_count, 1)

    def test_registry_all_declined(self):
        # If none of the registries can support an action, the
        # exception raised provide information on what actions are
        # supported.

        def registry1_get_handler():
            raise ActionNotSupported(
                editor_class=None,
                action_class=None,
                supported=[query.NestedUI],
            )

        def registry2_get_handler():
            raise ActionNotSupported(
                editor_class=None,
                action_class=None,
                supported=[command.MouseClick],
            )

        registry1 = StubRegistry(get_handler=registry1_get_handler)
        registry2 = StubRegistry(get_handler=registry2_get_handler)

        model = Order()
        tester = UITester([registry1, registry2])
        with tester.create_ui(model) as ui:
            interactor = tester.find_by_name(ui, "submit_label")
            with self.assertRaises(ActionNotSupported) as exception_context:
                interactor.perform(None)

        self.assertEqual(
            exception_context.exception.supported,
            [query.NestedUI, command.MouseClick],
        )


class TestUserInteractorWithCustomActionRegistry(unittest.TestCase):
    """ Test logic specific to the _CustomActionRegistry
    """

    def test_inspect_custom_action(self):
        # Test arbitrary extension using CustomAction

        def custom_func(interactor):
            return interactor.editor

        model = Order()
        tester = UITester()
        with tester.create_ui(model) as ui:
            interactor = tester.find_by_name(ui, "submit_label")
            value = interactor.inspect(query.CustomAction(custom_func))
            self.assertIs(value, interactor.editor)

    def test_perform_custom_action(self):
        # Test arbitrary extension using CustomAction
        custom_func = mock.Mock()
        model = Order()
        tester = UITester()
        with tester.create_ui(model) as ui:
            interactor = tester.find_by_name(ui, "submit_label")
            value = interactor.perform(query.CustomAction(custom_func))
            self.assertIsNone(value)
            self.assertEqual(custom_func.call_count, 1)

    def test_unknown_action(self):
        # Test error if the action type is not supported.
        model = Order()
        tester = UITester()
        with tester.create_ui(model) as ui:
            interactor = tester.find_by_name(ui, "submit_label")
            with self.assertRaises(ActionNotSupported) as exception_context:
                interactor.inspect(None)

            self.assertIn(
                "No handler is found ", str(exception_context.exception)
            )
            # CustomAction is supported.
            self.assertIn(
                query.CustomAction,
                exception_context.exception.supported,
            )


@requires_toolkit([ToolkitName.qt, ToolkitName.wx])
class TestUserInteractorEventProcessed(unittest.TestCase, UnittestTools):
    """ Test GUI events are processed and exceptions from the GUI event
    loop are handled.
    """

    def test_event_processed(self):
        # Test GUI events are processed such that the trait is changed.
        gui = GUI()
        model = Order()

        def handler(interactor):
            gui.set_trait_later(model, "submit_button", True)

        view = View(Item("submit_button"))
        tester = UITester()
        with tester.create_ui(model, dict(view=view)) as ui:
            interactor = tester.find_by_name(ui, "submit_button")
            with self.assertTraitChanges(model, "submit_button"):
                interactor.perform(query.CustomAction(handler))

    def test_event_processed_with_exception_captured(self):
        # Test exceptions in the GUI event loop are captured and then cause
        # the test to error.
        gui = GUI()

        def raise_error():
            raise ZeroDivisionError()

        def handler(interactor):
            gui.invoke_later(raise_error)

        model = Order()
        view = View(Item("submit_button"))
        tester = UITester()   # using the _CustomActionRegistry
        with tester.create_ui(model, dict(view=view)) as ui:
            interactor = tester.find_by_name(ui, "submit_button")
            with self.assertRaises(RuntimeError), self.assertLogs("traitsui"):
                interactor.perform(query.CustomAction(handler))
