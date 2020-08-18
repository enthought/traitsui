
from pyface.qt import QtCore, QtGui
from pyface.qt.QtTest import QTest

from traitsui.api import (
    CheckListEditor,
    EnumEditor,
    ListEditor,
    TreeEditor,
)
from traitsui.qt4.instance_editor import (
    SimpleEditor as SimpleInstanceEditor,
    CustomEditor as CustomInstanceEditor,
)
from traitsui.qt4.list_editor import (
    CustomEditor as CustomListEditor,
    NotebookEditor as NotebookListEditor,
)
from traitsui.qt4.range_editor import SimpleSliderEditor
from traitsui.qt4.tree_editor import SimpleEditor as SimpleTreeEditor
from traitsui.qt4.ui_panel import TabbedFoldGroupEditor
from traitsui.testing import command
from traitsui.testing import query
from traitsui.testing import locator
from traitsui.testing import registry_helper
from traitsui.testing.exceptions import Disabled
from traitsui.testing.qt4 import helpers
from traitsui.testing.qt4.implementation import (
    button_editor,
    check_list_editor,
    enum_editor,
    group_editor,
    list_editor,
    table_editor,
    text_editor,
    tree_editor,
    ui_base,
)
from traitsui.testing.interactor_registry import InteractionRegistry


def resolve_location_simple_editor(wrapper, location):
    if wrapper.editor._dialog_ui is None:
        wrapper.editor._button.click()
    return wrapper.editor._dialog_ui


def resolve_location_custom_instance_editor(wrapper, location):
    return wrapper.editor._ui


def resolve_location_range_editor(wrapper, location):
    type_to_widget = {
        locator.WidgetType.slider: wrapper.editor.control.slider,
        locator.WidgetType.textbox: wrapper.editor.control.text,
    }
    return type_to_widget[location]


def key_sequence_qwidget(wrapper, action):
    if not wrapper.editor.isEnabled():
        raise Disabled("{!r} is disabled.".format(wrapper.editor))
    QTest.keyClicks(wrapper.editor, action.sequence, delay=wrapper.delay)


def key_press_qwidget(wrapper, action):
    if not wrapper.editor.isEnabled():
        raise Disabled("{!r} is disabled.".format(wrapper.editor))
    helpers.key_press(
        wrapper.editor, action.key, delay=wrapper.delay
    )


def mouse_click_qwidget(wrapper, action):
    QTest.mouseClick(
        wrapper.editor,
        QtCore.Qt.LeftButton,
        delay=wrapper.delay,
    )


def get_default_registry():
    """ Return the default registry of implementations for Qt editors.

    Returns
    -------
    registry : InteractionRegistry
    """
    registry = get_generic_registry()

    # ButtonEditor
    button_editor.register(registry)

    # TextEditor
    text_editor.register(registry)

    # CheckListEditor
    check_list_editor.register(registry)

    # EnumEditor
    enum_editor.register(registry)

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

    # TableEditor
    table_editor.register(registry)

    # TreeEditor
    tree_editor.register(registry)

    # ListEditor
    list_editor.register_list_editor(registry)

    # Tabbed in the UI
    group_editor.register_tabbed_fold_group_editor(registry)

    # RangeEditor (slider)
    registry.register_location_solver(
        target_class=SimpleSliderEditor,
        locator_class=locator.WidgetType,
        solver=resolve_location_range_editor,
    )

    # UI buttons
    ui_base.register(registry)
    return registry


def get_generic_registry():
    registry = InteractionRegistry()
    widget_classes = [
        QtGui.QLineEdit,
        QtGui.QSlider,
        QtGui.QTextEdit,
        QtGui.QPushButton,
    ]
    handlers = [
        (command.KeySequence, key_sequence_qwidget),
        (command.KeyClick, key_press_qwidget),
        (command.MouseClick, mouse_click_qwidget),
    ]
    for widget_class in widget_classes:
        for interaction_class, handler in handlers:
            registry.register(
                target_class=widget_class,
                interaction_class=interaction_class,
                handler=handler,
            )

    registry.register(
        target_class=QtGui.QPushButton,
        interaction_class=query.DisplayedText,
        handler=lambda wrapper, _: wrapper.editor.text(),
    )
    registry.register(
        target_class=QtGui.QLineEdit,
        interaction_class=query.DisplayedText,
        handler=lambda wrapper, _: wrapper.editor.displayText(),
    )
    registry.register(
        target_class=QtGui.QTextEdit,
        interaction_class=query.DisplayedText,
        handler=lambda wrapper, _: wrapper.editor.toPlainText(),
    )
    registry.register(
        target_class=QtGui.QLabel,
        interaction_class=query.DisplayedText,
        handler=lambda wrapper, _: wrapper.editor.text(),
    )
    return registry
