#  Copyright (c) 2015, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt

import nose
import numpy as np
from numpy.testing import assert_array_equal

try:
    from pandas import DataFrame
except ImportError as exc:
    print "Can't import Pandas: skipping"
    raise nose.SkipTest

from traits.api import HasTraits, Instance

from traitsui.item import Item
from traitsui.ui_editors.data_frame_editor import (
    DataFrameEditor, DataFrameAdapter)
from traitsui.view import View

from traitsui.tests._tools import store_exceptions_on_all_threads


class DataFrameViewer(HasTraits):

    data = Instance('pandas.core.frame.DataFrame')

    view = View(
        Item('data', editor=DataFrameEditor())
    )

def sample_data():
    data = [[ 0,  1,  2],
            [ 3,  4,  5],
            [ 6,  7,  8],
            [ 9, 10, 11]]
    df = DataFrame(data, index=['one', 'two', 'three', 'four'],
                   columns=['X', 'Y', 'Z'])
    viewer = DataFrameViewer(data=df)
    return viewer

def sample_data_numerical_index():
    data = [[ 0,  1,  2],
            [ 3,  4,  5],
            [ 6,  7,  8],
            [ 9, 10, 11]]
    df = DataFrame(data, index=range(1,5),
                   columns=['X', 'Y', 'Z'])
    viewer = DataFrameViewer(data=df)
    return viewer


def test_adapter_get_item():
    viewer = sample_data()
    adapter = DataFrameAdapter()

    item_0_df = adapter.get_item(viewer, 'data', 0)

    assert_array_equal(item_0_df.values, [[0,  1,  2]])
    assert_array_equal(item_0_df.columns, ['X', 'Y', 'Z'])
    assert item_0_df.index[0] == 'one'


def test_adapter_empty_dataframe():
    data = DataFrame()
    viewer = DataFrameViewer(data=data)
    adapter = DataFrameAdapter()

    item_0_df = adapter.get_item(viewer, 'data', 0)

    assert_array_equal(item_0_df.values, np.array([]).reshape(0, 0))
    assert_array_equal(item_0_df.columns, [])


def test_adapter_no_rows():
    data = DataFrame(columns=['X', 'Y', 'Z'])
    viewer = DataFrameViewer(data=data)
    adapter = DataFrameAdapter()

    item_0_df = adapter.get_item(viewer, 'data', 0)

    assert_array_equal(item_0_df.values, np.array([]).reshape(0, 3))
    assert_array_equal(item_0_df.columns, ['X', 'Y', 'Z'])


def test_adapter_get_item_numerical():
    viewer = sample_data_numerical_index()
    adapter = DataFrameAdapter()

    item_0_df = adapter.get_item(viewer, 'data', 0)

    assert_array_equal(item_0_df.values, [[0,  1,  2]])
    assert_array_equal(item_0_df.columns, ['X', 'Y', 'Z'])
    assert item_0_df.index[0] == 1


def test_adapter_delete_start():
    viewer = sample_data()
    adapter = DataFrameAdapter()

    adapter.delete(viewer, 'data', 0)
    data = viewer.data

    assert_array_equal(data.values,
                       [[ 3,  4,  5],
                        [ 6,  7,  8],
                        [ 9, 10, 11]])
    assert_array_equal(data.columns, ['X', 'Y', 'Z'])
    assert_array_equal(data.index, ['two', 'three', 'four'])


def test_adapter_delete_start_numerical_index():
    viewer = sample_data_numerical_index()
    adapter = DataFrameAdapter()

    adapter.delete(viewer, 'data', 0)
    data = viewer.data

    assert_array_equal(data.values,
                       [[ 3,  4,  5],
                        [ 6,  7,  8],
                        [ 9, 10, 11]])
    assert_array_equal(data.columns, ['X', 'Y', 'Z'])
    assert_array_equal(data.index, [2, 3, 4])


def test_adapter_delete_middle():
    viewer = sample_data()
    adapter = DataFrameAdapter()

    adapter.delete(viewer, 'data', 1)
    data = viewer.data

    assert_array_equal(data.values,
                       [[ 0,  1,  2],
                        [ 6,  7,  8],
                        [ 9, 10, 11]])
    assert_array_equal(data.columns, ['X', 'Y', 'Z'])
    assert_array_equal(data.index, ['one', 'three', 'four'])


def test_adapter_delete_middle_numerical_index():
    viewer = sample_data_numerical_index()
    adapter = DataFrameAdapter()

    adapter.delete(viewer, 'data', 1)
    data = viewer.data

    assert_array_equal(data.values,
                       [[ 0,  1,  2],
                        [ 6,  7,  8],
                        [ 9, 10, 11]])
    assert_array_equal(data.columns, ['X', 'Y', 'Z'])
    assert_array_equal(data.index, [1, 3, 4])


def test_adapter_delete_end():
    viewer = sample_data()
    adapter = DataFrameAdapter()

    adapter.delete(viewer, 'data', 3)
    data = viewer.data

    assert_array_equal(data.values,
                       [[ 0,  1,  2],
                        [ 3,  4,  5],
                        [ 6,  7,  8]])
    assert_array_equal(data.columns, ['X', 'Y', 'Z'])
    assert_array_equal(data.index, ['one', 'two', 'three'])


