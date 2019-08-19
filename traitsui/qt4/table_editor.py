#------------------------------------------------------------------------------
# Copyright (c) 2008, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license.
#
# When used with the GPL version of PyQt the additional terms described
# in the PyQt GPL exception also apply.
#
# Author: Riverbank Computing Limited
#------------------------------------------------------------------------------

""" Defines the table editor for the PyQt user interface toolkit.
"""

#-------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------

from __future__ import absolute_import

from pyface.qt import QtCore, QtGui
from pyface.image_resource import ImageResource
from pyface.timer.api import do_later
from pyface.ui_traits import Image
from traits.api import Any, Bool, Button, Event, List, HasTraits, \
    Instance, Int, Property, Str, cached_property, on_trait_change

from traitsui.api import EnumEditor, InstanceEditor, Group, \
    Item, Label, ObjectColumn, TableColumn, TableFilter, UI, View, \
    default_handler, spring
from traitsui.editors.table_editor import BaseTableEditor, \
    ReversedList, customize_filter
from traitsui.ui_traits import SequenceTypes

from .editor import Editor
from .table_model import TableModel, SortFilterTableModel
import six


is_qt5 = QtCore.__version_info__ >= (5,)

if is_qt5:
    def set_qheader_section_resize_mode(header):
        return header.setSectionResizeMode
else:
    def set_qheader_section_resize_mode(header):
        return header.setResizeMode

#-------------------------------------------------------------------------
#  'TableEditor' class:
#-------------------------------------------------------------------------


