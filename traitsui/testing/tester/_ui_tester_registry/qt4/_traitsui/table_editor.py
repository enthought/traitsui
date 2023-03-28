# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

from traitsui.qt.table_editor import SimpleEditor

from traitsui.testing.tester.command import (
    MouseClick,
    MouseDClick,
    KeyClick,
    KeySequence,
)
from traitsui.testing.tester.locator import Cell
from traitsui.testing.tester.query import (
    DisplayedText,
    Selected,
    SelectedIndices,
)
from traitsui.testing.tester._ui_tester_registry._common_ui_targets import (
    BaseSourceWithLocation
)
from traitsui.testing.tester._ui_tester_registry.qt import (
    _interaction_helpers
)


def _query_table_editor_selected(wrapper, interaction):
    selected = wrapper._target.selected
    if not isinstance(selected, list):
        if selected is None:
            return []
        else:
            return [selected]
    else:
        return selected


def _query_table_editor_selected_indices(wrapper, interaction):
    selected_indices = wrapper._target.selected_indices
    if not isinstance(selected_indices, list):
        if selected_indices == -1:
            return []
        else:
            return [selected_indices]
    else:
        return selected_indices


class _SimpleEditorWithCell(BaseSourceWithLocation):
    source_class = SimpleEditor
    locator_class = Cell
    handlers = [
        (MouseClick, lambda wrapper, _: wrapper._target._mouse_click(
            delay=wrapper.delay)),
        (KeyClick, lambda wrapper, interaction: wrapper._target._key_click(
            key=interaction.key,
            delay=wrapper.delay,)),
        (
            KeySequence,
            lambda wrapper, interaction: wrapper._target._key_sequence(
                sequence=interaction.sequence,
                delay=wrapper.delay,
            )
        ),
        (
            DisplayedText,
            lambda wrapper, _: wrapper._target._get_displayed_text()
        ),
        (MouseDClick, lambda wrapper, _: wrapper._target._mouse_dclick(
            delay=wrapper.delay,)),
    ]

    def _get_model_view_index(self):
        table_view = self.source.table_view
        return dict(
            model=table_view.model(),
            view=table_view,
            index=table_view.model().index(
                self.location.row, self.location.column
            ),
        )

    def _mouse_click(self, delay=0):
        _interaction_helpers.mouse_click_item_view(
            **self._get_model_view_index(),
            delay=delay,
        )

    def _mouse_dclick(self, delay=0):
        _interaction_helpers.mouse_dclick_item_view(
            **self._get_model_view_index(),
            delay=delay,
        )

    def _key_sequence(self, sequence, delay=0):
        _interaction_helpers.key_sequence_item_view(
            **self._get_model_view_index(),
            sequence=sequence,
            delay=delay,
        )

    def _key_click(self, key, delay=0):
        _interaction_helpers.key_click_item_view(
            **self._get_model_view_index(),
            key=key,
            delay=delay,
        )

    def _get_displayed_text(self):
        return _interaction_helpers.get_display_text_item_view(
            **self._get_model_view_index(),
        )


def register(registry):
    """ Register interactions for the given registry.

    If there are any conflicts, an error will occur.

    Parameters
    ----------
    registry : TargetRegistry
        The registry being registered to.
    """
    _SimpleEditorWithCell.register(registry)
    registry.register_interaction(
        target_class=SimpleEditor,
        interaction_class=Selected,
        handler=_query_table_editor_selected
    )
    registry.register_interaction(
        target_class=SimpleEditor,
        interaction_class=SelectedIndices,
        handler=_query_table_editor_selected_indices
    )