def test_adapter_delete_end_numerical_index():
    viewer = sample_data_numerical_index()
    adapter = DataFrameAdapter()

    adapter.delete(viewer, 'data', 3)
    data = viewer.data

    assert_array_equal(data.values,
                       [[ 0,  1,  2],
                        [ 3,  4,  5],
                        [ 6,  7,  8]])
    assert_array_equal(data.columns, ['X', 'Y', 'Z'])
    assert_array_equal(data.index, [1, 2, 3])


def test_adapter_insert_start():
    viewer = sample_data()
    adapter = DataFrameAdapter()
    item = DataFrame([[-3, -2, -1]], index=['new'], columns=['X', 'Y', 'Z'])

    adapter.insert(viewer, 'data', 0, item)
    data = viewer.data

    assert_array_equal(data.values,
                       [[-3, -2, -1],
                        [ 0,  1,  2],
                        [ 3,  4,  5],
                        [ 6,  7,  8],
                        [ 9, 10, 11]])
    assert_array_equal(data.columns, ['X', 'Y', 'Z'])
    assert_array_equal(data.index, ['new', 'one', 'two', 'three', 'four'])


def test_adapter_insert_start_numerical_index():
    viewer = sample_data_numerical_index()
    adapter = DataFrameAdapter()
    item = DataFrame([[-3, -2, -1]], index=[0], columns=['X', 'Y', 'Z'])

    adapter.insert(viewer, 'data', 0, item)
    data = viewer.data

    assert_array_equal(data.values,
                       [[-3, -2, -1],
                        [ 0,  1,  2],
                        [ 3,  4,  5],
                        [ 6,  7,  8],
                        [ 9, 10, 11]])
    assert_array_equal(data.columns, ['X', 'Y', 'Z'])
    assert_array_equal(data.index, [0, 1, 2, 3 ,4])


def test_adapter_insert_middle():
    viewer = sample_data()
    adapter = DataFrameAdapter()
    item = DataFrame([[-3, -2, -1]], index=['new'], columns=['X', 'Y', 'Z'])

    adapter.insert(viewer, 'data', 1, item)
    data = viewer.data

    assert_array_equal(data.values,
                       [[ 0,  1,  2],
                        [-3, -2, -1],
                        [ 3,  4,  5],
                        [ 6,  7,  8],
                        [ 9, 10, 11]])
    assert_array_equal(data.columns, ['X', 'Y', 'Z'])
    assert_array_equal(data.index, ['one', 'new', 'two', 'three', 'four'])


def test_adapter_insert_middle_numerical_index():
    viewer = sample_data_numerical_index()
    adapter = DataFrameAdapter()
    item = DataFrame([[-3, -2, -1]], index=[0], columns=['X', 'Y', 'Z'])

    adapter.insert(viewer, 'data', 1, item)
    data = viewer.data

    assert_array_equal(data.values,
                       [[ 0,  1,  2],
                        [-3, -2, -1],
                        [ 3,  4,  5],
                        [ 6,  7,  8],
                        [ 9, 10, 11]])
    assert_array_equal(data.columns, ['X', 'Y', 'Z'])
    assert_array_equal(data.index, [1, 0, 2, 3, 4])


def test_adapter_insert_end():
    viewer = sample_data()
    adapter = DataFrameAdapter()
    item = DataFrame([[-3, -2, -1]], index=['new'], columns=['X', 'Y', 'Z'])

    adapter.insert(viewer, 'data', 5, item)
    data = viewer.data

    assert_array_equal(data.values,
                       [[ 0,  1,  2],
                        [ 3,  4,  5],
                        [ 6,  7,  8],
                        [ 9, 10, 11],
                        [-3, -2, -1]])
    assert_array_equal(data.columns, ['X', 'Y', 'Z'])
    assert_array_equal(data.index, ['one', 'two', 'three', 'four', 'new'])


def test_adapter_insert_end_numerical_index():
    viewer = sample_data_numerical_index()
    adapter = DataFrameAdapter()
    item = DataFrame([[-3, -2, -1]], index=[0], columns=['X', 'Y', 'Z'])

    adapter.insert(viewer, 'data', 5, item)
    data = viewer.data

    assert_array_equal(data.values,
                       [[ 0,  1,  2],
                        [ 3,  4,  5],
                        [ 6,  7,  8],
                        [ 9, 10, 11],
                        [-3, -2, -1]])
    assert_array_equal(data.columns, ['X', 'Y', 'Z'])
    assert_array_equal(data.index, [1, 2, 3, 4, 0])


def test_data_frame_editor():
    viewer = sample_data()
    with store_exceptions_on_all_threads():
        ui = viewer.edit_traits()
        ui.dispose()

def test_data_frame_editor_numerical_index():
    viewer = sample_data_numerical_index()
    with store_exceptions_on_all_threads():
        ui = viewer.edit_traits()
        ui.dispose()
