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

def find_by_name_in_nested_ui(wrapper, location):
    """ Helper function for resolving from an _IndexedCustomEditor to a
    TargetByName.

    Parameters
    ----------
    wrapper : UIWrapper
    location : instance of locator.TargetByName
    """
    new_interactor = wrapper.locate(locator.NestedUI())
    return new_interactor.find_by_name(location.name).target
