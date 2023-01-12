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
Demonstrates the use of the TitleEditor.

A TitleEditor can be used to dynamically label sections of a user interface.
The text displayed by the TitleEditor is specified by a trait associated with
the view.

This demonstration shows three variations of using a TitleEditor:

* In the first example, the TitleEditor values are supplied by an Enum trait.
  Simply select a new value for the title from the drop-down list to cause the
  title to change.
* In the second example, the TitleEditor values are supplied by a Str trait.
  Simply type a new value into the title field to cause the title to change.
* In the third example, the TitleEditor values are supplied by a Property
  whose value is derived from a calculation on a Float trait. Type a number
  into the value field to cause the title to changed.

Please refer to the `TitleEditor API docs`_ for further information.

.. _TitleEditor API docs: https://docs.enthought.com/traitsui/api/traitsui.editors.title_editor.html#traitsui.editors.title_editor.TitleEditor
"""

from traits.api import HasTraits, Enum, Str, Float, Property, cached_property

from traitsui.api import View, VGroup, HGroup, Item, TitleEditor


class TitleEditorDemo(HasTraits):

    # Define the selection of titles that can be displayed:
    title = Enum(
        'Select a new title from the drop down list below',
        'This is the TitleEditor demonstration',
        'Acme Widgets Sales for Each Quarter',
        'This is Not Intended to be a Real Application',
    )

    # A user settable version of the title:
    title_2 = Str('Type into the text field below to change this title')

    # A title driven by the result of a calculation:
    title_3 = Property(observe='value')

    # The number used to drive the calculation:
    value = Float()

    # Define the test view:
    traits_view = View(
        VGroup(
            VGroup(
                HGroup(
                    Item(
                        'title',
                        show_label=False,
                        springy=True,
                        editor=TitleEditor(),
                    )
                ),
                Item('title'),
                show_border=True,
            ),
            VGroup(
                HGroup(
                    Item(
                        'title_2',
                        show_label=False,
                        springy=True,
                        editor=TitleEditor(),
                    )
                ),
                Item('title_2', label='Title'),
                show_border=True,
            ),
            VGroup(
                HGroup(
                    Item(
                        'title_3',
                        show_label=False,
                        springy=True,
                        editor=TitleEditor(),
                    )
                ),
                Item('value'),
                show_border=True,
            ),
        ),
        width=0.4,
    )

    # -- Property Implementations ---------------------------------------------

    @cached_property
    def _get_title_3(self):
        if self.value >= 0:
            return 'The square root of {} is {}'.format(
                self.value, self.value ** 0.5
            )
        else:
            return 'The square root of {} is {}i'.format(
                self.value, (-self.value) ** 0.5
            )


# Create the demo:
demo = TitleEditorDemo()

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()
