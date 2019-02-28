#
#  Copyright (c) 2015, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Author: Senganal T.
#  Date:   Feb 2015
#

"""
Test cases for the Controller class.
"""

from __future__ import absolute_import
import nose

from traits.api import HasTraits, Instance, Str
from traitsui.api import Controller


class FooModel(HasTraits):
    my_str = Str('hallo')


class FooController(Controller):
    """ Test dialog that does nothing useful."""

    model = Instance(FooModel)

    def _model_default(self):
        return FooModel(my_str='meh')


def test_construction():
    # check default constructor.
    dialog = FooController()
    nose.tools.assert_is_not_none(dialog.model)
    nose.tools.assert_equal(dialog.model.my_str, 'meh')

    # check initialization when `model` is explcitly passed in.
    new_model = FooModel()
    dialog = FooController(model=new_model)
    nose.tools.assert_is(dialog.model, new_model)
