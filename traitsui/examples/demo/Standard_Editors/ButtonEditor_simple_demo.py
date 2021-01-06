# (C) Copyright 2004-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

"""
Button editor

A Button trait is displayed as a button in a Traits UI view. When the button is
clicked, Traits UI will execute a method of your choice (a 'listener').

In this example, the listener just increments a click counter.
"""

from traits.api import HasTraits, Button, Int

from traitsui.api import Item, View


class ButtonEditorDemo(HasTraits):
    """ Defines the main ButtonEditor demo class. """

    # Define a Button trait:
    my_button_trait = Button('Click Me')
    click_counter = Int(0)

    # When the button is clicked, do something.
    # The listener method is named '_TraitName_fired', where
    # 'TraitName' is the name of the button trait.
    def _my_button_trait_fired(self):
        self.click_counter += 1

    # Demo view:
    traits_view = View(
        'my_button_trait',
        Item('click_counter', style='readonly'),
        title='ButtonEditor',
        buttons=['OK'],
        resizable=True
    )


# Create the demo:
demo = ButtonEditorDemo()

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()
