from traitsui.qt4.enum_editor import (
    ListEditor,
    RadioEditor,
    SimpleEditor,
)
from traitsui.testing import command, locator
from traitsui.testing.qt4 import helpers


class _IndexedListEditor:
    """ Wrapper for (list) EnumEditor and index """

    def __init__(self, editor, index):
        self.editor = editor
        self.index = index

    @classmethod
    def from_location(cls, wrapper, location):
        return cls(
            editor=wrapper.editor,
            index=location.index,
        )

    @classmethod
    def register(cls, registry):
        registry.register_location_solver(
            target_class=ListEditor,
            locator_class=locator.Index,
            solver=cls.from_location,
        )
        registry.register(
            target_class=cls,
            interaction_class=command.MouseClick,
            handler=lambda wrapper, _: (
                wrapper.editor.mouse_click(delay=wrapper.delay)
            )
        )

    def mouse_click(self, delay=0):
        list_widget = self.editor.control
        helpers.mouse_click_item_view(
            model=list_widget.model(),
            view=list_widget,
            index=list_widget.model().index(self.index, 0)
        )


class _IndexedRadioEditor:
    """ Wrapper for RadioEditor and an index.
    """

    def __init__(self, editor, index):
        self.editor = editor
        self.index = index

    @classmethod
    def from_location(cls, wrapper, location):
        return cls(
            editor=wrapper.editor,
            index=location.index,
        )

    @classmethod
    def register(cls, registry):
        registry.register_location_solver(
            target_class=RadioEditor,
            locator_class=locator.Index,
            solver=cls.from_location,
        )
        registry.register(
            target_class=cls,
            interaction_class=command.MouseClick,
            handler=lambda wrapper, _: wrapper.editor.mouse_click(
                delay=wrapper.delay,
            ),
        )

    def mouse_click(self, delay=0):
        helpers.mouse_click_qlayout(
            layout=self.editor.control.layout(),
            index=self.index,
        )


class _IndexedSimpleEditor:
    """ Wrapper for (simple) EnumEditor and an index."""

    def __init__(self, editor, index):
        self.editor = editor
        self.index = index

    @classmethod
    def register(cls, registry):
        registry.register_location_solver(
            target_class=SimpleEditor,
            locator_class=locator.Index,
            solver=cls.from_location,
        )
        registry.register(
            target_class=cls,
            interaction_class=command.MouseClick,
            handler=lambda wrapper, _: wrapper.editor.mouse_click(
                delay=wrapper.delay,
            ),
        )

    @classmethod
    def from_location(cls, wrapper, location):
        return cls(
            editor=wrapper.editor,
            index=location.index,
        )

    def mouse_click(self, delay=0):
        helpers.mouse_click_combobox(
            combobox=self.editor.control,
            index=self.index,
            delay=delay,
        )


def register(registry):
    """ Registry location and interaction handlers for EnumEditor.

    Parameters
    ----------
    registry : InteractionRegistry
    """
    _IndexedListEditor.register(registry)
    _IndexedRadioEditor.register(registry)
    _IndexedSimpleEditor.register(registry)
