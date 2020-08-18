from traitsui.wx.text_editor import SimpleEditor, ReadonlyEditor
from traitsui.testing import locator


def register(registry):
    registry.register_location_solver(
        target_class=SimpleEditor,
        locator_class=locator.DefaultTarget,
        solver=lambda wrapper, _: wrapper.editor.control,
    )
    registry.register_location_solver(
        target_class=ReadonlyEditor,
        locator_class=locator.DefaultTarget,
        solver=lambda wrapper, _: wrapper.editor.control,
    )
