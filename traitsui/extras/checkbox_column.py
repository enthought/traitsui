# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Defines the table column descriptor used for toggleable columns.
"""


from traits.etsconfig.api import ETSConfig

from ..table_column import ObjectColumn

if ETSConfig.toolkit == "wx":
    from pyface.ui.wx.grid.checkbox_renderer import CheckboxRenderer
elif ETSConfig.toolkit in {"qt", "qt4"}:
    from ..qt.extra.checkbox_renderer import CheckboxRenderer
else:
    raise NotImplementedError("No checkbox renderer for backend")


class CheckboxColumn(ObjectColumn):
    def __init__(self, **traits):
        """Initializes the object."""
        super().__init__(**traits)

        # force the renderer to be a checkbox renderer
        self.renderer = CheckboxRenderer()

    def get_cell_color(self, object):
        """Returns the cell background color for the column for a specified
        object.
        """

        # Override the parent class to ALWAYS provide the standard color:
        return self.cell_color_

    def is_editable(self, object):
        """Returns whether the column is editable for a specified object."""

        # Although a checkbox column is always editable, we return this
        # to keep a standard editor from appearing. The editing is handled
        # in the renderer's handlers.
        return False
