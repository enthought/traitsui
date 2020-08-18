from functools import partial, reduce

import wx

from traitsui.api import (
    ButtonEditor,
    InstanceEditor,
)
from traitsui.wx.instance_editor import (
    SimpleEditor as SimpleInstanceEditor,
    CustomEditor as CustomInstanceEditor,
)
from traitsui.wx.range_editor import (
    SimpleSliderEditor,
    RangeTextEditor,
)
from traitsui.testing import command
from traitsui.testing import query
from traitsui.testing import locator
from traitsui.testing import registry_helper
from traitsui.testing.interactor_registry import InteractionRegistry
from traitsui.testing.wx import helpers
from traitsui.testing.wx.implementation import (
    button_editor,
    range_editor,
    text_editor,
    ui_base,
)


def resolve_location_simple_editor(interactor, _):
    return interactor.editor.edit_instance(None)


def resolve_location_custom_instance_editor(interactor, _):
    return interactor.editor._ui


def get_default_registry():
    registry = get_generic_registry()

    # ButtonEditor
    button_editor.register(registry)

    # InstanceEditor
    registry.register_location_solver(
        target_class=SimpleInstanceEditor,
        locator_class=locator.DefaultTarget,
        solver=resolve_location_simple_editor,
    )
    registry.register_location_solver(
        target_class=CustomInstanceEditor,
        locator_class=locator.DefaultTarget,
        solver=resolve_location_custom_instance_editor,
    )

    # RangeEditor
    range_editor.register(registry)

    # TextEditor
    text_editor.register(registry)

    ui_base.register(registry)
    return registry


def get_generic_registry():
    registry = InteractionRegistry()

    registry.register(
        target_class=wx.TextCtrl,
        interaction_class=command.KeyClick,
        handler=lambda interactor, action: (
            helpers.key_press_text_ctrl(
                control=interactor.editor,
                key=action.key,
                delay=interactor.delay,
            )
        ),
    )
    registry.register(
        target_class=wx.TextCtrl,
        interaction_class=command.KeySequence,
        handler=lambda interactor, action: (
            helpers.key_sequence_text_ctrl(
                control=interactor.editor,
                sequence=action.sequence,
                delay=interactor.delay,
            )
        ),
    )
    registry.register(
        target_class=wx.StaticText,
        interaction_class=query.DisplayedText,
        handler=lambda interactor, action: (
            interactor.editor.GetLabel()
        ),
    )
    registry.register(
        target_class=wx.Button,
        interaction_class=command.MouseClick,
        handler=lambda interactor, _: (
            helpers.mouse_click_button(
                control=interactor.editor, delay=interactor.delay,
            )
        )
    )
    return registry
