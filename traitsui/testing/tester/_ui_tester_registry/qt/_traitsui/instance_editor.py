# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

from traitsui.testing.tester.command import MouseClick
from traitsui.testing.tester.locator import Index
from traitsui.testing.tester.query import SelectedText
from traitsui.testing.tester._ui_tester_registry._common_ui_targets import (
    BaseSourceWithLocation,
)
from traitsui.testing.tester._ui_tester_registry.qt._interaction_helpers import (  # noqa
    mouse_click_combobox,
    mouse_click_qwidget,
)
from traitsui.testing.tester._ui_tester_registry._traitsui_ui import (
    register_traitsui_ui_solvers,
)
from traitsui.qt.instance_editor import CustomEditor, SimpleEditor


def _get_nested_ui_simple(target):
    """Obtains a nested UI within a Simple Instance Editor.

    Parameters
    ----------
    target : instance of SimpleEditor
    """
    return target._dialog_ui


def _get_nested_ui_custom(target):
    """Obtains a nested UI within a Custom Instance Editor.

    Parameters
    ----------
    target : instance of CustomEditor
    """
    return target._ui


def _get_combobox(target):
    """Obtains a nested combobox within an Instance Editor.

    Parameters
    ----------
    target : instance of CustomEditor
    """
    return target._choice


def _click_combobox_index(wrapper, _):
    return mouse_click_combobox(
        combobox=_get_combobox(wrapper._target.source),
        index=wrapper._target.location.index,
        delay=wrapper.delay,
    )


def _get_combobox_text(wrapper, _):
    return _get_combobox(wrapper._target).currentText()


class _IndexedCustomEditor(BaseSourceWithLocation):
    """Wrapper class for CustomEditors with a selection."""

    source_class = CustomEditor
    locator_class = Index
    handlers = [
        (MouseClick, _click_combobox_index),
    ]


def register(registry):
    """Register interactions for the given registry.

    If there are any conflicts, an error will occur.

    Parameters
    ----------
    registry : TargetRegistry
        The registry being registered to.
    """
    _IndexedCustomEditor.register(registry)

    registry.register_interaction(
        target_class=SimpleEditor,
        interaction_class=MouseClick,
        handler=lambda wrapper, _: (
            mouse_click_qwidget(wrapper._target._button, delay=wrapper.delay)
        ),
    )
    register_traitsui_ui_solvers(registry, SimpleEditor, _get_nested_ui_simple)

    registry.register_interaction(
        target_class=CustomEditor,
        interaction_class=SelectedText,
        handler=_get_combobox_text,
    )
    register_traitsui_ui_solvers(registry, CustomEditor, _get_nested_ui_custom)
