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

Implementation of a DirectoryEditor demo plugin for Traits UI demo program.

This demo shows each of the four styles of the DirectoryEditor.

Please refer to the `DirectoryEditor API docs`_ for further information.

.. _DirectoryEditor API docs: https://docs.enthought.com/traitsui/api/traitsui.editors.directory_editor.html#traitsui.editors.directory_editor.DirectoryEditor
"""
# Issue related to the demo warning: enthought/traitsui#889


from traits.api import HasTraits, Directory

from traitsui.api import Item, Group, View


# Define the demo class:
class DirectoryEditorDemo(HasTraits):
    """Define the main DirectoryEditor demo class."""

    # Define a Directory trait to view:
    dir_name = Directory()

    # Display specification (one Item per editor style):
    dir_group = Group(
        Item('dir_name', style='simple', label='Simple'),
        Item('_'),
        Item('dir_name', style='custom', label='Custom'),
        Item('_'),
        Item('dir_name', style='text', label='Text'),
        Item('_'),
        Item('dir_name', style='readonly', label='ReadOnly'),
    )

    # Demo view:
    traits_view = View(
        dir_group,
        title='DirectoryEditor',
        width=400,
        height=600,
        buttons=['OK'],
        resizable=True,
    )


# Create the demo:
demo = DirectoryEditorDemo()

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()