class TableEditor(Editor, BaseTableEditor):
    """ Editor that presents data in a table. Optionally, tables can have
        a set of filters that reduce the set of data displayed, according to
        their criteria.
    """

    #-------------------------------------------------------------------------
    #  Trait definitions:
    #-------------------------------------------------------------------------

    # The table view control associated with the editor:
    table_view = Any

    def _table_view_default(self):
        return TableView(editor=self)

    # A wrapper around the source model which provides filtering and sorting:
    model = Instance(SortFilterTableModel)

    def _model_default(self):
        return SortFilterTableModel(editor=self)

    # The table model associated with the editor:
    source_model = Instance(TableModel)

    def _source_model_default(self):
        return TableModel(editor=self)

    # The set of columns currently defined on the editor:
    columns = List(TableColumn)

    # The currently selected row(s), column(s), or cell(s).
    selected = Any

    # The current selected row
    selected_row = Property(Any, depends_on='selected')

    selected_indices = Property(Any, depends_on='selected')

    # Current filter object (should be a TableFilter or callable or None):
    filter = Any

    # The indices of the table items currently passing the table filter:
    filtered_indices = List(Int)

    # Current filter summary message
    filter_summary = Str('All items')

    # Update the filtered contents.
    update_filter = Event()

    # The event fired when a cell is clicked on:
    click = Event

    # The event fired when a cell is double-clicked on:
    dclick = Event

    # The Traits UI associated with the table editor toolbar:
    toolbar_ui = Instance(UI)

    # The context menu associated with empty space in the table
    empty_menu = Instance(QtGui.QMenu)

    # The context menu associated with the vertical header
    header_menu = Instance(QtGui.QMenu)

    # The context menu actions for moving rows up and down
    header_menu_up = Instance(QtGui.QAction)
    header_menu_down = Instance(QtGui.QAction)

    # The index of the row that was last right clicked on its vertical header
    header_row = Int

    # Whether to auto-size the columns or not.
    auto_size = Bool(False)

    # Dictionary mapping image names to QIcons
    images = Any({})

    # Dictionary mapping ImageResource objects to QIcons
    image_resources = Any({})

    # An image being converted:
    image = Image

    #-------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #-------------------------------------------------------------------------

    def init(self, parent):
        """Finishes initializing the editor by creating the underlying toolkit
        widget."""

        factory = self.factory
        self.filter = factory.filter

        columns = factory.columns[:]
        if (len(columns) == 0) and (len(self.value) > 0):
            columns = [ObjectColumn(name=name)
                       for name in self.value[0].editable_traits()]
        self.columns = columns

        if factory.table_view_factory is not None:
            self.table_view = factory.table_view_factory(editor=self)
        if factory.source_model_factory is not None:
            self.source_model = factory.source_model_factory(editor=self)
        if factory.model_factory is not None:
            self.model = factory.model_factory(editor=self)

        # Create the table view and model
        self.model.setDynamicSortFilter(True)
        self.model.setSourceModel(self.source_model)
        self.table_view.setModel(self.model)

        # Create the vertical header context menu and connect to its signals
        self.header_menu = QtGui.QMenu(self.table_view)
        insertable = factory.row_factory is not None
        if factory.editable:
            if insertable:
                action = self.header_menu.addAction('Insert new item')
                action.triggered.connect(self._on_context_insert)
            if factory.deletable:
                action = self.header_menu.addAction('Delete item')
                action.triggered.connect(self._on_context_remove)
        if factory.reorderable:
            if factory.editable and (insertable or factory.deletable):
                self.header_menu.addSeparator()
            self.header_menu_up = self.header_menu.addAction('Move item up')
            self.header_menu_up.triggered.connect(self._on_context_move_up)
            self.header_menu_down = self.header_menu.addAction(
                'Move item down')
            self.header_menu_down.triggered.connect(self._on_context_move_down)

        # Create the empty space context menu and connect its signals
        self.empty_menu = QtGui.QMenu(self.table_view)
        action = self.empty_menu.addAction('Add new item')
        action.triggered.connect(self._on_context_append)

        # When sorting is enabled, the first column is initially displayed with
        # the triangle indicating it is the sort index, even though no sorting
        # has actually been done. Sort here for UI/model consistency.
        if self.factory.sortable and not self.factory.reorderable:
            self.model.sort(0, QtCore.Qt.AscendingOrder)

        # Connect to the mode specific selection handler and select the first
        # row/column/cell. Do this before creating the edit_view to make sure
        # that it has a valid item to use when constructing its view.
        smodel = self.table_view.selectionModel()
        mode_slot = getattr(self, '_on_%s_selection' % factory.selection_mode)
        smodel.selectionChanged.connect(mode_slot)
        self.table_view.setCurrentIndex(self.model.index(0, 0))

        # Create the toolbar if necessary
        if factory.show_toolbar and len(factory.filters) > 0:
            main_view = QtGui.QWidget()
            layout = QtGui.QVBoxLayout(main_view)
            layout.setContentsMargins(0, 0, 0, 0)
            self.toolbar_ui = self.edit_traits(
                parent=parent,
                kind='subpanel',
                view=View(Group(Item('filter{View}',
                                     editor=factory._filter_editor),
                                Item('filter_summary{Results}',
                                     style='readonly'),
                                spring,
                                orientation='horizontal'),
                          resizable=True))
            self.toolbar_ui.parent = self.ui
            layout.addWidget(self.toolbar_ui.control)
            layout.addWidget(self.table_view)
        else:
            main_view = self.table_view

        # Create auxiliary editor and encompassing splitter if necessary
        mode = factory.selection_mode
        if (factory.edit_view == ' ') or mode not in {'row', 'rows'}:
            self.control = main_view
        else:
            if factory.orientation == 'horizontal':
                self.control = QtGui.QSplitter(QtCore.Qt.Horizontal)
            else:
                self.control = QtGui.QSplitter(QtCore.Qt.Vertical)
            self.control.setSizePolicy(QtGui.QSizePolicy.Expanding,
                                       QtGui.QSizePolicy.Expanding)
            self.control.addWidget(main_view)
            self.control.setStretchFactor(0, 2)

            # Create the row editor below the table view
            editor = InstanceEditor(view=factory.edit_view, kind='subpanel')
            self._ui = self.edit_traits(
                parent=self.control,
                kind='subpanel',
                view=View(Item('selected_row',
                               style='custom',
                               editor=editor,
                               show_label=False,
                               resizable=True,
                               width=factory.edit_view_width,
                               height=factory.edit_view_height),
                          resizable=True,
                          handler=factory.edit_view_handler))
            self._ui.parent = self.ui
            self.control.addWidget(self._ui.control)
            self.control.setStretchFactor(1, 1)

        # Connect to the click and double click handlers
        self.table_view.clicked.connect(self._on_click)
        self.table_view.doubleClicked.connect(self._on_dclick)

        # Make sure we listen for 'items' changes as well as complete list
        # replacements
        self.context_object.on_trait_change(
            self.update_editor, self.extended_name + '_items', dispatch='ui')

        # Listen for changes to traits on the objects in the list
        self.context_object.on_trait_change(
            self.refresh_editor, self.extended_name + '.-', dispatch='ui')

        # Listen for changes on column definitions
        self.on_trait_change(self._update_columns, 'columns', dispatch='ui')
        self.on_trait_change(self._update_columns, 'columns_items',
                             dispatch='ui')

        # Set up the required externally synchronized traits
        is_list = (mode in ('rows', 'columns', 'cells'))
        self.sync_value(factory.click, 'click', 'to')
        self.sync_value(factory.dclick, 'dclick', 'to')
        self.sync_value(factory.columns_name, 'columns', is_list=True)
        self.sync_value(factory.selected, 'selected', is_list=is_list)
        self.sync_value(
            factory.selected_indices,
            'selected_indices',
            is_list=is_list)
        self.sync_value(factory.filter_name, 'filter', 'from')
        self.sync_value(factory.filtered_indices, 'filtered_indices', 'to')
        self.sync_value(factory.update_filter_name, 'update_filter', 'from')

        self.auto_size = self.factory.auto_size

        # Initialize the ItemDelegates for each column
        self._update_columns()

    #-------------------------------------------------------------------------
    #  Disposes of the contents of an editor:
    #-------------------------------------------------------------------------

    def dispose(self):
        """ Disposes of the contents of an editor."""

        # Make sure that the auxiliary UIs are properly disposed
        if self.toolbar_ui is not None:
            self.toolbar_ui.dispose()
        if self._ui is not None:
            self._ui.dispose()

        # Remove listener for 'items' changes on object trait
        self.context_object.on_trait_change(
            self.update_editor, self.extended_name + '_items', remove=True)

        # Remove listener for changes to traits on the objects in the list
        self.context_object.on_trait_change(
            self.refresh_editor, self.extended_name + '.-', remove=True)

        # Remove listeners for column definition changes
        self.on_trait_change(self._update_columns, 'columns', remove=True)
        self.on_trait_change(
            self._update_columns,
            'columns_items',
            remove=True)

        super(TableEditor, self).dispose()

    #-------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #-------------------------------------------------------------------------

    def update_editor(self):
        """Updates the editor when the object trait changes externally to the
        editor."""

        if self._no_notify:
            return

        self.table_view.setUpdatesEnabled(False)
        try:
            filtering = len(
                self.factory.filters) > 0 or self.filter is not None
            if filtering:
                self._update_filtering()

            # invalidate the model, but do not reset it. Resetting the model
            # may cause problems if the selection sync'ed traits are being used
            # externally to manage the selections
            self.model.invalidate()

            self.table_view.resizeColumnsToContents()
            if self.auto_size:
                self.table_view.resizeRowsToContents()

        finally:
            self.table_view.setUpdatesEnabled(True)

    def restore_prefs(self, prefs):
        """ Restores any saved user preference information associated with the
            editor.
        """
        header = self.table_view.horizontalHeader()
        if header is not None and 'column_state' in prefs:
            header.restoreState(prefs['column_state'])

    def save_prefs(self):
        """ Returns any user preference information associated with the editor.
        """
        prefs = {}
        header = self.table_view.horizontalHeader()
        if header is not None:
            prefs['column_state'] = header.saveState().data()
        return prefs

    #-------------------------------------------------------------------------
    #  Requests that the underlying table widget to redraw itself:
    #-------------------------------------------------------------------------

    def refresh_editor(self):
        """Requests that the underlying table widget to redraw itself."""

        self.table_view.viewport().update()

    #-------------------------------------------------------------------------
    #  Creates a new row object using the provided factory:
    #-------------------------------------------------------------------------

    def create_new_row(self):
        """Creates a new row object using the provided factory."""

        factory = self.factory
        kw = factory.row_factory_kw.copy()
        if '__table_editor__' in kw:
            kw['__table_editor__'] = self

        return self.ui.evaluate(factory.row_factory,
                                *factory.row_factory_args, **kw)

    #-------------------------------------------------------------------------
    #  Returns the raw list of model objects:
    #-------------------------------------------------------------------------

    def items(self):
        """Returns the raw list of model objects."""

        items = self.value
        if not isinstance(items, SequenceTypes):
            items = [items]

        if self.factory and self.factory.reverse:
            items = ReversedList(items)

        return items

    #-------------------------------------------------------------------------
    #  Perform actions without notifying the underlying table view or model:
    #-------------------------------------------------------------------------

    def callx(self, func, *args, **kw):
        """Call a function without notifying the underlying table view or
        model."""

        old = self._no_notify
        self._no_notify = True
        try:
            func(*args, **kw)
        finally:
            self._no_notify = old

    def setx(self, **keywords):
        """Set one or more attributes without notifying the underlying table
        view or model."""

        old = self._no_notify
        self._no_notify = True
        try:
            for name, value in keywords.items():
                setattr(self, name, value)
        finally:
            self._no_notify = old

    #-------------------------------------------------------------------------
    #  Sets the current selection to a set of specified objects:
    #-------------------------------------------------------------------------

    def set_selection(self, objects=[], notify=True):
        """Sets the current selection to a set of specified objects."""

        if not isinstance(objects, list):
            objects = [objects]

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
        smodel = self.table_view.selectionModel()
        if smodel is None:
            # guard against selection during tear-down
            return
        for index in indexes:
            index = self.model.mapFromSource(index)
            if index.isValid():
                smodel.setCurrentIndex(
                    index, QtGui.QItemSelectionModel.NoUpdate)
                selection.select(index, index)

        smodel.blockSignals(not notify)
        try:
            if len(selection.indexes()):
                smodel.clear()
                smodel.select(selection, flags)
            else:
                smodel.clear()
        finally:
            smodel.blockSignals(False)

    #-------------------------------------------------------------------------
    #  Private methods:
    #-------------------------------------------------------------------------

    def _column_index_from_name(self, name):
        """Returns the index of the column with the given name or -1 if no
        column exists with that name."""

        for i, column in enumerate(self.columns):
            if name == column.name:
                return i
        return -1

    def _customize_filters(self, filter):
        """Allows the user to customize the current set of table filters."""

        filter_editor = TableFilterEditor(editor=self)
        ui = filter_editor.edit_traits(parent=self.control)
        if ui.result:
            self.factory.filters = filter_editor.templates
            self.filter = filter_editor.selected_filter
        else:
            self.setx(filter=filter)

    def _update_filtering(self):
        """Update the filter summary and the filtered indices."""

        items = self.items()
        num_items = len(items)

        f = self.filter
        if f is None:
            self._filtered_cache = None
            self.filtered_indices = list(range(num_items))
            self.filter_summary = 'All %i items' % num_items
        else:
            if not callable(f):
                f = f.filter
            self._filtered_cache = fc = [f(item) for item in items]
            self.filtered_indices = fi = [i for i, ok in enumerate(fc) if ok]
            self.filter_summary = '%i of %i items' % (len(fi), num_items)

    def _add_image(self, image_resource):
        """ Adds a new image to the image map.
        """
        image = image_resource.create_icon()

        self.image_resources[image_resource] = image
        self.images[image_resource.name] = image

        return image

    def _get_image(self, image):
        """ Converts a user specified image to a QIcon.
        """
        if isinstance(image, six.string_types):
            self.image = image
            image = self.image

        if isinstance(image, ImageResource):
            result = self.image_resources.get(image)
            if result is not None:
                return result
            return self._add_image(image)

        return self.images.get(image)

    #-- Trait Property getters/setters ---------------------------------------

    @cached_property
    def _get_selected_row(self):
        """Gets the selected row, or the first row if multiple rows are
        selected."""

        mode = self.factory.selection_mode

        if mode.startswith('column'):
            return None
        elif mode == 'row':
            return self.selected

        try:
            if mode == 'rows':
                return self.selected[0]
            elif mode == 'cell':
                return self.selected[0]
            elif mode == 'cells':
                return self.selected[0][0]
        except IndexError:
            return None

    @cached_property
    def _get_selected_indices(self):
        """Gets the row,column indices which match the selected trait"""
        selection_items = self.table_view.selectionModel().selection()
        indices = self.model.mapSelectionToSource(selection_items).indexes()
        if self.factory.selection_mode.startswith('row'):
            indices = sorted(set(index.row() for index in indices))
        elif self.factory.selection_mode.startswith('column'):
            indices = sorted(set(index.column() for index in indices))
        else:
            indices = [(index.row(), index.column()) for index in indices]

        if self.factory.selection_mode in {'rows', 'columns', 'cells'}:
            return indices
        elif len(indices) > 0:
            return indices[0]
        else:
            return -1

    def _set_selected_indices(self, indices):
        if not isinstance(indices, list):
            indices = [indices]
        selected = []
        if self.factory.selection_mode.startswith('row'):
            for row in indices:
                selected.append(self.value[row])
        elif self.factory.selection_mode.startswith('column'):
            for col in indices:
                selected.append(self.columns[col].name)
        else:
            for row, col in indices:
                selected.append((self.value[row], self.columns[col].name))

        self.selected = selected
        self.set_selection(self.selected, False)

    #-- Trait Change Handlers ------------------------------------------------

    def _filter_changed(self, old_filter, new_filter):
        """Handles the current filter being changed."""

        if not self._no_notify:
            if new_filter is customize_filter:
                do_later(self._customize_filters, old_filter)
            else:
                self._update_filtering()
                self.model.invalidate()
                self.set_selection(self.selected)

    def _update_columns(self):
        """Handle the column list being changed."""

        self.table_view.setItemDelegate(TableDelegate(self.table_view))
        for i, column in enumerate(self.columns):
            if column.renderer:
                self.table_view.setItemDelegateForColumn(i, column.renderer)

        self.model.invalidate()
        self.table_view.resizeColumnsToContents()
        if self.auto_size:
            self.table_view.resizeRowsToContents()

    def _selected_changed(self, new):
        """Handle the selected row/column/cell being changed externally."""
        if not self._no_notify:
            self.set_selection(self.selected, notify=False)

    def _update_filter_changed(self):
        """ The filter has changed internally.
        """
        self._filter_changed(self.filter, self.filter)

    #-- Event Handlers -------------------------------------------------------

    def _on_row_selection(self, added, removed):
        """Handle the row selection being changed."""

        items = self.items()
        indexes = self.table_view.selectionModel().selectedRows()
        if len(indexes):
            index = self.model.mapToSource(indexes[0])
            selected = items[index.row()]
        else:
            selected = None

        self.setx(selected=selected)
        self.ui.evaluate(self.factory.on_select, self.selected)

    def _on_rows_selection(self, added, removed):
        """Handle the rows selection being changed."""
        items = self.items()
        indexes = self.table_view.selectionModel().selectedRows()
        selected = [items[self.model.mapToSource(index).row()]
                    for index in indexes]

        self.setx(selected=selected)
        self.ui.evaluate(self.factory.on_select, self.selected)

    def _on_column_selection(self, added, removed):
        """Handle the column selection being changed."""

        indexes = self.table_view.selectionModel().selectedColumns()
        if len(indexes):
            index = self.model.mapToSource(indexes[0])
            selected = self.columns[index.column()].name
        else:
            selected = ''

        self.setx(selected=selected)
        self.ui.evaluate(self.factory.on_select, self.selected)

    def _on_columns_selection(self, added, removed):
        """Handle the columns selection being changed."""

        indexes = self.table_view.selectionModel().selectedColumns()
        selected = [self.columns[self.model.mapToSource(index).column()].name
                    for index in indexes]

        self.setx(selected=selected)
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

        self.setx(selected=selected)
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

        self.setx(selected=selected)
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

    def _on_context_insert(self):
        """Handle 'insert item' being selected from the header context menu."""

        self.model.insertRow(self.header_row)

    def _on_context_append(self):
        """Handle 'add item' being selected from the empty space context
        menu."""

        self.model.insertRow(self.model.rowCount())

    def _on_context_remove(self):
        """Handle 'remove item' being selected from the header context menu."""

        self.model.removeRow(self.header_row)

    def _on_context_move_up(self):
        """Handle 'move up' being selected from the header context menu."""

        self.model.moveRow(self.header_row, self.header_row - 1)

    def _on_context_move_down(self):
        """Handle 'move down' being selected from the header context menu."""

        self.model.moveRow(self.header_row, self.header_row + 1)


