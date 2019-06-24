from __future__ import absolute_import

from pyface.gui import GUI
from traits.api import HasTraits, Instance, Int, List, Str, Tuple

from traitsui.api import (
    EvalTableFilter, Item, ObjectColumn, TableEditor, View
)
from traitsui.tests._tools import (
    is_current_backend_qt4, is_current_backend_wx, press_ok_button,
    skip_if_not_qt4,  skip_if_null, store_exceptions_on_all_threads
)


class ListItem(HasTraits):
    """ Items to visualize in a table editor """
    value = Str
    other_value = Int


class ObjectListWithSelection(HasTraits):
    values = List(Instance(ListItem))
    selected = Instance(ListItem)
    selections = List(Instance(ListItem))
    selected_index = Int
    selected_indices = List(Int)
    selected_column = Str
    selected_columns = List(Str)
    selected_cell = Tuple(Instance(ListItem), Str)
    selected_cells = List(Tuple(Instance(ListItem), Str))
    selected_cell_index = Tuple(Int, Int)
    selected_cell_indices = List(Tuple(Int, Int))


class ObjectList(HasTraits):
    values = List(Instance(ListItem))


simple_view = View(
    Item(
        'values',
        show_label=False,
        editor=TableEditor(
            columns=[
                ObjectColumn(name='value'),
                ObjectColumn(name='other_value'),
            ],
        )
    ),
    buttons=['OK'],
)

filtered_view = View(
    Item(
        'values',
        show_label=False,
        editor=TableEditor(
            columns=[
                ObjectColumn(name='value'),
                ObjectColumn(name='other_value'),
            ],
            filter=EvalTableFilter(expression='other_value >= 2'),
        )
    ),
    buttons=['OK'],
)

select_row_view = View(
    Item(
        'values',
        show_label=False,
        editor=TableEditor(
            columns=[
                ObjectColumn(name='value'),
                ObjectColumn(name='other_value'),
            ],
            selection_mode='row',
            selected='selected',
        )
    ),
    buttons=['OK'],
)

select_rows_view = View(
    Item(
        'values',
        show_label=False,
        editor=TableEditor(
            columns=[
                ObjectColumn(name='value'),
            ],
            selection_mode='rows',
            selected='selections',
        )
    ),
    buttons=['OK'],
)

select_row_index_view = View(
    Item(
        'values',
        show_label=False,
        editor=TableEditor(
            columns=[
                ObjectColumn(name='value'),
                ObjectColumn(name='other_value'),
            ],
            selection_mode='row',
            selected_indices='selected_index',
        )
    ),
    buttons=['OK'],
)

select_row_indices_view = View(
    Item(
        'values',
        show_label=False,
        editor=TableEditor(
            columns=[
                ObjectColumn(name='value'),
                ObjectColumn(name='other_value'),
            ],
            selection_mode='rows',
            selected_indices='selected_indices',
        )
    ),
    buttons=['OK'],
)

select_column_view = View(
    Item(
        'values',
        show_label=False,
        editor=TableEditor(
            columns=[
                ObjectColumn(name='value'),
                ObjectColumn(name='other_value'),
            ],
            selection_mode='column',
            selected='selected_column',
        )
    ),
    buttons=['OK'],
)

select_columns_view = View(
    Item(
        'values',
        show_label=False,
        editor=TableEditor(
            columns=[
                ObjectColumn(name='value'),
                ObjectColumn(name='other_value'),
            ],
            selection_mode='columns',
            selected='selected_columns',
        )
    ),
    buttons=['OK'],
)

select_column_index_view = View(
    Item(
        'values',
        show_label=False,
        editor=TableEditor(
            columns=[
                ObjectColumn(name='value'),
                ObjectColumn(name='other_value'),
            ],
            selection_mode='column',
            selected_indices='selected_index',
        )
    ),
    buttons=['OK'],
)

select_column_indices_view = View(
    Item(
        'values',
        show_label=False,
        editor=TableEditor(
            columns=[
                ObjectColumn(name='value'),
                ObjectColumn(name='other_value'),
            ],
            selection_mode='columns',
            selected_indices='selected_indices',
        )
    ),
    buttons=['OK'],
)

select_cell_view = View(
    Item(
        'values',
        show_label=False,
        editor=TableEditor(
            columns=[
                ObjectColumn(name='value'),
                ObjectColumn(name='other_value'),
            ],
            selection_mode='cell',
            selected='selected_cell',
        )
    ),
    buttons=['OK'],
)

select_cells_view = View(
    Item(
        'values',
        show_label=False,
        editor=TableEditor(
            columns=[
                ObjectColumn(name='value'),
                ObjectColumn(name='other_value'),
            ],
            selection_mode='cells',
            selected='selected_cells',
        )
    ),
    buttons=['OK'],
)

select_cell_index_view = View(
    Item(
        'values',
        show_label=False,
        editor=TableEditor(
            columns=[
                ObjectColumn(name='value'),
                ObjectColumn(name='other_value'),
            ],
            selection_mode='cell',
            selected_indices='selected_cell_index',
        )
    ),
    buttons=['OK'],
)

