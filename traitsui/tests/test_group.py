# (C) Copyright 2004-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import unittest

from traits.api import Float, HasTraits, Int

from traitsui.api import HGroup, Item, Tabbed, VFold, VGroup, View
from traitsui.testing.api import KeyClick, UITester


class Foo(HasTraits):
    a = Int()
    b = Float()


def get_view(group_type, enabled_visible):
    if enabled_visible == "enabled":
        return View(
            group_type(
                VGroup(
                    HGroup(
                        Item('a')
                    ),
                    label='Fold #1',
                    enabled_when='object.b != 0.0',
                    id="first_fold"
                ),
                VGroup(
                    HGroup(
                        Item('b')
                    ),
                    label='Fold #2',
                    id="second_fold"
                ),
                id="interesting_group"
            )
        )
    else:
        return View(
            group_type(
                VGroup(
                    HGroup(
                        Item('a')
                    ),
                    label='Fold #1',
                    visible_when='object.b != 0.0',
                    id="first_fold"
                ),
                VGroup(
                    HGroup(
                        Item('b')
                    ),
                    label='Fold #2',
                    id="second_fold"
                ),
                id="interesting_group"
            )
        )



class TestTabbed(unittest.TestCase):

    def test_visible_when(self):
        tabbed_visible = Foo()
        view = get_view(Tabbed, "visible")
        tester = UITester()

        with tester.create_ui(tabbed_visible, dict(view=view)) as ui:
            tabbed_fold_group_editor = tester.find_by_id(
                ui, "interesting_group"
            )._target
            q_tab_widget = tabbed_fold_group_editor.container
            # only Tab#2 is available at first
            self.assertEqual(q_tab_widget.count(), 1)

            # change b to != 0.0 so Tab #1 is visible
            b_field = tester.find_by_name(ui, 'b')
            b_field.perform(KeyClick("1"))
            b_field.perform(KeyClick("Enter"))

            self.assertEqual(q_tab_widget.count(), 2)

    def test_enabled_when(self):
        tabbed_enabled = Foo()
        view = get_view(Tabbed, "enabled")
        tester = UITester()

        with tester.create_ui(tabbed_enabled, dict(view=view)) as ui:
            tabbed_fold_group_editor = tester.find_by_id(
                ui, "interesting_group"
            )._target
            q_tab_widget = tabbed_fold_group_editor.container
            # both tabs exist
            self.assertEqual(q_tab_widget.count(), 2)
            # but first is disabled
            self.assertFalse(q_tab_widget.isTabEnabled(0))

            # change b to != 0.0 so Tab #1 is enabled
            b_field = tester.find_by_name(ui, 'b')
            b_field.perform(KeyClick("1"))
            b_field.perform(KeyClick("Enter"))

            self.assertEqual(q_tab_widget.count(), 2)
            self.assertTrue(q_tab_widget.isTabEnabled(0))

class TestFold(unittest.TestCase):

    def test_visible_when(self):
        fold_visible = Foo()
        view = get_view(VFold, "visible")
        tester = UITester()

        with tester.create_ui(fold_visible, dict(view=view)) as ui:
            tabbed_fold_group_editor = tester.find_by_id(
                ui, "interesting_group"
            )._target
            q_tool_box = tabbed_fold_group_editor.container
            # only Fold #2 is available at first
            self.assertEqual(q_tool_box.count(), 1)

            # change b to != 0.0 so Fold #1 is visible
            b_field = tester.find_by_name(ui, 'b')
            b_field.perform(KeyClick("1"))
            b_field.perform(KeyClick("Enter"))

            self.assertEqual(q_tool_box.count(), 2)

    def test_enabled_when(self):
        fold_enabled = Foo()
        view = get_view(VFold, "enabled")
        tester = UITester()

        with tester.create_ui(fold_enabled, dict(view=view)) as ui:
            tabbed_fold_group_editor = tester.find_by_id(
                ui, "interesting_group"
            )._target
            q_tool_box = tabbed_fold_group_editor.container
            # both folds exist
            self.assertEqual(q_tool_box.count(), 2)
            # but first is disabled
            self.assertFalse(q_tool_box.isItemEnabled(0))

            # change b to != 0.0 so Fold #1 is enabled
            b_field = tester.find_by_name(ui, 'b')
            b_field.perform(KeyClick("1"))
            b_field.perform(KeyClick("Enter"))

            self.assertEqual(q_tool_box.count(), 2)
            self.assertTrue(q_tool_box.isItemEnabled(0))
