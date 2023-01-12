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

from traitsui.testing.tester._ui_tester_registry._layout import (
    column_major_to_row_major,
)


class TestLayout(unittest.TestCase):
    def test_column_major_index_too_large(self):
        # Test when the index is too large for the total number of elements
        # The indices would look like:
        # 0  2  3  4
        # 1  /  /  /
        with self.assertRaises(ValueError):
            column_major_to_row_major(
                index=10,
                n=5,
                num_rows=2,
                num_cols=4,
            )

    def test_column_major_index_index_overhanging(self):
        # This is the layout for displaying numbers from 0-9 with column
        # major setup:
        # 0  3  6  8
        # 1  4  7  9
        # 2  5  /  /
        # The index should be populated (row first) in this order:
        # 0, 3, 6, 8, 1, 4, 7, 9, 2, 5
        actual = column_major_to_row_major(
            index=9,
            n=10,
            num_rows=3,
            num_cols=4,
        )
        self.assertEqual(actual, 7)

    def test_column_major_index_in_grid_first_row(self):
        # Test when the index is small enough to be within the upper, filled
        # grid.
        # This is the layout for displaying numbers from 0-9 with column
        # major setup:
        # 0  3  6  8
        # 1  4  7  9
        # 2  5  /  /
        # The index should be populated (row first) in this order:
        # 0, 3, 6, 8, 1, 4, 7, 9, 2, 5
        actual = column_major_to_row_major(
            index=6,
            n=10,
            num_rows=3,
            num_cols=4,
        )
        self.assertEqual(actual, 2)

    def test_column_major_index_in_grid_last_row(self):
        # Test when the index is small enough to be within the upper, filled
        # grid.
        # This is the layout for displaying numbers from 0-9 with column
        # major setup:
        # 0  3  6  8
        # 1  4  7  9
        # 2  5  /  /
        # The index should be populated (row first) in this order:
        # 0, 3, 6, 8, 1, 4, 7, 9, 2, 5
        actual = column_major_to_row_major(
            index=4,
            n=10,
            num_rows=3,
            num_cols=4,
        )
        self.assertEqual(actual, 5)

    def test_column_major_index_last_row(self):
        # Test when the index is in the last row
        # This is the layout for displaying numbers from 0-9 with column
        # major setup:
        # 0  3  6  8
        # 1  4  7  9
        # 2  5  /  /
        # The index should be populated (row first) in this order:
        # 0, 3, 6, 8, 1, 4, 7, 9, 2, 5
        actual = column_major_to_row_major(
            index=2,
            n=10,
            num_rows=3,
            num_cols=4,
        )
        self.assertEqual(actual, 8)

    def test_column_major_index_long_overhang(self):
        # This is the layout for displaying numbers from 0-9 with column
        # major setup:
        # 0  2  3  4
        # 1  /  /  /
        # The index should be populated (row first) in this order:
        # 0, 2, 3, 4, 1
        actual = column_major_to_row_major(
            index=4,
            n=5,
            num_rows=2,
            num_cols=4,
        )
        self.assertEqual(actual, 3)

    def test_column_major_index_full_grid(self):
        # This is the layout for displaying numbers from 0-9 with column
        # major setup:
        # 0  3  6  9   12
        # 1  4  7  10  13
        # 2  5  8  11  14
        # The index should be populated (row first) in this order:
        # 0, 3, 6, 9, 12, 1, 4, 7, 10, 13, 2, 5, 8, 11, 14
        actual = column_major_to_row_major(
            index=11,
            n=15,
            num_rows=3,
            num_cols=5,
        )
        self.assertEqual(actual, 13)
