# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" This module contains helper functions for working with layouts inside an
editor. For example, converting indices so they count through the layout
appropriately.
"""


def column_major_to_row_major(index, n, num_rows, num_cols):
    """Helper function to convert an index of a grid layout so that the
    index counts over the grid in the correct direction.
    In TraitsUI, grids are typically populated in row major order, however,
    the elements can be assigned to each entry in the grid so that when
    displayed they appear in column major order. To access the correct element
    we may need to convert a column-major based index into a row-major one.

    Parameters
    ----------
    index : int
        the index of interest
    n : int
        The total number of elements in the layout
    num_rows : int
        the number of rows in the layout
    num_cols : int
        the number of columns in the layout

    Returns
    -------
    int
        The converted index (now corresponding to row_major order)

    Notes
    -----
    Since elements are populated in row major order, the resulting grid ends
    up having at most its last row as incomplete. The general approach for the
    algorithm is to find the coordinates as if we had counted through the
    grid in column major order, and then convert that back to a row major
    index. The complications come from the fact that the last row may be
    missing entries.
    Consider the example (n=17, num_row=4, num_cols=5)
    0  4  8  11  14
    1  5  9  12  15
    2  6  10 13  16
    3  7  /  /  /
    Row major order is 0, 4, 11, 14, 1, 5, ...

    If the given index is 7 then we are in a column of the matrix where
    all rows are full.  This corresponds to the else branch below. From here,
    we simply find the (i,j) coordinates of the entry 7 above, with the upper
    left corner representing (0,0).  Thus, (i,j) = (3,1).  Now, to convert
    this to a row major index, we can simply take i * num_cols + j.

    If the given index is 15, then we are in a column where the last row is
    missing an entry.  See the if branch below.  In the case the logic used
    before won't work, because it would expect the grid to be filled. (i.e.
    if one tried to do this in the same way you would get (i,j) = (3,4)).
    To adderess this we break up the grid into two grids:
    0  4     and    8  11  14
    1  5            9  12  15
    2  6            10 13  16
    3  7
    we find the (i2,j2) coordinates of the entry 15 above in grid2, with the
    upper left corner of grid2 representing (0,0). Hence, (i2,j2) = (1,2).
    We then find that index if we had counted in row major order for grid2,
    which would be i2 * num_empty_entries_last_row + j2 = 5, and add that to
    however many elements would need to be counted over from grid one to reach
    element 15 if we had been counting in row major order. Which is
    (num_cols - num_empty_entries_last_row)*(i2+1).
    """
    if index > n:
        raise ValueError("Index is higher number of elements in layout")
    num_empty_entries_last_row = num_cols * num_rows - n
    if num_empty_entries_last_row < 0:
        raise ValueError("n can not be greater than num_cols * num_rows")

    if index > num_rows * (num_cols - num_empty_entries_last_row):
        num_entries_grid1 = num_rows * (num_cols - num_empty_entries_last_row)
        new_index = index - num_entries_grid1
        i2 = new_index % (num_rows - 1)
        j2 = new_index // (num_rows - 1)
        return (num_cols - num_empty_entries_last_row) * (i2 + 1) + (
            i2 * num_empty_entries_last_row + j2
        )
    else:
        i = index % num_rows
        j = index // num_rows
    return i * num_cols + j
