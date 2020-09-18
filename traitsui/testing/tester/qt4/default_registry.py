#  Copyright (c) 2005-2020, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#

from traitsui.testing.tester.registry import TargetRegistry
from traitsui.testing.tester.qt4 import common_ui_targets
from traitsui.testing.tester.qt4.implementation import (
    button_editor,
    check_list_editor,
    editor_factory_readonly_editor,
    editor_factory_text_editor,
    enum_editor,
    font_editor,
    instance_editor,
    list_editor,
    range_editor,
    text_editor,
    ui_base,
)


def get_default_registry():
    """ Creates a default registry for UITester that is qt specific.

    Returns
    -------
    registry : TargetRegistry
        The default registry containing implementations for TraitsUI editors
        that is qt specific.
    """
    registry = TargetRegistry()

    common_ui_targets.LocatedTextbox.register(registry)

    common_ui_targets.LocatedSlider.register(registry)

    # ButtonEditor
    button_editor.register(registry)

    # CheckListEditor
    check_list_editor.register(registry)

    # EnumEditor
    enum_editor.register(registry)

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

    # Editor Factor Text Editor
    editor_factory_text_editor.register(registry)

    # Editor Factor Readonly Editor
    editor_factory_readonly_editor.register(registry)

    return registry
