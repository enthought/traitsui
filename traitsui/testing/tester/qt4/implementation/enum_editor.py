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

from traitsui.qt4.enum_editor import (
    ListEditor,
    RadioEditor,
    SimpleEditor,
)
from traitsui.testing.tester import command, locator, query
from traitsui.testing.tester.base_classes import _BaseSourceWithLocation
from traitsui.testing.tester.qt4 import helpers


class _IndexedListEditor(_BaseSourceWithLocation):
    """ Wrapper class for EnumListEditor and Index.
    """
    source_class = ListEditor
    locator_class = locator.Index
    handlers = [
        (command.MouseClick, (lambda wrapper, _: helpers.mouse_click_item_view(
            model=wrapper.target.source.control.model(),
            view=wrapper.target.source.control,
            index=wrapper.target.source.control.model().index(
                wrapper.target.location.index, 0),
            delay=wrapper.delay))),
    ]


class _IndexedRadioEditor(_BaseSourceWithLocation):
    """ Wrapper class for EnumRadioEditor and Index.
    """
    source_class = RadioEditor
    locator_class = locator.Index
    handlers = [
        (command.MouseClick, (lambda wrapper, _: helpers.mouse_click_qlayout(
            layout=wrapper.target.source.control.layout(),
            index = convert_index(
                layout=wrapper.target.source.control.layout(),
                index=wrapper.target.location.index,
                row_major=wrapper.target.source.row_major
            ),
            delay=wrapper.delay))),
    ]

def convert_index(layout, index, row_major):
    if row_major:
        return index
    else:
        # the grid is always populated in row major order. The row_major trait
        # simply changes what elements are assigned to each entry in the grid,
        # so that when displayed, they appear in column major order.
        # Qlayouts are indexed in the order they are populated, so to access
        # the correct element we need to convert a column-major based index
        # into a row-major one.

        n = layout.count()
        num_cols = layout.columnCount()
        num_rows = layout.rowCount()
        # the last entries of the last row can be empty. 
        num_empty_entries_last_row = num_cols * num_rows - n

        # count in column major order

        # if the index of interest extends into the part of the grid where
        # the columns have a missing entry in the last row 
        if index > num_rows * (num_cols - num_empty_entries_last_row):
            # break the grid up into 2 grids.  One of size 
            # num_rows x (num_cols - num_empty_entries_last_row).  The other
            # of size (num_rows-1) x num_empty_entries_last_row
            num_entries_grid1 = index - num_rows * (num_cols - num_empty_entries_last_row)
            # find i, j coordinates of the index in grid2 if we counted in
            # column major order
            new_index = index - num_entries_grid1
            i = new_index % (num_rows - 1)
            j = new_index // (num_empty_entries_last_row)
            # convert that back to an index found from row major order
            return num_entries_grid1 + (i * num_empty_entries_last_row + j)
        else:
            # find i,j coordinates of index if we counted in column major order
            i = index % num_rows
            j = index // num_rows
        # convert that back to an index found from row major order
        return i * num_cols + j



class _IndexedSimpleEditor(_BaseSourceWithLocation):
    """ Wrapper class for Simple EnumEditor and Index.
    """
    source_class = SimpleEditor
    locator_class = locator.Index
    handlers = [
        (command.MouseClick, (lambda wrapper, _: helpers.mouse_click_combobox(
            combobox=wrapper.target.source.control,
            index=wrapper.target.location.index,
            delay=wrapper.delay))),
    ]


def radio_displayed_text_handler(wrapper, interaction):
    """ Handler function used to query DisplayedText for EnumRadioEditor.

    Parameters
    ----------
    wrapper : UIWrapper
        The UIWrapper containing that object with text to be displayed.
    interaction : query.DisplayedText
        Unused in this function but included to match the expected format of a
        handler.  Should only be query.DisplayedText
    """
    control = wrapper.target.control
    for index in range(control.layout().count()):
        if control.layout().itemAt(index).widget().isChecked():
            return control.layout().itemAt(index).widget().text()


def register(registry):
    """ Registry location and interaction handlers for EnumEditor.

    Parameters
    ----------
    registry : InteractionRegistry
    """
    _IndexedListEditor.register(registry)
    _IndexedRadioEditor.register(registry)
    _IndexedSimpleEditor.register(registry)

    simple_editor_text_handlers = [
        (command.KeyClick,
            (lambda wrapper, interaction: helpers.key_click_qwidget(
                control=wrapper.target.control,
                interaction=interaction,
                delay=wrapper.delay))),
        (command.KeySequence,
            (lambda wrapper, interaction: helpers.key_sequence_qwidget(
                control=wrapper.target.control,
                interaction=interaction,
                delay=wrapper.delay))),
        (query.DisplayedText,
            lambda wrapper, _: wrapper.target.control.currentText())
    ]

    for interaction_class, handler in simple_editor_text_handlers:
        registry.register_handler(
            target_class=SimpleEditor,
            interaction_class=interaction_class,
            handler=handler
        )

    registry.register_handler(
        target_class=RadioEditor,
        interaction_class=query.DisplayedText,
        handler=radio_displayed_text_handler,
    )

    registry.register_handler(
        target_class=ListEditor,
        interaction_class=query.DisplayedText,
        handler=lambda wrapper, _: wrapper.target.control.currentItem().text(),
    )
