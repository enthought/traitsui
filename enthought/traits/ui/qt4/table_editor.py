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

from enthought.pyface.timer.api import do_later

from enthought.traits.api import Any, Button, Event, List, HasTraits, \
    Instance, Int, Property, Str, cached_property, on_trait_change

from enthought.traits.ui.api import EnumEditor, InstanceEditor, Group, \
    Handler, Item, Label, TableColumn, TableFilter, UI, View, default_handler, \
    spring
from enthought.traits.ui.editors.table_editor import ToolkitEditorFactory, \
    ReversedList, customize_filter
from enthought.traits.ui.ui_traits import SequenceTypes

from editor import Editor
from table_model import TableModel, SortFilterTableModel

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

    # The table view control associated with the editor:
    table_view = Any

    # A wrapper around the source model which provides filtering and sorting:
    model = Instance(SortFilterTableModel)

    # The table model associated with the editor:
    source_model = Instance(TableModel)

    # The set of columns currently defined on the editor:
    columns = List(TableColumn)

    # The currently selected row(s), column(s), or cell(s).
    selected = Any

    # Current filter object (should be a TableFilter or callable or None):
    filter = Any

    # The indices of the table items currently passing the table filter:
    filtered_indices = List(Int)

    # Current filter summary message
    filter_summary = Str('All items')

    # The event fired when a cell is clicked on:
    click = Event
    
    # The event fired when a cell is double-clicked on:
    dclick = Event

    # The Traits UI associated with the table editor toolbar:
    toolbar_ui = Instance(UI)

    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------

    def init(self, parent):
        """Finishes initializing the editor by creating the underlying toolkit
        widget."""

        factory = self.factory
        self.columns = factory.columns[:]

        # Create the table view and model
        self.table_view = TableView(editor=self)
        self.source_model = TableModel(editor=self)
        self.model = SortFilterTableModel(editor=self)
        self.model.setDynamicSortFilter(True)
        self.model.setSourceModel(self.source_model)
        self.table_view.setModel(self.model)

        # When sorting is enabled, the first column is initially displayed with
        # the triangle indicating it is the sort index, even though no sorting
        # has actually been done. Sort here for UI/model consistency.
        if self.factory.sortable:
            self.model.sort(0, QtCore.Qt.AscendingOrder)

        # Create the toolbar if necessary
        if factory.show_toolbar and len(factory.filters) > 0:
            main_view = QtGui.QWidget()
            layout = QtGui.QVBoxLayout(main_view)
            layout.setMargin(0)
            self.toolbar_ui = self.edit_traits(
                parent = parent, 
                kind = 'subpanel',
                view = View(Group(Item('filter{View}',
                                       editor = factory._filter_editor ),
                                  Item('filter_summary{Results}',
                                       style = 'readonly'),
                                  spring,
                                  orientation='horizontal'),
                            resizable = True))
            self.toolbar_ui.parent = self.ui
            layout.addWidget(self.toolbar_ui.control)
            layout.addWidget(self.table_view)
        else:
            main_view = self.table_view

        # Create auxillary editor and encompassing splitter if necessary
        mode = factory.selection_mode
        if (factory.edit_view == ' ') or not mode in ('row', 'rows'):
            self.control = main_view
        else:
            self.control = QtGui.QSplitter(QtCore.Qt.Vertical)
            self.control.setSizePolicy(QtGui.QSizePolicy.Expanding, 
                                       QtGui.QSizePolicy.Expanding)
            self.control.addWidget(main_view)
            self.control.setStretchFactor(0, 2)

            # Assign the initial object here, so a valid editor will be built
            # when the 'edit_traits' call is made:
            items = self.items()
            selected = None
            if factory.editable and len(items) > 0:
                selected = items[0]
            self.selected = selected

            # Create the row editor below the table view
            editor = InstanceEditor(view=factory.edit_view, kind='subpanel')
            self._ui = self.edit_traits(
                parent = self.control,
                kind = 'subpanel',
                view = View(Item('selected',
                                 style = 'custom',
                                 editor = editor,
                                 show_label = False,
                                 resizable = True,
                                 width = factory.edit_view_width,
                                 height = factory.edit_view_height),
                            resizable = True,
                            handler = factory.edit_view_handler))
            self._ui.parent = self.ui
            self.control.addWidget(self._ui.control)
            self.control.setStretchFactor(1, 1)

            # Reset the object so that the sub-sub-view will pick up the
            # correct history also:
            self.selected = None
            self.selected = selected
        
        # Connect to the mode specific selection handler
        smodel = self.table_view.selectionModel()
        signal = QtCore.SIGNAL('selectionChanged(QItemSelection, QItemSelection)')
        mode_slot = getattr(self, '_on_%s_selection' % factory.selection_mode)
        QtCore.QObject.connect(smodel, signal, mode_slot)

        # Select the first row/column/cell
        self.table_view.setCurrentIndex(self.model.index(0, 0))

        # Connect to the click and double click handlers
        signal = QtCore.SIGNAL('clicked(QModelIndex)')
        QtCore.QObject.connect(self.table_view, signal, self._on_click)
        signal = QtCore.SIGNAL('doubleClicked(QModelIndex)')
        QtCore.QObject.connect(self.table_view, signal, self._on_dclick)

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
        self.sync_value(factory.filter_name, 'filter', 'from')
        self.sync_value(factory.filtered_indices, 'filtered_indices', 'to')

        # Initialize the ItemDelegates for each column
        self._update_columns()

    #---------------------------------------------------------------------------
    #  Disposes of the contents of an editor:
    #---------------------------------------------------------------------------

    def dispose(self):
        """ Disposes of the contents of an editor."""

        # Make sure that the auxillary UIs are properly disposed
        if self.toolbar_ui is not None:
            self.toolbar_ui.dispose()
        if self._ui is not None:
            self._ui.dispose()

        # Remove listeners for any column definitions changing
        self.on_trait_change(self._update_columns, 'columns', remove=True)
        self.on_trait_change(self._update_columns, 'columns_items', remove=True)

    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------

    def update_editor(self):
        """Updates the editor when the object trait changes externally to the
        editor."""

        self.model.reset()

        filtering = len(self.factory.filters) > 0
        if filtering:
            self.update_filtering()
        if filtering or self.factory.sortable:
            self.model.invalidate()

        if self.factory.auto_size:
            self.table_view.resizeColumnsToContents()

        self.set_selection(self.selected)

    #---------------------------------------------------------------------------
    #  Returns the raw list of model objects:
    #---------------------------------------------------------------------------
    
    def items(self):
        """Returns the raw list of model objects."""

        items = self.value
        if not isinstance(items, SequenceTypes):
            items = [ items ]

        if self.factory.reverse:
            items = ReversedList(items)
            
        return items

    #---------------------------------------------------------------------------
    #  Set one or more attributes without notifying the table view:
    #---------------------------------------------------------------------------
    
    def setx(self, **keywords):
        """Set one or more attributes without notifying the table view."""

        self._no_notify = True
        try:
            for name, value in keywords.items():
                setattr(self, name, value)
        finally:
            self._no_notify = False

    #---------------------------------------------------------------------------
    #  Sets the current selection to a set of specified objects:
    #---------------------------------------------------------------------------

    def set_selection(self, objects=[], notify=True):
        """Sets the current selection to a set of specified objects."""

        if not isinstance(objects, SequenceTypes):
            objects = [ objects ]

        mode = self.factory.selection_mode
        indexes = []
        flags = QtGui.QItemSelectionModel.ClearAndSelect

        # In the case of row or column selection, we need a dummy value for the
        # other dimension that has not been filtered.
        source_index = self.model.mapToSource(self.model.index(0, 0))
        source_row, source_column = source_index.row(), source_index.column()

        # Selection mode is 'row' or 'rows'
        if mode.startswith('row'):
            flags |= QtGui.QItemSelectionModel.Rows
            items = self.items()
            for obj in objects:
                try:
                    row = items.index(obj)
                except ValueError:
                    continue
                indexes.append(self.source_model.index(row, source_column))

        # Selection mode is 'column' or 'columns'
        elif mode.startswith('column'):
            flags |= QtGui.QItemSelectionModel.Columns
            for name in objects:
                column = self._column_index_from_name(name)
                if column != -1:
                    indexes.append(self.source_model.index(source_row, column))

        # Selection mode is 'cell' or 'cells'
        else:
            items = self.items()
            for obj, name in objects:
                try:
                    row = items.index(obj)
                except ValueError:
                    continue
                column = self._column_index_from_name(name)
                if column != -1:
                    indexes.append(self.source_model.index(row, column))

        # Perform the selection so that only one signal is emitted
        selection = QtGui.QItemSelection()
        for index in indexes:
            index = self.model.mapFromSource(index)
            if index.isValid():
                selection.select(index, index)
        smodel = self.table_view.selectionModel()
        smodel.blockSignals(not notify)
        if len(selection.indexes()):
            smodel.select(selection, flags)
        else:
            smodel.clear()
        smodel.blockSignals(False)

    #---------------------------------------------------------------------------
    #  Private methods:
    #---------------------------------------------------------------------------

    def _column_index_from_name(self, name):
        """Returns the index of the column with the given name or -1."""

        for i, column in enumerate(self.columns):
            if name == column.name:
                return i

        return -1

    def _customize_filters(self, filter):
        """Allows the user to customize the current set of table filters."""

        filter_editor = TableFilterEditor(editor=self)
        ui = filter_editor.edit_traits()
        if ui.result:
            self.factory.filters = filter_editor.templates
            self.filter = filter_editor.selected_filter
        else:
            self.setx(filter = filter)

    def update_filtering(self):
        """Update the filter summary and the filtered indices."""

        items = self.items()
        num_items = len(items)

        f = self.filter
        if f is None:
            self._filtered_cache = None
            self.filtered_indices = range(num_items)
            self.filter_summary = 'All %i items' % num_items
        else:
            if not callable(f):
                f = f.filter
            self._filtered_cache = fc = [ f(item) for item in items ]
            self.filtered_indices = fi = [ i for i, ok in enumerate(fc) if ok ]
            self.filter_summary = '%i of %i items' % (len(fi), num_items)

    #-- Trait Change Handlers --------------------------------------------------

    def _filter_changed(self, old_filter, new_filter):
        """Handles the current filter being changed."""

        if not self._no_notify:
            if new_filter is customize_filter:
                do_later(self._customize_filters, old_filter)
            else:
                self.update_filtering()
                self.model.invalidate()
                self.set_selection(self.selected)

    def _update_columns(self):
        """Handle the column list being changed."""

        self.table_view.setItemDelegate(TableDelegate(self.table_view))
        for i, column in enumerate(self.columns):
            if column.renderer:
                column.renderer.setParent(self.table_view)
                self.table_view.setItemDelegateForColumn(i, column.renderer)

        self.model.reset()
        self.table_view.resizeColumnsToContents()

    def _selected_changed(self):
        """Handle the selected row/column/cell being changed externally."""
        
        if not self._no_notify:
            self.set_selection(self.selected, notify=False)

    #-- Event Handlers ---------------------------------------------------------
        
    def _on_row_selection(self, added, removed):
        """Handle the row selection being changed."""

        items = self.items()
        indexes = self.table_view.selectionModel().selectedRows()
        if len(indexes):
            index = self.model.mapToSource(indexes[0])
            selected = items[index.row()]
        else:
            selected = None

        self.setx(selected = selected)
        self.ui.evaluate(self.factory.on_select, self.selected)

    def _on_rows_selection(self, added, removed):
        """Handle the rows selection being changed."""

        items = self.items()
        indexes = self.table_view.selectionModel().selectedRows()
        selected = [ items[self.model.mapToSource(index).row()] 
                     for index in indexes ]

        self.setx(selected = selected)
        self.ui.evaluate(self.factory.on_select, self.selected)

    def _on_column_selection(self, added, removed):
        """Handle the column selection being changed."""

        indexes = self.table_view.selectionModel().selectedColumns()
        if len(indexes):
            index = self.model.mapToSource(indexes[0])
            selected = self.columns[index.column()].name
        else:
            selected = ''

        self.setx(selected = selected)
        self.ui.evaluate(self.factory.on_select, self.selected)

    def _on_columns_selection(self, added, removed):
        """Handle the columns selection being changed."""

        indexes = self.table_view.selectionModel().selectedColumns()
        selected = [ self.columns[self.model.mapToSource(index).column()].name 
                     for index in indexes ]

        self.setx(selected = selected)
        self.ui.evaluate(self.factory.on_select, self.selected)

    def _on_cell_selection(self, added, removed):
        """Handle the cell selection being changed."""

        items = self.items()
        indexes = self.table_view.selectionModel().selectedIndexes()
        if len(indexes):
            index = self.model.mapToSource(indexes[0])
            obj = items[index.row()]
            column_name = self.columns[index.column()].name
        else:
            obj = None
            column_name = ''
        selected = (obj, column_name)
        
        self.setx(selected = selected)
        self.ui.evaluate(self.factory.on_select, self.selected)

    def _on_cells_selection(self, added, removed):
        """Handle the cells selection being changed."""

        items = self.items()
        indexes = self.table_view.selectionModel().selectedIndexes()
        selected = []
        for index in indexes:
            index = self.model.mapToSource(index)
            obj = items[index.row()]
            column_name = self.columns[index.column()].name
            selected.append((obj, column_name))

        self.setx(selected = selected)
        self.ui.evaluate(self.factory.on_select, self.selected)

    def _on_click(self, index):
        """Handle a cell being clicked."""
        
        index = self.model.mapToSource(index)
        column = self.columns[index.column()]
        obj = self.items()[index.row()]
        
        # Fire the same event on the editor after mapping it to a model object
        # and column name:
        self.click = (obj, column)

        # Invoke the column's click handler:
        column.on_click(obj)

    def _on_dclick(self, index):
        """Handle a cell being double clicked."""
        
        index = self.model.mapToSource(index)
        column = self.columns[index.column()]
        obj = self.items()[index.row()]
        
        # Fire the same event on the editor after mapping it to a model object
        # and column name:
        self.dclick = (obj, column)

        # Invoke the column's double-click handler:
        column.on_dclick(obj)

