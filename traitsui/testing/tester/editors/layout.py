#  Copyright (c) 2005-2020, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
""" This module contains helper functions for working with layouts inside an
editor. For example, converting indices so they count through the layout
appropraitely.
"""


def column_major_to_row_major(index, n, num_rows, num_cols):
    """ Helper function to convert an index of a grid layout so that the
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
    """
    if index > n:
        raise ValueError("Index is higher number of elements in layout")
    # the last entries of the last row can be empty.
    num_empty_entries_last_row = num_cols * num_rows - n

    # if the index of interest extends into the part of the grid where
    # the columns have a missing entry in the last row
    if index > num_rows * (num_cols - num_empty_entries_last_row):
        # break the grid up into 2 grids.  One of size
        # num_rows x (num_cols - num_empty_entries_last_row).  The other
        # of size (num_rows-1) x num_empty_entries_last_row
        num_entries_grid1 = num_rows * (num_cols - num_empty_entries_last_row)
        # find i, j coordinates of the index in grid2 if we counted in
        # column major order
        new_index = index - num_entries_grid1
        i = new_index % (num_rows - 1)
        j = new_index // (num_empty_entries_last_row)
        # convert that back to an index found from row major order and add that
        # to the number of elements from grid 1 that would be counted in row
        # major order
        return (num_cols - num_empty_entries_last_row)*(i+1)  + (i * num_empty_entries_last_row + j)
    else:
        # find i,j coordinates of index if we counted in column major order
        i = index % num_rows
        j = index // num_rows
    # convert that back to an index found from row major order
    return i * num_cols + j
