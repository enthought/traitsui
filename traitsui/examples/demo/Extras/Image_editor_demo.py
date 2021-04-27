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
A simple demonstration of how to use the ImageEditor to add a graphic element
to a Traits UI View.
"""

# Imports:
from os.path \
    import join, dirname

from traits.api \
    import HasTraits, Str

from traitsui.api \
    import View, VGroup, Item, ImageEditor

from pyface.image_resource \
    import ImageResource

# Constants:

# The images folder is in the same folder as this file:
search_path = [dirname(__file__)]

# Define the demo class:


class Employee(HasTraits):

    # Define the traits:
    name = Str()
    dept = Str()
    email = Str()

    # Define the view:
    view = View(
        VGroup(
            VGroup(
                Item('name',
                     show_label=False,
                     editor=ImageEditor(
                         image=ImageResource('info',
                                             search_path=search_path)))
            ),
            VGroup(
                Item('name'),
                Item('dept'),
                Item('email'),
                Item('picture',
                     editor=ImageEditor(
                         scale=True,
                         preserve_aspect_ratio=True,
                         allow_upscaling=True),
                     springy=True),
            )
        ),
        resizable=True
    )

# Create the demo:
popup = Employee(name='William Murchison',
                 dept='Receiving',
                 email='wmurchison@acme.com',
                 picture=ImageResource('e-logo-rev',
                                       search_path=search_path))

# Run the demo (if invoked form the command line):
if __name__ == '__main__':
    popup.configure_traits()
