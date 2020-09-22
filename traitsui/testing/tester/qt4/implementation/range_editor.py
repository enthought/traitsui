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

from traitsui.qt4.range_editor import (
    LargeRangeSliderEditor,
    LogRangeSliderEditor,
    RangeTextEditor,
    SimpleSliderEditor,
)

from traitsui.testing.tester import locator
from traitsui.testing.tester.qt4 import _registry_helper
from traitsui.testing.tester.qt4.common_ui_targets import (
    LocatedSlider,
    LocatedTextbox
)


def register(registry):
    """ Register interactions for the given registry.

    If there are any conflicts, an error will occur.

    Parameters
    ----------
    registry : TargetRegistry
        The registry being registered to.
    """

    targets = [SimpleSliderEditor,
               LogRangeSliderEditor,
               LargeRangeSliderEditor]
    for target_class in targets:
        registry.register_solver(
            target_class=target_class,
            locator_class=locator.Textbox,
            solver=lambda wrapper, _: LocatedTextbox(
                textbox=wrapper._target.control.text),
        )
        registry.register_solver(
            target_class=target_class,
            locator_class=locator.Slider,
            solver=lambda wrapper, _: LocatedSlider(
                slider=wrapper._target.control.slider),
        )
    _registry_helper.register_editable_textbox_handlers(
        registry=registry,
        target_class=RangeTextEditor,
        widget_getter=lambda wrapper: wrapper._target.control,
    )