# Define the SimpleEditor class.
SimpleEditor = TableEditor


# Define the ReadonlyEditor class.
ReadonlyEditor = TableEditor

#-------------------------------------------------------------------------
#  Qt widgets that have been configured to behave as expected by Traits UI:
#-------------------------------------------------------------------------


class TableDelegate(QtGui.QStyledItemDelegate):
    """ A QStyledItemDelegate which fetches Traits UI editors.
    """

    def createEditor(self, parent, option, index):
        """ Reimplemented to return the editor for a given index."""

        model = index.model()
        index = model.mapToSource(index)
        table_editor = model._editor
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
        factory_method = getattr(factory, style + '_editor')
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
        # will be disposed in closeEditor of the TableView
        control._editor = editor
        return control

    def updateEditorGeometry(self, editor, option, index):
        """ Update the editor's geometry.
        """
        editor.setGeometry(option.rect)

    def paint(self, painter, option, index):
        self.initStyleOption(option, index)

        if ((option.state & QtGui.QStyle.State_Selected) and
                (option.state & QtGui.QStyle.State_Active)):
            factory = self.parent()._editor.factory
            if factory.selection_bg_color is not None:
                option.palette.setColor(
                    QtGui.QPalette.Highlight, factory.selection_bg_color_)
            if factory.selection_color is not None:
                option.palette.setColor(
                    QtGui.QPalette.HighlightedText, factory.selection_color_)

        QtGui.QApplication.style().drawControl(
            QtGui.QStyle.CE_ItemViewItem, option, painter, None);


