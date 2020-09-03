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

from traitsui.testing.tester import command, query
from traitsui.testing.tester.qt4 import helpers
from traitsui.testing.tester.qt4.common_ui_targets import (
    register_editable_textbox_handlers,
)
from traitsui.qt4.text_editor import CustomEditor, ReadonlyEditor, SimpleEditor


def register(registry):
    """ Register interactions for the given registry.

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
            widget_getter=lambda wrapper: wrapper.target.control,
        )
    for target_class in [ReadonlyEditor]:
        registry.register_handler(
            target_class=target_class,
            interaction_class=query.DisplayedText,
            handler=lambda wrapper, _: helpers.displayed_text_qobject(
                wrapper.target.control),
        )
