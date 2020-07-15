#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

"""
**WARNING**

  This demo might not work as expected and some documented features might be
  missing.

-------------------------------------------------------------------------------

Implementation of a RGBColorEditor demo plugin for Traits UI demo program.

This demo shows each of the four styles of the ColorEditor
"""
# Issue related to the demo warning: enthought/traitsui#939


from traits.api import HasTraits

from traitsui.api import Item, Group, View, RGBColor


# Demo class definition:
class RGBColorEditorDemo(HasTraits):
    """ Defines the main RGBColorEditor demo. """

    # Define a Color trait to view:
    color_trait = RGBColor()

    # Items are used to define the demo display, one item per editor style:
    color_group = Group(
        Item('color_trait', style='simple', label='Simple'),
        Item('_'),
        Item('color_trait', style='custom', label='Custom'),
        Item('_'),
        Item('color_trait', style='text', label='Text'),
        Item('_'),
        Item('color_trait', style='readonly', label='ReadOnly')
    )

    # Demo view
    traits_view = View(
        color_group,
        title='RGBColorEditor',
        buttons=['OK'],
        resizable=True
    )


# Create the demo:
demo = RGBColorEditorDemo()

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()
