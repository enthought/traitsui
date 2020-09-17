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

from traitsui.testing.tester import locator


def find_by_id_in_nested_ui(wrapper, location):
    """ Helper function for resolving from a target to a TargetById. The
    target must have a solver registered from it to an instance of
    traitsui.ui.UI

    Parameters
    ----------
    wrapper : UIWrapper
    location : instance of locator.TargetById
    """
    new_interactor = wrapper.locate(locator.NestedUI())
    return new_interactor.find_by_id(location.id).target


def find_by_name_in_nested_ui(wrapper, location):
    """ Helper function for resolving from a target to a TargetByName. The
    target must have a solver registered from it to an instance of
    traitsui.ui.UI

    Parameters
    ----------
    wrapper : UIWrapper
    location : instance of locator.TargetByName
    """
    new_interactor = wrapper.locate(locator.NestedUI())
    return new_interactor.find_by_name(location.name).target


def register_nested_ui_solvers(registry, target_class, nested_ui_getter):
    """ Function to register solvers for a particular target type to
    NestedUIs and TargetByNames within those NestedUIs.

    Parameters
    ----------
    registry : TargetRegistry
        The registry being registered to
    target_class : subclass of type
        The type of a UI target being used as the target_class for the
        solvers
    nested_ui_getter : callable(target: target_class) -> traitsui.ui.UI
        A callable specific to the particular target_class that resolves a
        NestedUI
    """

    registry.register_solver(
        target_class=target_class,
        locator_class=locator.NestedUI,
        solver=lambda wrapper, _: nested_ui_getter(wrapper.target),
    )
    registry.register_solver(
        target_class=target_class,
        locator_class=locator.TargetByName,
        solver=find_by_name_in_nested_ui,
    )
    registry.register_solver(
        target_class=target_class,
        locator_class=locator.TargetById,
        solver=find_by_id_in_nested_ui,
    )
