""" Example for utilizing UI Tester on various styles of enum editor.

In this example, the Tester locates the combobox for the simple style of the
editor, and modifies the trait via text. It also clicks on an option in both
the radio and list styles.
"""
import time

from traits.api import Enum, HasStrictTraits
from traitsui.api import EnumEditor, View, Group, Item
from traitsui.testing.tester import command, locator
from traitsui.testing.tester.ui_tester import UITester


class EnumEditorDemo(HasStrictTraits):
    """ Defines the main EnumEditor demo class for showcasing UI Tester. """

    # define an Enum trait
    name_list = Enum('A-495', 'A-498', 'R-1226', 'TS-17', 'TS-18',
                     'Foo', 12345, (11, 7), None)

    # create a group to show each style of the editor
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

    # Demo view:
    traits_view = View(
        enum_group,
        title='EnumEditor',
        buttons=['OK'],
        resizable=True
    )


# Create the demo:
demo = EnumEditorDemo()


if __name__ == '__main__':
    tester = UITester(delay=750)
    with tester.create_ui(demo) as ui:
        combobox = tester.find_by_id(ui, "name_list_simple")
        # change the delay of the combobox specifically so typing is faster
        combobox.delay = 200
        for _ in range(5):
            combobox.perform(command.KeyClick("Backspace"))
        combobox.perform(command.KeySequence("R-1226"))
        combobox.perform(command.KeyClick("Enter"))
        radio = tester.find_by_id(ui, "name_list_radio")
        radio.locate(locator.Index(5)).perform(command.MouseClick())
        custom_list = tester.find_by_id(ui, "name_list_list")
        custom_list.locate(locator.Index(3)).perform(command.MouseClick())
        # added so last click can be seen (in real tests this would be removed)
        time.sleep(1)