select_cell_indices_view = View(
    Item(
        'values',
        show_label=False,
        editor=TableEditor(
            columns=[
                ObjectColumn(name='value'),
                ObjectColumn(name='other_value'),
            ],
            selection_mode='cells',
            selected_indices='selected_cell_indices',
        )
    ),
    buttons=['OK'],
)


@skip_if_null
def test_table_editor():
    gui = GUI()
    object_list = ObjectListWithSelection(
        values=[ListItem(value=str(i**2)) for i in range(10)]
    )

    with store_exceptions_on_all_threads():
        ui = object_list.edit_traits(view=simple_view)
        gui.process_events()
        press_ok_button(ui)
        gui.process_events()


@skip_if_null
def test_filtered_table_editor():
    gui = GUI()
    object_list = ObjectListWithSelection(
        values=[ListItem(value=str(i**2)) for i in range(10)]
    )

    with store_exceptions_on_all_threads():
        ui = object_list.edit_traits(view=filtered_view)
        gui.process_events()

        filter = ui.get_editors('values')[0].filter

        press_ok_button(ui)
        gui.process_events()

    assert filter is not None


@skip_if_null
def test_table_editor_select_row():
    gui = GUI()
    object_list = ObjectListWithSelection(
        values=[ListItem(value=str(i**2)) for i in range(10)]
    )
    object_list.selected = object_list.values[5]

    with store_exceptions_on_all_threads():
        ui = object_list.edit_traits(view=select_row_view)
        editor = ui.get_editors('values')[0]
        gui.process_events()
        if is_current_backend_qt4():
            selected = editor.selected
        elif is_current_backend_wx():
            selected = editor.selected_row

        press_ok_button(ui)
        gui.process_events()

    assert selected is object_list.values[5]


@skip_if_null
def test_table_editor_select_rows():
    gui = GUI()
    object_list = ObjectListWithSelection(
        values=[ListItem(value=str(i**2)) for i in range(10)]
    )
    object_list.selections = object_list.values[5:7]

    with store_exceptions_on_all_threads():
        ui = object_list.edit_traits(view=select_rows_view)
        editor = ui.get_editors('values')[0]
        gui.process_events()
        if is_current_backend_qt4():
            selected = editor.selected
        elif is_current_backend_wx():
            selected = editor.selected_rows

        press_ok_button(ui)
        gui.process_events()

    assert selected == object_list.values[5:7]


@skip_if_null
def test_table_editor_select_row_index():
    gui = GUI()
    object_list = ObjectListWithSelection(
        values=[ListItem(value=str(i**2)) for i in range(10)]
    )
    object_list.selected_index = 5

    with store_exceptions_on_all_threads():
        ui = object_list.edit_traits(view=select_row_index_view)
        editor = ui.get_editors('values')[0]
        gui.process_events()
        if is_current_backend_qt4():
            selected = editor.selected_indices
        elif is_current_backend_wx():
            selected = editor.selected_row_index

        press_ok_button(ui)
        gui.process_events()

    assert selected == 5


@skip_if_null
def test_table_editor_select_row_indices():
    gui = GUI()
    object_list = ObjectListWithSelection(
        values=[ListItem(value=str(i**2)) for i in range(10)]
    )
    object_list.selected_indices = [5, 7, 8]

    with store_exceptions_on_all_threads():
        ui = object_list.edit_traits(view=select_row_indices_view)
        editor = ui.get_editors('values')[0]
        gui.process_events()
        if is_current_backend_qt4():
            selected = editor.selected_indices
        elif is_current_backend_wx():
            selected = editor.selected_row_indices

        press_ok_button(ui)
        gui.process_events()

    assert selected == [5, 7, 8]


@skip_if_null
def test_table_editor_select_column():
    gui = GUI()
    object_list = ObjectListWithSelection(
        values=[ListItem(value=str(i**2)) for i in range(10)]
    )
    object_list.selected_column = 'value'

    with store_exceptions_on_all_threads():
        ui = object_list.edit_traits(view=select_column_view)
        editor = ui.get_editors('values')[0]
        gui.process_events()
        if is_current_backend_qt4():
            selected = editor.selected
        elif is_current_backend_wx():
            selected = editor.selected_column

        press_ok_button(ui)
        gui.process_events()

    assert selected == 'value'


@skip_if_null
def test_table_editor_select_columns():
    gui = GUI()
    object_list = ObjectListWithSelection(
        values=[ListItem(value=str(i**2)) for i in range(10)]
    )
    object_list.selected_columns = ['value', 'other_value']

    with store_exceptions_on_all_threads():
        ui = object_list.edit_traits(view=select_columns_view)
        editor = ui.get_editors('values')[0]
        gui.process_events()
        if is_current_backend_qt4():
            selected = editor.selected
        elif is_current_backend_wx():
            selected = editor.selected_columns

        press_ok_button(ui)
        gui.process_events()

    assert selected == ['value', 'other_value']


