import unittest

from traits.api import HasStrictTraits, Instance, Int, List, Str
from traitsui.api import Item, ListEditor, View
from traitsui.testing.api import (
    DisplayedText,
    Index,
    KeyClick,
    KeySequence,
    LocationNotSupported,
    MouseClick,
    Textbox,
    UITester
)
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
    style = Str("custom")

    # Traits view definitions:
    def default_traits_view(self):
        view = View(
            Item(
                'people',
                label='List',
                id='list',
                style=self.style,
                editor=ListEditor(style=self.style, columns=self.num_columns),
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
                item = people_list.locate(Index(7))
                name_field = item.find_by_name("name")
                for _ in range(6):
                    name_field.perform(KeyClick("Backspace"))
                name_field.perform(KeySequence("David"))
                displayed = name_field.inspect(DisplayedText())
                self.assertEqual(obj.people[7].name, "David")
                self.assertEqual(displayed, obj.people[7].name)

    def test_useful_err_message(self):
        obj = ListTraitTest(people=get_people())
        tester = UITester()
        with tester.create_ui(obj) as ui:
            with self.assertRaises(LocationNotSupported) as exc:
                people_list = tester.find_by_name(ui, "people")
                people_list.locate(Textbox())
            self.assertIn(Index, exc.exception.supported)

    def test_index_out_of_range(self):
        obj = ListTraitTest(people=get_people())
        tester = UITester()
        with tester.create_ui(obj) as ui:
            people_list = tester.find_by_name(ui, "people")
            with self.assertRaises(IndexError):
                people_list.locate(Index(10))


@requires_toolkit([ToolkitName.qt, ToolkitName.wx])
class TestSimpleListEditor(unittest.TestCase):

    def test_locate_element_and_edit(self):
        obj = ListTraitTest(people=get_people(), style="simple")
        tester = UITester()
        with tester.create_ui(obj) as ui:
            # sanity check
            self.assertEqual(obj.people[7].name, "Fields")
            people_list = tester.find_by_name(ui, "people")
            item = people_list.locate(Index(7))
            item.perform(MouseClick())
            name_field = item.find_by_name("name")
            for _ in range(6):
                name_field.perform(KeyClick("Backspace"))
            name_field.perform(KeySequence("David"))
            displayed = name_field.inspect(DisplayedText())
            self.assertEqual(obj.people[7].name, "David")
            self.assertEqual(displayed, obj.people[7].name)

    def test_useful_err_message(self):
        obj = ListTraitTest(people=get_people(), style="simple")
        tester = UITester()
        with tester.create_ui(obj) as ui:
            with self.assertRaises(LocationNotSupported) as exc:
                people_list = tester.find_by_name(ui, "people")
                people_list.locate(Textbox())
            self.assertIn(Index, exc.exception.supported)

    def test_index_out_of_range(self):
        obj = ListTraitTest(people=get_people(), style="simple")
        tester = UITester()
        with tester.create_ui(obj) as ui:
            people_list = tester.find_by_name(ui, "people")
            with self.assertRaises(IndexError):
                people_list.locate(Index(10))


@requires_toolkit([ToolkitName.qt, ToolkitName.wx])
class TestNotebookListEditor(unittest.TestCase):

    def test_modify_person_name(self):
        phonebook = Phonebook(
            people=get_people(),
        )
        tester = UITester()
        with tester.create_ui(phonebook, dict(view=notebook_view)) as ui:
            list_ = tester.find_by_name(ui, "people")
            list_.locate(Index(1)).perform(MouseClick())
            name_field = list_.locate(Index(1)).find_by_name("name")
            for _ in range(4):
                name_field.perform(KeyClick("Backspace"))
            name_field.perform(KeySequence("Pete"))

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
            list_.locate(Index(1)).perform(MouseClick())
            name_field = list_.locate(Index(1)).find_by_name("name")
            actual = name_field.inspect(DisplayedText())
            self.assertEqual(actual, "Mary")

    def test_index_out_of_bound(self):
        phonebook = Phonebook(
            people=[],
        )
        tester = UITester()
        with tester.create_ui(phonebook, dict(view=notebook_view)) as ui:
            with self.assertRaises(IndexError):
                tester.find_by_name(ui, "people").\
                    locate(Index(0)).\
                    perform(MouseClick())
