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

Implementation of a FileEditor demo plugin for Traits UI demo program.

This demo shows each of the four styles of the FileEditor.

Please refer to the `FileEditor API docs`_ for further information.

.. _FileEditor API docs: https://docs.enthought.com/traitsui/api/traitsui.editors.file_editor.html#traitsui.editors.file_editor.FileEditor
"""
# Issue related to the demo warning: enthought/traitsui#889


from traits.api import HasTraits, File

from traitsui.api import Item, Group, View


# Define the demo class:
class FileEditorDemo(HasTraits):
    """Defines the main FileEditor demo class."""

    # Define a File trait to view:
    file_name = File()

    # Display specification (one Item per editor style):
    file_group = Group(
        Item('file_name', style='simple', label='Simple', id='simple_file'),
        Item('_'),
        Item('file_name', style='custom', label='Custom'),
        Item('_'),
        Item('file_name', style='text', label='Text'),
        Item('_'),
        Item('file_name', style='readonly', label='ReadOnly'),
    )

    # Demo view:
    traits_view = View(
        file_group,
        title='FileEditor',
        width=400,
        height=600,
        buttons=['OK'],
        resizable=True,
    )


# Create the demo:
demo = FileEditorDemo()

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()
