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
Edit a string, password, or integer

The TextEditor displays a Str, Password, or Int trait for the user to edit.

The demo shows all styles of the editor for each of the traits, however certain
styles are more useful than others:

- When editing a Str, consider styles 'simple' (one-line), 'custom'
  (multi-line), or 'readonly' (multi-line).
- When editing a Password, style 'simple' is recommended (shows asterisks).
- When editing an Int, consider styles 'simple' and 'readonly'.

Please refer to the `TextEditor API docs`_ for further information.

.. _TextEditor API docs: https://docs.enthought.com/traitsui/api/traitsui.editors.text_editor.html#traitsui.editors.text_editor.TextEditor
"""

from traits.api import HasTraits, Str, Int, Password

from traitsui.api import Item, Group, View


# The main demo class:
class TextEditorDemo(HasTraits):
    """Defines the TextEditor demo class."""

    # Define a trait for each of three TextEditor variants:
    string_trait = Str("sample string")
    int_trait = Int(1)
    password = Password()

    # TextEditor display with multi-line capability (for a string):
    text_str_group = Group(
        Item('string_trait', style='simple', label='Simple'),
        Item('_'),
        Item('string_trait', style='custom', label='Custom'),
        Item('_'),
        Item('string_trait', style='text', label='Text'),
        Item('_'),
        Item('string_trait', style='readonly', label='ReadOnly'),
        label='String',
    )

    # TextEditor display without multi-line capability (for an integer):
    text_int_group = Group(
        Item('int_trait', style='simple', label='Simple', id="simple_int"),
        Item('_'),
        Item('int_trait', style='custom', label='Custom', id="custom_int"),
        Item('_'),
        Item('int_trait', style='text', label='Text', id="text_int"),
        Item('_'),
        Item(
            'int_trait',
            style='readonly',
            label='ReadOnly',
            id="readonly_int",
        ),
        label='Integer',
    )

    # TextEditor display with secret typing capability (for Password traits):
    text_pass_group = Group(
        Item('password', style='simple', label='Simple'),
        Item('_'),
        Item('password', style='custom', label='Custom'),
        Item('_'),
        Item('password', style='text', label='Text'),
        Item('_'),
        Item('password', style='readonly', label='ReadOnly'),
        label='Password',
    )

    # The view includes one group per data type. These will be displayed
    # on separate tabbed panels:
    traits_view = View(
        text_str_group,
        text_pass_group,
        text_int_group,
        title='TextEditor',
        buttons=['OK'],
    )


# Create the demo:
demo = TextEditorDemo()

# Run the demo (if invoked from the command line):
if __name__ == "__main__":
    demo.configure_traits()
