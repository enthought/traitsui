#------------------------------------------------------------------------------
#
#  Copyright (c) 2005, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
#  Author: David C. Morrill
#
#------------------------------------------------------------------------------

""" Table column object for Color traits.
"""

#-------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------

from traitsui.table_column \
    import ObjectColumn

#-------------------------------------------------------------------------
#  'ColorColumn' class:
#-------------------------------------------------------------------------


class ColorColumn(ObjectColumn):
    """ Table column object for Color traits. """

#-- ObjectColumn Overrides -----------------------------------------------

    def get_cell_color(self, object):
        """ Returns the cell background color for the column for a specified
            object.
        """
        color_values = getattr(object, self.name + '_')
        if isinstance(color_values, tuple):
            tk_color = self._as_int_rgb_tuple(color_values)
        else:
            tk_color = super(ColorColumn, self).get_cell_color(object)
        return tk_color

    def get_value(self, object):
        """ Gets the value of the column for a specified object.
        """
        value = getattr(self.get_object(object), self.name)
        if isinstance(value, tuple):
            value = "(%3d, %3d, %3d)" % self._as_int_rgb_tuple(value[:-1])
        elif not isinstance(value, str):
            value = str(value)

        return value

#-- Private Methods ------------------------------------------------------

    def _as_int_rgb_tuple(self, color_values):
        """ Returns object color as RGB integers. """
        return (int(255 * color_values[0]),
                int(255 * color_values[1]),
                int(255 * color_values[2]))
