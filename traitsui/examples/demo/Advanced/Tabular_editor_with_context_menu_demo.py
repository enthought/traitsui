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
**WARNING**

  This demo might not work as expected and some documented features might be
  missing.

-------------------------------------------------------------------------------

Defining column-specific context menu in a Tabular Editor. Shows how the
example for the Table Editor (`Table_Editor_with_context_menu_demo.py`) can be
adapted to work with a Tabular Editor.

The demo is a simple baseball scoring system, which lists each player and
their current batting statistics. After a given player has an at bat, you
right-click on the table cell corresponding to the player and the result of
the at-bat (e.g. 'S' = single) and select the 'Add' menu option to register
that the player hit a single and update the player's overall statistics.

This demo also illustrates the use of Property traits, and how using 'event'
meta-data can simplify event handling by collapsing an event that can
occur on a number of traits into a category of event, which can be handled by
a single event handler defined for the category (in this case, the category
is 'affects_average').
"""
# Issue related to the demo warning: enthought/traitsui#960


from random import randint
from traits.api import HasStrictTraits, Str, Int, Float, List, Property
from traitsui.api import (
    Action,
    Item,
    Menu,
    TabularAdapter,
    TabularEditor,
    View,
)


# Define a custom tabular adapter for handling items which affect the player's
# batting average:
class PlayerAdapter(TabularAdapter):

    # Overwrite default values
    alignment = 'center'
    width = 0.09

    def get_menu(self, object, trait, row, column):
        column_name = self.column_map[column]
        if column_name not in ['name', 'average']:
            menu = Menu(
                Action(name='Add', action='editor.adapter.add(item, column)'),
                Action(name='Sub', action='editor.adapter.sub(item, column)'),
            )
            return menu
        else:
            return super().get_menu(object, trait, row, column)

    def get_format(self, object, trait, row, column):
        column_name = self.column_map[column]
        if column_name == 'average':
            return '%0.3f'
        else:
            return super().get_format(object, trait, row, column)

    def add(self, object, column):
        """Increment the affected player statistic."""
        column_name = self.column_map[column]
        setattr(object, column_name, getattr(object, column_name) + 1)

    def sub(self, object, column):
        """Decrement the affected player statistic."""
        column_name = self.column_map[column]
        setattr(object, column_name, getattr(object, column_name) - 1)


# The 'players' trait table editor:
columns = [
    ('Player Name', 'name'),
    ('AB', 'at_bats'),
    ('SO', 'strike_outs'),
    ('S', 'singles'),
    ('D', 'doubles'),
    ('T', 'triples'),
    ('HR', 'home_runs'),
    ('W', 'walks'),
    ('Ave', 'average'),
]

player_editor = TabularEditor(
    editable=True,
    auto_resize=True,
    auto_resize_rows=True,
    stretch_last_section=False,
    auto_update=True,
    adapter=PlayerAdapter(columns=columns),
)


# 'Player' class:
class Player(HasStrictTraits):

    # Trait definitions:
    name = Str()
    at_bats = Int()
    strike_outs = Int(event='affects_average')
    singles = Int(event='affects_average')
    doubles = Int(event='affects_average')
    triples = Int(event='affects_average')
    home_runs = Int(event='affects_average')
    walks = Int()
    average = Property(Float)

    def _get_average(self):
        """Computes the player's batting average from the current statistics."""
        if self.at_bats == 0:
            return 0.0

        return (
            float(self.singles + self.doubles + self.triples + self.home_runs)
            / self.at_bats
        )

    def _affects_average_changed(self):
        """Handles an event that affects the player's batting average."""
        self.at_bats += 1


class Team(HasStrictTraits):

    # Trait definitions:
    players = List(Player)

    # Trait view definitions:
    traits_view = View(
        Item('players', show_label=False, editor=player_editor),
        title='Baseball Scoring Demo',
        width=0.5,
        height=0.5,
        resizable=True,
    )


def random_player(name):
    """Generates and returns a random player."""
    p = Player(
        name=name,
        strike_outs=randint(0, 50),
        singles=randint(0, 50),
        doubles=randint(0, 20),
        triples=randint(0, 5),
        home_runs=randint(0, 30),
        walks=randint(0, 50),
    )
    return p.trait_set(
        at_bats=(
            p.strike_outs
            + p.singles
            + p.doubles
            + p.triples
            + p.home_runs
            + randint(100, 200)
        )
    )


# Create the demo:
demo = Team(
    players=[
        random_player(name)
        for name in [
            'Dave',
            'Mike',
            'Joe',
            'Tom',
            'Dick',
            'Harry',
            'Dirk',
            'Fields',
            'Stretch',
        ]
    ]
)

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()
