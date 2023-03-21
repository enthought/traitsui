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
from unittest.mock import Mock

from traits.api import HasTraits, Instance, Int, List, Str, Tuple

from traitsui.api import (
    Action,
    EvalTableFilter,
    Item,
    ObjectColumn,
    TableEditor,
    View,
)
from traitsui.tests._tools import (
    BaseTestMixin,
    requires_toolkit,
    ToolkitName,
)
from traitsui.testing.api import (
    Cell,
    Disabled,
    DisplayedText,
    KeySequence,
    KeyClick,
    MouseClick,
    MouseDClick,
    Selected,
    SelectedIndices,
    UITester,
)


class ListItem(HasTraits):
    """Items to visualize in a table editor"""

    value = Str()
    other_value = Int()


class ObjectListWithSelection(HasTraits):
    values = List(Instance(ListItem))
    selected = Instance(ListItem)
    selections = List(Instance(ListItem))
    selected_index = Int()
    selected_indices = List(Int)
    selected_column = Str()
    selected_columns = List(Str)
    selected_cell = Tuple(Instance(ListItem), Str)
    selected_cells = List(Tuple(Instance(ListItem), Str))
    selected_cell_index = Tuple(Int, Int)
    selected_cell_indices = List(Tuple(Int, Int))


class ObjectList(HasTraits):
    values = List(Instance(ListItem))


simple_view = View(
    Item(
        "values",
        show_label=False,
        editor=TableEditor(
            columns=[
                ObjectColumn(name="value"),
                ObjectColumn(name="other_value"),
            ]
        ),
    ),
    buttons=["OK"],
)

filtered_view = View(
    Item(
        "values",
        show_label=False,
        editor=TableEditor(
            sortable=False,
            columns=[
                ObjectColumn(name="value"),
                ObjectColumn(name="other_value"),
            ],
            filter=EvalTableFilter(expression="other_value > 4"),
        ),
    ),
    buttons=["OK"],
)

select_row_view = View(
    Item(
        "values",
        show_label=False,
        editor=TableEditor(
            sortable=False,
            columns=[
                ObjectColumn(name="value"),
                ObjectColumn(name="other_value"),
            ],
            selection_mode="row",
            selected="selected",
        ),
    ),
    buttons=["OK"],
)

select_rows_view = View(
    Item(
        "values",
        show_label=False,
        editor=TableEditor(
            sortable=False,
            columns=[ObjectColumn(name="value")],
            selection_mode="rows",
            selected="selections",
        ),
    ),
    buttons=["OK"],
)

select_row_index_view = View(
    Item(
        "values",
        show_label=False,
        editor=TableEditor(
            sortable=False,
            columns=[
                ObjectColumn(name="value"),
                ObjectColumn(name="other_value"),
            ],
            selection_mode="row",
            selected_indices="selected_index",
        ),
    ),
    buttons=["OK"],
)

select_row_indices_view = View(
    Item(
        "values",
        show_label=False,
        editor=TableEditor(
            sortable=False,
            columns=[
                ObjectColumn(name="value"),
                ObjectColumn(name="other_value"),
            ],
            selection_mode="rows",
            selected_indices="selected_indices",
        ),
    ),
    buttons=["OK"],
)

select_column_view = View(
    Item(
        "values",
        show_label=False,
        editor=TableEditor(
            sortable=False,
            columns=[
                ObjectColumn(name="value"),
                ObjectColumn(name="other_value"),
            ],
            selection_mode="column",
            selected="selected_column",
        ),
    ),
    buttons=["OK"],
)

select_columns_view = View(
    Item(
        "values",
        show_label=False,
        editor=TableEditor(
            sortable=False,
            columns=[
                ObjectColumn(name="value"),
                ObjectColumn(name="other_value"),
            ],
            selection_mode="columns",
            selected="selected_columns",
        ),
    ),
    buttons=["OK"],
)

select_column_index_view = View(
    Item(
        "values",
        show_label=False,
        editor=TableEditor(
            sortable=False,
            columns=[
                ObjectColumn(name="value"),
                ObjectColumn(name="other_value"),
            ],
            selection_mode="column",
            selected_indices="selected_index",
        ),
    ),
    buttons=["OK"],
)

select_column_indices_view = View(
    Item(
        "values",
        show_label=False,
        editor=TableEditor(
            sortable=False,
            columns=[
                ObjectColumn(name="value"),
                ObjectColumn(name="other_value"),
            ],
            selection_mode="columns",
            selected_indices="selected_indices",
        ),
    ),
    buttons=["OK"],
)

