# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!
import shutil
import tempfile
import unittest

from pyface.toolkit import toolkit_object
from traits.api import (
    Directory,
    HasStrictTraits,
    Instance,
    Int,
    List,
    Str,
    TraitError,
)

from traitsui.api import Item, ListEditor, View
from traitsui.testing.api import (
    DisplayedText,
    Index,
    KeyClick,
    KeySequence,
    LocationNotSupported,
    MouseClick,
    Textbox,
    UITester,
)
from traitsui.tests._tools import (
    requires_toolkit,
    ToolkitName,
)

ModalDialogTester = toolkit_object(
    "util.modal_dialog_tester:ModalDialogTester"
)


# 'Person' class:
class Person(HasStrictTraits):

    # Trait definitions:
    name = Str()
    age = Int()

    # Traits view definition:
    traits_view = View('name', 'age', width=0.18, buttons=['OK', 'Cancel'])


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
        Person(name='Fields', age=31),
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
            resizable=True,
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

    # regression test for enthought/traitsui#1154
    @requires_toolkit([ToolkitName.qt])
    def test_add_item_fails(self):
        class Foo(HasStrictTraits):
            dirs = List(Directory(exists=True))

        obj = Foo()
        tester = UITester(auto_process_events=False)
        with tester.create_ui(obj) as ui:
            dirs_list_editor = tester.find_by_name(ui, "dirs")

            def trigger_error():
                try:
                    dirs_list_editor._target.add_empty()
                except TraitError:
                    return False
                return True

            mdtester = ModalDialogTester(trigger_error)
            mdtester.open_and_run(lambda x: x.close())
            # we want an error dialog to open, but don't want to raise a
            # TraitError and crash the full application
            self.assertTrue(mdtester.dialog_was_opened)
            self.assertTrue(mdtester.result)

            self.assertEqual(len(obj.dirs), 0)

    # this test hits a problem on wx, see issue enthought/traitsui#1653
    @requires_toolkit([ToolkitName.qt])
    def test_default_factory(self):
        temp_dir = tempfile.mkdtemp()

        def test_callable():
            return temp_dir

        class Foo(HasStrictTraits):
            dirs = List(Directory(exists=True))
            view = View(
                Item("dirs", editor=ListEditor(item_factory=test_callable))
            )

        obj = Foo()
        tester = UITester()
        with tester.create_ui(obj) as ui:
            dirs_list_editor = tester.find_by_name(ui, "dirs")
            # should not raise error (see above test_add_item_fails)
            dirs_list_editor._target.add_empty()
            self.assertEqual(len(obj.dirs), 1)

        shutil.rmtree(temp_dir)

    def test_default_factory_with_args(self):
        class Foo(HasStrictTraits):
            bar = Int()
            baz = Str()

        def test_callable(bar, baz=''):
            return Foo(bar=bar, baz=baz)

        class TestFoo(HasStrictTraits):
            foos = List(Foo)
            view = View(
                Item(
                    "foos",
                    editor=ListEditor(
                        item_factory=test_callable,
                        item_factory_args=(7,),
                        item_factory_kwargs={'baz': "python"},
                    ),
                )
            )

        obj = TestFoo()
        tester = UITester()
        with tester.create_ui(obj) as ui:
            foos_list_editor = tester.find_by_name(ui, "foos")
            # should not raise error (see above test_add_item_fails)
            foos_list_editor._target.add_empty()
            self.assertEqual(len(obj.foos), 1)
            self.assertEqual(obj.foos[0].bar, 7)
            self.assertEqual(obj.foos[0].baz, "python")


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
                tester.find_by_name(ui, "people").locate(Index(0)).perform(
                    MouseClick()
                )

    # regression test for enthought/traitsui#1790
    def test_initial_selected(self):
        class PhoneBookWithSelected(Phonebook):
            selected = Instance(Person)

            traits_view = View(
                Item(
                    "people",
                    style="custom",
                    editor=ListEditor(
                        use_notebook=True,
                        selected='selected',
                    ),
                )
            )

        tester = UITester()
        phonebook = PhoneBookWithSelected(people=get_people())
        with tester.create_ui(phonebook) as ui:
            self.assertEqual(
                phonebook.selected, phonebook.people[0]
            )
