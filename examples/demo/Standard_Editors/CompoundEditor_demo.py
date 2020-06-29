#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

"""
Implementation of a CompoundEditor demo plugin for Traits UI demo program.

This demo shows each of the four styles of the CompoundEditor
"""

from traits.api import Enum, HasTraits, Range, Union

from traitsui.api import Item, Group, View


# Define the demo class:
class CompoundEditorDemo(HasTraits):
    """ Defines the main CompoundEditor demo class.
    """

    # Define a compund trait to view:
    compound_trait = Union(
        Range(1, 6), Enum('a', 'b', 'c', 'd', 'e', 'f'),
        default_value=1
    )

    # Display specification (one Item per editor style):
    comp_group = Group(
        Item('compound_trait', style='simple', label='Simple'),
        Item('_'),
        Item('compound_trait', style='custom', label='Custom'),
        Item('_'),
        Item('compound_trait', style='text', label='Text'),
        Item('_'),
        Item('compound_trait', style='readonly', label='ReadOnly')
    )

    # Demo view:
    traits_view = View(
        comp_group,
        title='CompoundEditor',
        buttons=['OK'],
        resizable=True
    )


# Create the demo:
demo = CompoundEditorDemo()

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()
