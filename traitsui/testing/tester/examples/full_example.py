import random

from traits.api import (
    Any,
    Button,
    Enum,
    HasStrictTraits,
    Instance,
    Int,
    List,
    Str,
)

from traitsui.api import (
    CheckListEditor,
    EnumEditor,
    Group,
    Item,
    ListEditor,
    RangeEditor,
    TextEditor,
    View,
    UItem,
)
from traitsui.testing.tester import command, locator, query
from traitsui.testing.tester.ui_tester import UITester

class ButtonExample(HasStrictTraits):
    cool_button = Button('Click Me')
    click_counter = Int(0)

    def _cool_button_fired(self):
        self.click_counter += 1

    # Currently there is some erroneous behavior with Qt5 and OSX causing
    # the click_counter to not immediately increment when the button is 
    # clicked. For more deailts, see enthought/traitsui #913.   
    
    view = View(
        'cool_button',
        Item('click_counter', style='readonly'),
        title='ButtonEditor',
        buttons=['OK'],
        resizable=True
    )


class TextboxExample(HasStrictTraits):
    name = Str()
    view = View(
        Item("name", editor=TextEditor(auto_set=False), style='simple')
    )


class RangeExample(HasStrictTraits):
    value = Int(1)
    view = View(
        Item(
            "value",
            editor=RangeEditor(low=1, high=12, mode='slider')
        )
    )


class CheckListExample(HasStrictTraits):
    value = List()
    view = View(
        UItem(
            "value",
            editor=CheckListEditor(
                values=["one", "two", "three", "four"],
            ),
            style="custom",
        ),
    )


class EnumExample(HasStrictTraits):
    name_list = Enum('A-495', 'A-498', 'R-1226', 'TS-17', 'TS-18',
                     'Foo', 12345, (11, 7), None)
    enum_group = Group(
        Item(
            'name_list',
            style='simple',
            label='Simple',
            editor=EnumEditor(
                values=name_list,
                evaluate=True
            ),
            id='name_list_simple',
        ),
        Item('_'),
        Item(
            'name_list',
            style='custom',
            label='Custom radio',
            editor=EnumEditor(
                values=name_list,
                mode='radio',
                cols=3,
            ),
            id='name_list_radio'
        ),
        Item('_'),
        Item(
            'name_list',
            style='custom',
            label='Custom list',
            editor=EnumEditor(values=name_list, mode='list'),
            id='name_list_list',
        ),
    )

    view = View(
        enum_group,
        title='EnumEditor',
        buttons=['OK'],
        resizable=True
    )


class Team(HasStrictTraits):
    location = Str()
    team_name = Str()


class Person(HasStrictTraits):
    name = Str()
    age = Int()
    favorite_teams = List(Instance(Team))
    view = View(
        Item('name'),
        Item('age'),
        Item(
            'favorite_teams',
            style='custom',
            editor=ListEditor(use_notebook=True)
        ),
    )


def get_favorite_teams():
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
    return [
        Person(name='Dave', age=39, favorite_teams=get_favorite_teams()),
        Person(name='Mike', age=28, favorite_teams=get_favorite_teams()),
        Person(name='Joe', age=34, favorite_teams=get_favorite_teams()),
        Person(name='Tom', age=22, favorite_teams=get_favorite_teams()),
    ]


class ListExample(HasStrictTraits):
    people = List(Instance(Person))

    view = View(
        UItem(
            'people',
            label='List',
            id='list',
            style='custom',
            editor=ListEditor(style='custom', columns=2),
        ),
        resizable=True
    )


class Notebook(HasStrictTraits):
    editors = List(Any())
    view = View(
        UItem(
            "editors",
            style="custom",
            editor=ListEditor(use_notebook=True)
        ),
        resizable=True
    )

editors_list = [ButtonExample(), TextboxExample(), RangeExample(),
    CheckListExample(), EnumExample(), ListExample(people=get_people()),
]
notebook = Notebook(editors=editors_list)


if __name__ == '__main__':
    notebook.configure_traits()

    tester = UITester(delay=500)
    with tester.create_ui(notebook) as ui:
        editors = tester.find_by_name(ui, "editors")

        # Button Example
        button_example = editors.locate(locator.Index(0))
        button_example.perform(command.MouseClick())
        button = button_example.find_by_name("cool_button")
        button.delay=100
        for _ in range(5):
            button.perform(command.MouseClick())
        assert notebook.editors[0].click_counter >= 5

        # Textbox Example
        textbox_example = editors.locate(locator.Index(1))
        textbox_example.perform(command.MouseClick())
        textbox = textbox_example.find_by_name("name")
        textbox.delay=100
        textbox.perform(command.KeySequence("Aaton"))
        for _ in range(3):
            textbox.perform(command.KeyClick("Backspace"))
        textbox.perform(command.KeySequence("ron"))
        displayed = textbox.inspect(query.DisplayedText())
        assert displayed == "Aaron"
        assert notebook.editors[1].name == ""
        textbox.perform(command.KeyClick("Enter"))
        assert notebook.editors[1].name == "Aaron"

        # Range Example
        range_example = editors.locate(locator.Index(2))
        range_example.perform(command.MouseClick())
        number_field = range_example.find_by_name("value")
        range_text = number_field.locate(locator.WidgetType.textbox)
        range_text.perform(command.KeyClick("0"))
        range_text.perform(command.KeyClick("Enter"))
        assert notebook.editors[2].value == 10

        # CheckList Example
        checklist_example = editors.locate(locator.Index(3))
        checklist_example.perform(command.MouseClick())
        check_list = checklist_example.find_by_name("value")
        item_1 = check_list.locate(locator.Index(1))
        item_2 = check_list.locate(locator.Index(2))
        item_1.perform(command.MouseClick())
        item_2.perform(command.MouseClick())
        item_1.perform(command.MouseClick())
        assert check_list.target.value == ["three"]

        # Enum Example
        enum_example = editors.locate(locator.Index(4))
        enum_example.perform(command.MouseClick())
        combobox = enum_example.find_by_id("name_list_simple")
        combobox.delay=200
        for _ in range(5):
            combobox.perform(command.KeyClick("Backspace"))
        combobox.perform(command.KeySequence("R-1226"))
        combobox.perform(command.KeyClick("Enter"))
        radio = enum_example.find_by_id("name_list_radio")
        # bug here for qt (this doesn't click but in the enum_example code it clicks just fine)
        # this also works fine on wx right now
        radio.locate(locator.Index(5)).perform(command.MouseClick())
        custom_list = enum_example.find_by_id("name_list_list")
        custom_list.locate(locator.Index(3)).perform(command.MouseClick())

        # List Example
        list_example = editors.locate(locator.Index(5))
        list_example.perform(command.MouseClick()) 
        people_list = list_example.find_by_name("people")
        person_4 = people_list.locate(locator.Index(3))
        fav_teams_list = person_4.find_by_name("favorite_teams")
        fav_team_2 = fav_teams_list.locate(locator.Index(1))
        fav_team_2.perform(command.MouseClick())
        team_location = fav_team_2.find_by_name("location")
        team_location.delay = 100
        for _ in range(11):
            team_location.perform(command.KeyClick("Backspace"))
        team_location.perform(command.KeySequence("Cambridge"))
