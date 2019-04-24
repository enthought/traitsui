"""
Range editor

A Range Trait holds a numeric value which is restricted to a specified range.

This example shows how the RangeEditor's simple and custom styles vary
depending on the type (integer or float) and size (small, medium, or large
integer) of the specified range.

The example also shows how multiple Groups at the top level of a View are
automatically placed into separate tabs.

For an example of how to dynamically vary the bounds of a Range trait, see
the *Dynamic Range Editor* example.
"""

from __future__ import absolute_import
from traits.api import HasTraits, Range
from traitsui.api import Item, Group, View


class RangeEditorDemo(HasTraits):
    """ Defines the RangeEditor demo class.
    """

    # Define a trait for each of four range variants:
    small_int_range = Range(1, 16)
    medium_int_range = Range(1, 25)
    large_int_range = Range(1, 150)
    float_range = Range(0.0, 150.0)

    # RangeEditor display for narrow integer Range traits (< 17 wide):
    int_range_group1 = Group(
        Item('small_int_range', style='simple', label='Simple'),
        Item('_'),
        Item('small_int_range', style='custom', label='Custom'),
        Item('_'),
        Item('small_int_range', style='text', label='Text'),
        Item('_'),
        Item('small_int_range', style='readonly', label='ReadOnly'),
        label='Small Int'
    )

    # RangeEditor display for medium-width integer Range traits (17 to 100):
    int_range_group2 = Group(
        Item('medium_int_range', style='simple', label='Simple'),
        Item('_'),
        Item('medium_int_range', style='custom', label='Custom'),
        Item('_'),
        Item('medium_int_range', style='text', label='Text'),
        Item('_'),
        Item('medium_int_range', style='readonly', label='ReadOnly'),
        label='Medium Int'
    )

    # RangeEditor display for wide integer Range traits (> 100):
    int_range_group3 = Group(
        Item('large_int_range', style='simple', label='Simple'),
        Item('_'),
        Item('large_int_range', style='custom', label='Custom'),
        Item('_'),
        Item('large_int_range', style='text', label='Text'),
        Item('_'),
        Item('large_int_range', style='readonly', label='ReadOnly'),
        label='Large Int'
    )

    # RangeEditor display for float Range traits:
    float_range_group = Group(
        Item('float_range', style='simple', label='Simple'),
        Item('_'),
        Item('float_range', style='custom', label='Custom'),
        Item('_'),
        Item('float_range', style='text', label='Text'),
        Item('_'),
        Item('float_range', style='readonly', label='ReadOnly'),
        label='Float'
    )

    # The view includes one group per data type. These will be displayed
    # on separate tabbed panels:
    traits_view = View(
        int_range_group1,
        int_range_group2,
        int_range_group3,
        float_range_group,
        title='RangeEditor',
        buttons=['OK'],
        resizable=True
    )


# Create the demo:
demo = RangeEditorDemo()

# Run the demo (if invoked from the comand line):
if __name__ == '__main__':
    demo.configure_traits()
