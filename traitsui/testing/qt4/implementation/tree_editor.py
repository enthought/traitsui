from traitsui.qt4.tree_editor import SimpleEditor
from traitsui.testing.qt4 import helpers
from traitsui.testing import command, locator, registry_helper, query


class _SimpleEditorWithTreeNode:
    """ Wrapper for (simple) TreeEditor and locator.TreeNode"""

    def __init__(self, editor, node):
        self.editor = editor
        self.node = node

    @classmethod
    def from_location(cls, wrapper, location):
        return cls(
            editor=wrapper.editor,
            node=location,
        )

    @classmethod
    def register(cls, registry):
        registry.register_location_solver(
            target_class=SimpleEditor,
            locator_class=locator.TreeNode,
            solver=cls.from_location,
        )
        registry.register(
            target_class=cls,
            interaction_class=command.MouseClick,
            handler=lambda wrapper, _: wrapper.editor._mouse_click(
                delay=wrapper.delay,
            ),
        )
        registry.register(
            target_class=cls,
            interaction_class=command.MouseDClick,
            handler=lambda wrapper, _: wrapper.editor._mouse_dclick(
                delay=wrapper.delay,
            ),
        )
        registry.register(
            target_class=cls,
            interaction_class=command.KeySequence,
            handler=lambda wrapper, action: wrapper.editor._key_sequence(
                sequence=action.sequence,
                delay=wrapper.delay,
            ),
        )
        registry.register(
            target_class=cls,
            interaction_class=command.KeyClick,
            handler=lambda wrapper, action: wrapper.editor._key_press(
                key=action.key,
                delay=wrapper.delay,
            ),
        )
        registry.register(
            target_class=cls,
            interaction_class=query.DisplayedText,
            handler=lambda wrapper, _: (
                wrapper.editor._get_displayed_text()
            ),
        )

    def _get_model_view_index(self):
        tree_view = self.editor._tree
        i_column = self.node.column
        i_rows = iter(self.node.row)
        item = tree_view.topLevelItem(next(i_rows))
        for i_row in i_rows:
            item = item.child(i_row)
        q_model_index = tree_view.indexFromItem(item, i_column)
        return dict(
            model=tree_view.model(),
            view=tree_view,
            index=q_model_index,
        )

    def _mouse_click(self, delay=0):
        helpers.mouse_click_item_view(
            **self._get_model_view_index(),
            delay=delay,
        )

    def _mouse_dclick(self, delay=0):
        helpers.mouse_dclick_item_view(
            **self._get_model_view_index(),
            delay=delay,
        )

    def _key_press(self, key, delay=0):
        helpers.key_press_item_view(
            **self._get_model_view_index(),
            key=key,
            delay=delay,
        )

    def _key_sequence(self, sequence, delay=0):
        helpers.key_sequence_item_view(
            **self._get_model_view_index(),
            sequence=sequence,
            delay=delay,
        )

    def _get_displayed_text(self):
        return helpers.get_display_text_item_view(
            **self._get_model_view_index(),
        )


def register(registry):
    _SimpleEditorWithTreeNode.register(registry)
    registry.register_location_solver(
        target_class=SimpleEditor,
        locator_class=locator.NestedUI,
        solver=lambda wrapper, _: wrapper.editor._editor._node_ui,
    )
    registry_helper.register_find_by_in_nested_ui(
        registry=registry,
        target_class=SimpleEditor,
    )