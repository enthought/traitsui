# (C) Copyright 2004-2022 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

# handler_override.py -- Example of a Handler that overrides setattr(), and
# that has a user interface notification method

from traits.api import Bool, HasTraits
from traitsui.api import Handler, View


class TC_Handler(Handler):
    def setattr(self, info, object, name, value):
        Handler.setattr(self, info, object, name, value)
        info.object._updated = True

    def object__updated_changed(self, info):
        if info.initialized:
            info.ui.title += "*"


class TestClass(HasTraits):
    b1 = Bool()
    b2 = Bool()
    b3 = Bool()
    _updated = Bool(False)


view1 = View(
    'b1',
    'b2',
    'b3',
    title="Alter Title",
    handler=TC_Handler(),
    buttons=['OK', 'Cancel'],
)

tc = TestClass()
tc.configure_traits(view=view1)