select_cell_view = View(
    Item(
        "values",
        show_label=False,
        editor=TableEditor(
            sortable=False,
            columns=[
                ObjectColumn(name="value"),
                ObjectColumn(name="other_value"),
            ],
            selection_mode="cell",
            selected="selected_cell",
        ),
    ),
    buttons=["OK"],
)

select_cells_view = View(
    Item(
        "values",
        show_label=False,
        editor=TableEditor(
            sortable=False,
            columns=[
                ObjectColumn(name="value"),
                ObjectColumn(name="other_value"),
            ],
            selection_mode="cells",
            selected="selected_cells",
        ),
    ),
    buttons=["OK"],
)

select_cell_index_view = View(
    Item(
        "values",
        show_label=False,
        editor=TableEditor(
            sortable=False,
            columns=[
                ObjectColumn(name="value"),
                ObjectColumn(name="other_value"),
            ],
            selection_mode="cell",
            selected_indices="selected_cell_index",
        ),
    ),
    buttons=["OK"],
)

select_cell_indices_view = View(
    Item(
        "values",
        show_label=False,
        editor=TableEditor(
            sortable=False,
            columns=[
                ObjectColumn(name="value"),
                ObjectColumn(name="other_value"),
            ],
            selection_mode="cells",
            selected_indices="selected_cell_indices",
        ),
    ),
    buttons=["OK"],
)

edit_on_first_click_false_view = View(
    Item(
        "values",
        show_label=False,
        editor=TableEditor(
            sortable=False,
            columns=[
                ObjectColumn(name="value"),
                ObjectColumn(name="other_value"),
            ],
            selection_mode="row",
            selected="selected",
            edit_on_first_click=False
        ),
    ),
    buttons=["OK"],
)