# Define the SimpleEditor class.
SimpleEditor = TableEditor

# Define the ReadonlyEditor class.
ReadonlyEditor = TableEditor

#-------------------------------------------------------------------------------
#  Qt widgets that have been configured to behave as expected by Traits UI:
#-------------------------------------------------------------------------------

class TableDelegate(QtGui.QStyledItemDelegate):
    """ A QStyledItemDelegate which fetches Traits UI editors.
    """

    def createEditor(self, parent, option, index):
        """ Reimplemented to return the editor for a given index."""

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

        # Create and initialize the editor 
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

        # Make sure that editors are disposed of correctly
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

        # Configure the row headings.
        vheader = self.verticalHeader()
        vheader.hide()

        # Configure the column headings.
        hheader = self.horizontalHeader()
        if factory.show_column_labels:
            hheader.setHighlightSections(False)
        else:
            hheader.hide()

        # Configure the grid lines.
        self.setShowGrid(factory.show_lines)

        # Configure the selection behaviour.
        self.setCornerButtonEnabled(False)
        behav, mode = self._SELECTION_MAP[factory.selection_mode]
        self.setSelectionBehavior(behav)
        self.setSelectionMode(mode)

        # Configure the editing behavior.
        triggers = (QtGui.QAbstractItemView.DoubleClicked |
                    QtGui.QAbstractItemView.SelectedClicked)
        if factory.edit_on_first_click:
            triggers |= QtGui.QAbstractItemView.CurrentChanged
        self.setEditTriggers(triggers)

        # Configure the sorting behavior.
        if factory.sortable:
            self.setSortingEnabled(True)

    def resizeEvent(self, event):
        """Reimplemented to autoresize columns when the size of the TableEditor
        changes."""

        QtGui.QTableView.resizeEvent(self, event)

        self.resizeColumnsToContents()

    def sizeHintForColumn(self, column_index):
        """Reimplemented to support width specification via TableColumns."""

        editor = self._editor
        column = editor.columns[column_index]
        requested_width = column.get_width()

        # Autosize based on column contents and label. Qt's default
        # implementation of this function does content, we handle the label.
        if editor.factory.auto_size or requested_width < 0:
            base_width = QtGui.QTableView.sizeHintForColumn(self, column_index)

            # Determine what font to use in the calculation
            font = column.get_text_font(None)
            if font is None:
                font = self.font()
                font.setBold(True)
            else:
                font = QtGui.QFont(font)

            # Determine the width of the column label
            text = column.get_label()
            width = QtGui.QFontMetrics(font).width(text)
        
            # Add a margin to the calculated width
            option = QtGui.QStyleOptionHeader()
            option.section = column_index
            margin = self.style().pixelMetric(QtGui.QStyle.PM_HeaderMargin,
                                              option, self)
            width += margin * 2
            
            return max(base_width, width)

        # Set width proportionally
        elif requested_width < 1:
            return int(requested_width * self.viewport().width())
        
        # Set width absolutely
        else:
            return requested_width

