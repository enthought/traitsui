from traitsui.testing import locator
from traitsui.qt4.button_editor import CustomEditor, SimpleEditor


def register(registry):
    """ Register actions for the given registry.

    If there are any conflicts, an error will occur.
    """
    registry.register_location_solver(
        target_class=SimpleEditor,
        locator_class=locator.DefaultTarget,
        solver=lambda interactor, _: interactor.editor.control,
    )
    registry.register_location_solver(
        target_class=CustomEditor,
        locator_class=locator.DefaultTarget,
        solver=lambda interactor, _: interactor.editor.control,
    )
