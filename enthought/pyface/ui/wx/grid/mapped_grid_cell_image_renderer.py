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
""" A renderer which will display a cell-specific image in addition to some
    text displayed in the same way the standard string renderer normally
    would, all data retrieved from specified value maps. """

from grid_cell_image_renderer import GridCellImageRenderer

class MappedGridCellImageRenderer(GridCellImageRenderer):
    """ Maps data values to image and text. """

    def __init__(self, image_map = None, text_map = None):

        # Base-class constructor. We pass ourself as the provider
        super(MappedGridCellImageRenderer, self).__init__(self)

        self.image_map = image_map
        self.text_map = text_map

        return

    def get_image_for_cell(self, grid, row, col):

        if self.image_map is None:
            return

        value = self._get_value(grid, row, col)

        if self.image_map.has_key(value):
            result = self.image_map[value]
        else:
            result = None

        return result

    def get_text_for_cell(self, grid, row, col):

        if self.text_map is None:
            return

        value = self._get_value(grid, row, col)

        if self.text_map.has_key(value):
            result = self.text_map[value]
        else:
            result = None

        return result

    def _get_value(self, grid, row, col):

        # first grab the PyGridTableBase object
        base = grid.GetTable()

        # from that we can get the pyface-level model object
        model = base.model

        # retrieve the unformatted value from the model and return it
        return model.get_cell_drag_value(row, col)

#### EOF ######################################################################
