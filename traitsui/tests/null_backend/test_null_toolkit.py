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

from traits.api import HasTraits, Int
from traitsui.tests._tools import BaseTestMixin, requires_toolkit, ToolkitName


class TestNullToolkit(BaseTestMixin, unittest.TestCase):
    def setUp(self):
        BaseTestMixin.setUp(self)

    def tearDown(self):
        BaseTestMixin.tearDown(self)

    @requires_toolkit([ToolkitName.null])
    def test_configure_traits_error(self):
        """Verify that configure_traits fails with NotImplementedError."""

        class Test(HasTraits):
            x = Int()

        t = Test()

        with self.assertRaises(NotImplementedError):
            t.configure_traits()
