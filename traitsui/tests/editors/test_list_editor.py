import unittest

from traits.api import HasStrictTraits, Instance, Int, List, Str
from traitsui.api import Item, ListEditor, View
from traitsui.testing.tester import command, locator, query
from traitsui.testing.tester.exceptions import LocationNotSupported
from traitsui.testing.tester.ui_tester import UITester
from traitsui.tests._tools import (
    requires_toolkit,
    ToolkitName,
)


# 'Person' class:
class Person(HasStrictTraits):

    # Trait definitions:
    name = Str()
    age = Int()

    # Traits view definition:
    traits_view = View(
        'name', 'age',
        width=0.18,
        buttons=['OK', 'Cancel']
    )


def get_people():
    # Sample data:
    return [
        Person(name='Dave', age=39),
        Person(name='Mike', age=28),
        Person(name='Joe', age=34),
        Person(name='Tom', age=22),
        Person(name='Dick', age=63),
        Person(name='Harry', age=46),
        Person(name='Sally', age=43),
        Person(name='Fields', age=31)
    ]


# 'ListTraitTest' class:
class ListTraitTest(HasStrictTraits):

    # Trait definitions:
    people = List(Instance(Person, ()))
    num_columns = Int(1)

    # Traits view definitions:
    def default_traits_view(self):
        view = View(
            Item(
                'people',
                label='List',
                id='list',
                style='custom',
                editor=ListEditor(style='custom', columns=self.num_columns),
            ),
            resizable=True
        )
        return view


class Phonebook(HasStrictTraits):
    people = List(Instance(Person))


notebook_view = View(
    Item(
        "people",
        style="custom",
        editor=ListEditor(use_notebook=True),
    )
)


@requires_toolkit([ToolkitName.qt, ToolkitName.wx])
class TestCustomListEditor(unittest.TestCase):

    def test_locate_element_and_edit(self):
        # varying the number of columns in the view tests the logic for
        # getting the correct nested ui
        for col in range(1, 5):
            obj = ListTraitTest(people=get_people(), num_columns=col)
            tester = UITester()
            with tester.create_ui(obj) as ui:
                # sanity check
                self.assertEqual(obj.people[7].name, "Fields")
                people_list = tester.find_by_name(ui, "people")
                item = people_list.locate(locator.Index(7))
                name_field = item.find_by_name("name")
                for _ in range(6):
                    name_field.perform(command.KeyClick("Backspace"))
                name_field.perform(command.KeySequence("David"))
                displayed = name_field.inspect(query.DisplayedText())
                self.assertEqual(obj.people[7].name, "David")
                self.assertEqual(displayed, obj.people[7].name)

    def test_useful_err_message(self):
        obj = ListTraitTest(people=get_people())
        tester = UITester()
        with tester.create_ui(obj) as ui:
            with self.assertRaises(LocationNotSupported) as exc:
                people_list = tester.find_by_name(ui, "people")
                people_list.locate(locator.WidgetType.textbox)
            self.assertIn(locator.Index, exc.exception.supported)

    def test_index_out_of_range(self):
        obj = ListTraitTest(people=get_people())
        tester = UITester()
        with tester.create_ui(obj) as ui:
            people_list = tester.find_by_name(ui, "people")
            item = people_list.locate(locator.Index(10))
            with self.assertRaises(IndexError):
                item.find_by_name("name")


@requires_toolkit([ToolkitName.qt, ToolkitName.wx])
class TestNotebookListEditor(unittest.TestCase):

    def test_modify_person_name(self):
        phonebook = Phonebook(
            people=get_people(),
        )
        tester = UITester()
        with tester.create_ui(phonebook, dict(view=notebook_view)) as ui:
            list_ = tester.find_by_name(ui, "people")
            list_.locate(locator.Index(1)).perform(command.MouseClick())
            name_field = list_.locate(locator.Index(1)).find_by_name("name")
            for _ in range(4):
                name_field.perform(command.KeyClick("Backspace"))
            name_field.perform(command.KeySequence("Pete"))

            self.assertEqual(phonebook.people[1].name, "Pete")

    def test_get_person_name(self):
        person1 = Person()
        person2 = Person(name="Mary")
        phonebook = Phonebook(
            people=[person1, person2],
        )
        tester = UITester()
        with tester.create_ui(phonebook, dict(view=notebook_view)) as ui:
            list_ = tester.find_by_name(ui, "people")
            list_.locate(locator.Index(1)).perform(command.MouseClick())
            name_field = list_.locate(locator.Index(1)).find_by_name("name")
            actual = name_field.inspect(query.DisplayedText())
            self.assertEqual(actual, "Mary")

    def test_index_out_of_bound(self):
        phonebook = Phonebook(
            people=[],
        )
        tester = UITester(delay=500)
        with tester.create_ui(phonebook, dict(view=notebook_view)) as ui:
            with self.assertRaises(IndexError):
                tester.find_by_name(ui, "people").\
                    locate(locator.Index(0)).\
                    perform(command.MouseClick())
