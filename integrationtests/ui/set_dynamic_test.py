# (C) Copyright 2004-2022 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

from traits.api import HasTraits, List, Str
from traitsui.api import Item, SetEditor, View


class Team(HasTraits):

    batting_order = List(Str)
    roster = List(['Tom', 'Dick', 'Harry', 'Sally'], Str)

    view = View(
        Item('batting_order', editor=SetEditor(name='roster', ordered=True)),
        '_',
        'roster@',
        height=500,
        resizable=True,
    )


if __name__ == '__main__':
    Team().configure_traits()
