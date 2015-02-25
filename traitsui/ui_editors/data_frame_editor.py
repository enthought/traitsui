#  Copyright (c) 2015, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt

from __future__ import absolute_import

from traits.api import Bool, Enum, Font, Instance, List, Property, Str, Tuple

from traitsui.basic_editor_factory import BasicEditorFactory
from traitsui.editors.tabular_editor import TabularEditor
from traitsui.item import Item
from traitsui.tabular_adapter import TabularAdapter
from traitsui.toolkit import toolkit_object
from traitsui.ui_editor import UIEditor
from traitsui.view import View


class DataFrameAdapter(TabularAdapter):
    """ Generic tabular adapter for data frames
    """

    #: The text to use for a generic entry.
    text = Property

    #: The alignment for each cell
    alignment = Property(Enum('left', 'center', 'right'))

    #: The text to use for a row index.
    index_text = Property

    #: The alignment to use for a row index.
    index_alignment = Property

    def _get_index_alignment(self):
        import numpy as np

        index = getattr(self.object, self.name).index
        if np.issubdtype(index.dtype, np.number):
            return 'right'
        else:
            return 'left'

    def _get_alignment(self):
        import numpy as np

        column = getattr(self.object, self.name)[self.column_id]
        if np.issubdtype(column.dtype, np.number):
            return 'right'
        else:
            return 'left'

    def _get_content(self):
        return getattr(self.object, self.name)[self.column_id][self.row]

    def _get_text ( self ):
        format = self.get_format(self.object, self.name, self.row, self.column)
        return format % self.get_content(self.object, self.name, self.row,
                                         self.column )

    def _set_text(self, value):
        column = getattr(self.object, self.name)[self.column_id]
        dtype = column.dtype
        value = dtype.type(value)
        column.iloc[self.row] = value

    def _get_index_text(self):
        return str(self.item.index[0])

    def _set_index_text(self, value):
        index = getattr(self.object, self.name).index
        dtype = index.dtype
        value = dtype.type(value)
        index.values[self.row] = value

    #-- Adapter methods that are not sensitive to item type --------------------

    def get_item(self, object, trait, row):
        """ Override the base implementation to work with DataFrames """
        return getattr(object, trait).iloc[row:row+1]

    def delete(self, object, trait, row):
        """ Override the base implementation to work with DataFrames

        Unavoidably does a copy of the data, setting the trait with the new
        value.
        """
        import pandas as pd

        df = getattr(object, trait)
        if 0 < row < len(df)-1:
            new_df = pd.concat([df.iloc[:row, :], df.iloc[row+1:, :]])
        elif row == 0:
            new_df = df.iloc[row+1:, :]
        else:
            new_df = df.iloc[:row, :]
        setattr(object, trait, new_df)

    def insert(self, object, trait, row, value):
        """ Override the base implementation to work with DataFrames

        Unavoidably does a copy of the data, setting the trait with the new
        value.
        """
        import pandas as pd

        df = getattr(object, trait)
        if 0 < row < len(df)-1:
            new_df = pd.concat([df.iloc[:row, :], value, df.iloc[row:, :]])
        elif row == 0:
            new_df = pd.concat([value, df])
        else:
            new_df = pd.concat([df, value])
        setattr(object, trait, new_df)


class _DataFrameEditor(UIEditor):
    """ TraitsUI-based editor implementation for data frames """

    # Indicate that the editor is scrollable/resizable:
    scrollable = True

    # Should column titles be displayed:
    show_titles = Bool(True)

    # The tabular adapter being used for the editor view:
    adapter = Instance(DataFrameAdapter)

    #-- Private Methods ------------------------------------------------------

    def _data_frame_view(self):
        """ Return the view used by the editor.
        """
        return View(
            Item(
                'object.object.' + self.name,
                id = 'tabular_editor',
                show_label = False,
                editor = TabularEditor(
                    show_titles=self.show_titles,
                    editable=True,
                    adapter=self.adapter,
                    operations=['delete', 'insert', 'append', 'edit', 'move']
                )
            ),
            id = 'array_view_editor',
            resizable = True
        )

    def init_ui ( self, parent ):
        """ Creates the Traits UI for displaying the array.
        """
        factory = self.factory
        self.show_titles = (factory.title_map != [])
        if self.show_titles:
            columns = []
            for column in factory.title_map:
                if isinstance(column, basestring):
                    title = column
                    column_id = column
                else:
                    title, column_id = column
                if column_id not in self.value.columns:
                    continue
                columns.append((title, column_id))
        else:
            columns = [(column_id, column_id)
                       for column_id in self.value.columns]

        if factory.show_index:
            columns.insert(0, (self.value.index.name, 'index'))

        self.adapter = DataFrameAdapter(
            columns=columns,
            format=factory.format,
            font=factory.font
        )

        return self.edit_traits(
            view='_data_frame_view',
            parent=parent,
            kind='subpanel'
        )


class DataFrameEditor(BasicEditorFactory):
    """ Editor factory for basic data frame editor """

    #: The editor implementation class.
    klass = Property

    #: Should an index column be displayed.
    show_index = Bool(True)

    #: Optional list of either column ID or pairs of (column title, column ID).
    title_map = List()

    #: The format used to display each array element.
    format = Str('%s')

    #: Whether or not the entries can be edited.
    editable = Bool(False)

    #: The font to use for displaying each array element.
    font = Font('Courier 10')

    def _get_klass( self ):
        """ The class used to construct editor objects.
        """
        return toolkit_object('data_frame_editor:_DataFrameEditor')
