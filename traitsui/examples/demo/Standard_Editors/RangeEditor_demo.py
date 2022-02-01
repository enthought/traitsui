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
Range editor

A Range Trait holds a numeric value which is restricted to a specified range.

This example shows how the RangeEditor's simple and custom styles vary
depending on the type (integer or float) and size (small, medium, or large
integer) of the specified range.

The example also shows how multiple Groups at the top level of a View are
automatically placed into separate tabs.

For an example of how to dynamically vary the bounds of a Range trait, see
the *Dynamic Range Editor* example.

Please refer to the `RangeEditor API docs`_ for further information.

.. _RangeEditor API docs: https://docs.enthought.com/traitsui/api/traitsui.editors.range_editor.html#traitsui.editors.range_editor.RangeEditor
"""

from traits.api import HasTraits, Range as _Range
from traitsui.api import Item, Group, View


# TODO: Update traits.api.Range with the following in order to avoid the popup-error-dialog.
# TODO: Remove redefinition of Range here once the traits.api.Range is updated.
class Range(_Range):
    def create_editor(self):
        """ Returns the default UI editor for the trait.
        """
        # fixme: Needs to support a dynamic range editor.

        auto_set = self.auto_set
        if auto_set is None:
            auto_set = True
        show_error_dialog = self.show_error_dialog
        if show_error_dialog is None:
            show_error_dialog = True

        from traitsui.api import RangeEditor
        return RangeEditor(
            self,
            mode=self.mode or "auto",
            cols=self.cols or 3,
            auto_set=auto_set,
            enter_set=self.enter_set or False,
            low_label=self.low or "",
            high_label=self.high or "",
            low_name=self._low_name,
            high_name=self._high_name,
            show_error_dialog=show_error_dialog
        )


class RangeEditorDemo(HasTraits):
    """Defines the RangeEditor demo class."""

    # Define a trait for each of four range variants:
    small_int_range = Range(1, 16, show_error_dialog=False)
    medium_int_range = Range(1, 25, show_error_dialog=False)
    large_int_range = Range(1, 150, show_error_dialog=False)
    float_range = Range(0.0, 150.0, show_error_dialog=False)

    # RangeEditor display for narrow integer Range traits (< 17 wide):
    int_range_group1 = Group(
        Item(
            'small_int_range',
            style='simple',
            label='Simple',
            id='simple_small',
        ),
        Item('_'),
        Item(
            'small_int_range',
            style='custom',
            label='Custom',
            id='custom_small',
        ),
        Item('_'),
        Item('small_int_range', style='text', label='Text', id='text_small'),
        Item('_'),
        Item(
            'small_int_range',
            style='readonly',
            label='ReadOnly',
            id='readonly_small',
        ),
        label='Small Int',
    )

    # RangeEditor display for medium-width integer Range traits (17 to 100):
    int_range_group2 = Group(
        Item(
            'medium_int_range',
            style='simple',
            label='Simple',
            id='simple_medium',
        ),
        Item('_'),
        Item(
            'medium_int_range',
            style='custom',
            label='Custom',
            id='custom_medium',
        ),
        Item('_'),
        Item('medium_int_range', style='text', label='Text', id='text_medium'),
        Item('_'),
        Item(
            'medium_int_range',
            style='readonly',
            label='ReadOnly',
            id='readonly_medium',
        ),
        label='Medium Int',
    )

    # RangeEditor display for wide integer Range traits (> 100):
    int_range_group3 = Group(
        Item(
            'large_int_range',
            style='simple',
            label='Simple',
            id='simple_large',
        ),
        Item('_'),
        Item(
            'large_int_range',
            style='custom',
            label='Custom',
            id='custom_large',
        ),
        Item('_'),
        Item('large_int_range', style='text', label='Text', id='text_large'),
        Item('_'),
        Item(
            'large_int_range',
            style='readonly',
            label='ReadOnly',
            id='readonly_large',
        ),
        label='Large Int',
    )

    # RangeEditor display for float Range traits:
    float_range_group = Group(
        Item('float_range', style='simple', label='Simple', id='simple_float'),
        Item('_'),
        Item('float_range', style='custom', label='Custom', id='custom_float'),
        Item('_'),
        Item('float_range', style='text', label='Text', id='text_float'),
        Item('_'),
        Item(
            'float_range',
            style='readonly',
            label='ReadOnly',
            id='readonly_float',
        ),
        label='Float',
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
        resizable=True,
    )


# Create the demo:
demo = RangeEditorDemo()

# Run the demo (if invoked from the comand line):
if __name__ == '__main__':
    demo.configure_traits()
