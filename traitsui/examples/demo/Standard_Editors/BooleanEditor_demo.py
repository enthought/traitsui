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
Implementation of a BooleanEditor demo plugin for Traits UI demo program.

This demo shows each of the four styles of the BooleanEditor.

Please refer to the `BooleanEditor API docs`_ for further information.

.. _BooleanEditor API docs: https://docs.enthought.com/traitsui/api/traitsui.editors.boolean_editor.html#traitsui.editors.boolean_editor.BooleanEditor
"""

from traits.api import HasTraits, Bool
from traitsui.api import Item, Group, View


# -------------------------------------------------------------------------
#  Demo Class
# -------------------------------------------------------------------------


class BooleanEditorDemo(HasTraits):
    """This class specifies the details of the BooleanEditor demo."""

    # To demonstrate any given Trait editor, an appropriate Trait is required.
    boolean_trait = Bool()

    # Items are used to define the demo display - one Item per editor style
    bool_group = Group(
        Item('boolean_trait', style='simple', label='Simple', id='simple'),
        Item('_'),
        Item('boolean_trait', style='custom', label='Custom', id='custom'),
        Item('_'),
        Item('boolean_trait', style='text', label='Text', id='text'),
        Item('_'),
        Item(
            'boolean_trait', style='readonly', label='ReadOnly', id='readonly'
        ),
    )

    # Demo view
    traits_view = View(
        bool_group, title='BooleanEditor', buttons=['OK'], width=300
    )


# Hook for 'demo.py'
demo = BooleanEditorDemo()

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()
