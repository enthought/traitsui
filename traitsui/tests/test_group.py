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

from traitsui.api import HGroup, Item, Tabbed, VGroup, View
from traitsui.testing.api import KeyClick, UITester


class Foo(HasTraits):

    a = Int
    b = Float
    
    view = View(
        Tabbed(
            VGroup(
                HGroup(
                    Item('a')
                ),
                label='Tab #1',
                visible_when='object.b != 0.0',
                id="first_tab"
            ),
            VGroup(
                HGroup(
                    Item('b')
                ),
                label='Tab #2',
                visible_when='True',
                id="second_tab"
            ),
            id="tabbed_group"
        )
    )


class TestTabbed(unittest.TestCase):

    def test_visible_when(self):
        foo = Foo()
        tester = UITester()

        with tester.create_ui(foo) as ui:
            tabbed_fold_group_editor = tester.find_by_id(
                ui, "tabbed_group"
            )._target
            q_tab_widget = tabbed_fold_group_editor.container
            # only Tab#2 is available at first
            self.assertEqual(q_tab_widget.count(), 1)

            # change b to != 0.0 so Tab #1 is visible
            b_field = tester.find_by_name(ui, 'b')
            b_field.perform(KeyClick("1"))
            b_field.perform(KeyClick("Enter"))

            self.assertEqual(q_tab_widget.count(), 2)
