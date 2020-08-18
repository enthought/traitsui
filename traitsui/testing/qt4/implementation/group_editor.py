
from traitsui.qt4.ui_panel import TabbedFoldGroupEditor
from traitsui.testing import command, locator


class _IndexedTabbedFoldGroupEditor:

    def __init__(self, editor, index):
        # TabbedFoldGroupEditor could hold a Toolbar as well.
        qtab_or_qtoolbox = editor.container
        if qtab_or_qtoolbox.widget(index) is None:
            raise IndexError(index)
        self.editor = editor
        self.index = index

    def mouse_click(self, delay=0):
        # Not actually mouse click, but setCurrentIndex is available
        # for both QToolbar and QTabWidget
        self.editor.container.setCurrentIndex(self.index)

    @classmethod
    def from_location_index(cls, interactor, location):
        return cls(
            editor=interactor.editor, index=location.index,
        )


def register_tabbed_fold_group_editor(registry):
    registry.register_location_solver(
        target_class=TabbedFoldGroupEditor,
        locator_class=locator.Index,
        solver=_IndexedTabbedFoldGroupEditor.from_location_index,
    )
    registry.register(
        target_class=_IndexedTabbedFoldGroupEditor,
        interaction_class=command.MouseClick,
        handler=lambda interactor, _: (
            interactor.editor.mouse_click(delay=interactor.delay)
        )
    )
