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
This demo shows a combination of the **DirectoryEditor**, the
**TabularEditor** and the **CodeEditor** used to create a simple Python
source browser:

- Use the **DirectoryEditor** on the left to navigate to and select
  directories containing Python source files.
- Use the **TabularEditor** on the top-right to view information about and
  to select Python source files in the currently selected directory.
- View the currently selected Python source file's contents in the
  **CodeEditor** in the bottom-right.

As an extra *feature*, the **TabularEditor** also displays a:

- Red ball if the file size > 64KB.
- Blue ball if the file size > 16KB.
"""

from time import localtime, strftime

from os import listdir

from os.path import (
    getsize,
    getmtime,
    isfile,
    join,
    splitext,
    basename,
    dirname,
)

from traits.api import (
    HasPrivateTraits,
    Str,
    Float,
    List,
    Directory,
    File,
    Code,
    Instance,
    Property,
    cached_property,
)

import traitsui.api

from traitsui.api import View, Item, HSplit, VSplit, TabularEditor, Font

from traitsui.tabular_adapter import TabularAdapter

from pyface.image_resource import ImageResource
from io import open

# -- Constants ------------------------------------------------------------

# The images folder is in the same folder as this file:
search_path = [dirname(__file__)]


# -- FileInfo Class Definition --------------------------------------------


class FileInfo(HasPrivateTraits):

    file_name = File()
    name = Property()
    size = Property()
    time = Property()
    date = Property()

    @cached_property
    def _get_name(self):
        return basename(self.file_name)

    @cached_property
    def _get_size(self):
        return getsize(self.file_name)

    @cached_property
    def _get_time(self):
        return strftime('%I:%M:%S %p', localtime(getmtime(self.file_name)))

    @cached_property
    def _get_date(self):
        return strftime('%m/%d/%Y', localtime(getmtime(self.file_name)))


# -- Tabular Adapter Definition -------------------------------------------


class FileInfoAdapter(TabularAdapter):

    columns = [
        ('File Name', 'name'),
        ('Size', 'size'),
        ('', 'big'),
        ('Time', 'time'),
        ('Date', 'date'),
    ]

    even_bg_color = (201, 223, 241)
    # FIXME: Font fails with wx in OSX; see traitsui issue #13:
    font = Font('Courier 10')
    size_alignment = Str('right')
    time_alignment = Str('right')
    date_alignment = Str('right')
    big_text = Str()
    big_width = Float(18)
    big_image = Property()

    def _get_big_image(self):
        size = self.item.size
        if size > 65536:
            return ImageResource('red_ball')

        return (None, ImageResource('blue_ball'))[size > 16384]


# -- Tabular Editor Definition --------------------------------------------

tabular_editor = TabularEditor(
    editable=False,
    selected='file_info',
    adapter=FileInfoAdapter(),
    operations=[],
    images=[
        ImageResource('blue_ball', search_path=search_path),
        ImageResource('red_ball', search_path=search_path),
    ],
)

# -- PythonBrowser Class Definition ---------------------------------------


class PythonBrowser(HasPrivateTraits):

    # -- Trait Definitions ----------------------------------------------------

    dir = Directory()
    files = List(FileInfo)
    file_info = Instance(FileInfo)
    code = Code()

    # -- Traits View Definitions ----------------------------------------------

    view = View(
        HSplit(
            Item('dir', style='custom'),
            VSplit(
                Item('files', editor=tabular_editor),
                Item('code', style='readonly'),
                show_labels=False,
            ),
            show_labels=False,
        ),
        resizable=True,
        width=0.75,
        height=0.75,
    )

    # -- Event Handlers -------------------------------------------------------

    def _dir_changed(self, dir):
        if dir != '':
            self.files = [
                FileInfo(file_name=join(dir, name))
                for name in listdir(dir)
                if ((splitext(name)[1] == '.py') and isfile(join(dir, name)))
            ]
        else:
            self.files = []

    def _file_info_changed(self, file_info):
        fh = None
        try:
            fh = open(file_info.file_name, 'rU', encoding='utf8')
            self.code = fh.read()
        except:
            pass

        if fh is not None:
            fh.close()


# Create the demo:
demo = PythonBrowser(dir=dirname(dirname(__file__)))

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()
