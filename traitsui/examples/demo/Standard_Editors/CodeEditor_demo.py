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
Implementation of a CodeEditor demo plugin for Traits UI demo program.

This demo shows each of the four styles of the CodeEditor.

Please refer to the `CodeEditor API docs`_ for further information.

.. _CodeEditor API docs: https://docs.enthought.com/traitsui/api/traitsui.editors.code_editor.html#traitsui.editors.code_editor.CodeEditor
"""

from traits.api import HasTraits, Code

from traitsui.api import Item, Group, View


# The main demo class:
class CodeEditorDemo(HasTraits):
    """Defines the CodeEditor demo class."""

    # Define a trait to view:
    code_sample = Code('import sys\n\nsys.print("hello world!")')

    # Display specification:
    code_group = Group(
        Item('code_sample', style='simple', label='Simple'),
        Item('_'),
        Item('code_sample', style='custom', label='Custom'),
        Item('_'),
        Item('code_sample', style='text', label='Text'),
        Item('_'),
        Item('code_sample', style='readonly', label='ReadOnly'),
    )

    # Demo view:
    traits_view = View(
        code_group, title='CodeEditor', width=600, height=600, buttons=['OK']
    )


# Create the demo:
demo = CodeEditorDemo()

# Run the demo (if invoked from the command line):
if __name__ == "__main__":
    demo.configure_traits()
