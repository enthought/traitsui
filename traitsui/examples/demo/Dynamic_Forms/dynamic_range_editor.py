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
Dynamic Range editor

Demonstrates how to dynamically modify the low and high limits of a Range Trait.

In the simple *Range Editor* example, we saw how to define a Range Trait, whose
values were restricted to a fixed range. Here, we show how the limits of the
range can be changed dynamically using the editor's *low_name* and *high_name*
attributes.

In this example, these range limits are set with sliders. In practice, the
limits would often be calculated from other user input or model data.

The demo is divided into three tabs:

* A dynamic range using a simple slider.
* A dynamic range using a large-range slider.
* A dynamic range using a spinner.

In each section of the demo, the top-most 'value' trait can have its range
end points changed dynamically by modifying the 'low' and 'high' sliders
below it.

The large-range slider includes low-end and high-end arrows, which are used
to step the visible range through the full range, when the latter is too large
to be entirely visible.

This demo also illustrates how the value, label formatting and label
widths can also be specified if desired.
"""

# Imports:
from traits.api import HasPrivateTraits, Float, Range, Int

from traitsui.api import View, Group, Item, Label, RangeEditor


class DynamicRangeEditor(HasPrivateTraits):
    """Defines an editor for dynamic ranges (i.e. ranges whose bounds can be
    changed at run time).
    """

    # The value with the dynamic range:
    value = Float()

    # This determines the low end of the range:
    low = Range(0.0, 10.0, 0.0)

    # This determines the high end of the range:
    high = Range(20.0, 100.0, 20.0)

    # An integer value:
    int_value = Int()

    # This determines the low end of the integer range:
    int_low = Range(0, 10, 0)

    # This determines the high end of the range:
    int_high = Range(20, 100, 20)

    # Traits view definitions:
    traits_view = View(
        # Dynamic simple slider demo:
        Group(
            Item(
                'value',
                editor=RangeEditor(
                    low_name='low',
                    high_name='high',
                    format_str='%.1f',
                    label_width=28,
                    mode='auto',
                ),
            ),
            '_',
            Item('low'),
            Item('high'),
            '_',
            Label(
                'Move the Low and High sliders to change the range of '
                'Value.'
            ),
            label='Simple Slider',
        ),
        # Dynamic large range slider demo:
        Group(
            Item(
                'value',
                editor=RangeEditor(
                    low_name='low',
                    high_name='high',
                    format_str='%.1f',
                    label_width=28,
                    mode='xslider',
                ),
            ),
            '_',
            Item('low'),
            Item('high'),
            '_',
            Label(
                'Move the Low and High sliders to change the range of '
                'Value.'
            ),
            label='Large Range Slider',
        ),
        # Dynamic spinner demo:
        Group(
            Item(
                'int_value',
                editor=RangeEditor(
                    low=0,
                    high=20,
                    low_name='int_low',
                    high_name='int_high',
                    format_str='%d',
                    is_float=False,
                    label_width=28,
                    mode='spinner',
                ),
            ),
            '_',
            Item('int_low'),
            Item('int_high'),
            '_',
            Label(
                'Move the Low and High sliders to change the range of '
                'Value.'
            ),
            label='Spinner',
        ),
        title='Dynamic Range Editor Demonstration',
        buttons=['OK'],
        resizable=True,
    )


# Create the demo:
demo = DynamicRangeEditor()

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()
