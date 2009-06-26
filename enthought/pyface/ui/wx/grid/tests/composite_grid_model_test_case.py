import unittest

from enthought.pyface.ui.wx.grid.api \
     import CompositeGridModel, GridRow, GridColumn, SimpleGridModel


class CompositeGridModelTestCase( unittest.TestCase ):

    def setUp(self):

        self.model_1 = SimpleGridModel(data=[[1,2],[3,4]],
                                       rows=[GridRow(label='foo'),
                                             GridRow(label='bar')],
                                       columns=[GridColumn(label='cfoo'),
                                                GridColumn(label='cbar')]
                                       )
        self.model_2 = SimpleGridModel(data=[[3,4,5],[6,7,8]],
                                       rows=[GridRow(label='baz'),
                                             GridRow(label='bat')],
                                       columns=[GridColumn(label='cfoo_2'),
                                                GridColumn(label='cbar_2'),
                                                GridColumn(label='cbaz_2')]
                                       )

        self.model = CompositeGridModel(data=[self.model_1, self.model_2])

        return

    def test_get_column_count(self):

        column_count_1 = self.model_1.get_column_count()
        column_count_2 = self.model_2.get_column_count()

        self.assertEqual(self.model.get_column_count(),
                         column_count_1 + column_count_2)

        return

    def test_get_row_count(self):

        self.assertEqual(self.model.get_row_count(), 2)

        return

    def test_get_row_name(self):

        # Regardless of the rows specified in the composed models, the
        # composite model returns its own rows.
        self.assertEqual(self.model.get_row_name(0), '1')
        self.assertEqual(self.model.get_row_name(1), '2')

        return

    def test_get_column_name(self):

        self.assertEqual(self.model.get_column_name(0), 'cfoo')
        self.assertEqual(self.model.get_column_name(1), 'cbar')
        self.assertEqual(self.model.get_column_name(2), 'cfoo_2')
        self.assertEqual(self.model.get_column_name(3), 'cbar_2')
        self.assertEqual(self.model.get_column_name(4), 'cbaz_2')

        return

    def test_get_value(self):

        self.assertEqual(self.model.get_value(0,0), 1)
        self.assertEqual(self.model.get_value(0,1), 2)
        self.assertEqual(self.model.get_value(0,2), 3)
        self.assertEqual(self.model.get_value(0,3), 4)
        self.assertEqual(self.model.get_value(0,4), 5)
        self.assertEqual(self.model.get_value(1,0), 3)
        self.assertEqual(self.model.get_value(1,1), 4)
        self.assertEqual(self.model.get_value(1,2), 6)
        self.assertEqual(self.model.get_value(1,3), 7)
        self.assertEqual(self.model.get_value(1,4), 8)

        return

    def test_is_cell_empty(self):

        rows = self.model.get_row_count()
        columns = self.model.get_column_count()

        self.assertEqual(self.model.is_cell_empty(0,0), False,
                         "Cell (0,0) should not be empty.")
        self.assertEqual(self.model.is_cell_empty(rows,0), True,
                         "Cell below the table should be empty.")
        self.assertEqual(self.model.is_cell_empty(0,columns), True,
                         "Cell right of the table should be empty.")
        self.assertEqual(self.model.is_cell_empty(rows,columns), True,
                         "Cell below and right of table should be empty.")

        return


#### EOF ######################################################################
