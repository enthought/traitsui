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

from enthought.traits.api import List, Instance, Any, Event
from enthought.traits.ui.api import UI, default_handler
     
# FIXME: ToolkitEditorFactory is a proxy class defined here just for backward
# compatibility. The class has been moved to the 
# enthought.traits.ui.editors.table_editor file.
from enthought.traits.ui.editors.table_editor import ToolkitEditorFactory

from enthought.traits.ui.table_column import TableColumn
from enthought.traits.ui.ui_traits import SequenceTypes

from editor import Editor
from table_model import TableModel

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

        self.control = TableView(editor=self)

        # Connect to the mode specific selection handler
        mode = factory.selection_mode
        mode_slot = getattr(self, '_on_%s_selection' % mode)
        signal = QtCore.SIGNAL('selectionChanged(QItemSelection, QItemSelection)')
        QtCore.QObject.connect(self.control.selectionModel(), signal, mode_slot)

        # Select the first row/column/cell
        self.control.setCurrentIndex(self.model.createIndex(0, 0))

        # Connect to the click and double click handlers
        signal = QtCore.SIGNAL('clicked(QModelIndex)')
        QtCore.QObject.connect(self.control, signal, self._on_click)
        signal = QtCore.SIGNAL('doubleClicked(QModelIndex)')
        QtCore.QObject.connect(self.control, signal, self._on_dclick)

        # Set up listeners for any column definitions changing
        self.on_trait_change(self._update_columns, 'columns', dispatch='ui')
        self.on_trait_change(self._update_columns, 'columns_items', 
                             dispatch='ui')

        # Set up the required externally synchronized traits
        is_list = (mode in ('rows', 'columns', 'cells'))
        self.sync_value(factory.click, 'click', 'to')
        self.sync_value(factory.dclick, 'dclick', 'to')
        self.sync_value(factory.columns_name, 'columns', 'from', is_list=True)
        self.sync_value(factory.selected, 'selected', is_list=is_list)

        # Initialize the ItemDelegates for each column
        self._update_columns()

    #---------------------------------------------------------------------------
    #  Disposes of the contents of an editor:
    #---------------------------------------------------------------------------

    def dispose(self):
        """ Disposes of the contents of an editor."""

        # Remove listeners for any column definitions changing
        self.on_trait_change(self._update_columns, 'columns', remove=True )
        self.on_trait_change(self._update_columns, 'columns_items', remove=True)

    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------

    def update_editor(self):
        """Updates the editor when the object trait changes externally to the
        editor."""

        self.model.reset()
        if self.factory.auto_size:
            self.control.resizeColumnsToContents()

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

    def _update_columns(self):
        """ Handle the column list being changed."""

        self.control.setItemDelegate(TableDelegate(self.control))
        for i, column in enumerate(self.columns):
            if column.renderer:
                column.renderer.setParent(self.control)
                self.control.setItemDelegateForColumn(i, column.renderer)

        self.model.reset()
        self.control.resizeColumnsToContents()
        
    def _on_row_selection(self, added, removed):
        """Handle the row selection being changed."""

        items = self.items()
        indexes = self.control.selectionModel().selectedRows()

        if len(indexes):
            self.selected = items[indexes[0].row()]
        else:
            self.selected = None

        self.ui.evaluate(self.factory.on_select, self.selected)

    def _on_rows_selection(self, added, removed):
        """Handle the rows selection being changed."""

        items = self.items()
        indexes = self.control.selectionModel().selectedRows()

        self.selected = [ items[index.row()] for index in indexes ]

        self.ui.evaluate(self.factory.on_select, self.selected)

    def _on_column_selection(self, added, removed):
        """Handle the column selection being changed."""

        indexes = self.control.selectionModel().selectedColumns()

        if len(indexes):
            self.selected = self.columns[indexes[0].column()].name
        else:
            self.selected = ''

        self.ui.evaluate(self.factory.on_select, self.selected)

    def _on_columns_selection(self, added, removed):
        """Handle the columns selection being changed."""

        indexes = self.control.selectionModel().selectedColumns()

        self.selected = [ self.columns[index.column()].name 
                          for index in indexes ]

        self.ui.evaluate(self.factory.on_select, self.selected)

    def _on_cell_selection(self, added, removed):
        """Handle the cell selection being changed."""

        items = self.items()
        indexes = self.control.selectionModel().selectedIndexes()

        if len(indexes):
            obj = items[indexes[0].row()]
            column_name = self.columns[indexes[0].column()].name
        else:
            obj = None
            column_name = ''
        self.selected = (obj, column_name)

        self.ui.evaluate(self.factory.on_select, self.selected)

    def _on_cells_selection(self, added, removed):
        """Handle the cells selection being changed."""

        items = self.items()
        indexes = self.control.selectionModel().selectedIndexes()

        selected = []
        for index in indexes:
            obj = items[index.row()]
            column_name = self.columns[index.column()].name
            selected.append((obj, column_name))
        self.selected = selected

        self.ui.evaluate(self.factory.on_select, self.selected)

    def _on_click(self, index):
        """Handle a cell being clicked."""
        
        column = self.columns[index.column()]
        obj = self.items()[index.row()]
        
        # Fire the same event on the editor after mapping it to a model object
        # and column name:
        self.click = (obj, column)

        # Invoke the column's click handler:
        column.on_click(obj)

    def _on_dclick(self, index):
        """Handle a cell being double clicked."""
        
        column = self.columns[index.column()]
        obj = self.items()[index.row()]
        
        # Fire the same event on the editor after mapping it to a model object
        # and column name:
        self.dclick = (obj, column)

        # Invoke the column's double-click handler:
        column.on_dclick(obj)

