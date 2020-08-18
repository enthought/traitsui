
from traitsui.wx.range_editor import (
    SimpleSliderEditor,
    RangeTextEditor,
)
from traitsui.testing.wx import helpers
from traitsui.testing import command, locator


class _SimpleSliderEditorWithSlider:
    """ Wrapper for SimpleSliderEditor + locator.WidgetType.slider"""

    def __init__(self, editor):
        self.editor = editor

    @classmethod
    def register(cls, registry):
        registry.register(
            target_class=cls,
            interaction_class=command.KeyClick,
            handler=lambda wrapper, action: (
                wrapper.editor.key_press(
                    key=action.key, delay=wrapper.delay,
                )
            )
        )

    def key_press(self, key, delay=0):
        helpers.key_press_slider(
            slider=self.editor.control.slider,
            key=key,
            delay=delay,
        )


def resolve_location_simple_slider(wrapper, location):
    if location == locator.WidgetType.slider:
        return _SimpleSliderEditorWithSlider(
            editor=wrapper.editor,
        )
    if location == locator.WidgetType.textbox:
        return wrapper.editor.control.text

    raise NotImplementedError()


def register(registry):

    registry.register_location_solver(
        target_class=SimpleSliderEditor,
        locator_class=locator.WidgetType,
        solver=resolve_location_simple_slider,
    )
    _SimpleSliderEditorWithSlider.register(registry)

