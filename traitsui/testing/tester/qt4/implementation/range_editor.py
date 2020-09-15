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


def resolve_location_spin(wrapper, location):
    """ Solver from a UIWrapper wrapped Range Editor to a LocatedTextbox
    containing the textbox of interest.

    If there are any conflicts, an error will occur.

    Parameters
    ----------
    wrapper : UIWrapper
        Wrapper containing the SimpleSpin Range Editor target.
    location : locator.WidgetType
        The location we are looking to resolve.
    """
    if location == locator.WidgetType.textbox:
        # FIX ME: THIS CODE DOESNT BELONG HERE
        textbox = wrapper.target.control.lineEdit()
        textbox.end(False)
        return LocatedTextbox(textbox=textbox)
    raise ValueError(
        f"Unable to resolve {location} on {wrapper.target}."
        " Currently supported: {locator.WidgetType.textbox}"
    )


def resolve_location_range_text(wrapper, location):
    """ Solver from a UIWrapper wrapped RangeTextEditor to a LocatedTextbox
    containing the textbox of interest

    If there are any conflicts, an error will occur.

    Parameters
    ----------
    wrapper : UIWrapper
        Wrapper containing the RangeTextEditor target.
    location : locator.WidgetType
        The location we are looking to resolve.
    """

    if location == locator.WidgetType.textbox:
        return LocatedTextbox(textbox=wrapper.target.control)
    raise ValueError(
        f"Unable to resolve {location} on {wrapper.target}."
        " Currently supported: {locator.WidgetType.textbox}"
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

    registry.register_solver(
        target_class=RangeTextEditor,
        locator_class=locator.WidgetType,
        solver=resolve_location_range_text,
    )
    registry.register_solver(
        target_class=SimpleSpinEditor,
        locator_class=locator.WidgetType,
        solver=resolve_location_spin,
    )
