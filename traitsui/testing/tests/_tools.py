from traitsui.testing.interactor_registry import InteractionRegistry
from traitsui.testing.ui_tester import command, UIWrapper


class FakeEditor:
    def __init__(self, control):
        self.control = control


def create_interactor(control=None, editor=None, locator_classes=None):
    registry = InteractionRegistry()

    if locator_classes:
        for locator_class in locator_classes:
            registry.register_location_solver(
                target_class=FakeEditor,
                locator_class=locator_class,
                solver=None,
            )

    if editor is None:
        editor = FakeEditor(control=control)
    return UIWrapper(editor, [registry])