#-------------------------------------------------------------------------------
#  Qt widgets that have been configured to behave as expected by Traits UI:
#-------------------------------------------------------------------------------

class TableDelegate(QtGui.QStyledItemDelegate):
    """ A QStyledItemDelegate which fetches Traits UI editors.
    """

    def createEditor(self, parent, option, index):
        """ Return the editor for a given index."""

        table_editor = index.model()._editor
        column = table_editor.columns[index.column()]
        obj = table_editor.items()[index.row()]

        factory = column.get_editor(obj)
        style = column.get_style(obj)
        if factory is None:
            return None

        target, name = column.target_name(obj)
        handler = default_handler()
        if table_editor.ui.context is None:
            ui = UI(handler=handler)
        else:
            context = table_editor.ui.context.copy()
            context['table_editor_object'] = context['object']
            context['object'] = target
            ui = UI(handler=handler, context=context)

        factory_method = getattr(factory, style+'_editor')
        editor = factory_method(ui, target, name, '', parent)
        editor.prepare(parent)

        control = editor.control
        control.setParent(parent)
        
        # Required for QMouseEvents to propagate to the widget
        control.setFocusPolicy(QtCore.Qt.StrongFocus)

        # The table view's background will shine through unless the editor
        # paints its own background
        control.setAutoFillBackground(True)

        # Make sure that editors are disposed up correctly
        QtCore.QObject.connect(control, QtCore.SIGNAL('destroyed()'),
                               lambda: editor.dispose())

        return control

class TableView(QtGui.QTableView):
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

        # Configure the row headings.
        self.verticalHeader().hide()

        # Configure the column headings.
        hheader = self.horizontalHeader()
        hheader.setStretchLastSection(True)
        if factory.show_column_labels:
            hheader.setHighlightSections(False)
        else:
            hheader.hide()

        # Configure the selection behaviour.
        behav, mode = self._SELECTION_MAP[factory.selection_mode]
        self.setSelectionBehavior(behav)
        self.setSelectionMode(mode)

        # Configure the editing behavior.
        triggers = (QtGui.QAbstractItemView.DoubleClicked |
                    QtGui.QAbstractItemView.SelectedClicked)
        if factory.edit_on_first_click:
            triggers |= QtGui.QAbstractItemView.CurrentChanged
        self.setEditTriggers(triggers)

    def sizeHint(self):
        """Reimplemented to support auto_size."""

        sh = QtGui.QTableView.sizeHint(self)

        if self._editor.factory.auto_size:
            w = 0
            for colnr in range(len(self._editor.columns)):
                w += self.sizeHintForColumn(colnr)
            sh.setWidth(w)

        return sh

    def sizeHintForColumn(self, column):
        """ Reimplemented to include column labels in the calculation.
        """
        base_width = QtGui.QTableView.sizeHintForColumn(self, column)

        # Determine what font to use in the calculation
        variant = self.model().headerData(column, QtCore.Qt.Horizontal,
                                          QtCore.Qt.FontRole)
        if variant.isValid():
            font = variant.toPyObject()
        else:
            font = self.font()
        font.setBold(True)

        # Determine the width of the column label
        text = self.model().headerData(column, QtCore.Qt.Horizontal,
                                       QtCore.Qt.DisplayRole).toString()
        width = QtGui.QFontMetrics(font).width(text)
        
        # Add a margin to the calculated width
        option = QtGui.QStyleOptionHeader()
        option.section = column
        margin = self.style().pixelMetric(QtGui.QStyle.PM_HeaderMargin,
                                          option, self)
        width += margin * 2
                                          
        return max(base_width, width)

# Define the SimpleEditor class.
SimpleEditor = TableEditor

# Define the ReadonlyEditor class.
ReadonlyEditor = TableEditor
