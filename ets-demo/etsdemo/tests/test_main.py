# (C) Copyright 2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import unittest
from unittest import mock

from pyface.api import GUI

from etsdemo.app import Demo
from etsdemo import main as main_module
from etsdemo.tests.testing import require_gui


def fake_configure_traits(instance):
    ui = instance.edit_traits()
    try:
        GUI.process_events()
    finally:
        ui.dispose()
        GUI.process_events()


def mock_demo_launch():
    """ Mock Demo.configure_traits so that we can open and then close the UI
    for testing the main function.
    """
    return mock.patch.object(Demo, "configure_traits", fake_configure_traits)


class TestMain(unittest.TestCase):

    def setUp(self):
        self.demo_launch_patcher = mock_demo_launch()
        self.demo_launch_patcher.start()

    def tearDown(self):
        self.demo_launch_patcher.stop()

    @require_gui
    def test_main(self):
        # Main function must be launchable with no argument.
        main_module.main()

    def test_create_demo(self):
        # This does not require GUI and it should not fail.
        main_module._create_demo()
