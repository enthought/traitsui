# -----------------------------------------------------------------------------
#
#  Copyright (c) 2013, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Author: Stefano Borini
#  Date:   Oct 2016
#
# -----------------------------------------------------------------------------
"""
Test case for ListStrEditor and ListStrAdapter
"""

from traits.has_traits import HasTraits
from traits.trait_types import List, Str
from traitsui.list_str_adapter import ListStrAdapter


class TraitObject(HasTraits):
    list_str = List(Str)


def test_list_str_adapter_length():
    """Test the ListStringAdapter len method"""

    object = TraitObject()
    object.list_str = ["hello"]

    adapter = ListStrAdapter()

    assert adapter.len(object, "list_str") == 1
    assert adapter.len(None, "list_str") == 0
