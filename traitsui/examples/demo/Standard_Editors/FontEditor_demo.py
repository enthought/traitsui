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
Font editor

A Font editor in a Traits UI allows the user to select a font from the
operating system.

Typically, you then pass the Font trait to another UI editor, which uses it to
display text. You can also read the Font trait as a string, or access its
individual attributes (note that these attributes are specific to the UI
toolkit -- QT or WX.)

The default 'simple' Font editor style is usually the most useful and powerful
style - it pops up a font selection dialog which is specific to the OS and
toolkit.

This example also displays some other less common style choices.

Please refer to the `FontEditor API docs`_ for further information.

.. _FontEditor API docs: https://docs.enthought.com/traitsui/api/traitsui.editors.font_editor.html#traitsui.editors.font_editor.FontEditor
"""

from traits.api import HasTraits

from traitsui.api import Item, Group, View, Font


class FontEditorDemo(HasTraits):
    """Defines the main FontEditor demo class."""

    # Define a Font trait to view:
    my_font_trait = Font()

    # Display specification (one Item per editor style):
    font_group = Group(
        Item('my_font_trait', style='simple', label='Simple'),
        Item('_'),
        Item('my_font_trait', style='custom', label='Custom'),
        Item('_'),
        Item('my_font_trait', style='text', label='Text'),
        Item('_'),
        Item('my_font_trait', style='readonly', label='ReadOnly'),
    )

    # Demo view:
    traits_view = View(
        font_group, title='FontEditor', buttons=['OK'], resizable=True
    )


# Create the demo:
demo = FontEditorDemo()


# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()
