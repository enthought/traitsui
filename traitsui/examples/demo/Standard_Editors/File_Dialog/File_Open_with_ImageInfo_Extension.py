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

This demonstrates using the TraitsUI file dialog with a file dialog extension,
in this case, the **ImageInfo** extension, which displays (if possible) the
contents, width and height information for the currently selected image file
so that the user can quickly verify they are opening the correct file before
leaving the file dialog.

For more information about why you would want to use the TraitsUI file dialog
over the standard OS file dialog, select the **File Open** demo. For a
demonstration of writing a custom file dialog extension, select the
**File Open with Custom Extension** demo.

This example also shows setting a file name filter which only allows common
image file formats (i.e. ``*.png``, ``*.gif``, ``*.jpg``, ``*.jpeg``) files to
be viewed and selected.
"""
# Issue related to the demo warning: enthought/traitsui#953

from traits.api import HasTraits, File, Button

from traitsui.api import View, HGroup, Item

from traitsui.file_dialog import open_file, ImageInfo

# -- FileDialogDemo Class -------------------------------------------------

# Demo specific file dialig id:
demo_id = 'traitsui.demo.standard_editors.file_dialog.image_info'

# The image filters description:
filters = [
    'PNG file (*.png)|*.png',
    'GIF file (*.gif)|*.gif',
    'JPG file (*.jpg)|*.jpg',
    'JPEG file (*.jpeg)|*.jpeg',
]


class FileDialogDemo(HasTraits):

    # The name of the selected file:
    file_name = File()

    # The button used to display the file dialog:
    open = Button('Open...')

    # -- Traits View Definitions ----------------------------------------------

    traits_view = View(
        HGroup(
            Item('open', show_label=False),
            '_',
            Item('file_name', style='readonly', springy=True),
        ),
        width=0.5,
    )

    # -- Traits Event Handlers ------------------------------------------------

    def _open_changed(self):
        """Handles the user clicking the 'Open...' button."""
        file_name = open_file(
            extensions=ImageInfo(), filter=filters, id=demo_id
        )
        if file_name != '':
            self.file_name = file_name


# Create the demo:
demo = FileDialogDemo()

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()
