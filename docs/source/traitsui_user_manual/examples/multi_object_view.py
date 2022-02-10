# (C) Copyright 2004-2022 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

# multi_object_view.py -- Sample code to show multi-object view with context

from traits.api import Bool, HasTraits, Int, Str
from traitsui.api import Group, Item, View


class House(HasTraits):
    address = Str()
    bedrooms = Int()
    pool = Bool()
    price = Int()


# View object designed to display two objects of class 'House'
comp_view = View(
    Group(
        Group(
            Item('h1.address', resizable=True),
            Item('h1.bedrooms'),
            Item('h1.pool'),
            Item('h1.price'),
            show_border=True,
        ),
        Group(
            Item('h2.address', resizable=True),
            Item('h2.bedrooms'),
            Item('h2.pool'),
            Item('h2.price'),
            show_border=True,
        ),
        orientation='horizontal',
    ),
    title='House Comparison',
)

# A pair of houses to demonstrate the View
house1 = House(
    address='4743 Dudley Lane',
    bedrooms=3,
    pool=False,
    price=150000,
)
house2 = House(
    address='11604 Autumn Ridge',
    bedrooms=3,
    pool=True,
    price=200000,
)

# ...And the actual display command
house1.configure_traits(view=comp_view, context={'h1': house1, 'h2': house2})
