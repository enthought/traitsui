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
from traitsui.api import EnumEditor, Item, View


def evaluate_value(v):
    print('evaluate_value', v)
    return str(v)


class Team(HasTraits):

    captain = Str('Dick')
    players = List(['Tom', 'Dick', 'Harry', 'Sally'], Str)

    captain_editor = EnumEditor(name='players', evaluate=evaluate_value)

    view = View(
        Item('captain', editor=captain_editor), '_', 'players@', height=200
    )


if __name__ == '__main__':
    team = Team()
    team.configure_traits()
    team.print_traits()
