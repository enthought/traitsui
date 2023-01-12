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
Displaying large NumPy arrays with TabularEditor

A demonstration of how the TabularEditor can be used to display (large) NumPy
arrays, in this case 100,000 random 3D points from a unit cube.

In addition to showing the coordinates of each point, it also displays the
index of each point in the array, as well as a red flag if the point lies
within 0.25 of the center of the cube.
"""

from numpy import sqrt
from numpy.random import random

from traits.api import HasTraits, Property, Array
from traitsui.api import View, Item, TabularAdapter, TabularEditor


# -- Tabular Adapter Definition -------------------------------------------
class ArrayAdapter(TabularAdapter):

    columns = [('i', 'index'), ('x', 0), ('y', 1), ('z', 2)]

    font = 'Courier 10'
    alignment = 'right'
    format = '%.4f'

    index_text = Property()
    index_image = Property()

    def _get_index_text(self):
        return str(self.row)

    def _get_index_image(self):
        x, y, z = self.item
        if sqrt((x - 0.5) ** 2 + (y - 0.5) ** 2 + (z - 0.5) ** 2) <= 0.25:
            return '@icons:red_ball'

        return None


# -- ShowArray Class Definition -------------------------------------------


class ShowArray(HasTraits):

    data = Array

    traits_view = View(
        Item(
            'data',
            show_label=False,
            editor=TabularEditor(
                adapter=ArrayAdapter(),
                auto_resize=True,
                # Do not allow any kind of editing of the array:
                editable=False,
                operations=[],
                drag_move=False,
            ),
        ),
        title='Array Viewer',
        width=0.3,
        height=0.8,
        resizable=True,
    )


# Create the demo:
demo = ShowArray(data=random((100000, 3)))

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()
