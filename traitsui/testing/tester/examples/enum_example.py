import time 

from traits.api import Enum, HasStrictTraits, Int, List
from traitsui.api import EnumEditor, UItem, View, Group, Item
from traitsui.testing.tester import command, locator, query
from traitsui.testing.tester.ui_tester import UITester


class EnumEditorDemo(HasStrictTraits):
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
        Item('name_list', style='custom', label='Custom radio', id='name_list_radio'),
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
    #demo.configure_traits()
    tester = UITester(delay=500)
    with tester.create_ui(demo) as ui:
        combobox = tester.find_by_id(ui, "name_list_simple")
        for _ in range(5):
            combobox.perform(command.KeyClick("Backspace"))
        combobox.perform(command.KeySequence("R-1226"))
        combobox.perform(command.KeyClick("Enter"))
        radio = tester.find_by_id(ui, "name_list_radio")
        print(radio)
        print(radio.target)
        print(radio.locate(locator.Index(5)))
        print(radio.locate(locator.Index(5)).target)
        print(radio.locate(locator.Index(5)).target.source)
        print(radio.locate(locator.Index(5)).target.source.control)
        radio.locate(locator.Index(5)).perform(command.MouseClick())
        custom_list = tester.find_by_id(ui, "name_list_list")
        custom_list.locate(locator.Index(3)).perform(command.MouseClick())
        time.sleep(2)