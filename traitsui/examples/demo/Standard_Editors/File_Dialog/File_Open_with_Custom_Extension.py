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

This demonstrates using the TraitsUI file dialog with a custom written file
dialog extension, in this case an extension called **LineCountInfo**, which
displays the number of text lines in the currently selected file.

For more information about why you would want to use the TraitsUI file dialog
over the standard OS file dialog, select the **File Open** demo.
"""
# Issue related to the demo warning: enthought/traitsui#953

from os.path import getsize

from traits.api import HasTraits, File, Button, Property, cached_property

from traitsui.api import View, VGroup, HGroup, Item

from traitsui.file_dialog import open_file, MFileDialogModel


# -- LineCountInfo Class --------------------------------------------------
class LineCountInfo(MFileDialogModel):
    """Defines a file dialog extension that displays the number of text lines
    in the currently selected file.
    """

    # The number of text lines in the currently selected file:
    lines = Property(observe='file_name')

    # -- Traits View Definitions ----------------------------------------------

    traits_view = View(
        VGroup(
            Item('lines', style='readonly'),
            label='Line Count Info',
            show_border=True,
        )
    )

    # -- Property Implementations ---------------------------------------------

    @cached_property
    def _get_lines(self):
        try:
            if getsize(self.file_name) > 10000000:
                return 'File too big...'

            with open(self.file_name, 'r', encoding='utf8') as fh:
                data = fh.read()
        except OSError:
            return ''

        if (data.find('\x00') >= 0) or (data.find('\xFF') >= 0):
            return 'File contains binary data...'

        return '{:n} lines'.format(len(data.splitlines()))


# -- FileDialogDemo Class -------------------------------------------------

# Demo specific file dialig id:
demo_id = 'traitsui.demo.standard_editors.file_dialog.line_count_info'


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
        file_name = open_file(extensions=LineCountInfo(), id=demo_id)
        if file_name != '':
            self.file_name = file_name


# Create the demo:
demo = FileDialogDemo()

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()
