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
    SimpleSpinEditor,
)

from traitsui.testing.tester import locator
from traitsui.testing.tester.qt4 import registry_helper
from traitsui.testing.tester.qt4.common_ui_targets import (
    LocatedSlider,
    LocatedTextbox
)


def resolve_location_slider(wrapper, location):
    """ Solver from a UIWrapper wrapped Range Editor to a LocatedTextbox
    containing the textbox of interest, or a LocatedSlider containing the
    slider.

    If there are any conflicts, an error will occur.

    Parameters
    ----------
    wrapper : UIWrapper
        Wrapper containing the Range Editor target.
    location : locator.WidgetType
        The location we are looking to resolve.
    """
    if location == locator.WidgetType.textbox:
        return LocatedTextbox(textbox=wrapper.target.control.text)
    if location in [locator.WidgetType.slider]:
        return LocatedSlider(slider=wrapper.target.control.slider)
    raise ValueError(
        f"Unable to resolve {location} on {wrapper.target}."
        " Currently supported: {locator.WidgetType.textbox} and"
        " {locator.WidgetType.slider}"
    )


def _register_simple_spin(registry):
    """ Register interactions for the given registry for a SimpleSpinEditor.

    If there are any conflicts, an error will occur.

    This is kept separate from the below register function because the
    SimpleSpinEditor is not yet implemented on wx.  This function can be used
    with a local reigstry for tests.

    Parameters
    ----------
    registry : TargetRegistry
        The registry being registered to.
    """
    registry_helper.register_editable_textbox_handlers(
        registry=registry,
        target_class=SimpleSpinEditor,
        widget_getter=lambda wrapper: wrapper.target.control.lineEdit(),
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
            locator_class=locator.WidgetType,
            solver=resolve_location_slider,
        )
    registry_helper.register_editable_textbox_handlers(
        registry=registry,
        target_class=RangeTextEditor,
        widget_getter=lambda wrapper: wrapper.target.control,
    )
