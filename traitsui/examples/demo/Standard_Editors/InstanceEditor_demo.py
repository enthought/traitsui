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

Implementation of an InstanceEditor demo plugin for the Traits UI demo program.

This demo shows each of the four styles of the InstanceEditor

Fixme: This version of the demo only shows the old-style InstanceEditor
capabilities.

Please refer to the `InstanceEditor API docs`_ for further information.

.. _InstanceEditor API docs: https://docs.enthought.com/traitsui/api/traitsui.editors.instance_editor.html#traitsui.editors.instance_editor.InstanceEditor
"""
# Issue related to the demo warning: enthought/traitsui#939


from traits.api import HasTraits, Str, Range, Bool, Instance

from traitsui.api import Item, Group, View


# -------------------------------------------------------------------------
#  Classes:
# -------------------------------------------------------------------------


class SampleClass(HasTraits):
    """This Sample class is used to demonstrate the InstanceEditor demo."""

    # The actual attributes don't matter here; we just need an assortment
    # to demonstrate the InstanceEditor's capabilities.:
    name = Str()
    occupation = Str()
    age = Range(21, 65)
    registered_voter = Bool()

    # The InstanceEditor uses whatever view is defined for the class.  The
    # default view lists the fields alphabetically, so it's best to define one
    # explicitly:
    traits_view = View('name', 'occupation', 'age', 'registered_voter')


class InstanceEditorDemo(HasTraits):
    """This class specifies the details of the InstanceEditor demo."""

    # Create an Instance trait to view:
    sample_instance = Instance(SampleClass, ())

    # Items are used to define the demo display, one item per editor style:
    inst_group = Group(
        Item('sample_instance', style='simple', label='Simple', id="simple"),
        Item('_'),
        Item('sample_instance', style='custom', label='Custom', id="custom"),
        Item('_'),
        Item('sample_instance', style='text', label='Text'),
        Item('_'),
        Item('sample_instance', style='readonly', label='ReadOnly'),
    )

    # Demo View:
    traits_view = View(
        inst_group, title='InstanceEditor', buttons=['OK'], resizable=True
    )


# Create the demo:
demo = InstanceEditorDemo()

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()
