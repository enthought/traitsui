# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import wx

from traitsui.wx.enum_editor import (
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
from traitsui.testing.tester._ui_tester_registry.wx import _interaction_helpers
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
                lambda wrapper, _: _interaction_helpers.mouse_click_listbox(
                    control=wrapper._target.source.control,
                    index=wrapper._target.location.index,
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
                lambda wrapper, _: _interaction_helpers.mouse_click_radiobutton_child_in_panel(
                    control=wrapper._target.source.control,
                    index=convert_index(
                        source=wrapper._target.source,
                        index=wrapper._target.location.index,
                    ),
                    delay=wrapper.delay,
                )
            ),
        ),
    ]


def convert_index(source, index):
    """Helper function to convert an index for a GridSizer so that the
    index counts over the grid in the correct direction.
    The grid is always populated in row major order, however, the elements
    are assigned to each entry in the grid so that when displayed they appear
    in column major order.
    Sizers are indexed in the order they are populated, so to access
    the correct element we may need to convert a column-major based index
    into a row-major one.

    Parameters
    ----------
    control : RadioEditor
        The RadioEditor of interest. Its control is the wx.Panel containing
        child objects organized with a wx.GridSizer
    index : int
        the index of interest
    """
    sizer = source.control.GetSizer()
    if isinstance(sizer, wx.BoxSizer):
        return index
    n = len(source.names)
    num_cols = sizer.GetCols()
    num_rows = sizer.GetEffectiveRowsCount()
    return column_major_to_row_major(index, n, num_rows, num_cols)


class _IndexedSimpleEditor(BaseSourceWithLocation):
    """Wrapper class for Simple EnumEditor and Index."""

    source_class = SimpleEditor
    locator_class = Index
    handlers = [
        (
            MouseClick,
            (
                lambda wrapper, _: _interaction_helpers.mouse_click_combobox_or_choice(
                    control=wrapper._target.source.control,
                    index=wrapper._target.location.index,
                    delay=wrapper.delay,
                )
            ),
        ),
    ]


def simple_displayed_selected_text_handler(wrapper, interaction):
    """Handler function used to query DisplayedText for Simple Enum Editor.
    Note that depending on the factories evaluaute trait, the control for a
    Simple Enum Editor can either be a wx.ComboBox or a wx.Choice.

    Parameters
    ----------
    wrapper : UIWrapper
        The UIWrapper containing that object with text to be displayed.
    interaction : DisplayedText
        Unused in this function but included to match the expected format of a
        handler.  Should only be DisplayedText
    """
    control = wrapper._target.control
    if isinstance(control, wx.ComboBox):
        return control.GetValue()
    else:  # wx.Choice
        return control.GetString(control.GetSelection())


def radio_selected_text_handler(wrapper, interaction):
    """Handler function used to query SelectedText for EnumRadioEditor.

    Parameters
    ----------
    wrapper : UIWrapper
        The UIWrapper containing that object with text that is selected.
    interaction : SelectedText
        Unused in this function but included to match the expected format of a
        handler.  Should only be SelectedText
    """
    children_list = wrapper._target.control.GetSizer().GetChildren()
    for child in children_list:
        if child.GetWindow().GetValue():
            return child.GetWindow().GetLabel()
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
                lambda wrapper, interaction: _interaction_helpers.key_click_combobox(
                    control=wrapper._target.control,
                    interaction=interaction,
                    delay=wrapper.delay,
                )
            ),
        ),
        (
            KeySequence,
            (
                lambda wrapper, interaction: _interaction_helpers.key_sequence_text_ctrl(
                    control=wrapper._target.control,
                    interaction=interaction,
                    delay=wrapper.delay,
                )
            ),
        ),
        (DisplayedText, simple_displayed_selected_text_handler),
        (SelectedText, simple_displayed_selected_text_handler),
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
        handler=lambda wrapper, _: wrapper._target.control.GetString(
            wrapper._target.control.GetSelection()
        ),
    )
