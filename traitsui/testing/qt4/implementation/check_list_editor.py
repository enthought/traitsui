from traitsui.qt4.check_list_editor import CustomEditor
from traitsui.testing import command, locator
from traitsui.testing.qt4 import helpers


class _IndexedCustomCheckListEditor:
    """ Wrapper for CheckListEditor + locator.Index """

    def __init__(self, editor, index):
        self.editor = editor
        self.index = index

    @classmethod
    def from_location_index(cls, wrapper, location):
        # Conform to the call signature specified in the register
        return cls(
            editor=wrapper.editor,
            index=location.index,
        )

    @classmethod
    def register(cls, registry):
        registry.register_location_solver(
            target_class=CustomEditor,
            locator_class=locator.Index,
            solver=cls.from_location_index,
        )
        registry.register(
            target_class=cls,
            interaction_class=command.MouseClick,
            handler=lambda wrapper, _: wrapper.editor.mouse_click(
                delay=wrapper.delay,
            )
        )

    def mouse_click(self, delay=0):
        helpers.mouse_click_qlayout(
            layout=self.editor.control.layout(),
            index=self.index,
            delay=delay,
        )


def register(registry):
    _IndexedCustomCheckListEditor.register(registry)
