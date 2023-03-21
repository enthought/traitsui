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

Implementation of a ColorEditor demo plugin for Traits UI demo program.

This demo shows each of the four styles of the ColorEditor.

Please refer to the `ColorEditor API docs`_ for further information.

.. _ColorEditor API docs: https://docs.enthought.com/traitsui/api/traitsui.editors.color_editor.html#traitsui.editors.color_editor.ColorEditor
"""
# Issues related to the demo warning:
# enthought/traitsui#946


from traits.api import HasTraits

from traitsui.api import Item, Group, View, Color


# Demo class definition:
class ColorEditorDemo(HasTraits):
    """Defines the main ColorEditor demo."""

    # Define a Color trait to view:
    color_trait = Color()

    # Items are used to define the demo display, one item per editor style:
    color_group = Group(
        Item('color_trait', style='simple', label='Simple'),
        Item('_'),
        Item('color_trait', style='custom', label='Custom'),
        Item('_'),
        Item('color_trait', style='text', label='Text'),
        Item('_'),
        Item('color_trait', style='readonly', label='ReadOnly'),
    )

    # Demo view
    traits_view = View(
        color_group, title='ColorEditor', buttons=['OK'], resizable=True
    )


# Create the demo:
demo = ColorEditorDemo()

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()
