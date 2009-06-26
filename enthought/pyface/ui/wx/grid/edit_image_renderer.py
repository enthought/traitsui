#------------------------------------------------------------------------------
# Copyright (c) 2007, Enthought, Inc.
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

# ETS imports
from enthought.pyface.image_resource import ImageResource

# Local import
from grid_cell_image_renderer import GridCellImageRenderer

class EditImageRenderer(GridCellImageRenderer):
    image = ImageResource('table_edit')
    
    def __init__(self, **kw):
        super(EditImageRenderer, self).__init__(self, **kw)
    
    def get_image_for_cell(self, grid, row, col): 
        """ returns the image resource for the table_edit bitmap """

        # show the icon if the obj does not have an editable trait
        # or if the editable trait is True
        
        obj = grid.GetTable().model.get_rows_drag_value([row])[0]
        
        if (not hasattr(obj, 'editable')) or obj.editable:
            return self.image
        return None
        
    def _get_text(self, grid, row, col):
        return None
