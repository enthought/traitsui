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

""" Table column object for RGBColor traits.
"""

from __future__ import absolute_import
from traitsui.table_column import ObjectColumn
import six


class ColorColumn(ObjectColumn):
    """ Table column object for RGBColor traits. """

    #: For display by default.
    style = 'readonly'

    #-- ObjectColumn Overrides -----------------------------------------------

    def get_cell_color(self, object):
        """ Returns the cell background color for the column for a specified
            object.
        """
        color_values = getattr(object, self.name + '_', None)
        if color_values is None:
            tk_color = super(ColorColumn, self).get_cell_color(object)
        elif isinstance(color_values, tuple):
            tk_color = self._as_int_rgb_tuple(color_values)
        else:
            tk_color = color_values
        return tk_color

    def get_value(self, object):
        """ Gets the value of the column for a specified object.
        """
        value = getattr(self.get_object(object), self.name, '')
        if isinstance(value, tuple):
            value = self._float_rgb_tuple_to_str(value)
        elif not isinstance(value, six.string_types):
            value = ''
        return value

    #-- Private Methods ------------------------------------------------------

    def _as_int_rgb_tuple(self, color_values):
        """ Returns object color as RGB integers. """
        return tuple(int(255 * v + 0.5) for v in color_values)

    def _float_rgb_tuple_to_str(self, color_values):
        """ Returns object color as RGB floats. """
        csv = ', '.join('{:5.3f}'.format(x) for x in color_values)
        return '({})'.format(csv)