@requires_toolkit([ToolkitName.qt])
class TestTableEditor(BaseTestMixin, unittest.TestCase):
    def setUp(self):
        BaseTestMixin.setUp(self)

    def tearDown(self):
        BaseTestMixin.tearDown(self)

    def test_table_editor(self):
        object_list = ObjectListWithSelection(
            values=[ListItem(value=str(i ** 2)) for i in range(10)]
        )
        tester = UITester()
        with tester.create_ui(object_list, dict(view=simple_view)):
            pass

    def test_filtered_table_editor(self):
        object_list = ObjectListWithSelection(
            values=[ListItem(other_value=i ** 2) for i in range(10)]
        )
        tester = UITester()
        with tester.create_ui(object_list, dict(view=filtered_view)) as ui:
            values = tester.find_by_name(ui, "values")
            filter = values._target.filter
            num_filtered_indices = len(values._target.filtered_indices)
            self.assertIsNotNone(filter)
            self.assertEqual(num_filtered_indices, 7)

    def test_table_editor_select_row(self):
        object_list = ObjectListWithSelection(
            values=[ListItem(value=str(i ** 2)) for i in range(10)]
        )

        tester = UITester()
        with tester.create_ui(object_list, dict(view=select_row_view)) as ui:
            # click the first cell in the 6th row to select the row
            values_table = tester.find_by_name(ui, "values")
            row6_cell = values_table.locate(Cell(5, 0))
            row6_cell.perform(MouseClick())
            selected = values_table.inspect(Selected())

        self.assertEqual(selected, [object_list.values[5]])
        self.assertIs(selected[0], object_list.values[5])
        self.assertIs(object_list.selected, selected[0])

    def test_table_editor_select_rows(self):
        object_list = ObjectListWithSelection(
            values=[ListItem(value=str(i ** 2)) for i in range(10)]
        )
        object_list.selections = object_list.values[5:7]

        tester = UITester()
        with tester.create_ui(object_list, dict(view=select_rows_view)) as ui:
            values_table = tester.find_by_name(ui, "values")
            selected = values_table.inspect(Selected())

        self.assertEqual(selected, object_list.values[5:7])

    def test_table_editor_select_row_index(self):
        object_list = ObjectListWithSelection(
            values=[ListItem(value=str(i ** 2)) for i in range(10)]
        )
        object_list.selected_index = 5

        tester = UITester()
        with tester.create_ui(object_list, dict(view=select_row_index_view)) \
                as ui:
            values_table = tester.find_by_name(ui, "values")
            values_table.locate(Cell(5, 0)).perform(MouseClick())
            selected = values_table.inspect(SelectedIndices())

        self.assertEqual(selected, [5])

    def test_table_editor_select_row_indices(self):
        object_list = ObjectListWithSelection(
            values=[ListItem(value=str(i ** 2)) for i in range(10)]
        )
        object_list.selected_indices = [5, 7, 8]

        view = select_row_indices_view
        tester = UITester()
        with tester.create_ui(object_list, dict(view=view)) as ui:
            values_table = tester.find_by_name(ui, "values")
            selected = values_table.inspect(SelectedIndices())

        self.assertEqual(selected, [5, 7, 8])

    def test_table_editor_select_column(self):
        object_list = ObjectListWithSelection(
            values=[ListItem(value=str(i ** 2)) for i in range(10)]
        )

        tester = UITester()
        with tester.create_ui(object_list, dict(view=select_column_view)) \
                as ui:
            values_table = tester.find_by_name(ui, "values")
            # click a cell in the first column (the "value" column)
            first_cell = values_table.locate(Cell(0, 0))
            first_cell.perform(MouseClick())

            selected = values_table.inspect(Selected())

        self.assertEqual(selected, ["value"])
        self.assertIs(selected[0], "value")
        self.assertIs(selected[0], object_list.selected_column)

    def test_table_editor_select_columns(self):
        object_list = ObjectListWithSelection(
            values=[ListItem(value=str(i ** 2)) for i in range(10)]
        )
        object_list.selected_columns = ["value", "other_value"]

        tester = UITester()
        with tester.create_ui(object_list, dict(view=select_columns_view)) \
                as ui:
            values_table = tester.find_by_name(ui, "values")
            selected = values_table.inspect(Selected())

        self.assertEqual(selected, ["value", "other_value"])

    def test_table_editor_select_column_index(self):
        object_list = ObjectListWithSelection(
            values=[ListItem(value=str(i ** 2)) for i in range(10)]
        )

        view = select_column_index_view
        tester = UITester()
        with tester.create_ui(object_list, dict(view=view)) as ui:
            # click a cell in the index 1 column
            values_table = tester.find_by_name(ui, "values")
            col1_cell = values_table.locate(Cell(0, 1))
            col1_cell.perform(MouseClick())

            selected = values_table.inspect(SelectedIndices())

        self.assertEqual(selected, [1])

    def test_table_editor_select_column_indices(self):
        object_list = ObjectListWithSelection(
            values=[ListItem(value=str(i ** 2)) for i in range(10)]
        )
        object_list.selected_indices = [0, 1]

        view = select_column_indices_view
        tester = UITester()
        with tester.create_ui(object_list, dict(view=view)) as ui:
            values_table = tester.find_by_name(ui, "values")
            selected = values_table.inspect(SelectedIndices())

        self.assertEqual(selected, [0, 1])

    def test_table_editor_select_cell(self):
        object_list = ObjectListWithSelection(
            values=[ListItem(value=str(i ** 2)) for i in range(10)]
        )

        tester = UITester()
        with tester.create_ui(object_list, dict(view=select_cell_view)) as ui:
            # click the cell at (5,0)
            values_table = tester.find_by_name(ui, "values")
            cell_5_0 = values_table.locate(Cell(5, 0))
            cell_5_0.perform(MouseClick())

            selected = values_table.inspect(Selected())

        self.assertEqual(selected, [(object_list.values[5], "value")])
        self.assertIs(selected[0], object_list.selected_cell)

    def test_table_editor_modify_cell_with_tester(self):
        object_list = ObjectListWithSelection(
            values=[ListItem(value=str(i ** 2)) for i in range(10)]
        )
        tester = UITester()
        with tester.create_ui(object_list, dict(view=select_row_view)) as ui:
            wrapper = tester.find_by_name(ui, "values").locate(Cell(5, 0))
            wrapper.perform(MouseClick())             # activate edit mode
            wrapper.perform(KeySequence("abc"))
            self.assertEqual(object_list.selected.value, "abc")

            # second column refers to an Int type
            original = object_list.selected.other_value
            wrapper = tester.find_by_name(ui, "values").locate(Cell(5, 1))
            wrapper.perform(MouseClick())
            wrapper.perform(KeySequence("abc"))       # invalid
            self.assertEqual(object_list.selected.other_value, original)

            for _ in range(3):
                wrapper.perform(KeyClick("Backspace"))
            wrapper.perform(KeySequence("12"))  # now ok
            self.assertEqual(object_list.selected.other_value, 12)

    def test_table_editor_check_display_with_tester(self):
        object_list = ObjectListWithSelection(
            values=[ListItem(other_value=0)]
        )
        tester = UITester()
        with tester.create_ui(object_list, dict(view=select_row_view)) as ui:
            wrapper = tester.find_by_name(ui, "values").locate(Cell(0, 1))

            actual = wrapper.inspect(DisplayedText())
            self.assertEqual(actual, "0")

            object_list.values[0].other_value = 123

            actual = wrapper.inspect(DisplayedText())
            self.assertEqual(actual, "123")

    def test_table_editor_escape_retain_edit(self):
        object_list = ObjectListWithSelection(
            values=[ListItem(other_value=0)]
        )
        tester = UITester()
        with tester.create_ui(object_list, dict(view=select_row_view)) as ui:
            cell = tester.find_by_name(ui, "values").locate(Cell(0, 1))

            cell.perform(MouseClick())
            cell.perform(KeySequence("123"))
            cell.perform(KeyClick("Esc"))  # exit edit mode, did not revert

            self.assertEqual(object_list.values[0].other_value, 123)

    def test_table_editor_select_cells(self):
        object_list = ObjectListWithSelection(
            values=[ListItem(value=str(i ** 2)) for i in range(10)]
        )
        object_list.selected_cells = [
            (object_list.values[5], "value"),
            (object_list.values[6], "other value"),
            (object_list.values[8], "value"),
        ]

        tester = UITester()
        with tester.create_ui(object_list, dict(view=select_cells_view)) as ui:
            values_table = tester.find_by_name(ui, "values")
            selected = values_table.inspect(Selected())

        self.assertEqual(
            selected,
            [
                (object_list.values[5], "value"),
                (object_list.values[6], "other value"),
                (object_list.values[8], "value"),
            ],
        )

    def test_table_editor_select_cell_index(self):
        object_list = ObjectListWithSelection(
            values=[ListItem(value=str(i ** 2)) for i in range(10)]
        )

        view = select_cell_index_view
        tester = UITester()
        with tester.create_ui(object_list, dict(view=view)) as ui:
            # click the cell at (5,1)
            values_table = tester.find_by_name(ui, "values")
            cell_5_1 = values_table.locate(Cell(5, 1))
            cell_5_1.perform(MouseClick())
            selected = values_table.inspect(SelectedIndices())

        self.assertEqual(selected, [(5, 1)])

    def test_table_editor_select_cell_indices(self):
        object_list = ObjectListWithSelection(
            values=[ListItem(value=str(i ** 2)) for i in range(10)]
        )
        object_list.selected_cell_indices = [(5, 0), (6, 1), (8, 0)]

        view = select_cell_indices_view
        tester = UITester()
        with tester.create_ui(object_list, dict(view=view)) as ui:
            values_table = tester.find_by_name(ui, "values")
            selected = values_table.inspect(SelectedIndices())

        self.assertEqual(selected, [(5, 0), (6, 1), (8, 0)])

    def test_progress_column(self):
        from traitsui.extras.progress_column import ProgressColumn

        progress_view = View(
            Item(
                "values",
                show_label=False,
                editor=TableEditor(
                    columns=[
                        ObjectColumn(name="value"),
                        ProgressColumn(name="other_value"),
                    ]
                ),
            ),
            buttons=["OK"],
        )
        object_list = ObjectList(
            values=[ListItem(value=str(i ** 2)) for i in range(10)]
        )
        tester = UITester()
        with tester.create_ui(object_list, dict(view=progress_view)):
            pass

    def test_on_perform_action(self):
        # A test for issue #741, where actions with an on_perform function set
        # would get called twice
        object_list = ObjectList(
            values=[ListItem(value=str(i ** 2)) for i in range(10)]
        )
        mock_function = Mock()
        action = Action(on_perform=mock_function)

        tester = UITester()
        with tester.create_ui(object_list, dict(view=simple_view)) as ui:
            editor = tester.find_by_name(ui, "values")._target
            editor.set_menu_context(None, None, None)
            editor.perform(action)
        mock_function.assert_called_once()

    def test_edit_on_first_click_false(self):
        object_list = ObjectListWithSelection(
            values=[ListItem(value=str(i ** 2)) for i in range(10)]
        )
        tester = UITester()
        with tester.create_ui(
                object_list,
                dict(view=edit_on_first_click_false_view)
        ) as ui:
            wrapper = tester.find_by_name(ui, "values").locate(Cell(5, 0))
            # single click will not activate edit mode
            wrapper.perform(MouseClick())
            with self.assertRaises(Disabled):
                wrapper.perform(KeySequence("abc"))

            # double click will activate edit mode
            wrapper.perform(MouseDClick())
            wrapper.perform(KeySequence("abc"))
            self.assertEqual(object_list.values[5].value, "abc")
