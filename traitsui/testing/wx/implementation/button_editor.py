from traitsui.wx.button_editor import SimpleEditor
from traitsui.testing import locator
from traitsui.testing.wx import helpers


def register(registry):
    registry.register_location_solver(
        target_class=SimpleEditor,
        locator_class=locator.DefaultTarget,
        solver=lambda interactor, _: interactor.editor.control,
    )
