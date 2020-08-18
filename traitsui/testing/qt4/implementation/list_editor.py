from pyface.qt.QtTest import QTest

from traitsui.qt4.list_editor import (
    CustomEditor,
    NotebookEditor,
)
from traitsui.testing import (
    command,
    locator,
    registry_helper,
)
from traitsui.testing.qt4.helpers import mouse_click_tab_index


class _IndexedNotebookEditor:

    def __init__(self, editor, index):
        self.editor = editor
        self.index = index

    @classmethod
    def from_location(cls, interactor, location):
        # Raise IndexError early
        interactor.editor._uis[location.index]
        return cls(
            editor=interactor.editor,
            index=location.index,
        )

    @classmethod
    def register(cls, registry):
        registry.register_location_solver(
            target_class=NotebookEditor,
            locator_class=locator.Index,
            solver=cls.from_location,
        )
        registry.register_location_solver(
            target_class=cls,
            locator_class=locator.NestedUI,
            solver=lambda interactor, _: interactor.editor.get_nested_ui(),
        )
        registry_helper.register_find_by_in_nested_ui(
            registry=registry,
            target_class=cls,
        )
        registry.register(
            target_class=cls,
            interaction_class=command.MouseClick,
            handler=lambda interactor, _: (
                interactor.editor.mouse_click(delay=interactor.delay)
            ),
        )

    def get_nested_ui(self):
        return self.editor._uis[self.index][1]

    def mouse_click(self, delay=0):
        mouse_click_tab_index(self.editor.control, self.index, delay=delay)


class _IndexedCustomEditor:
    """ Wrapper for a ListEditor (custom) with an index.
    """

    def __init__(self, editor, index):
        self.editor = editor
        self.index = index

    @classmethod
    def from_location(cls, interactor, location):
        return cls(
            editor=interactor.editor,
            index=location.index,
        )

    @classmethod
    def register(cls, registry):
        registry.register_location_solver(
            target_class=CustomEditor,
            locator_class=locator.Index,
            solver=cls.from_location,
        )
        registry.register_location_solver(
            target_class=cls,
            locator_class=locator.NestedUI,
            solver=lambda interactor, _: interactor.editor._get_nested_ui(),
        )
        registry_helper.register_find_by_in_nested_ui(
            registry=registry,
            target_class=cls,
        )

    def _get_nested_ui(self):
        row, column = divmod(self.index, self.editor.factory.columns)
        grid_layout = self.editor._list_pane.layout()
        item = grid_layout.itemAtPosition(row, column)
        if item is None:
            raise IndexError(self.index)
        if self.editor.scrollable:
            self.editor.control.ensureWidgetVisible(item.widget())
        return item.widget()._editor._ui


def register_list_editor(registry):
    # NotebookEditor
    _IndexedNotebookEditor.register(registry)

    # CustomEditor
    _IndexedCustomEditor.register(registry)
