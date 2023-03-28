# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

from traitsui.testing.tester.target_registry import TargetRegistry
from traitsui.testing.tester._ui_tester_registry.qt._traitsui import (
    boolean_editor,
    button_editor,
    check_list_editor,
    directory_editor,
    editor_factory,
    enum_editor,
    file_editor,
    font_editor,
    instance_editor,
    list_editor,
    range_editor,
    table_editor,
    text_editor,
    ui_base,
)
from ._control_widget_registry import get_widget_registry


def get_default_registries():
    """Creates the default registries for UITester that are qt specific.

    Returns
    -------
    registries : list of AbstractTargetRegistry
        The default registries containing implementations for TraitsUI editors
        that are qt specific.
    """
    registry = TargetRegistry()

    # BooleanEditor
    boolean_editor.register(registry)

    # ButtonEditor
    button_editor.register(registry)

    # CheckListEditor
    check_list_editor.register(registry)

    # DirectoryEditor
    directory_editor.register(registry)

    # EnumEditor
    enum_editor.register(registry)

    # FileEditor
    file_editor.register(registry)

    # FontEditor
    font_editor.register(registry)

    # TextEditor
    text_editor.register(registry)

    # ListEditor
    list_editor.register(registry)

    # RangeEditor
    range_editor.register(registry)

    # ui_base
    ui_base.register(registry)

    # InstanceEditor
    instance_editor.register(registry)

    # Editor Factory
    editor_factory.register(registry)

    # TableEditor
    table_editor.register(registry)

    # The more general registry goes after the more specific registry.
    return [
        registry,
        get_widget_registry(),
    ]
