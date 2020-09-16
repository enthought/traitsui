"""
Simple example for utilizing UI Tester on a button editor.
Currently, the clicks happen instantaneously, so visually in the example,
the button will not change color as it normally would while being clicked
manually.
In this example, the Tester simply clicks the button 5 times (which can be
observed by the displayed click counter incrementing).
"""

from traits.api import HasTraits, Button, Int

from traitsui.api import Item, View
from traitsui.testing.tester import command
from traitsui.testing.tester.ui_tester import UITester


class ButtonEditorDemo(HasTraits):
    """ Defines the main ButtonEditor demo class. """

    # Define a Button trait:
    my_button = Button('Click Me')
    click_counter = Int(0)

    def _my_button_fired(self):
        """ Button listener to increment click_counter on a click."""
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
        for _ in range(5):
            button.perform(command.MouseClick())
