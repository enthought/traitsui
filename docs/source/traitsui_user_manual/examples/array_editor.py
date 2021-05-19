# (C) Copyright 2004-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

# array_editor.py -- Example of using array editors

import numpy as np

from traits.api import Array, HasPrivateTraits
from traitsui.api import ArrayEditor, Item, View
from traitsui.menu import NoButtons


class ArrayEditorTest(HasPrivateTraits):

    three = Array(np.int, (3, 3))

    four = Array(
        np.float, (4, 4), editor=ArrayEditor(width=-50),
    )

    view = View(
        Item('three', label='3x3 Integer'),
        '_',
        Item('three', label='Integer Read-only', style='readonly'),
        '_',
        Item('four', label='4x4 Float'),
        '_',
        Item('four', label='Float Read-only', style='readonly'),
        buttons=NoButtons,
        resizable=True,
    )


if __name__ == '__main__':
    ArrayEditorTest().configure_traits()
