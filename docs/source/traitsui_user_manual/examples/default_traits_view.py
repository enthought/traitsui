# (C) Copyright 2004-2022 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

# default_traits_view.py -- Sample code to demonstrate the use of 'traits_view'

from traits.api import HasTraits, Int, Str
from traitsui.api import Group, Item, View


class SimpleEmployee2(HasTraits):
    first_name = Str()
    last_name = Str()
    department = Str()

    employee_number = Str()
    salary = Int()

    traits_view = View(
        Group(
            Item(name='first_name'),
            Item(name='last_name'),
            Item(name='department'),
            label='Personnel profile',
            show_border=True,
        ),
    )


sam = SimpleEmployee2()
sam.configure_traits()
