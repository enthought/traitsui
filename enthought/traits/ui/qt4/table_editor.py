#------------------------------------------------------------------------------
# Copyright (c) 2008, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD license.
# However, when used with the GPL version of PyQt the additional terms described
# in the PyQt GPL exception also apply.
#
# Author: Riverbank Computing Limited
#------------------------------------------------------------------------------

""" Defines the table editor for the PyQt user interface toolkit.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from PyQt4 import QtCore, QtGui

from enthought.traits.api \
    import List, Instance, Any, Event
     
# FIXME: ToolkitEditorFactory is a proxy class defined here just for backward
# compatibility. The class has been moved to the 
# enthought.traits.ui.editors.table_editor file.
from enthought.traits.ui.editors.table_editor \
    import ToolkitEditorFactory

from enthought.traits.ui.table_column \
    import TableColumn

from enthought.traits.ui.ui_traits \
    import SequenceTypes

from editor \
    import Editor

from table_model \
    import TableModel


#-------------------------------------------------------------------------------
#  'TableEditor' class:
#-------------------------------------------------------------------------------

class TableEditor(Editor):
    """ Editor that presents data in a table. Optionally, tables can have
        a set of filters that reduce the set of data displayed, according to 
        their criteria.
    """

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # The set of columns currently defined on the editor:
    columns = List(TableColumn)

    # The table model associated with the editor:
    model = Instance(TableModel)

    # The currently selected row(s), column(s), or cell(s).
    selected = Any

    # The event fired when a cell is clicked on:
    click = Event
    
    # The event fired when a cell is double-clicked on:
    dclick = Event

    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------

    def init(self, parent):
        """Finishes initializing the editor by creating the underlying toolkit
        widget."""

        factory = self.factory
        self.columns = factory.columns[:]
        self.model = TableModel(editor=self)

        self.control = _TableView(editor=self)
        smodel = self.control.selectionModel()

        # Connect to the mode specific selection handler.
        mode = factory.selection_mode
        mode_slot = getattr(self, '_on_%s_selection' % mode)
        signal = QtCore.SIGNAL('selectionChanged(QItemSelection, QItemSelection)')
        QtCore.QObject.connect(smodel, signal, mode_slot)

        is_list = (mode in ('rows', 'columns', 'cells'))
        self.sync_value(factory.selected, 'selected', is_list=is_list)

        # Select the first row/column/cell.
        self.control.setCurrentIndex(self.model.createIndex(0, 0))

        # Connect to the click and double click handlers
        signal = QtCore.SIGNAL('clicked(QModelIndex)')
        QtCore.QObject.connect(self.control, signal, self._on_click)
        self.sync_value(factory.click, 'click', 'to')

        signal = QtCore.SIGNAL('doubleClicked(QModelIndex)')
        QtCore.QObject.connect(self.control, signal, self._on_dclick)
        self.sync_value(factory.dclick, 'dclick', 'to')

    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------

    def update_editor(self):
        """Updates the editor when the object trait changes externally to the
        editor."""

        self.model.reset()

    #---------------------------------------------------------------------------
    #  Helper methods for TableModel:
    #---------------------------------------------------------------------------

    def items(self):
        """Returns the raw sequence of model objects."""

        items = self.value
        if not isinstance(items, SequenceTypes):
            items = [items]

        return items

    #---------------------------------------------------------------------------
    #  Private methods:
    #---------------------------------------------------------------------------

    def _on_row_selection(self, new, old):
        """Handle the row selection being changed."""

        items = self.items()
        indexes = new.indexes()

        rownr = indexes[0].row()
        self.selected = items[rownr]

        self.ui.evaluate(self.factory.on_select, self.selected)

    def _on_rows_selection(self, new, old):
        """Handle the rows selection being changed."""

        items = self.items()
        indexes = new.indexes()

        rownr_first = indexes[0].row()
        rownr_last = indexes[-1].row()
        self.selected = items[rownr_first:rownr_last + 1]

        self.ui.evaluate(self.factory.on_select, self.selected)

    def _on_column_selection(self, new, old):
        """Handle the column selection being changed."""

        indexes = new.indexes()

        colnr = indexes[0].column()
        self.selected = self.columns[colnr].get_label()

        self.ui.evaluate(self.factory.on_select, self.selected)

    def _on_columns_selection(self, new, old):
        """Handle the columns selection being changed."""

        indexes = new.indexes()

        colnr_first = indexes[0].column()
        colnr_last = indexes[-1].column()
        col_range = self.columns[colnr_first:colnr_last + 1]
        self.selected = [col.get_label() for col in col_range]

        self.ui.evaluate(self.factory.on_select, self.selected)

    def _on_cell_selection(self, new, old):
        """Handle the cell selection being changed."""

        items = self.items()
        indexes = new.indexes()

        rownr = indexes[0].row()
        colnr = indexes[0].column()
        self.selected = self.columns[colnr].get_value(items[rownr])

        self.ui.evaluate(self.factory.on_select, self.selected)

    def _on_cells_selection(self, new, old):
        """Handle the cells selection being changed."""

        items = self.items()
        indexes = new.indexes()

        self.selected = [self.columns[mi.row()].get_value(items[mi.row()]) for mi in indexes]

        self.ui.evaluate(self.factory.on_select, self.selected)

    def _on_click(self, index):
        """Handle a cell being clicked."""
        
        column = self.columns[index.column()]
        object = self.items()[index.row()]
        
        # Fire the same event on the editor after mapping it to a model object
        # and column name:
        self.click = (object, column)

        # Invoke the column's click handler:
        column.on_click(object)

    def _on_dclick(self, index):
        """Handle a cell being double clicked."""
        
        column = self.columns[index.column()]
        object = self.items()[index.row()]
        
        # Fire the same event on the editor after mapping it to a model object
        # and column name:
        self.dclick = (object, column)

        # Invoke the column's double-click handler:
        column.on_dclick(object)


#-------------------------------------------------------------------------------
#  '_TableView' class:
#-------------------------------------------------------------------------------

class _TableView(QtGui.QTableView):
    """A QTableView configured to behave as expected by TraitsUI."""

    _SELECTION_MAP = {
        'row':      (QtGui.QAbstractItemView.SelectRows,
                            QtGui.QAbstractItemView.SingleSelection),
        'rows':     (QtGui.QAbstractItemView.SelectRows,
                            QtGui.QAbstractItemView.ExtendedSelection),
        'column':   (QtGui.QAbstractItemView.SelectColumns,
                            QtGui.QAbstractItemView.SingleSelection),
        'columns':  (QtGui.QAbstractItemView.SelectColumns,
                            QtGui.QAbstractItemView.ExtendedSelection),
        'cell':     (QtGui.QAbstractItemView.SelectItems,
                            QtGui.QAbstractItemView.SingleSelection),
        'cells':    (QtGui.QAbstractItemView.SelectItems,
                            QtGui.QAbstractItemView.ExtendedSelection)
    }

    def __init__(self, editor):
        """Initialise the object."""

        QtGui.QTableView.__init__(self)

        self._editor = editor

        factory = editor.factory

        self.setModel(editor.model)
        self.verticalHeader().hide()

        # Configure the column headings.
        hheader = self.horizontalHeader()

        if factory.show_column_labels:
            hheader.setHighlightSections(False)
            hheader.setStretchLastSection(True)
        else:
            hheader.hide()

        self.resizeColumnsToContents()

        # Configure the selection behaviour.
        behav, mode = self._SELECTION_MAP[factory.selection_mode]
        self.setSelectionBehavior(behav)
        self.setSelectionMode(mode)

    def sizeHint(self):
        """Reimplemented to support auto_size."""

        sh = QtGui.QTableView.sizeHint(self)

        if self._editor.factory.auto_size:
            w = 0

            for colnr in range(len(self._editor.columns)):
                w += self.sizeHintForColumn(colnr)

            sh.setWidth(w)

        return sh


# Define the SimpleEditor class.
SimpleEditor = TableEditor

# Define the ReadonlyEditor class.
ReadonlyEditor = TableEditor
