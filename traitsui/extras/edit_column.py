# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Defines the table column descriptor used for editing the object represented
    by the row
"""


from ..table_column import ObjectColumn


class EditColumn(ObjectColumn):
    def __init__(self, **traits):
        """Initializes the object."""
        super().__init__(**traits)

        from traitsui.toolkit import toolkit_object

        EditRenderer = toolkit_object('extra.edit_renderer:EditRenderer')
        self.renderer = EditRenderer()

        self.label = ""

    def get_cell_color(self, object):
        """Returns the cell background color for the column for a specified
        object.
        """

        # Override the parent class to ALWAYS provide the standard color:
        return self.cell_color_

    def is_editable(self, object):
        """Returns whether the column is editable for a specified object."""
        return False
