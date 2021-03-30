# (C) Copyright 2004-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

"""
This demo shows how to dynamically change the label or image of a button.

Please refer to the `ButtonEditor API docs`_ for further information.

.. _ButtonEditor API docs: https://docs.enthought.com/traitsui/api/traitsui.editors.button_editor.html#traitsui.editors.button_editor.ButtonEditor
"""
from pyface.api import ImageResource
from traits.api import Button, Enum, HasTraits, List, Str

from traitsui.api import ButtonEditor, Group, message, UItem, View 


class ButtonEditorDemo(HasTraits):
    my_button = Button()

    my_button_label = Str("Initial Label")

    my_button_image = Enum(
        ImageResource("run"),
        ImageResource("previous"),
        ImageResource("next"),
        ImageResource("parent")
    )

    traits_view = View(
        UItem(
            "my_button",
            style="custom",
            editor=ButtonEditor(
                label_value="my_button_label",
                image_value="my_button_image",
            )
        ),
        UItem("my_button_label"),
        UItem("my_button_image")
    )

# Create the demo:
demo = ButtonEditorDemo()

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()