class TableView(QtGui.QTableView):
    """A QTableView configured to behave as expected by TraitsUI."""

    _SELECTION_MAP = {
        'row': (QtGui.QAbstractItemView.SelectRows,
                QtGui.QAbstractItemView.SingleSelection),
        'rows': (QtGui.QAbstractItemView.SelectRows,
                 QtGui.QAbstractItemView.ExtendedSelection),
        'column': (QtGui.QAbstractItemView.SelectColumns,
                   QtGui.QAbstractItemView.SingleSelection),
        'columns': (QtGui.QAbstractItemView.SelectColumns,
                    QtGui.QAbstractItemView.ExtendedSelection),
        'cell': (QtGui.QAbstractItemView.SelectItems,
                 QtGui.QAbstractItemView.SingleSelection),
        'cells': (QtGui.QAbstractItemView.SelectItems,
                  QtGui.QAbstractItemView.ExtendedSelection)
    }

    def __init__(self, editor):
        """Initialise the object."""

        QtGui.QTableView.__init__(self)

        self._initial_size = False
        self._editor = editor
        factory = editor.factory

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
        if factory.edit_on_first_click and not factory.reorderable:
            triggers |= QtGui.QAbstractItemView.CurrentChanged
        self.setEditTriggers(triggers)

        # Configure the reordering and sorting behavior.
        self.setDragEnabled(True)
        self.viewport().setAcceptDrops(True)
        self.setDropIndicatorShown(True)

        if factory.reorderable:
            self.setDragDropMode(QtGui.QAbstractItemView.InternalMove)
        if factory.sortable:
            self.setSortingEnabled(True)

        if factory._qt_stylesheet is not None:
            self.setStyleSheet(factory._qt_stylesheet)

        self.resizeColumnsToContents()

    def setModel(self, model):
        super(TableView, self).setModel(model)
        self._update_header_sizing()

    def contextMenuEvent(self, event):
        """Reimplemented to create context menus for cells and empty space."""

        # Determine the logical indices of the cell where click occured
        hheader, vheader = self.horizontalHeader(), self.verticalHeader()
        position = event.globalPos()
        row = vheader.logicalIndexAt(vheader.mapFromGlobal(position))
        column = hheader.logicalIndexAt(hheader.mapFromGlobal(position))

        # Map the logical row index to a real index for the source model
        model = self.model()
        row = model.mapToSource(model.index(row, 0)).row()

        # Show a context menu for empty space at bottom of table...
        editor = self._editor
        if row == -1:
            factory = editor.factory
            if (factory.editable and factory.row_factory is not None):
                event.accept()
                editor.empty_menu.exec_(position)

        # ...or show a context menu for a cell.
        elif column != -1:
            obj = editor.items()[row]
            column = editor.columns[column]
            menu_manager = column.get_menu(obj)
            if menu_manager is None:
                menu_manager = editor.factory.menu
            if menu_manager is not None:
                event.accept()
                selected = editor.selected
                if not isinstance(selected, SequenceTypes):
                    selected = [selected]
                if obj not in selected:
                    selected = [obj]
                editor.set_menu_context(selected, obj, column)
                menu = menu_manager.create_menu(self, controller=editor)
                menu.exec_(position)

    def eventFilter(self, obj, event):
        """Reimplemented to create context menu for the vertical header."""

        vheader = self.verticalHeader()
        if (obj is vheader and event.type() == QtCore.QEvent.ContextMenu):
            event.accept()
            editor = self._editor
            row = vheader.logicalIndexAt(event.pos().y())
            if row == -1:
                factory = editor.factory
                if factory.row_factory is not None:
                    editor.empty_menu.exec_(event.globalPos())
            else:
                editor.header_row = row
                if editor.factory.reorderable:
                    show_up = row > 0
                    show_down = row < editor.model.rowCount() - 1
                    editor.header_menu_up.setVisible(show_up)
                    editor.header_menu_down.setVisible(show_down)
                self._editor.header_menu.exec_(event.globalPos())
            return True

        else:
            return QtGui.QTableView.eventFilter(self, obj, event)

    def resizeEvent(self, event):
        """Reimplemented to size the table columns when the size of the table
        changes. Because the layout algorithm requires that the available
        space be known, we have to wait until the UI that contains this table
        gives it its initial size."""

        QtGui.QTableView.resizeEvent(self, event)

        if self._editor.auto_size:
            self.resizeColumnsToContents()
            self.resizeRowsToContents()

        else:
            parent = self.parent()
            if (not self._initial_size and parent and (
                    self.isVisible()
                    or isinstance(parent, QtGui.QMainWindow))):
                self._initial_size = True
                if self._editor.auto_size:
                    self.resizeColumnsToContents()
                    self.resizeRowsToContents()

    def sizeHint(self):
        """Reimplemented to define a better size hint for the width of the
        TableEditor."""

        size_hint = QtGui.QTableView.sizeHint(self)

        # This method is sometimes called by Qt after the editor has been
        # disposed but before this control has been deleted:
        if self._editor.factory is None:
            return size_hint

        width = self.style().pixelMetric(QtGui.QStyle.PM_ScrollBarExtent,
                                         QtGui.QStyleOptionHeader(), self)
        for column in range(len(self._editor.columns)):
            width += self.sizeHintForColumn(column)
        size_hint.setWidth(width)
        return size_hint

    def sizeHintForColumn(self, column_index):
        """Reimplemented to support absolute width specification via
        TableColumns and to improve the metric for autosizing columns."""

        editor = self._editor
        column = editor.columns[column_index]
        requested_width = column.get_width()

        # Autosize based on column contents and label width. Qt's default
        # implementation of this function does content, we handle the label.
        if requested_width < 1:
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

            # Add margin to the calculated width as appropriate
            style = self.style()
            option = QtGui.QStyleOptionHeader()
            width += style.pixelMetric(QtGui.QStyle.PM_HeaderGripMargin,
                                       option, self) * 2
            if editor.factory.sortable and not editor.factory.reorderable:
                # Add size of sort indicator
                width += style.pixelMetric(QtGui.QStyle.PM_HeaderMarkSize,
                                           option, self)
                # Add distance between sort indicator and text
                width += style.pixelMetric(
                    QtGui.QStyle.PM_HeaderMargin, option, self)
            return max(base_width, width)

        # Or else set width absolutely
        else:
            return requested_width

    def resizeColumnsToContents(self):
        """ Support proportional column width specifications. """

        # TODO: The proportional size specification approach found in the
        # TableColumns is not entirely compatible with the ability to
        # specify the resize_mode.  Namely, there are combinations of
        # specifications that are redundant, and others which are
        # contradictory.  Rework this method so that the various values
        # for **width** have a well-defined, sensible meaning for each
        # of the possible values of resize_mode.

        editor = self._editor
        available_space = self.viewport().width()
        hheader = self.horizontalHeader()

        # Compute sizes for columns with absolute or no size requests
        proportional = []
        for column_index in range(len(editor.columns)):
            column = editor.columns[column_index]
            requested_width = column.get_width()
            if column.resize_mode in ("interactive", "stretch") \
                    and 0 < requested_width <= 1.0:
                proportional.append((column_index, requested_width))
            elif column.resize_mode == "interactive" and requested_width < 0 \
                    and self._initial_size:
                # Keep previous size if initial sizing has been done
                available_space -= hheader.sectionSize(column_index)
            else:
                base_width = hheader.sectionSizeHint(column_index)
                width = max(base_width, self.sizeHintForColumn(column_index))
                hheader.resizeSection(column_index, width)
                available_space -= width

        # Now use the remaining space for columns with proportional width
        # requests
        for column_index, percent in proportional:
            base_width = hheader.sectionSizeHint(column_index)
            width = max(base_width, int(percent * available_space))
            hheader.resizeSection(column_index, width)

    def closeEditor(self, control, hint):
        # dispose traits editor associated with control if any
        editor = getattr(control, "_editor", None)
        if editor is not None:
            editor.dispose()
            delattr(control, "_editor")

        return super(TableView, self).closeEditor(control, hint)

    def _update_header_sizing(self):
        """ Header section sizing can be done only after a valid model is set.
        Otherwise results in segfault with Qt5.
        """
        editor = self._editor
        factory = editor.factory
        # Configure the row headings.
        vheader = self.verticalHeader()
        set_resize_mode = set_qheader_section_resize_mode(vheader)
        insertable = factory.row_factory is not None
        if ((factory.editable and (insertable or factory.deletable)) or
                factory.reorderable):
            vheader.installEventFilter(self)
            set_resize_mode(QtGui.QHeaderView.ResizeToContents)
        elif not factory.show_row_labels:
            vheader.hide()
        if factory.row_height > 0:
            vheader.setDefaultSectionSize(factory.row_height)
        self.setAlternatingRowColors(factory.alternate_bg_color)
        self.setHorizontalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        # Configure the column headings.
        # We detect if there are any stretchy sections at all; if not, then
        # we make the last non-fixed-size column stretchy.
        hheader = self.horizontalHeader()
        set_resize_mode = set_qheader_section_resize_mode(hheader)
        resize_mode_map = dict(
            interactive=QtGui.QHeaderView.Interactive,
            fixed=QtGui.QHeaderView.Fixed,
            stretch=QtGui.QHeaderView.Stretch,
            resize_to_contents=QtGui.QHeaderView.ResizeToContents,
        )
        stretchable_columns = []
        for i, column in enumerate(editor.columns):
            set_resize_mode(i, resize_mode_map[column.resize_mode])
            if column.resize_mode in ("stretch", "interactive"):
                stretchable_columns.append(i)
        if not stretchable_columns:
            # Use the behavior from before the "resize_mode" trait was added
            # to TableColumn
            hheader.setStretchLastSection(True)
        else:
            # hheader.setSectionResizeMode(
            #     stretchable_columns[-1], QtGui.QHeaderView.Stretch)
            hheader.setStretchLastSection(False)
        if factory.show_column_labels:
            hheader.setHighlightSections(False)
        else:
            hheader.hide()

