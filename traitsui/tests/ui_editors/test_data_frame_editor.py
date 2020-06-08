#  Copyright (c) 2015, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt

import unittest
import numpy as np
from numpy.testing import assert_array_equal


try:
    from pandas import DataFrame
except ImportError:
    raise unittest.SkipTest("Can't import Pandas: skipping")

from traits.api import Event, HasTraits, Instance

from traitsui.item import Item
from traitsui.ui_editors.data_frame_editor import (
    DataFrameEditor,
    DataFrameAdapter,
)
from traitsui.view import View

from traitsui.tests._tools import (
    create_ui,
    store_exceptions_on_all_threads,
    skip_if_null,
)


class DataFrameViewer(HasTraits):

    data = Instance("pandas.core.frame.DataFrame")

    view = View(Item("data", editor=DataFrameEditor(), width=400))


format_mapping_view = View(
    Item(
        "data",
        editor=DataFrameEditor(formats={"X": "%05d", "Y": "%s"}),
        width=400,
    )
)


font_mapping_view = View(
    Item(
        "data",
        editor=DataFrameEditor(fonts={"X": "Courier 10 bold", "Y": "Swiss"}),
        width=400,
    )
)


columns_view = View(
    Item(
        "data",
        editor=DataFrameEditor(columns=["X", ("Zed", "Z"), "missing"]),  # noqa
        width=400,
    )
)

DATA = [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9, 10, 11]]


def sample_data():
    df = DataFrame(
        DATA, index=["one", "two", "three", "four"], columns=["X", "Y", "Z"]
    )
    viewer = DataFrameViewer(data=df)
    return viewer


def sample_data_numerical_index():
    df = DataFrame(DATA, index=list(range(1, 5)), columns=["X", "Y", "Z"])
    viewer = DataFrameViewer(data=df)
    return viewer


def sample_text_data():
    data = [[0, 1, "two"], [3, 4, "five"], [6, 7, "eight"], [9, 10, "eleven"]]
    df = DataFrame(
        data, index=["one", "two", "three", "four"], columns=["X", "Y", "Z"]
    )
    viewer = DataFrameViewer(data=df)
    return viewer


