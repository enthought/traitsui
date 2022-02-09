# (C) Copyright 2004-2022 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

# configure_traits_view_buttons.py -- Sample code to demonstrate
# configure_traits()

from traits.api import HasTraits, Str, Int
from traitsui.api import CancelButton, Item, OKButton, View


class SimpleEmployee(HasTraits):
    first_name = Str()
    last_name = Str()
    department = Str()

    employee_number = Str()
    salary = Int()


view1 = View(
    Item(name='first_name'),
    Item(name='last_name'),
    Item(name='department'),
    buttons=[OKButton, CancelButton],
)

sam = SimpleEmployee()
sam.configure_traits(view=view1)
