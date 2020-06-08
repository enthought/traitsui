# -----------------------------------------------------------------------------
#
#  Copyright (c) 2020, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
# -----------------------------------------------------------------------------

import unittest

from traits.api import HasTraits, Bool
from traitsui.api import BooleanEditor, Item, View
from traitsui.tests._tools import (
    create_ui,
    skip_if_not_qt4,
    store_exceptions_on_all_threads,
)


class BoolModel(HasTraits):

    true_or_false = Bool()


# Run this against wx once enthought/traitsui#752 is also fixed for
# BooleanEditor
@skip_if_not_qt4
class TestBooleanEditor(unittest.TestCase):

    def test_init_dispose(self):
        # Test init and dispose of the editor.
        view = View(Item("true_or_false", editor=BooleanEditor()))
        obj = BoolModel()
        with store_exceptions_on_all_threads(), \
                create_ui(obj, dict(view=view)):
            pass
