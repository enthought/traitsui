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
Implementation of a CheckListEditor demo plugin for the Traits UI demo program.

For each of three CheckListEditor column formations, this demo shows
each of the four styles of the CheckListEditor.

Please refer to the `CheckListEditor API docs`_ for further information.

.. _CheckListEditor API docs: https://docs.enthought.com/traitsui/api/traitsui.editors.check_list_editor.html#traitsui.editors.check_list_editor.CheckListEditor
"""

from traits.api import HasTraits, List

from traitsui.api import Item, Group, View, CheckListEditor


# Define the demo class:
class CheckListEditorDemo(HasTraits):
    """Define the main CheckListEditor demo class."""

    # Define a trait for each of three formations:
    checklist_4col = List(
        editor=CheckListEditor(values=['one', 'two', 'three', 'four'], cols=4)
    )

    checklist_2col = List(
        editor=CheckListEditor(values=['one', 'two', 'three', 'four'], cols=2)
    )

    checklist_1col = List(
        editor=CheckListEditor(values=['one', 'two', 'three', 'four'], cols=1)
    )

    # CheckListEditor display with four columns:
    cl_4_group = Group(
        Item('checklist_4col', style='simple', label='Simple'),
        Item('_'),
        Item('checklist_4col', style='custom', label='Custom'),
        Item('_'),
        Item('checklist_4col', style='text', label='Text'),
        Item('_'),
        Item('checklist_4col', style='readonly', label='ReadOnly'),
        label='4-column',
    )

    # CheckListEditor display with two columns:
    cl_2_group = Group(
        Item('checklist_2col', style='simple', label='Simple'),
        Item('_'),
        Item('checklist_2col', style='custom', label='Custom'),
        Item('_'),
        Item('checklist_2col', style='text', label='Text'),
        Item('_'),
        Item('checklist_2col', style='readonly', label='ReadOnly'),
        label='2-column',
    )

    # CheckListEditor display with one column:
    cl_1_group = Group(
        Item('checklist_1col', style='simple', label='Simple'),
        Item('_'),
        Item('checklist_1col', style='custom', label='Custom'),
        Item('_'),
        Item('checklist_1col', style='text', label='Text'),
        Item('_'),
        Item('checklist_1col', style='readonly', label='ReadOnly'),
        label='1-column',
    )

    # The view includes one group per column formation.  These will be
    # displayed on separate tabbed panels.
    traits_view = View(
        cl_4_group,
        cl_2_group,
        cl_1_group,
        title='CheckListEditor',
        buttons=['OK'],
        resizable=True,
    )


# Create the demo:
demo = CheckListEditorDemo()

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()
