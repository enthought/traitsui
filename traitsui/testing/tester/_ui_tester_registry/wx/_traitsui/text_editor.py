# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

from traitsui.wx.text_editor import CustomEditor, ReadonlyEditor, SimpleEditor
from traitsui.testing.tester.query import DisplayedText
from traitsui.testing.tester._ui_tester_registry.wx import _interaction_helpers
from traitsui.testing.tester._ui_tester_registry.wx._registry_helper import (
    register_editable_textbox_handlers,
)


def register(registry):
    """Register interactions for the given registry.

    If there are any conflicts, an error will occur.

    Parameters
    ----------
    registry : TargetRegistry
        The registry being registered to.
    """
    for target_class in [CustomEditor, SimpleEditor]:
        register_editable_textbox_handlers(
            registry=registry,
            target_class=target_class,
            widget_getter=lambda wrapper: wrapper._target.control,
        )

    registry.register_interaction(
        target_class=ReadonlyEditor,
        interaction_class=DisplayedText,
        handler=lambda wrapper, _: _interaction_helpers.readonly_textbox_displayed_text(
            wrapper._target.control
        ),
    )
