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
Enum editor

The Enum editor provides a simple way for the user to choose one item from
a list of known values (normally strings or numbers).

An Enum trait can take any value from a specified list of values. These values
are typically strings, integers, or floats, but can also be None or hashable
tuples.

An Enum can be displayed / edited in one of five styles:

* 'simple' displays a drop-down list of allowed values
* 'custom' by default, displays one or more columns of radio buttons (only
  one of which is selected at a time).
* 'custom' in 'list' mode (see source code below), displays a list of all the
  allowed values at once.
* 'readonly' displays the current value as non-editable text.
* 'text' displays the current value as text. You can also edit this text,
  but your text must be in the list of allowed values.

Please refer to the `EnumEditor API docs`_ for further information.

.. _EnumEditor API docs: https://docs.enthought.com/traitsui/api/traitsui.editors.enum_editor.html#traitsui.editors.enum_editor.EnumEditor
"""

from traits.api import HasTraits, Enum

from traitsui.api import Item, Group, View, EnumEditor


class EnumEditorDemo(HasTraits):
    """Defines the main EnumEditor demo class."""

    # Define an Enum trait to view.
    name_list = Enum(
        'A-495',
        'A-498',
        'R-1226',
        'TS-17',
        'TS-18',
        'Foo',
        12345,
        (11, 7),
        None,
    )

    # Items are used to define the display, one Item per editor style:
    enum_group = Group(
        Item('name_list', style='simple', label='Simple', id="simple"),
        Item('_'),
        # The simple style also supports text entry:
        Item(
            'name_list',
            style='simple',
            label='Simple (text entry)',
            editor=EnumEditor(
                values=name_list, completion_mode='popup', evaluate=True
            ),
            id="simple_text",
        ),
        Item('_'),
        # The custom style defaults to radio button mode:
        Item('name_list', style='custom', label='Custom radio', id="radio"),
        Item('_'),
        # The custom style can also display in list mode, with extra work:
        Item(
            'name_list',
            style='custom',
            label='Custom list',
            editor=EnumEditor(values=name_list, mode='list'),
            id="list",
        ),
        Item('_'),
        Item('name_list', style='text', label='Text', id="text"),
        Item('_'),
        Item('name_list', style='readonly', label='ReadOnly', id="readonly"),
    )

    # Demo view:
    traits_view = View(
        enum_group, title='EnumEditor', buttons=['OK'], resizable=True
    )


# Create the demo:
demo = EnumEditorDemo()

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()
