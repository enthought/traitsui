import unittest

from traits.api import HasTraits, Instance, List, Str
from traitsui.api import ListEditor, Item, View
from traitsui.testing.api import command, locator, query, UITester


class Person(HasTraits):

    name = Str()


class Phonebook(HasTraits):
    people = List(Instance(Person))


notebook_view = View(
    Item(
        "people",
        style="custom",
        editor=ListEditor(use_notebook=True),
    )
)


class TestNoteListEditor(unittest.TestCase):

    def test_modify_person_name(self):
        person1 = Person()
        person2 = Person()
        phonebook = Phonebook(
            people=[person1, person2],
        )
        tester = UITester()
        with tester.create_ui(phonebook, dict(view=notebook_view)) as ui:
            list_ = tester.find_by_name(ui, "people")
            list_.locate(locator.Index(1)).perform(command.MouseClick())

            name_field = list_.locate(locator.Index(1)).find_by_name("name")
            name_field.perform(command.KeySequence("Pete"))

            self.assertEqual(person2.name, "Pete")

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
        tester = UITester()
        with tester.create_ui(phonebook, dict(view=notebook_view)) as ui:
            with self.assertRaises(IndexError):
                tester.find_by_name(ui, "people").\
                    locate(locator.Index(0)).\
                    perform(command.MouseClick())