#-------------------------------------------------------------------------
#  Editor for configuring the filters available to a TableEditor:
#-------------------------------------------------------------------------


class TableFilterEditor(HasTraits):
    """ An editor that manages table filters.
    """

    #-------------------------------------------------------------------------
    #  Trait definitions:
    #-------------------------------------------------------------------------

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
    view = View(
        Group(
            Group(
                Group(
                    Item(
                        'add_button',
                        enabled_when='selected_template'
                    ),
                    Item(
                        'remove_button',
                        enabled_when='len(templates) > 1 and '
                                     'selected_filter is not None',
                    ),
                    orientation='horizontal',
                    show_labels=False,
                ),
                Label('Base filter for new filters:'),
                Item(
                    'selected_template',
                    editor=EnumEditor(name='templates')
                ),
                Item(
                    'selected_filter',
                    style='custom',
                    editor=EnumEditor(
                        name='filters',
                        mode='list',
                    )
                ),
                show_labels=False,
            ),
            Item(
                'selected_filter',
                width=0.75,
                style='custom',
                editor=InstanceEditor(view_name='selected_filter_view')
            ),
            id='TableFilterEditorSplit',
            show_labels=False,
            layout='split',
            orientation='horizontal',
        ),
        id='traitsui.qt4.table_editor.TableFilterEditor',
        buttons=['OK', 'Cancel'],
        kind='livemodal',
        resizable=True,
        width=800,
        height=400,
        title='Customize filters',
    )

    #-------------------------------------------------------------------------
    #  Private methods:
    #-------------------------------------------------------------------------

    #-- Trait Property getter/setters ----------------------------------------

    @cached_property
    def _get_selected_filter_view(self):
        view = None
        if self.selected_filter:
            model = self.editor.model
            index = model.mapToSource(model.index(0, 0))
            if index.isValid():
                obj = self.editor.items()[index.row()]
            else:
                obj = None
            view = self.selected_filter.edit_view(obj)
        return view

    @cached_property
    def _get_templates(self):
        templates = [f for f in self.editor.factory.filters if f.template]
        templates.extend(self.filters)
        return templates

    #-- Trait Change Handlers ------------------------------------------------

    def _editor_changed(self):
        self.filters = [f.clone_traits() for f in self.editor.factory.filters
                        if not f.template]
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
