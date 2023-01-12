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
A simple demonstration of how to use the ImageEditor to add a graphic element
to a Traits UI View.

This example needs NumPy to show an example of a dynamically created image.
"""

# Imports:
from os.path import join, dirname

import numpy as np

from pyface.api import ArrayImage, Image, ImageResource
from traits.api import HasTraits, Str
from traitsui.api import View, VGroup, Item, ImageEditor

# Constants:

# The images folder is in the same folder as this file:
search_path = [dirname(__file__)]


# Define the demo class:
class Employee(HasTraits):

    # Define the traits:
    name = Str()
    dept = Str()
    email = Str()
    picture = Image()
    gradient = Image()

    # Define the view:
    view = View(
        VGroup(
            VGroup(
                Item(
                    'name',
                    show_label=False,
                    editor=ImageEditor(
                        image=ImageResource('info', search_path=search_path)
                    ),
                )
            ),
            VGroup(
                Item('name'),
                Item('dept'),
                Item('email'),
                Item(
                    'picture',
                    editor=ImageEditor(
                        scale=True,
                        preserve_aspect_ratio=True,
                        allow_upscaling=True,
                    ),
                    springy=True,
                ),
                Item(
                    'gradient',
                    editor=ImageEditor(
                        scale=True,
                        preserve_aspect_ratio=True,
                        allow_upscaling=True,
                    ),
                    springy=True,
                ),
            ),
        ),
        resizable=True,
    )


# generate a 2D NumPy array of RGB values
gradient = np.empty(shape=(256, 256, 3), dtype='uint8')
gradient[:, :, 0] = np.arange(256).reshape(256, 1)
gradient[:, :, 1] = np.arange(256).reshape(1, 256)
gradient[:, :, 2] = np.arange(255, -1, -1).reshape(1, 256)

# Create the demo:
popup = Employee(
    name='William Murchison',
    dept='Receiving',
    email='wmurchison@acme.com',
    picture=ImageResource('python-logo', search_path=search_path),
    gradient=ArrayImage(data=gradient),
)

# Run the demo (if invoked form the command line):
if __name__ == '__main__':
    popup.configure_traits()
