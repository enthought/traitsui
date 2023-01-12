# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
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

try:
    from pyface.qt import QtWebkit  # noqa: F401

    NO_WEBKIT_OR_WEBENGINE = False
except ImportError:
    try:
        from pyface.qt import QtWebEngine  # noqa: F401

        NO_WEBKIT_OR_WEBENGINE = False
    except ImportError:
        NO_WEBKIT_OR_WEBENGINE = True
from traits.api import HasTraits, Int
from traitsui.api import HelpButton, HGroup, Item, spring, VGroup, View
from traitsui.testing.api import MouseClick, UITester
from traitsui.tests._tools import (
    BaseTestMixin,
    create_ui,
    requires_toolkit,
    ToolkitName,
)

ModalDialogTester = toolkit_object(
    "util.modal_dialog_tester:ModalDialogTester"
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
    @requires_toolkit([ToolkitName.qt])
    @unittest.skipIf(
        NO_WEBKIT_OR_WEBENGINE, "Tests require either QtWebKit or QtWebEngine"
    )
    def test_show_help(self):

        # This help window is not actually modal, when opened it will be the
        # active window not active modal widget
        class MyTester(ModalDialogTester):
            def get_dialog_widget(self):
                return self._qt_app.activeWindow()

        panel = HelpPanel()
        tester = UITester(auto_process_events=False)
        with tester.create_ui(panel) as ui:
            help_button = tester.find_by_id(ui, 'Help')

            def click_help():
                # should not fail
                help_button.perform(MouseClick())

            mdtester = MyTester(click_help)
            mdtester.open_and_run(lambda x: x.click_button(OK))
