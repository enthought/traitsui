#  Copyright (c) 2005-2020, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!

import unittest

from traits.api import HasTraits, Str
from traitsui.api import DropEditor, Item, View
from traitsui.tests._tools import (
    create_ui,
    skip_if_not_qt4,
    store_exceptions_on_all_threads,
)


class Model(HasTraits):

    value = Str()


# Run this test against wx when enthought/traitsui#752 is fixed.
@skip_if_not_qt4
class TestDropEditor(unittest.TestCase):
    """ Test DropEditor. """

    def test_init_dispose_editable(self):

        obj = Model()
        view = View(Item("value", editor=DropEditor(readonly=False)))
        with store_exceptions_on_all_threads():
            with create_ui(obj, dict(view=view)):
                pass
            # Mutating value after UI is closed should be okay.
            obj.value = "New"

    def test_init_dispose_readonly(self):

        obj = Model()
        view = View(Item("value", editor=DropEditor(readonly=True)))
        with store_exceptions_on_all_threads():
            with create_ui(obj, dict(view=view)):
                pass
            # Mutating value after UI is closed should be okay.
            obj.value = "New"
