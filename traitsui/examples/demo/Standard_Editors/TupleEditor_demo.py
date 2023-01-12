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
**WARNING**

  This demo might not work as expected and some documented features might be
  missing.

-------------------------------------------------------------------------------

Implementation of a TupleEditor demo plugin for Traits UI demo program.

This demo shows each of the four styles of the TupleEditor.

Please refer to the `TupleEditor API docs`_ for further information.

.. _TupleEditor API docs: https://docs.enthought.com/traitsui/api/traitsui.editors.tuple_editor.html#traitsui.editors.tuple_editor.TupleEditor
"""
# Issue related to the demo warning: enthought/traitsui#939


from traits.api import HasTraits, Tuple, Range, Str

from traitsui.api import Item, Group, View, Color


# The main demo class:
class TupleEditorDemo(HasTraits):
    """Defines the TupleEditor demo class."""

    # Define a trait to view:
    tuple = Tuple(Color, Range(1, 4), Str)

    # Display specification (one Item per editor style):
    tuple_group = Group(
        Item('tuple', style='simple', label='Simple'),
        Item('_'),
        Item('tuple', style='custom', label='Custom'),
        Item('_'),
        Item('tuple', style='text', label='Text'),
        Item('_'),
        Item('tuple', style='readonly', label='ReadOnly'),
    )

    # Demo view
    traits_view = View(
        tuple_group, title='TupleEditor', buttons=['OK'], resizable=True
    )


# Create the demo:
demo = TupleEditorDemo()

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()
