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
from traitsui.wx.range_editor import (
    LargeRangeSliderEditor,
    LogRangeSliderEditor,
    RangeTextEditor,
    SimpleSliderEditor,
)

from traitsui.testing.tester import locator
from traitsui.testing.tester.wx.common_ui_targets import LocatedTextbox


def resolve_location_slider(wrapper, location):
    """ Solver from a UIWrapper wrapped Range Editor to a LocatedTextbox
    containing the textbox of interest

    If there are any conflicts, an error will occur.

    Parameters
    ----------
    wrapper : UIWrapper
        Wrapper containing the Range Editor target.
    location : locator.WidgetType
        The location we are looking to resolve.
    """
    if location == locator.WidgetType.textbox:
        textbox = wrapper.target.control.text
        # wx defaults to having insertion point start at 0
        # for consistent behavior accross toolkits, we set this default to
        # be the right most point of the textbox
        textbox.SetInsertionPoint(textbox.GetLastPosition()+1)
        return LocatedTextbox(textbox=textbox)
    if location in [locator.WidgetType.slider]:
        raise NotImplementedError(
            f"Logic for interacting with the {location}"
            " has not been implemented."
        )
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
        textbox = wrapper.target.control
        # wx defaults to having insertion point start at 0
        # for consistent behavior accross toolkits, we set this default to
        # be the right most point of the textbox
        textbox.SetInsertionPoint(textbox.GetLastPosition()+1)
        return LocatedTextbox(textbox=textbox)
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
