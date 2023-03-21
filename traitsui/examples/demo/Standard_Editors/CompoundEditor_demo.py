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

Implementation of a CompoundEditor demo plugin for Traits UI demo program.

This demo shows each of the four styles of the CompoundEditor.

Please refer to the `CompoundEditor API docs`_ for further information.

.. _CompoundEditor API docs: https://docs.enthought.com/traitsui/api/traitsui.editors.compound_editor.html#traitsui.editors.compound_editor.CompoundEditor
"""
# Issue related to the demo warning: enthought/traitsui#945


from traits.api import Enum, HasTraits, Range, Union

from traitsui.api import Item, Group, View


# Define the demo class:
class CompoundEditorDemo(HasTraits):
    """Defines the main CompoundEditor demo class."""

    # Define a compound trait to view:
    compound_trait = Union(
        Range(1, 6), Enum('a', 'b', 'c', 'd', 'e', 'f'), default_value=1
    )

    # Display specification (one Item per editor style):
    comp_group = Group(
        Item('compound_trait', style='simple', label='Simple'),
        Item('_'),
        Item('compound_trait', style='custom', label='Custom'),
        Item('_'),
        Item('compound_trait', style='text', label='Text'),
        Item('_'),
        Item('compound_trait', style='readonly', label='ReadOnly'),
    )

    # Demo view:
    traits_view = View(
        comp_group, title='CompoundEditor', buttons=['OK'], resizable=True
    )


# Create the demo:
demo = CompoundEditorDemo()

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()
