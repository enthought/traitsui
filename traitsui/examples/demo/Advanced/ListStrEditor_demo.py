# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

"""
Edit a List of Strings

Simple demonstration of the ListStrEditor, which can be used for editing and
displaying lists of strings, or other data that can be logically mapped to a
list of strings.
"""

from traits.api import HasTraits, List, Str
from traitsui.api import View, Item, ListStrEditor

# -- ShoppingListDemo Class -----------------------------------------------


class ShoppingListDemo(HasTraits):

    # The list of things to buy at the store:
    shopping_list = List(Str)

    # -- Traits View Definitions ----------------------------------------------

    view = View(
        Item(
            'shopping_list',
            show_label=False,
            editor=ListStrEditor(title='Shopping List', auto_add=True),
        ),
        title='Shopping List',
        width=0.2,
        height=0.5,
        resizable=True,
    )


# -- Set up the Demo ------------------------------------------------------

demo = ShoppingListDemo(
    shopping_list=[
        'Carrots',
        'Potatoes (5 lb. bag)',
        'Cocoa Puffs',
        'Ice Cream (French Vanilla)',
        'Peanut Butter',
        'Whole wheat bread',
        'Ground beef (2 lbs.)',
        'Paper towels',
        'Soup (3 cans)',
        'Laundry detergent',
    ]
)

# Run the demo (in invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()
