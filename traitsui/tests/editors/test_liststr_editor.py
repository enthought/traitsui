# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

"""
Test case for ListStrEditor and ListStrAdapter
"""
import unittest

from traits.has_traits import HasTraits
from traits.trait_types import List, Str
from traitsui.list_str_adapter import ListStrAdapter
from traitsui.tests._tools import BaseTestMixin


class TraitObject(HasTraits):
    list_str = List(Str)


class TestListStrAdapter(BaseTestMixin, unittest.TestCase):
    def setUp(self):
        BaseTestMixin.setUp(self)

    def tearDown(self):
        BaseTestMixin.tearDown(self)

    def test_list_str_adapter_length(self):
        """Test the ListStringAdapter len method"""

        object = TraitObject()
        object.list_str = ["hello"]

        adapter = ListStrAdapter()

        self.assertEqual(adapter.len(object, "list_str"), 1)
        self.assertEqual(adapter.len(None, "list_str"), 0)
