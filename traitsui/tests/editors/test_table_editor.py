
from pyface.gui import GUI
from traits.api import HasTraits, Instance, Int, List, Str

from traitsui.api import Item, ObjectColumn, TableEditor, View
from traitsui.tests._tools import (
    skip_if_not_qt4, press_ok_button,
    skip_if_null, store_exceptions_on_all_threads)


class ListItem(HasTraits):
    """ Items to visualize in a table editor """
    value = Str
    other_value = Int


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


@skip_if_null
def test_table_editor():
    gui = GUI()
    object_list = ObjectList(
        values=[ListItem(value=str(i**2)) for i in range(10)]
    )

    with store_exceptions_on_all_threads():
        ui = object_list.edit_traits(view=simple_view)
        gui.process_events()
        press_ok_button(ui)
        gui.process_events()


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
