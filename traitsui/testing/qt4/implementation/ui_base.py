from traitsui.qt4.ui_base import ButtonEditor
from traitsui.testing import locator


def register(registry):
    registry.register_location_solver(
        target_class=ButtonEditor,
        locator_class=locator.DefaultTarget,
        solver=lambda wrapper, _: wrapper.editor.control,
    )
