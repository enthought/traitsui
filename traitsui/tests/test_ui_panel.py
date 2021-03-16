# (C) Copyright 2004-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Tests to exercise logic for layouts, e.g. VGroup, HGroup.
"""

import unittest

from pyface.toolkit import toolkit_object
from pyface.constant import OK
from traits.api import HasTraits, Int
from traitsui.api import HelpButton, HGroup, Item, spring, VGroup, View
from traitsui.testing.api import MouseClick, UITester
from traitsui.tests._tools import (
    BaseTestMixin,
    create_ui,
    requires_toolkit,
    ToolkitName,
)


class ObjectWithNumber(HasTraits):
    number1 = Int()
    number2 = Int()
    number3 = Int()


class HelpPanel(HasTraits):
    my_int = Int(2, help='this is the help for my int')

    def default_traits_view(self):
        view = View(
            Item(name="my_int"),
            title="HelpPanel",
            buttons=[HelpButton],
        )
        return view


@requires_toolkit([ToolkitName.qt, ToolkitName.wx])
class TestUIPanel(BaseTestMixin, unittest.TestCase):

    def setUp(self):
        BaseTestMixin.setUp(self)

    def tearDown(self):
        BaseTestMixin.tearDown(self)

    def test_grouped_layout_with_springy(self):
        # Regression test for enthought/traitsui#1066
        obj1 = ObjectWithNumber()
        view = View(
            HGroup(
                VGroup(
                    Item("number1"),
                ),
                VGroup(
                    Item("number2"),
                ),
                spring,
            )
        )
        # This should not fail.
        with create_ui(obj1, dict(view=view)):
            pass

    # Regression test for enthought/traitsui#1538
    def test_show_help(self):
        panel = HelpPanel()
        tester = UITester()
        with tester.create_ui(panel) as ui:
            help_button = tester.find_by_id(ui, 'Help')

            # should not fail
            help_button.perform(MouseClick())
