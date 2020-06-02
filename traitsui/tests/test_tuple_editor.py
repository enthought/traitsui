# ------------------------------------------------------------------------------
#
#  Copyright (c) 2014, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Author: Ioannis Tziakos
#  Date:   Aug 2014
#
# ------------------------------------------------------------------------------
"""
Test cases for the TupleEditor object.
"""

import unittest

from traits.api import Float, HasStrictTraits, Str, Tuple
from traits.testing.api import UnittestTools

from traitsui.api import Item, TupleEditor, View
from traitsui.tests._tools import (
    create_ui,
    skip_if_null,
    store_exceptions_on_all_threads,
)


class DummyModel(HasStrictTraits):
    """ Dummy model with a Tuple trait.
    """

    data = Tuple(Float, Float, Str)

    traits_view = View(Item(name="data", editor=TupleEditor()))


class TestTupleEditor(UnittestTools, unittest.TestCase):
    @skip_if_null
    def test_value_update(self):
        # Regression test for #179
        model = DummyModel()
        with store_exceptions_on_all_threads(), create_ui(model) as ui:
            with self.assertTraitChanges(model, "data", count=1):
                model.data = (3, 4.6, "nono")


if __name__ == "__main__":
    unittest.run()
