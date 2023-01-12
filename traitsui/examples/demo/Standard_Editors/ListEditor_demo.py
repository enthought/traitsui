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
Implemention of a ListEditor demo plugin for Traits UI demo program

This demo shows each of the four styles of ListEditor.

Please refer to the `ListEditor API docs`_ for further information.

.. _ListEditor API docs: https://docs.enthought.com/traitsui/api/traitsui.editors.list_editor.html#traitsui.editors.list_editor.ListEditor
"""

from traits.api import HasTraits, List, Str

from traitsui.api import Item, Group, View


# Define the demo class:
class ListEditorDemo(HasTraits):
    """Defines the main ListEditor demo class."""

    # Define a List trait to display:
    play_list = List(Str, ["The Merchant of Venice", "Hamlet", "MacBeth"])

    # Items are used to define display, one per editor style:
    list_group = Group(
        Item(
            'play_list', style='simple', label='Simple', height=75, id='simple'
        ),
        Item('_'),
        Item('play_list', style='custom', label='Custom', id='custom'),
        Item('_'),
        Item('play_list', style='text', label='Text', id='text'),
        Item('_'),
        Item('play_list', style='readonly', label='ReadOnly', id='readonly'),
    )

    # Demo view:
    traits_view = View(
        list_group,
        title='ListEditor',
        buttons=['OK'],
        height=600,
        width=400,
        resizable=True,
    )


# Create the demo:
demo = ListEditorDemo()

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()
