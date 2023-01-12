# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

"""
Tiny application: convert length measurements from one unit system to another

Select the input and output units using the drop down combo-boxes in the
*Input:* and *Output:* sections respectively. Type the input quantity
to convert into the left most text box. The output value corresponding to the
current input value will automatically be updated in the *Output:*
section.

Use the *Undo* and *ReDo* buttons to undo and redo changes you
have made to any of the input fields.

Note that other than the 'output_amount' property implementation, the rest
of the code is simply declarative.
"""

# FIXME: Help is broken in QT

from traits.api import HasStrictTraits, Trait, CFloat, Property
from traitsui.api import View, VGroup, HGroup, Item

# Help text:
ViewHelp = """
This program converts length measurements from one unit system to another.

Select the input and output units using the drop down combo-boxes in the
*Input:* and *Output:* sections respectively. Type the input quantity
to convert into the left most text box. The output value corresponding to the
current input value will automatically be updated in the *Output:*
section.

Use the *Undo* and *ReDo* buttons to undo and redo changes you
have made to any of the input fields.
"""

# Units trait maps all units to centimeters:
Units = Trait(
    'inches',
    {
        'inches': 2.54,
        'feet': (12 * 2.54),
        'yards': (36 * 2.54),
        'miles': (5280 * 12 * 2.54),
        'millimeters': 0.1,
        'centimeters': 1.0,
        'meters': 100.0,
        'kilometers': 100000.0,
    },
)

# Converter Class:


class Converter(HasStrictTraits):

    # Trait definitions:
    input_amount = CFloat(12.0, desc="the input quantity")
    input_units = Units('inches', desc="the input quantity's units")
    output_amount = Property(
        observe=['input_amount', 'input_units', 'output_units'],
        desc="the output quantity",
    )
    output_units = Units('feet', desc="the output quantity's units")

    # User interface views:
    traits_view = View(
        VGroup(
            HGroup(
                Item('input_amount', springy=True),
                Item('input_units', show_label=False),
                label='Input',
                show_border=True,
            ),
            HGroup(
                Item('output_amount', style='readonly', springy=True),
                Item('output_units', show_label=False),
                label='Output',
                show_border=True,
            ),
            help=ViewHelp,
        ),
        title='Units Converter',
        buttons=['Undo', 'OK', 'Help'],
    )

    # Property implementations
    def _get_output_amount(self):
        return (self.input_amount * self.input_units_) / self.output_units_


# Create the demo:
popup = Converter()

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    popup.configure_traits()
