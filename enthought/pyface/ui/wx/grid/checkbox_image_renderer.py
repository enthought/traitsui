#------------------------------------------------------------------------------
# Copyright (c) 2006, Enthought, Inc.
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in enthought/LICENSE.txt and may be redistributed only
# under the conditions described in the aforementioned license.  The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
# Thanks for using Enthought open source!
#
# Author: Enthought, Inc.
# Description: <Enthought pyface package component>
#------------------------------------------------------------------------------
""" A renderer which displays a checked-box for a True value and an unchecked
    box for a false value. """

# Enthought-library imports
from enthought.pyface.image_resource import ImageResource

# local imports
from mapped_grid_cell_image_renderer import MappedGridCellImageRenderer

checked_image_map = { True: ImageResource('checked'),
                      False: ImageResource('unchecked'),
                    }

class CheckboxImageRenderer(MappedGridCellImageRenderer):

    def __init__(self, display_text = False):

        text_map = None
        if display_text:
            text_map = { True: 'True', False: 'False' }

        # Base-class constructor
        super(CheckboxImageRenderer, self).__init__(checked_image_map,
                                                    text_map)

        return

#### EOF ######################################################################
