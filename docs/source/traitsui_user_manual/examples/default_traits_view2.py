# (C) Copyright 2004-2022 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

# default_traits_view2.py -- Sample code to demonstrate the use of
# 'default_traits_view'

from traits.api import HasTraits, Str, Int
from traitsui.api import View, Item, Group


class SimpleEmployee2(HasTraits):
    first_name = Str()
    last_name = Str()
    department = Str()

    employee_number = Str()
    salary = Int()

    def default_traits_view(self):
        return View(
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
