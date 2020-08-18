from traitsui.qt4.table_editor import SimpleEditor
from traitsui.testing import command, locator, query
from traitsui.testing.qt4 import helpers


class _SimpleEditorWithCell:
    """ Wrapper for (simple) TableEditor + Cell location."""
    def __init__(self, editor, cell):
        self.editor = editor
        self.cell = cell

    @classmethod
    def from_location(cls, interactor, location):
        return cls(
            editor=interactor.editor,
            cell=location,
        )

    @classmethod
    def register(cls, registry):
        registry.register_location_solver(
            target_class=SimpleEditor,
            locator_class=locator.Cell,
            solver=cls.from_location,
        )
        registry.register(
            target_class=cls,
            interaction_class=command.MouseClick,
            handler=lambda interactor, _: interactor.editor._mouse_click(
                delay=interactor.delay,
            ),
        )
        registry.register(
            target_class=cls,
            interaction_class=command.KeySequence,
            handler=lambda interactor, action: interactor.editor._key_sequence(
                sequence=action.sequence,
                delay=interactor.delay,
            ),
        )
        registry.register(
            target_class=cls,
            interaction_class=command.KeyClick,
            handler=lambda interactor, action: interactor.editor._key_press(
                key=action.key,
                delay=interactor.delay,
            ),
        )
        registry.register(
            target_class=cls,
            interaction_class=query.DisplayedText,
            handler=lambda interactor, _: (
                interactor.editor._get_displayed_text()
            ),
        )

    def _get_model_view_index(self):
        table_view = self.editor.table_view
        return dict(
            model=table_view.model(),
            view=table_view,
            index=table_view.model().index(self.cell.row, self.cell.column),
        )

    def _mouse_click(self, delay=0):
        helpers.mouse_click_item_view(
            **self._get_model_view_index(),
            delay=delay,
        )

    def _key_sequence(self, sequence, delay=0):
        helpers.key_sequence_item_view(
            **self._get_model_view_index(),
            sequence=sequence,
            delay=delay,
        )

    def _key_press(self, key, delay=0):
        helpers.key_press_item_view(
            **self._get_model_view_index(),
            key=key,
            delay=delay,
        )

    def _get_displayed_text(self):
        return helpers.get_display_text_item_view(
            **self._get_model_view_index(),
        )


def register(registry):
    _SimpleEditorWithCell.register(registry)
