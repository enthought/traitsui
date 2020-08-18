
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


def resolve_location_simple_editor(interactor, location):
    if interactor.editor._dialog_ui is None:
        interactor.editor._button.click()
    return interactor.editor._dialog_ui


def resolve_location_custom_instance_editor(interactor, location):
    return interactor.editor._ui


def resolve_location_range_editor(interactor, location):
    type_to_widget = {
        locator.WidgetType.slider: interactor.editor.control.slider,
        locator.WidgetType.textbox: interactor.editor.control.text,
    }
    return type_to_widget[location]


def key_sequence_qwidget(interactor, action):
    if not interactor.editor.isEnabled():
        raise Disabled("{!r} is disabled.".format(interactor.editor))
    QTest.keyClicks(interactor.editor, action.sequence, delay=interactor.delay)


def key_press_qwidget(interactor, action):
    if not interactor.editor.isEnabled():
        raise Disabled("{!r} is disabled.".format(interactor.editor))
    helpers.key_press(
        interactor.editor, action.key, delay=interactor.delay
    )


def mouse_click_qwidget(interactor, action):
    QTest.mouseClick(
        interactor.editor,
        QtCore.Qt.LeftButton,
        delay=interactor.delay,
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
        handler=lambda interactor, _: interactor.editor.text(),
    )
    registry.register(
        target_class=QtGui.QLineEdit,
        interaction_class=query.DisplayedText,
        handler=lambda interactor, _: interactor.editor.displayText(),
    )
    registry.register(
        target_class=QtGui.QTextEdit,
        interaction_class=query.DisplayedText,
        handler=lambda interactor, _: interactor.editor.toPlainText(),
    )
    registry.register(
        target_class=QtGui.QLabel,
        interaction_class=query.DisplayedText,
        handler=lambda interactor, _: interactor.editor.text(),
    )
    return registry