class TestDataFrameEditor(unittest.TestCase):

    @skip_if_null
    def test_adapter_get_item(self):
        viewer = sample_data()
        adapter = DataFrameAdapter()

        item_0_df = adapter.get_item(viewer, "data", 0)

        assert_array_equal(item_0_df.values, [[0, 1, 2]])
        assert_array_equal(item_0_df.columns, ["X", "Y", "Z"])
        self.assertEqual(item_0_df.index[0], "one")

    @skip_if_null
    def test_adapter_empty_dataframe(self):
        data = DataFrame()
        viewer = DataFrameViewer(data=data)
        adapter = DataFrameAdapter()

        item_0_df = adapter.get_item(viewer, "data", 0)

        assert_array_equal(item_0_df.values, np.array([]).reshape(0, 0))
        assert_array_equal(item_0_df.columns, [])

    @skip_if_null
    def test_adapter_no_rows(self):
        data = DataFrame(columns=["X", "Y", "Z"])
        viewer = DataFrameViewer(data=data)
        adapter = DataFrameAdapter()

        item_0_df = adapter.get_item(viewer, "data", 0)

        assert_array_equal(item_0_df.values, np.array([]).reshape(0, 3))
        assert_array_equal(item_0_df.columns, ["X", "Y", "Z"])

    @skip_if_null
    def test_adapter_get_item_numerical(self):
        viewer = sample_data_numerical_index()
        adapter = DataFrameAdapter()

        item_0_df = adapter.get_item(viewer, "data", 0)

        assert_array_equal(item_0_df.values, [[0, 1, 2]])
        assert_array_equal(item_0_df.columns, ["X", "Y", "Z"])
        self.assertEqual(item_0_df.index[0], 1)

    @skip_if_null
    def test_adapter_delete_start(self):
        viewer = sample_data()
        adapter = DataFrameAdapter()

        adapter.delete(viewer, "data", 0)
        data = viewer.data

        assert_array_equal(data.values, [[3, 4, 5], [6, 7, 8], [9, 10, 11]])
        assert_array_equal(data.columns, ["X", "Y", "Z"])
        assert_array_equal(data.index, ["two", "three", "four"])

    @skip_if_null
    def test_adapter_delete_start_numerical_index(self):
        viewer = sample_data_numerical_index()
        adapter = DataFrameAdapter()

        adapter.delete(viewer, "data", 0)
        data = viewer.data

        assert_array_equal(data.values, [[3, 4, 5], [6, 7, 8], [9, 10, 11]])
        assert_array_equal(data.columns, ["X", "Y", "Z"])
        assert_array_equal(data.index, [2, 3, 4])

    @skip_if_null
    def test_adapter_delete_middle(self):
        viewer = sample_data()
        adapter = DataFrameAdapter()

        adapter.delete(viewer, "data", 1)
        data = viewer.data

        assert_array_equal(data.values, [[0, 1, 2], [6, 7, 8], [9, 10, 11]])
        assert_array_equal(data.columns, ["X", "Y", "Z"])
        assert_array_equal(data.index, ["one", "three", "four"])

    @skip_if_null
    def test_adapter_delete_middle_numerical_index(self):
        viewer = sample_data_numerical_index()
        adapter = DataFrameAdapter()

        adapter.delete(viewer, "data", 1)
        data = viewer.data

        assert_array_equal(data.values, [[0, 1, 2], [6, 7, 8], [9, 10, 11]])
        assert_array_equal(data.columns, ["X", "Y", "Z"])
        assert_array_equal(data.index, [1, 3, 4])

    @skip_if_null
    def test_adapter_delete_end(self):
        viewer = sample_data()
        adapter = DataFrameAdapter()

        adapter.delete(viewer, "data", 3)
        data = viewer.data

        assert_array_equal(data.values, [[0, 1, 2], [3, 4, 5], [6, 7, 8]])
        assert_array_equal(data.columns, ["X", "Y", "Z"])
        assert_array_equal(data.index, ["one", "two", "three"])

    @skip_if_null
    def test_adapter_delete_end_numerical_index(self):
        viewer = sample_data_numerical_index()
        adapter = DataFrameAdapter()

        adapter.delete(viewer, "data", 3)
        data = viewer.data

        assert_array_equal(data.values, [[0, 1, 2], [3, 4, 5], [6, 7, 8]])
        assert_array_equal(data.columns, ["X", "Y", "Z"])
        assert_array_equal(data.index, [1, 2, 3])

    @skip_if_null
    def test_adapter_insert_start(self):
        viewer = sample_data()
        adapter = DataFrameAdapter()
        item = DataFrame(
            [[-3, -2, -1]], index=["new"], columns=["X", "Y", "Z"]
        )

        adapter.insert(viewer, "data", 0, item)
        data = viewer.data

        assert_array_equal(
            data.values,
            [[-3, -2, -1], [0, 1, 2], [3, 4, 5], [6, 7, 8], [9, 10, 11]],
        )
        assert_array_equal(data.columns, ["X", "Y", "Z"])
        assert_array_equal(data.index, ["new", "one", "two", "three", "four"])

    @skip_if_null
    def test_adapter_insert_start_numerical_index(self):
        viewer = sample_data_numerical_index()
        adapter = DataFrameAdapter()
        item = DataFrame([[-3, -2, -1]], index=[0], columns=["X", "Y", "Z"])

        adapter.insert(viewer, "data", 0, item)
        data = viewer.data

        assert_array_equal(
            data.values,
            [[-3, -2, -1], [0, 1, 2], [3, 4, 5], [6, 7, 8], [9, 10, 11]],
        )
        assert_array_equal(data.columns, ["X", "Y", "Z"])
        assert_array_equal(data.index, [0, 1, 2, 3, 4])

    @skip_if_null
    def test_adapter_insert_middle(self):
        viewer = sample_data()
        adapter = DataFrameAdapter()
        item = DataFrame(
            [[-3, -2, -1]], index=["new"], columns=["X", "Y", "Z"]
        )

        adapter.insert(viewer, "data", 1, item)
        data = viewer.data

        assert_array_equal(
            data.values,
            [[0, 1, 2], [-3, -2, -1], [3, 4, 5], [6, 7, 8], [9, 10, 11]],
        )
        assert_array_equal(data.columns, ["X", "Y", "Z"])
        assert_array_equal(data.index, ["one", "new", "two", "three", "four"])

    @skip_if_null
    def test_adapter_insert_middle_numerical_index(self):
        viewer = sample_data_numerical_index()
        adapter = DataFrameAdapter()
        item = DataFrame([[-3, -2, -1]], index=[0], columns=["X", "Y", "Z"])

        adapter.insert(viewer, "data", 1, item)
        data = viewer.data

        assert_array_equal(
            data.values,
            [[0, 1, 2], [-3, -2, -1], [3, 4, 5], [6, 7, 8], [9, 10, 11]],
        )
        assert_array_equal(data.columns, ["X", "Y", "Z"])
        assert_array_equal(data.index, [1, 0, 2, 3, 4])

    @skip_if_null
    def test_adapter_insert_end(self):
        viewer = sample_data()
        adapter = DataFrameAdapter()
        item = DataFrame(
            [[-3, -2, -1]], index=["new"], columns=["X", "Y", "Z"]
        )

        adapter.insert(viewer, "data", 5, item)
        data = viewer.data

        assert_array_equal(
            data.values,
            [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9, 10, 11], [-3, -2, -1]],
        )
        assert_array_equal(data.columns, ["X", "Y", "Z"])
        assert_array_equal(data.index, ["one", "two", "three", "four", "new"])

    @skip_if_null
    def test_adapter_insert_end_numerical_index(self):
        viewer = sample_data_numerical_index()
        adapter = DataFrameAdapter()
        item = DataFrame([[-3, -2, -1]], index=[0], columns=["X", "Y", "Z"])

        adapter.insert(viewer, "data", 5, item)
        data = viewer.data

        assert_array_equal(
            data.values,
            [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9, 10, 11], [-3, -2, -1]],
        )
        assert_array_equal(data.columns, ["X", "Y", "Z"])
        assert_array_equal(data.index, [1, 2, 3, 4, 0])

    @skip_if_null
    def test_data_frame_editor(self):
        viewer = sample_data()
        with store_exceptions_on_all_threads():
            ui = viewer.edit_traits()
            ui.dispose()

    @skip_if_null
    def test_data_frame_editor_alternate_adapter(self):
        class AlternateAdapter(DataFrameAdapter):
            pass

        alternate_adapter_view = View(
            Item(
                "data",
                editor=DataFrameEditor(adapter=AlternateAdapter()),
                width=400,
            )
        )
        viewer = sample_data()
        with store_exceptions_on_all_threads():
            ui = viewer.edit_traits(view=alternate_adapter_view)
            ui.dispose()

    @skip_if_null
    def test_data_frame_editor_numerical_index(self):
        viewer = sample_data_numerical_index()
        with store_exceptions_on_all_threads():
            ui = viewer.edit_traits()
            ui.dispose()

    @skip_if_null
    def test_data_frame_editor_text_data(self):
        viewer = sample_text_data()
        with store_exceptions_on_all_threads():
            ui = viewer.edit_traits()
            ui.dispose()

    @skip_if_null
    def test_data_frame_editor_format_mapping(self):
        viewer = sample_data()
        with store_exceptions_on_all_threads():
            ui = viewer.edit_traits(view=format_mapping_view)
            ui.dispose()

    @skip_if_null
    def test_data_frame_editor_font_mapping(self):
        viewer = sample_data()
        with store_exceptions_on_all_threads():
            ui = viewer.edit_traits(view=font_mapping_view)
            ui.dispose()

    @skip_if_null
    def test_data_frame_editor_columns(self):
        viewer = sample_data()
        with store_exceptions_on_all_threads():
            ui = viewer.edit_traits(view=columns_view)
            ui.dispose()

    @skip_if_null
    def test_data_frame_editor_with_update_refresh(self):
        class DataFrameViewer(HasTraits):
            data = Instance(DataFrame)
            df_updated = Event()
            view = View(
                Item("data", editor=DataFrameEditor(update="df_updated"))
            )

        df = DataFrame(
            DATA,
            index=["one", "two", "three", "four"],
            columns=["X", "Y", "Z"]
        )
        viewer = DataFrameViewer(data=df)
        with store_exceptions_on_all_threads(), create_ui(viewer) as ui:
            viewer.df_updated = True

    @skip_if_null
    def test_data_frame_editor_with_refresh(self):
        class DataFrameViewer(HasTraits):
            data = Instance(DataFrame)
            df_refreshed = Event()
            view = View(
                Item("data", editor=DataFrameEditor(refresh="df_refreshed"))
            )

        df = DataFrame(
            DATA,
            index=["one", "two", "three", "four"],
            columns=["X", "Y", "Z"]
        )
        viewer = DataFrameViewer(data=df)
        with store_exceptions_on_all_threads(), create_ui(viewer) as ui:
            viewer.df_refreshed = True

    @skip_if_null
    def test_data_frame_editor_multi_select(self):
        view = View(
            Item("data", editor=DataFrameEditor(multi_select=True), width=400)
        )
        viewer = sample_data()
        with store_exceptions_on_all_threads():
            ui = viewer.edit_traits(view=view)
            ui.dispose()

    @skip_if_null
    def test_adapter_set_text(self):
        viewer = sample_data()
        columns = [(column, column) for column in viewer.data.columns]
        adapter = DataFrameAdapter(columns=columns)

        adapter.set_text(viewer, 'data', 0, 0, '10')

        item_0_df = adapter.get_item(viewer, 'data', 0)

        assert_array_equal(item_0_df.values, [[10, 1, 2]])
        assert_array_equal(item_0_df.columns, ['X', 'Y', 'Z'])

    @skip_if_null
    def test_adapter_set_text_invalid(self):
        viewer = sample_data()
        columns = [(column, column) for column in viewer.data.columns]
        adapter = DataFrameAdapter(columns=columns)

        adapter.set_text(viewer, 'data', 0, 0, 'invalid')

        # expect no error, and values unchanged
        item_0_df = adapter.get_item(viewer, 'data', 0)

        assert_array_equal(item_0_df.values, [[0, 1, 2]])
        assert_array_equal(item_0_df.columns, ['X', 'Y', 'Z'])

    @skip_if_null
    def test_adapter_set_index_text(self):
        viewer = sample_data()
        columns = (
            [('', 'index')] +
            [(column, column) for column in viewer.data.columns]
        )
        adapter = DataFrameAdapter(columns=columns)

        adapter.set_text(viewer, 'data', 0, 0, 'NewIndex')

        item_0_df = adapter.get_item(viewer, 'data', 0)

        assert_array_equal(item_0_df.values, [[0, 1, 2]])
        assert_array_equal(item_0_df.columns, ['X', 'Y', 'Z'])
        self.assertEqual(item_0_df.index[0], 'NewIndex')

    @skip_if_null
    def test_adapter_set_index_text_numeric(self):
        viewer = sample_data_numerical_index()
        columns = (
            [('', 'index')] +
            [(column, column) for column in viewer.data.columns]
        )
        adapter = DataFrameAdapter(columns=columns)

        adapter.set_text(viewer, 'data', 0, 0, 100)

        item_0_df = adapter.get_item(viewer, 'data', 0)

        assert_array_equal(item_0_df.values, [[0, 1, 2]])
        assert_array_equal(item_0_df.columns, ['X', 'Y', 'Z'])
        self.assertEqual(item_0_df.index[0], 100)

    @skip_if_null
    def test_adapter_set_index_text_numeric_invalid(self):
        viewer = sample_data_numerical_index()
        columns = (
            [('', 'index')] +
            [(column, column) for column in viewer.data.columns]
        )
        adapter = DataFrameAdapter(columns=columns)

        adapter.set_text(viewer, 'data', 0, 0, 'invalid')

        item_0_df = adapter.get_item(viewer, 'data', 0)

        assert_array_equal(item_0_df.values, [[0, 1, 2]])
        assert_array_equal(item_0_df.columns, ['X', 'Y', 'Z'])
        self.assertEqual(item_0_df.index[0], 1)
