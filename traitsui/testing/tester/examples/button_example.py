"""
Button editor

A Button trait is displayed as a button in a Traits UI view. When the button is
clicked, Traits UI will execute a method of your choice (a 'listener').

In this example, the listener just increments a click counter.
"""

from traits.api import HasTraits, Button, Int, Str

from traitsui.api import Item, View
from traitsui.testing.tester import command
from traitsui.testing.tester.ui_tester import UITester



class ButtonEditorDemo(HasTraits):
    """ Defines the main ButtonEditor demo class. """

    # Define a Button trait:
    my_button = Button('Click Me')
    click_counter = Int(0)

    def _my_button_fired(self):
        self.click_counter += 1

    # Currently there is some erroneous behavior with Qt5 and OSX causing
    # the click_counter to not immediately increment when the button is 
    # clicked. For more deailts, see enthought/traitsui #913.   

    view = View(
        'my_button',
        Item('click_counter', style='readonly'),
        title='ButtonEditor',
        buttons=['OK'],
        resizable=True
    )


# Create the demo:
demo = ButtonEditorDemo()


if __name__ == '__main__':
    tester = UITester(delay=500)
    with tester.create_ui(demo) as ui:
        button = tester.find_by_name(ui, "my_button")
        for _ in range(10):
            button.perform(command.MouseClick())
