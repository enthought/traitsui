#------------------------------------------------------------------------------
#
#  Copyright (c) 2016, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
#  Author: Corran Webster
#
#------------------------------------------------------------------------------

""" A column class for for the TableEditor that displays progress bars. """

from __future__ import absolute_import

from traits.etsconfig.api import ETSConfig
from traits.api import Str

from traitsui.table_column import ObjectColumn


if ETSConfig.toolkit == 'qt4':
    from traitsui.qt4.extra.progress_renderer import ProgressRenderer
else:
    raise NotImplementedError("No checkbox renderer for backend")


class ProgressColumn(ObjectColumn):

    # Format string to apply to column values:
    format = Str('%s%%')

    def __init__(self, **traits):
        super(ProgressColumn, self).__init__(**traits)
        # force the renderer to be a progress bar renderer
        self.renderer = ProgressRenderer()

    def is_editable(self, object):
        """ Returns whether the column is editable for a specified object.
        """
        # Although a checkbox column is always editable, we return this
        # to keep a standard editor from appearing. The editing is handled
        # in the renderer's handlers.
        return False

    def get_minimum(self, object):
        return 0

    def get_maximum(self, object):
        return 100

    def get_text_visible(self, object):
        """ Whether or not to display text in column.

        Note, may not render on some platforms (eg. OS X) due to
        the rendering style.
        """
        return True
