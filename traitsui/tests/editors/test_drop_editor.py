# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import unittest

from traits.api import HasTraits, Str
from traitsui.api import DropEditor, Item, View
from traitsui.tests._tools import (
    BaseTestMixin,
    create_ui,
    requires_toolkit,
    reraise_exceptions,
    ToolkitName,
)


class Model(HasTraits):

    value = Str()


# Run this test against wx when enthought/traitsui#752 is fixed.
@requires_toolkit([ToolkitName.qt])
class TestDropEditor(BaseTestMixin, unittest.TestCase):
    """Test DropEditor."""

    def setUp(self):
        BaseTestMixin.setUp(self)

    def tearDown(self):
        BaseTestMixin.tearDown(self)

    def test_init_dispose_editable(self):

        obj = Model()
        view = View(Item("value", editor=DropEditor(readonly=False)))
        with reraise_exceptions():
            with create_ui(obj, dict(view=view)):
                pass
            # Mutating value after UI is closed should be okay.
            obj.value = "New"

    def test_init_dispose_readonly(self):

        obj = Model()
        view = View(Item("value", editor=DropEditor(readonly=True)))
        with reraise_exceptions():
            with create_ui(obj, dict(view=view)):
                pass
            # Mutating value after UI is closed should be okay.
            obj.value = "New"
