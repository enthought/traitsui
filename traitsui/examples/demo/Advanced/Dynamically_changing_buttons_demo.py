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
This demo shows how to dynamically change the label or image of a button. Note
in this demo clicking the button itself does nothing.

Please refer to the `ButtonEditor API docs`_ for further information.

.. _ButtonEditor API docs: https://docs.enthought.com/traitsui/api/traitsui.editors.button_editor.html#traitsui.editors.button_editor.ButtonEditor
"""
from pyface.api import Image, ImageResource
from traits.api import Button, Enum, HasTraits, Instance, List, Str

from traitsui.api import (
    ButtonEditor,
    Group,
    ImageEditor,
    InstanceChoice,
    InstanceEditor,
    Item,
    UItem,
    View,
)
import traitsui.extras


class ImageChoice(InstanceChoice):
    def get_view(self):
        return View(UItem('name', editor=ImageEditor(image=self.object)))


class ButtonEditorDemo(HasTraits):
    my_button = Button()

    my_button_label = Str("Initial Label")

    my_button_image = Image()

    my_button_image_options = List(
        Image(),
        value=[
            ImageResource("run", [traitsui.extras]),
            ImageResource("previous", [traitsui.extras]),
            ImageResource("next", [traitsui.extras]),
            ImageResource("parent", [traitsui.extras]),
            ImageResource("reload", [traitsui.extras]),
        ],
    )

    def _my_button_image_default(self):
        return self.my_button_image_options[0]

    traits_view = View(
        Item(
            "my_button",
            style="custom",
            editor=ButtonEditor(
                label_value="my_button_label",
                image_value="my_button_image",
                orientation="horizontal",
            ),
        ),
        Item("my_button_label"),
        Item(
            "my_button_image",
            editor=InstanceEditor(
                name="my_button_image_options", adapter=ImageChoice
            ),
            style="custom",
        ),
    )


# Create the demo:
demo = ButtonEditorDemo()

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()
