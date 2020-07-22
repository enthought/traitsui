# (C) Copyright 2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import os
import tempfile
import unittest

from etsdemo.loader import (
    __name__ as LOGGER_NAME,
    get_responses,
    response_to_node,
)
from etsdemo.tests.testing import mock_iter_entry_points


def amazing_demo_response(request):
    return {
        "version": 1,
        "name": "Amazing Demo",
        "root": "",
    }


def wonderful_demo_response(request):
    return {
        "version": 1,
        "name": "Wonderful Demo",
        "root": "",
    }


def misbehaving_demo_response(request):
    raise ZeroDivisionError()


# Data to mock the entry points for testing.
# Mapping from distribution names to entry points
GOOD_ENTRY_POINTS = {
    "traitsui": {
        "etsdemo_data": [
            "amazing_demo={}:amazing_demo_response".format(__name__),
            "wonderful_demo={}:wonderful_demo_response".format(__name__),
        ],
    },
}


class TestResponseToNode(unittest.TestCase):
    """ Test conversion from response to node. """

    def test_good_response_to_node(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            with open(os.path.join(temp_dir, "index.rst"), "w"):
                pass
            response = {
                "version": 1,
                "name": "Amazing Demo",
                "root": temp_dir,
            }
            resource = response_to_node(response)
            self.assertEqual(resource.name, temp_dir)
            self.assertEqual(resource.nice_name, "Amazing Demo")
            self.assertTrue(resource.has_children())

    def test_good_response_but_nonexisting_root_to_node(self):
        # If the response refers to a nonexisting root path,
        # it is detected and replaced with a placeholder.
        response = {
            "version": 1,
            "name": "Amazing Demo",
            "root": "I_do_not_exist",
        }
        with self.assertLogs(LOGGER_NAME) as watcher:
            resource = response_to_node(response)
        self.assertEqual(resource.nice_name, "Amazing Demo")
        self.assertFalse(resource.has_children())
        self.assertIn(
            "Unable to load data.", resource.description,
        )
        log_content, = watcher.output
        self.assertIn("TraitError", log_content)

    def test_bad_response_replaced(self):
        # If the response is badly formatted, replace with a placeholder.
        response = {}
        with self.assertLogs(LOGGER_NAME) as watcher:
            resource = response_to_node(response)

        self.assertFalse(resource.has_children())
        self.assertEqual(resource.nice_name, "(Empty)")
        self.assertIn(
            "Unable to load data.",
            resource.description
        )
        log_content, = watcher.output
        self.assertIn("KeyError", log_content)

    def test_bad_response_type_error(self):
        bad_values = [
            None,
            "1",
            1,
            (),
        ]
        for bad_value in bad_values:
            with self.subTest(bad_value=bad_value):
                with self.assertLogs(LOGGER_NAME) as watcher:
                    resource = response_to_node(bad_value)

                self.assertFalse(resource.has_children())
                self.assertEqual(resource.nice_name, "(Empty)")
                self.assertIn(
                    "Unable to load data.",
                    resource.description
                )
                log_content, = watcher.output
                self.assertIn("TypeError", log_content)

    def test_bad_response_missing_name(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            response = {
                "version": 1,
                "root": temp_dir,
            }
            with self.assertLogs(LOGGER_NAME) as watcher:
                resource = response_to_node(response)

            self.assertFalse(resource.has_children())
            self.assertEqual(resource.nice_name, "(Empty)")
            log_content, = watcher.output
            self.assertIn("KeyError: \'name\'", log_content)

    def test_bad_response_missing_version(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            response = {
                "name": "Name",
                "root": temp_dir,
            }
            with self.assertLogs(LOGGER_NAME) as watcher:
                resource = response_to_node(response)

            self.assertFalse(resource.has_children())
            log_content, = watcher.output
            self.assertIn("KeyError: \'version\'", log_content)

    def test_bad_response_bad_version(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            response = {
                "version": 2,
                "name": "Name",
                "root": temp_dir,
            }
            with self.assertLogs(LOGGER_NAME) as watcher:
                resource = response_to_node(response)

            self.assertFalse(resource.has_children())
            log_content, = watcher.output
            self.assertIn("TraitError", log_content)

    def test_bad_response_bad_name_type(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            response = {
                "version": 1,
                "name": 1,
                "root": temp_dir,
            }
            with self.assertLogs(LOGGER_NAME) as watcher:
                resource = response_to_node(response)

            self.assertFalse(resource.has_children())
            log_content, = watcher.output
            self.assertIn("TraitError", log_content)


class TestGetResponse(unittest.TestCase):
    """ Test the routine to obtain resources from entry points."""

    def test_load_good_entry_points(self):
        with mock_iter_entry_points(GOOD_ENTRY_POINTS):
            resources = get_responses()
        expected = [
            amazing_demo_response({}),
            wonderful_demo_response({}),
        ]
        self.assertEqual(resources, expected)

    def test_load_errored_entry_points(self):
        # entry points are contributed by other packages, and running them
        # may fail.
        error_entry_point = {
            "traitsui": {
                "etsdemo_data": [
                    "error_demo={}:misbehaving_demo_response".format(__name__),
                    "amazing_demo={}:amazing_demo_response".format(__name__),
                ],
            },
        }
        with mock_iter_entry_points(error_entry_point):
            with self.assertLogs(LOGGER_NAME) as watcher:
                resources = get_responses()

        self.assertEqual(len(resources), 1)
        log_output, = watcher.output
        self.assertIn("Failed to obtain data from", log_output)

    def test_load_import_error(self):
        # entry points are contributed by other packages, and loading them
        # may fail. In this test, the path is wrong and results in ImportError.
        error_entry_point = {
            "traitsui": {
                "etsdemo_data": [
                    "missing_demo={}:nonexisting_function".format(__name__),
                    "amazing_demo={}:amazing_demo_response".format(__name__),
                ],
            },
        }
        with mock_iter_entry_points(error_entry_point):
            with self.assertLogs(LOGGER_NAME) as watcher:
                resources = get_responses()

        self.assertEqual(len(resources), 1)
        log_output, = watcher.output
        self.assertIn("Failed to load entry point", log_output)
