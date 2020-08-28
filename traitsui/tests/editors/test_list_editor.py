import unittest

from traits.api import HasStrictTraits, Instance, Int, List, Str
from traitsui.api import Item, ListEditor, Item, View
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


# Sample data:
people = [
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

    # Traits view definitions:
    traits_view = View(
        Item(
            'people',
            label='List',
            id='list',
            style='custom',
            editor=ListEditor(style='custom', columns=3),
        ),
        resizable=True
    )

@requires_toolkit([ToolkitName.qt, ToolkitName.wx])
class TestCustomListEditor(unittest.TestCase):

    @requires_toolkit([ToolkitName.qt])
    def test_locate_element_and_edit_qt(self):
        obj = ListTraitTest(people=people)
        tester = UITester()
        with tester.create_ui(obj) as ui:
            # sanity check
            self.assertEqual(obj.people[7].name, "Fields")
            item = tester.find_by_name(ui, "people").locate(locator.Index(7))
            item.find_by_name("name").perform(command.KeySequence("\b\b\b\b\b\bDavid"))
            displayed = item.find_by_name("name").inspect(query.DisplayedText())
            self.assertEqual(obj.people[7].name, "David")
            self.assertEqual(displayed, obj.people[7].name)

    # The above test should in theory work for wx, but the tester currently 
    # has a bug for typing "\b" with wx (it types a literal "\x08" to the
    # textbox)
    @requires_toolkit([ToolkitName.wx])
    def test_locate_element_and_edit_wx(self):
        obj = ListTraitTest(people=people)
        tester = UITester()
        with tester.create_ui(obj) as ui:
            # sanity check
            self.assertEqual(obj.people[7].name, "Fields")
            item = tester.find_by_name(ui, "people").locate(locator.Index(7))
            for _ in range(6):
                item.find_by_name("name").perform(command.KeyClick("Backspace"))
            item.find_by_name("name").perform(command.KeySequence("David"))
            displayed = item.find_by_name("name").inspect(query.DisplayedText())
            self.assertEqual(obj.people[7].name, "David")
            self.assertEqual(displayed, obj.people[7].name)

    def test_useful_err_message(self):
        obj = ListTraitTest(people=people)
        tester = UITester()
        with tester.create_ui(obj) as ui:
            with self.assertRaises(LocationNotSupported) as exc:
                tester.find_by_name(ui, "people").locate(locator.WidgetType.textbox)
            self.assertIn(locator.Index, exc.exception.supported)