#-------------------------------------------------------------------------------
#  Editor for configuring the filters available to a TableEditor:
#-------------------------------------------------------------------------------

class TableFilterEditor(HasTraits):
    """ An editor that manages table filters.
    """

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # TableEditor this editor is associated with
    editor = Instance(TableEditor)

    # The list of filters
    filters = List(TableFilter)

    # The list of available templates from which filters can be created
    templates = Property(List(TableFilter), depends_on='filters')

    # The currently selected filter template
    selected_template = Instance(TableFilter)

    # The currently selected filter
    selected_filter = Instance(TableFilter, allow_none=True)

    # The view to use for the current filter
    selected_filter_view = Property(depends_on='selected_filter')

    # Buttons for add/removing filters
    add_button = Button('New')
    remove_button = Button('Delete')

    # The default view for this editor
    view = View(Group(Group(Group(Item('add_button',
                                       enabled_when='selected_template'),
                                  Item('remove_button',
                                       enabled_when='len(templates) and selected_filter'),
                                  orientation='horizontal',
                                  show_labels=False),
                            Label('Base filter for new filters:'),
                            Item('selected_template',
                                 editor=EnumEditor(name='templates')),
                            Item('selected_filter',
                                 style='custom',
                                 editor=EnumEditor(name='filters', 
                                                   mode='list')),
                            show_labels=False),
                      Item('selected_filter',
                           width=0.75,
                           style='custom',
                           editor=InstanceEditor(view_name='selected_filter_view')),
                      id='TableFilterEditorSplit',
                      show_labels=False,
                      layout='split',
                      orientation='horizontal'),
                id='enthought.traits.ui.qt4.table_editor.TableFilterEditor',
                buttons=[ 'OK', 'Cancel' ],
                kind='livemodal',
                resizable=True, width=800, height=400,
                title='Customize filters')     
        
    #---------------------------------------------------------------------------
    #  Private methods:
    #---------------------------------------------------------------------------

    #-- Trait Property getter/setters ------------------------------------------

    @cached_property
    def _get_selected_filter_view(self):
        view = None
        if self.selected_filter:
            model = self.editor.model
            index = model.mapToSource(model.index(0, 0))
            obj = self.editor.items()[index.row()]
            view = self.selected_filter.edit_view(obj)
        return view

    @cached_property
    def _get_templates(self):
        templates = [ f for f in self.editor.factory.filters if f.template ] 
        templates.extend(self.filters)
        return templates

    #-- Trait Change Handlers --------------------------------------------------

    def _editor_changed(self):
        self.filters = [ f.clone_traits() for f in self.editor.factory.filters 
                         if not f.template ]
        self.selected_template = self.templates[0]

    def _add_button_fired(self):
        """ Create a new filter based on the selected template and select it.
        """
        new_filter = self.selected_template.clone_traits()
        new_filter.template = False
        new_filter.name = new_filter._name = 'New filter'
        self.filters.append(new_filter)
        self.selected_filter = new_filter
    
    def _remove_button_fired(self):
        """ Delete the currently selected filter.
        """
        if self.selected_template == self.selected_filter:
            self.selected_template = self.templates[0]

        index = self.filters.index(self.selected_filter)        
        del self.filters[index]
        if index < len(self.filters):
            self.selected_filter = self.filters[index]
        else:
            self.selected_filter = None

    @on_trait_change('selected_filter:name')
    def _update_filter_list(self):
        """ A hack to make the EnumEditor watching the list of filters refresh
            their text when the name of the selected filter changes.
        """
        filters = self.filters
        self.filters = []
        self.filters = filters
