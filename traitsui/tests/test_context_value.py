# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import unittest

from traits.testing.unittest_tools import UnittestTools
from traits.api import HasTraits, Str

from traitsui.tests._tools import BaseTestMixin
from traitsui.context_value import ContextValue, CVFloat, CVInt, CVStr, CVType


class CVExample(HasTraits):

    cv_float = CVFloat

    cv_int = CVInt

    cv_str = CVStr

    cv_unicode = CVType(Str, something="meta", sync_value="both")


class TestContextvalue(BaseTestMixin, UnittestTools, unittest.TestCase):
    def setUp(self):
        BaseTestMixin.setUp(self)

    def tearDown(self):
        BaseTestMixin.tearDown(self)

    def test_context_value(self):
        cv = ContextValue("trait_name")

        self.assertEqual(cv.name, "trait_name")

    def test_cv_float_constant(self):
        cve = CVExample(cv_float=1.1)

        self.assertEqual(cve.cv_float, 1.1)

    def test_cv_float_context_value(self):
        cv = ContextValue("trait_name")
        cve = CVExample(cv_float=cv)

        self.assertIs(cve.cv_float, cv)

    def test_cv_int_constant(self):
        cve = CVExample(cv_int=1)

        self.assertEqual(cve.cv_int, 1)

    def test_cv_int_context_value(self):
        cv = ContextValue("trait_name")
        cve = CVExample(cv_int=cv)

        self.assertIs(cve.cv_int, cv)

    def test_cv_str_constant(self):
        cve = CVExample(cv_str="test")

        self.assertEqual(cve.cv_str, "test")

    def test_cv_str_context_value(self):
        cv = ContextValue("trait_name")
        cve = CVExample(cv_str=cv)

        self.assertIs(cve.cv_str, cv)

    def test_cv_unicode_constant(self):
        cve = CVExample(cv_unicode="test")

        self.assertEqual(cve.cv_unicode, "test")

    def test_cv_unicode_context_value(self):
        cv = ContextValue("trait_name")
        cve = CVExample(cv_unicode=cv)

        self.assertIs(cve.cv_unicode, cv)

    def test_cv_unicode_not_none(self):
        with self.assertRaises(Exception):
            CVExample(cv_unicode=None)

    def test_metadata(self):
        cve = CVExample()
        t = cve.trait("cv_unicode")

        self.assertEqual(t.something, "meta")
        self.assertEqual(t.sync_value, "both")

        t = cve.trait("cv_float")
        self.assertEqual(t.sync_value, "to")