@skip_if_null
def test_table_editor_select_column_index():
    gui = GUI()
    object_list = ObjectListWithSelection(
        values=[ListItem(value=str(i**2)) for i in range(10)]
    )
    object_list.selected_index = 1

    with store_exceptions_on_all_threads():
        ui = object_list.edit_traits(view=select_column_index_view)
        editor = ui.get_editors('values')[0]
        gui.process_events()
        if is_current_backend_qt4():
            selected = editor.selected_indices
        elif is_current_backend_wx():
            selected = editor.selected_column_index

        press_ok_button(ui)
        gui.process_events()

    assert selected == 1


@skip_if_null
def test_table_editor_select_column_indices():
    gui = GUI()
    object_list = ObjectListWithSelection(
        values=[ListItem(value=str(i**2)) for i in range(10)]
    )
    object_list.selected_indices = [0, 1]

    with store_exceptions_on_all_threads():
        ui = object_list.edit_traits(view=select_column_indices_view)
        editor = ui.get_editors('values')[0]
        gui.process_events()
        if is_current_backend_qt4():
            selected = editor.selected_indices
        elif is_current_backend_wx():
            selected = editor.selected_column_indices

        press_ok_button(ui)
        gui.process_events()

    assert selected == [0, 1]


@skip_if_null
def test_table_editor_select_cell():
    gui = GUI()
    object_list = ObjectListWithSelection(
        values=[ListItem(value=str(i**2)) for i in range(10)]
    )
    object_list.selected_cell = (object_list.values[5], 'value')

    with store_exceptions_on_all_threads():
        ui = object_list.edit_traits(view=select_cell_view)
        editor = ui.get_editors('values')[0]
        gui.process_events()
        if is_current_backend_qt4():
            selected = editor.selected
        elif is_current_backend_wx():
            selected = editor.selected_cell

        press_ok_button(ui)
        gui.process_events()

    assert selected == (object_list.values[5], 'value')


@skip_if_null
def test_table_editor_select_cells():
    gui = GUI()
    object_list = ObjectListWithSelection(
        values=[ListItem(value=str(i**2)) for i in range(10)]
    )
    object_list.selected_cells = [
        (object_list.values[5], 'value'),
        (object_list.values[6], 'other value'),
        (object_list.values[8], 'value'),
    ]

    with store_exceptions_on_all_threads():
        ui = object_list.edit_traits(view=select_cells_view)
        editor = ui.get_editors('values')[0]
        gui.process_events()
        if is_current_backend_qt4():
            selected = editor.selected
        elif is_current_backend_wx():
            selected = editor.selected_cells

        press_ok_button(ui)
        gui.process_events()

    assert selected == [
        (object_list.values[5], 'value'),
        (object_list.values[6], 'other value'),
        (object_list.values[8], 'value'),
    ]


@skip_if_null
def test_table_editor_select_cell_index():
    gui = GUI()
    object_list = ObjectListWithSelection(
        values=[ListItem(value=str(i**2)) for i in range(10)]
    )
    object_list.selected_cell_index = (5, 1)

    with store_exceptions_on_all_threads():
        ui = object_list.edit_traits(view=select_cell_index_view)
        editor = ui.get_editors('values')[0]
        gui.process_events()
        if is_current_backend_qt4():
            selected = editor.selected_indices
        elif is_current_backend_wx():
            selected = editor.selected_cell_index

        press_ok_button(ui)
        gui.process_events()

    assert selected == (5, 1)


@skip_if_null
def test_table_editor_select_cell_indices():
    gui = GUI()
    object_list = ObjectListWithSelection(
        values=[ListItem(value=str(i**2)) for i in range(10)]
    )
    object_list.selected_cell_indices = [(5, 0), (6, 1), (8, 0)]

    with store_exceptions_on_all_threads():
        ui = object_list.edit_traits(view=select_cell_indices_view)
        editor = ui.get_editors('values')[0]
        gui.process_events()
        if is_current_backend_qt4():
            selected = editor.selected_indices
        elif is_current_backend_wx():
            selected = editor.selected_cell_indices

        press_ok_button(ui)
        gui.process_events()

    assert selected == [(5, 0), (6, 1), (8, 0)]


@skip_if_not_qt4
def test_progress_column():
    from traitsui.extras.progress_column import ProgressColumn
    progress_view = View(
        Item(
            'values',
            show_label=False,
            editor=TableEditor(
                columns=[
                    ObjectColumn(name='value'),
                    ProgressColumn(name='other_value'),
                ],
            )
        ),
        buttons=['OK'],
    )
    gui = GUI()
    object_list = ObjectList(
        values=[ListItem(value=str(i**2)) for i in range(10)]
    )

    with store_exceptions_on_all_threads():
        ui = object_list.edit_traits(view=progress_view)
        gui.process_events()
        press_ok_button(ui)
        gui.process_events()
