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

from pyface.api import GUI
from traits.api import (
    Button, Instance, HasTraits, Str,
)
from traitsui.api import Item, ModelView, View
from traitsui.tests._tools import (
    requires_toolkit,
    ToolkitName,
)
from traitsui.testing.tester.ui_tester import (
    UITester,
)
from traitsui.testing.tester.ui_wrapper import (
    UIWrapper,
)


class Order(HasTraits):

    submit_button = Button()

    submit_label = Str("Submit")


class Model(HasTraits):

    order = Instance(Order, ())


class SimpleApplication(ModelView):

    model = Instance(Model)


@requires_toolkit([ToolkitName.qt, ToolkitName.wx])
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

    def test_create_ui_reraise_exception(self):
        tester = UITester()
        order = Order()
        view = View(Item("submit_button"))

        with self.assertRaises(RuntimeError), \
                self.assertLogs("traitsui", level="ERROR"):

            with tester.create_ui(order, dict(view=view)) as ui:

                def raise_error():
                    raise ZeroDivisionError()

                GUI().invoke_later(raise_error)

        self.assertIsNone(ui.control)


@requires_toolkit([ToolkitName.qt, ToolkitName.wx])
class TestUITesterFindEditor(unittest.TestCase):
    """ Test logic for finding a target."""

    def test_interactor_found_if_editor_found(self):
        tester = UITester()
        view = View(Item("submit_button"))
        with tester.create_ui(Order(), dict(view=view)) as ui:
            wrapper = tester.find_by_name(ui, "submit_button")
            self.assertIsInstance(wrapper, UIWrapper)

            expected, = ui.get_editors("submit_button")
            self.assertEqual(wrapper._target, expected)
            self.assertEqual(
                wrapper._registries,
                tester._registries,
            )

    def test_no_editors_found(self):
        # The view does not have "submit_n_events"
        tester = UITester()
        view = View(Item("submit_button"))
        with tester.create_ui(Order(), dict(view=view)) as ui:
            with self.assertRaises(ValueError) as exception_context:
                tester.find_by_name(ui, "submit_n_events")

        self.assertIn(
            "No editors can be found", str(exception_context.exception),
        )

    def test_multiple_editors_found(self):
        # There may be more than one target with the same name.
        # find_by_name cannot be used in this case.
        tester = UITester()
        view = View(Item("submit_button"), Item("submit_button"))
        with tester.create_ui(Order(), dict(view=view)) as ui:
            with self.assertRaises(ValueError) as exception_context:
                tester.find_by_name(ui, "submit_button")

        self.assertIn(
            "Found multiple editors", str(exception_context.exception),
        )

    def test_delay_persisted(self):
        tester = UITester(delay=.01)
        view = View(Item("submit_button"))
        with tester.create_ui(Order(), dict(view=view)) as ui:
            wrapped = tester.find_by_name(ui, "submit_button")
            self.assertEqual(wrapped.delay, .01)

    def test_find_by_id(self):
        tester = UITester(delay=123)
        item1 = Item("submit_button", id="item1")
        item2 = Item("submit_button", id="item2")
        view = View(item1, item2)
        with tester.create_ui(Order(), dict(view=view)) as ui:
            wrapper = tester.find_by_id(ui, "item2")
            self.assertIs(wrapper._target.item, item2)
            self.assertEqual(wrapper._registries, tester._registries)
            self.assertEqual(wrapper.delay, tester.delay)

    def test_find_by_id_multiple(self):
        # The uniqueness is not enforced. The first one is returned.
        tester = UITester()
        item1 = Item("submit_button", id="item1")
        item2 = Item("submit_button", id="item2")
        item3 = Item("submit_button", id="item2")
        view = View(item1, item2, item3)
        with tester.create_ui(Order(), dict(view=view)) as ui:
            wrapper = tester.find_by_id(ui, "item2")
            self.assertIs(wrapper._target.item, item2)
