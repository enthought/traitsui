#
#  Copyright (c) 2015, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Author: Senganal T.
#  Date:   Feb 2015
#

"""
Test cases for the Controller class.
"""

import unittest

from traits.api import HasTraits, Instance, Str
from traitsui.api import Controller


class FooModel(HasTraits):
    my_str = Str("hallo")


class FooController(Controller):
    """ Test dialog that does nothing useful."""

    model = Instance(FooModel)

    def _model_default(self):
        return FooModel(my_str="meh")


class TestController(unittest.TestCase):

    def test_construction(self):
        # check default constructor.
        dialog = FooController()
        self.assertIsNotNone(dialog.model)
        self.assertEqual(dialog.model.my_str, "meh")

        # check initialization when `model` is explcitly passed in.
        new_model = FooModel()
        dialog = FooController(model=new_model)
        self.assertIs(dialog.model, new_model)
