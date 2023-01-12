# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

from unittest import TestCase

from traitsui.helper import compute_column_widths
from traitsui.tests._tools import BaseTestMixin


class TestComputeColumnWidths(BaseTestMixin, TestCase):
    def setUp(self):
        BaseTestMixin.setUp(self)

    def tearDown(self):
        BaseTestMixin.tearDown(self)

    def test_all_default(self):
        available_space = 200
        requested = [-1, -1, -1, -1]

        widths = compute_column_widths(available_space, requested, None, None)

        self.assertEqual(widths, [50, 50, 50, 50])

    def test_all_fixed(self):
        available_space = 200
        requested = [10, 50, 40, 20]

        widths = compute_column_widths(available_space, requested, None, None)

        self.assertEqual(widths, [10, 50, 40, 20])

    def test_all_fixed_too_wide(self):
        available_space = 100
        requested = [10, 50, 40, 20]

        widths = compute_column_widths(available_space, requested, None, None)

        self.assertEqual(widths, [10, 50, 40, 20])

    def test_all_weighted(self):
        available_space = 200
        requested = [0.3, 0.2, 0.25, 0.25]

        widths = compute_column_widths(available_space, requested, None, None)

        self.assertEqual(widths, [60, 40, 50, 50])

    def test_all_weighted_default_min(self):
        available_space = 200
        requested = [0.4, 0.1, 0.1, 0.4]

        widths = compute_column_widths(available_space, requested, None, None)

        self.assertEqual(widths, [70, 30, 30, 70])

    def test_mixed(self):
        available_space = 200
        requested = [0.5, 50, 25, 0.75]

        widths = compute_column_widths(available_space, requested, None, None)

        self.assertEqual(widths, [50, 50, 25, 75])

    def test_mixed_too_wide(self):
        available_space = 100
        requested = [0.5, 50, 25, 0.75]

        widths = compute_column_widths(available_space, requested, None, None)

        self.assertEqual(widths, [30, 50, 25, 30])

    def test_user_widths(self):
        available_space = 225
        requested = [0.5, 50, 25, 0.75]
        user_widths = [None, None, 50, None]

        widths = compute_column_widths(
            available_space, requested, None, user_widths
        )

        self.assertEqual(widths, [50, 50, 50, 75])

    def test_min_widths(self):
        available_space = 225
        requested = [0.5, 50, 0.25, 0.75]
        min_widths = [30, 100, 50, 30]

        widths = compute_column_widths(
            available_space, requested, min_widths, None
        )

        self.assertEqual(widths, [50, 50, 50, 75])

    def test_user_and_min_widths(self):
        available_space = 200
        requested = [0.5, 50, 0.25, 0.75]
        min_widths = [30, 100, 50, 30]
        user_widths = [None, 75, 25, 50]

        widths = compute_column_widths(
            available_space, requested, min_widths, user_widths
        )

        self.assertEqual(widths, [50, 75, 25, 50])
