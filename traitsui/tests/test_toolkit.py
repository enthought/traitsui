# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

from contextlib import contextmanager

import unittest

from traits.trait_base import ETSConfig
import traitsui.toolkit
from traitsui.tests._tools import BaseTestMixin


@contextmanager
def clear_toolkit():
    """If a toolkit has been selected, clear it, resetting on exit"""
    old_ETS_toolkit = ETSConfig._toolkit
    old_traitsui_toolkit = traitsui.toolkit._toolkit
    ETSConfig._toolkit = ""
    traitsui.toolkit._toolkit = None
    try:
        yield
    finally:
        ETSConfig._toolkit = old_ETS_toolkit
        traitsui.toolkit._toolkit = old_traitsui_toolkit


class TestToolkit(BaseTestMixin, unittest.TestCase):
    def setUp(self):
        BaseTestMixin.setUp(self)

    def tearDown(self):
        BaseTestMixin.tearDown(self)

    def test_default_toolkit(self):
        with clear_toolkit():
            # try to import default toolkit - this is just a smoke test
            tk = traitsui.toolkit.toolkit()

            self.assertNotEqual(ETSConfig.toolkit, "")
            self.assertIsInstance(tk, traitsui.toolkit.Toolkit)

    def test_nonstandard_toolkit(self):
        with clear_toolkit():
            # try to import a non-default toolkit
            tk = traitsui.toolkit.toolkit("null")

            self.assertEqual(ETSConfig.toolkit, "null")
            from traitsui.null import toolkit

            self.assertIs(tk, toolkit)

    def test_nonexistent_toolkit(self):
        with clear_toolkit():
            # try to import a non-existent toolkit
            tk = traitsui.toolkit.toolkit("nosuchtoolkit")

            # should fail, and give us a standard toolkit, but don't know which
            # exactly we get what depends on what is installed in test
            # environment
            self.assertTrue(ETSConfig.toolkit in {"null", "qt4", "wx", "qt"})
            self.assertTrue(tk.toolkit in {"null", "qt4", "wx", "qt"})
