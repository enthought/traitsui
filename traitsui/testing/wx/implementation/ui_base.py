from traitsui.wx.ui_base import ButtonEditor
from traitsui.testing import locator


def register(registry):
    registry.register_location_solver(
        target_class=ButtonEditor,
        locator_class=locator.DefaultTarget,
        solver=lambda interactor, _: interactor.editor.control,
    )
