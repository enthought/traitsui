# (C) Copyright 2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import io
import tempfile
import unittest
from unittest import mock

from pyface.api import GUI

from etsdemo.app import Demo
from etsdemo import main as main_module
from etsdemo.tests.testing import (
    mock_iter_entry_points,
    require_gui,
)


def fake_configure_traits(instance):
    ui = instance.edit_traits()
    try:
        GUI.process_events()
    finally:
        try:
            ui.dispose()
        finally:
            GUI.process_events()


def mock_demo_launch():
    """ Mock Demo.configure_traits so that we can open and then close the UI
    for testing the main function.
    """
    return mock.patch.object(Demo, "configure_traits", fake_configure_traits)


class TestMain(unittest.TestCase):
    """ Test main function."""

    @require_gui
    def test_main(self):
        # Main function must be launchable even if there are no data available.
        # In normal running situation, no loggings should be emitted
        argv = ["etsdemo"]
        mocked_io = io.StringIO()
        with mock_iter_entry_points({}), \
                mock_demo_launch(), \
                mocked_io, \
                mock.patch("sys.stdout", mocked_io), \
                mock.patch("sys.stderr", mocked_io), \
                mock.patch("sys.argv", argv):
            main_module.main()
            console_output = mocked_io.getvalue()

        self.assertNotIn("Found 0 resource(s).", console_output)

    @require_gui
    def test_main_with_log(self):
        # Test logging configuration with the main function.
        argv = ["etsdemo", "-v"]
        mocked_io = io.StringIO()
        with mock_iter_entry_points({}), \
                mock_demo_launch(), \
                mocked_io, \
                mock.patch("sys.stdout", mocked_io), \
                mock.patch("sys.stderr", mocked_io), \
                mock.patch("sys.argv", argv):
            main_module.main()
            console_output = mocked_io.getvalue()

        self.assertIn("Found 0 resource(s).", console_output)


class TestCreateDemo(unittest.TestCase):
    """ Test _create_demo """

    def test_create_demo_default_entry_points(self):
        # This does not require GUI and it should not fail.
        # This will load the entry points contributed by the dependencies
        # of etsdemo.
        main_module._create_demo()

    def test_create_demo_with_specific_info(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            infos = [
                {
                    "version": 1,
                    "name": "Pretty Demo",
                    "root": temp_dir,
                },
                {
                    "version": 1,
                    "name": "Delicious Demo",
                    "root": temp_dir,
                }
            ]
            demo = main_module._create_demo(infos)
        children = demo.model.get_children()
        self.assertEqual(len(children), 2)
        child1, child2 = children
        self.assertEqual(child1.nice_name, "Pretty Demo")
        self.assertEqual(child2.nice_name, "Delicious Demo")

    def test_create_demo_with_title(self):
        demo = main_module._create_demo([], "Nice Title")
        self.assertEqual(demo.title, "Nice Title")
