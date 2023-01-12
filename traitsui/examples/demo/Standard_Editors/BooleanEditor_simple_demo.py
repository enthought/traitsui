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
Boolean editor (checkbox or text)

A Boolean (True/False) trait is displayed and edited as a checkbox, by default.

It can also be displayed as text 'True'/'False', either editable or read-only.

This example also shows how to listen for a change in a trait, and take
action when its value changes.

It also demonstrates how to add vertical space and a Label (plain text which is
not editable.)

Please refer to the `BooleanEditor API docs`_ for further information.

.. _BooleanEditor API docs: https://docs.enthought.com/traitsui/api/traitsui.editors.boolean_editor.html#traitsui.editors.boolean_editor.BooleanEditor
"""

from traits.api import HasTraits, Bool, Int
from traitsui.api import Item, Label, Group, View


class BooleanEditorDemo(HasTraits):
    """Defines the main BooleanEditor demo class."""

    # a boolean trait to view:
    my_boolean_trait = Bool()
    count_changes = Int(0)

    # When the trait's value changes, do something.
    # The listener method is named '_TraitName_changed', where
    # 'TraitName' is the name of the trait being monitored.
    def _my_boolean_trait_changed(self):
        self.count_changes += 1

    # Demo view
    traits_view = View(
        '10',  # vertical space
        Item('my_boolean_trait', style='simple', id='simple'),
        '10',  # vertical space
        # We put this label in its own group so that it will be left justified.
        # Otherwise it will line up with other edit fields (indented):
        Group(
            Label(
                'The same Boolean trait can also be displayed and edited as '
                'text (True/False):'
            )
        ),
        '10',  # vertical space
        Item(
            'my_boolean_trait',
            style='readonly',
            label='Read-only style',
            id='readonly',
        ),
        Item('my_boolean_trait', style='text', label='Text style', id='text'),
        '10',
        'count_changes',
        title='Boolean trait',
        buttons=['OK'],
        resizable=True,
    )


# Create the demo view (but do not yet display it):
demo = BooleanEditorDemo()

# Display and edit the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()
