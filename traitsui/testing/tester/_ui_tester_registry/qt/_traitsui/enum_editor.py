# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

from traitsui.qt.enum_editor import (
    ListEditor,
    RadioEditor,
    SimpleEditor,
)
from traitsui.testing.tester.command import (
    KeyClick,
    KeySequence,
    MouseClick,
)
from traitsui.testing.tester.locator import Index
from traitsui.testing.tester.query import DisplayedText, SelectedText
from traitsui.testing.tester._ui_tester_registry._common_ui_targets import (
    BaseSourceWithLocation,
)
from traitsui.testing.tester._ui_tester_registry.qt import (
    _interaction_helpers,
)
from traitsui.testing.tester._ui_tester_registry._layout import (
    column_major_to_row_major,
)


class _IndexedListEditor(BaseSourceWithLocation):
    """Wrapper class for EnumListEditor and Index."""

    source_class = ListEditor
    locator_class = Index
    handlers = [
        (
            MouseClick,
            (
                lambda wrapper, _: _interaction_helpers.mouse_click_item_view(
                    model=wrapper._target.source.control.model(),
                    view=wrapper._target.source.control,
                    index=wrapper._target.source.control.model().index(
                        wrapper._target.location.index, 0
                    ),
                    delay=wrapper.delay,
                )
            ),
        ),
    ]


class _IndexedRadioEditor(BaseSourceWithLocation):
    """Wrapper class for EnumRadioEditor and Index."""

    source_class = RadioEditor
    locator_class = Index
    handlers = [
        (
            MouseClick,
            (
                lambda wrapper, _: _interaction_helpers.mouse_click_qlayout(
                    layout=wrapper._target.source.control.layout(),
                    index=convert_index(
                        layout=wrapper._target.source.control.layout(),
                        index=wrapper._target.location.index,
                        row_major=wrapper._target.source.row_major,
                    ),
                    delay=wrapper.delay,
                )
            ),
        ),
    ]


def convert_index(layout, index, row_major):
    """Helper function to convert an index for a QGridLayout so that the
    index counts over the grid in the correct direction.
    The grid is always populated in row major order. The row_major trait of a
    Radio Enum Editor simply changes what elements are assigned to each entry
    in the grid, so that when displayed, they appear in column major order.
    Qlayouts are indexed in the order they are populated, so to access
    the correct element we may need to convert a column-major based index
    into a row-major one.

    Parameters
    ----------
    layout : QGridLayout
        The layout of interest
    index : int
        the index of interest
    row_major : bool
        whether or not the grid entries are organized in row major order
    """
    if row_major:
        return index
    else:
        n = layout.count()
        num_cols = layout.columnCount()
        num_rows = layout.rowCount()
        return column_major_to_row_major(index, n, num_rows, num_cols)


class _IndexedSimpleEditor(BaseSourceWithLocation):
    """Wrapper class for Simple EnumEditor and Index."""

    source_class = SimpleEditor
    locator_class = Index
    handlers = [
        (
            MouseClick,
            (
                lambda wrapper, _: _interaction_helpers.mouse_click_combobox(
                    combobox=wrapper._target.source.control,
                    index=wrapper._target.location.index,
                    delay=wrapper.delay,
                )
            ),
        ),
    ]


def radio_selected_text_handler(wrapper, interaction):
    """Handler function used to query SelectedText for EnumRadioEditor.

    Parameters
    ----------
    wrapper : UIWrapper
        The UIWrapper containing that object with text to be displayed.
    interaction : SelectedText
        Unused in this function but included to match the expected format of a
        handler.  Should only be SelectedText
    """
    control = wrapper._target.control
    for index in range(control.layout().count()):
        if control.layout().itemAt(index).widget().isChecked():
            return control.layout().itemAt(index).widget().text()
    return None


def register(registry):
    """Registry location and interaction handlers for EnumEditor.

    Parameters
    ----------
    registry : InteractionRegistry
    """
    _IndexedListEditor.register(registry)
    _IndexedRadioEditor.register(registry)
    _IndexedSimpleEditor.register(registry)

    simple_editor_text_handlers = [
        (
            KeyClick,
            (
                lambda wrapper, interaction: _interaction_helpers.key_click_qwidget(
                    control=wrapper._target.control,
                    interaction=interaction,
                    delay=wrapper.delay,
                )
            ),
        ),
        (
            KeySequence,
            (
                lambda wrapper, interaction: _interaction_helpers.key_sequence_qwidget(
                    control=wrapper._target.control,
                    interaction=interaction,
                    delay=wrapper.delay,
                )
            ),
        ),
        (
            DisplayedText,
            lambda wrapper, _: wrapper._target.control.currentText(),
        ),
        (
            SelectedText,
            lambda wrapper, _: wrapper._target.control.currentText(),
        ),
    ]

    for interaction_class, handler in simple_editor_text_handlers:
        registry.register_interaction(
            target_class=SimpleEditor,
            interaction_class=interaction_class,
            handler=handler,
        )

    registry.register_interaction(
        target_class=RadioEditor,
        interaction_class=SelectedText,
        handler=radio_selected_text_handler,
    )

    registry.register_interaction(
        target_class=ListEditor,
        interaction_class=SelectedText,
        handler=lambda wrapper, _: wrapper._target.control.currentItem().text(),
    )
