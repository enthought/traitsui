""" Example for utilizing UI Tester on a Custom and Notebook List editor.

In this example, the Tester locates a specific person via navigating to a
specific tab of the Notebook editor.  From there it locates the list of that
persons favorite teams, locates a specific team, and modifies that teams
location.
"""
import random

from traits.api import HasStrictTraits, Instance, Int, List, Str
from traitsui.api import Item, ListEditor, View
from traitsui.testing.tester import command, locator
from traitsui.testing.tester.ui_tester import UITester


class Team(HasStrictTraits):
    """ Team class """

    location = Str()
    team_name = Str()


class Person(HasStrictTraits):
    """ Person class """

    name = Str()
    age = Int()
    favorite_teams = List(Instance(Team))

    traits_view = View(
        Item('name'),
        Item('age'),
        Item(
            'favorite_teams',
            style='custom',
            editor=ListEditor(use_notebook=True)
        ),
    )


def get_favorite_teams():
    """ Gets a list of three random Teams. """

    locations = ['New York', 'Los Angeles', 'Boston', 'Austin', 'Tucson']
    team_names = ['Toros', 'Beavers', 'Falcons', 'Eagles', 'Wildcats']
    selected_locations = random.sample(locations, 3)
    selected_teams = random.sample(team_names, 3)
    return [
        Team(location=selected_locations[0], team_name=selected_teams[0]),
        Team(location=selected_locations[1], team_name=selected_teams[1]),
        Team(location=selected_locations[2], team_name=selected_teams[2])
    ]


def get_people():
    """ Gets a list of sample people. """

    return [
        Person(name='Dave', age=39, favorite_teams=get_favorite_teams()),
        Person(name='Mike', age=28, favorite_teams=get_favorite_teams()),
        Person(name='Joe', age=34, favorite_teams=get_favorite_teams()),
        Person(name='Tom', age=22, favorite_teams=get_favorite_teams()),
        Person(name='Dick', age=63, favorite_teams=get_favorite_teams()),
        Person(name='Harry', age=46, favorite_teams=get_favorite_teams()),
        Person(name='Sally', age=43, favorite_teams=get_favorite_teams()),
        Person(name='Fields', age=31, favorite_teams=get_favorite_teams())
    ]


class Party(HasStrictTraits):
    """ Party class to define a list of People. """

    people = List(Instance(Person))

    traits_view = View(
        Item(
            "people",
            style="custom",
            editor=ListEditor(use_notebook=True),
        )
    )


example = Party(people=get_people())

if __name__ == '__main__':
    tester = UITester(delay=1000)
    with tester.create_ui(example) as ui:
        people_list = tester.find_by_name(ui, "people")
        person_4 = people_list.locate(locator.Index(3))
        person_4.perform(command.MouseClick())

        fav_teams_list = person_4.find_by_name("favorite_teams")
        fav_team_2 = fav_teams_list.locate(locator.Index(1))
        fav_team_2.perform(command.MouseClick())

        team_location = fav_team_2.find_by_name("location")
        team_location.delay = 100
        for _ in range(11):
            team_location.perform(command.KeyClick("Backspace"))
        team_location.perform(command.KeySequence("Cambridge"))
