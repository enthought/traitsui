# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Tests for the ShadowGroup class.
"""

import unittest

from traitsui.api import Group
from traitsui.group import ShadowGroup

from traitsui.tests._tools import BaseTestMixin


class TestShadowGroup(BaseTestMixin, unittest.TestCase):
    def setUp(self):
        BaseTestMixin.setUp(self)

    def tearDown(self):
        BaseTestMixin.tearDown(self)

    def test_creation_sets_shadow_first(self):
        group = Group()
        # We end up with a DelegationError if the 'shadow' trait is not set
        # first.  Initialization order is dependent on dictionary order, which
        # we can't control, so we throw in a good number of other traits to
        # increase the chance that some other trait is set first.
        ShadowGroup(
            label="dummy",
            show_border=True,
            show_labels=True,
            show_left=True,
            orientation="horizontal",
            scrollable=True,
            shadow=group,
        )
