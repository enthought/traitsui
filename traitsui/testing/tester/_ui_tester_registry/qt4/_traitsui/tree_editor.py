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

from traitsui.qt4.tree_editor import SimpleEditor


from traitsui.testing.tester.command import (
    MouseClick, MouseDClick, KeyClick, KeySequence
)
from traitsui.testing.tester.locator import TreeNode
from traitsui.testing.tester.query import DisplayedText
from traitsui.testing.tester._ui_tester_registry.qt4 import (
    _interaction_helpers
)

from traitsui.testing.tester._ui_tester_registry._common_ui_targets import (
    BaseSourceWithLocation
)
from traitsui.testing.tester._ui_tester_registry._traitsui_ui import (
    register_traitsui_ui_solvers,
)

class _SimpleEditorWithTreeNode(BaseSourceWithLocation):
    source_class = SimpleEditor
    locator_class = TreeNode
    handlers = [
        (MouseClick, lambda wrapper, _: wrapper._target._mouse_click(
            delay=wrapper.delay)),
        (MouseDClick, lambda wrapper, _: wrapper._target._mouse_dclick(
            delay=wrapper.delay)),
        (KeySequence,
            lambda wrapper, action: wrapper._target._key_sequence(
                sequence=action.sequence,
                delay=wrapper.delay,
            )),
        (KeyClick,
            lambda wrapper, action: wrapper._target._key_press(
                key=action.key,
                delay=wrapper.delay,
            )),
        (DisplayedText,
            lambda wrapper, _:  wrapper._target._get_displayed_text()),
    ]

    @classmethod
    def register(cls, registry):
        """ Class method to register interactions on a
        _SimpleEditorWithTreeNode for the given registry.

        If there are any conflicts, an error will occur.

        Parameters
        ----------
        registry : TargetRegistry
            The registry being registered to.
        """
        super().register(registry)
        register_traitsui_ui_solvers(
            registry=registry,
            target_class=cls,
            traitsui_ui_getter=lambda target: target._get_nested_ui()
        )

    def _get_model_view_index(self):
        tree_widget = self.source._tree
        i_column = self.location.column
        i_rows = iter(self.location.row)
        item = tree_widget.topLevelItem(next(i_rows))
        for i_row in i_rows:
            item = item.child(i_row)
        q_model_index = tree_widget.indexFromItem(item, i_column)
        return dict(
            model=tree_widget.model(),
            view=tree_widget,
            index=q_model_index,
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

    def _key_press(self, key, delay=0):
        _interaction_helpers.key_press_item_view(
            **self._get_model_view_index(),
            key=key,
            delay=delay,
        )

    def _key_sequence(self, sequence, delay=0):
        _interaction_helpers.key_sequence_item_view(
            **self._get_model_view_index(),
            sequence=sequence,
            delay=delay,
        )

    def _get_displayed_text(self):
        return _interaction_helpers.get_display_text_item_view(
            **self._get_model_view_index(),
        )

    def _get_nested_ui(self):
        """ Method to get the nested ui corresponding to the List element at
        the given index.
        """
        return self.source._editor._node_ui


def register(registry):
    _SimpleEditorWithTreeNode.register(registry)
