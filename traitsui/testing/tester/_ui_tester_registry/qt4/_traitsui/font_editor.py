# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

from traitsui.testing.tester._ui_tester_registry.qt._registry_helper import (
    register_editable_textbox_handlers,
)
from traitsui.qt.font_editor import TextFontEditor


def register(registry):
    """Register interactions pertaining to (Qt) FontEditor for the given
    registry.

    Parameters
    ----------
    registry : TargetRegistry
        The registry being registered to.
    """
    register_editable_textbox_handlers(
        registry=registry,
        target_class=TextFontEditor,
        widget_getter=lambda wrapper: wrapper._target.control,
    )
