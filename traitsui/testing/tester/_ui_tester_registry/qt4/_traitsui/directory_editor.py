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
from traitsui.qt.directory_editor import SimpleEditor


def register(registry):
    """Register interactions for the given registry.

    If there are any conflicts, an error will occur.

    Parameters
    ----------
    registry : TargetRegistry
        The registry being registered to.
    """

    register_editable_textbox_handlers(
        registry=registry,
        target_class=SimpleEditor,
        widget_getter=lambda wrapper: wrapper._target._file_name,
    )
