#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

"""
**WARNING**

  This demo might not work as expected and some documented features might be
  missing.

-------------------------------------------------------------------------------

Implementation of an ImageEnumEditor demo plugin for the Traits UI demo
program.

This demo shows each of the four styles of the ImageEnumEditor.
"""
# Issues related to the demo warning:
# enthought/traitsui#947


from traits.api import Enum, HasTraits, Str

from traitsui.api import Item, Group, View, ImageEnumEditor

# This list of image names (with the standard suffix "_origin") is used to
# construct an image enumeration trait to demonstrate the ImageEnumEditor:
image_list = ['top left', 'top right', 'bottom left', 'bottom right']


class Dummy(HasTraits):
    """ Dummy class for ImageEnumEditor
    """
    x = Str()

    traits_view = View()


class ImageEnumEditorDemo(HasTraits):
    """ Defines the ImageEnumEditor demo class.
    """

    # Define a trait to view:
    image_from_list = Enum(
        *image_list,
        editor=ImageEnumEditor(
            values=image_list,
            prefix='@icons:',
            suffix='_origin',
            cols=4,
            klass=Dummy
        )
    )

    # Items are used to define the demo display, one Item per editor style:
    img_group = Group(
        Item('image_from_list', style='simple', label='Simple'),
        Item('_'),
        Item('image_from_list', style='text', label='Text'),
        Item('_'),
        Item('image_from_list', style='readonly', label='ReadOnly'),
        Item('_'),
        Item('image_from_list', style='custom', label='Custom')
    )

    # Demo view:
    traits_view = View(
        img_group,
        title='ImageEnumEditor',
        buttons=['OK'],
        resizable=True
    )


# Create the demo:
demo = ImageEnumEditorDemo()

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()
