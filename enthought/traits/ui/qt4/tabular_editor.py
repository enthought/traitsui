#-------------------------------------------------------------------------------
#
#  Copyright (c) 2009, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
#  Author: Evan Patterson
#  Date:   06/22/2009
#
#-------------------------------------------------------------------------------

""" A traits UI editor for editing tabular data (arrays, list of tuples, lists
    of objects, etc).
"""

# FIXME: The following features present in the wx implementation are not 
# currently implemented:
#     * right_clicked and right_dclicked events
#     * drag and drop support
#     * editable labels (column headers)

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from PyQt4 import QtCore, QtGui

from enthought.pyface.image_resource import ImageResource

from enthought.traits.api import Any, Bool, Event, HasStrictTraits, Instance, \
    Int, List, Property, TraitListEvent

from enthought.traits.ui.tabular_adapter import TabularAdapter
from enthought.traits.ui.ui_traits import Image

from editor import Editor
from tabular_model import TabularModel

#-------------------------------------------------------------------------------
#  'TabularEditor' class
#-------------------------------------------------------------------------------

class TabularEditor(Editor):
    """ A traits UI editor for editing tabular data (arrays, list of tuples,
        lists of objects, etc).
    """

    #-- Trait Definitions ------------------------------------------------------

    # The event fired when a table update is needed:
    update = Event

    # The current set of selected items (which one is used depends upon the
    # initial state of the editor factory 'multi_select' trait):
    selected       = Any
    multi_selected = List

    # The current set of selected item indices (which one is used depends upon
    # the initial state of the editor factory 'multi_select' trait):
    selected_row        = Int(-1)
    multi_selected_rows = List(Int)

    # The most recently actived item and its index:
    activated     = Any
    activated_row = Int

    # The most recent left click data:
    clicked = Instance('TabularEditorEvent')

    # The most recent left double click data:
    dclicked = Instance('TabularEditorEvent')

    # The most recent right click data:
    right_clicked = Instance('TabularEditorEvent')

    # The most recent right double click data:
    right_dclicked = Instance('TabularEditorEvent')

    # The most recent column click data:
    column_clicked = Instance('TabularEditorEvent')

    # Is the tabular editor scrollable? This value overrides the default.
    scrollable = True

    # Row index of item to select after rebuilding editor list:
    row = Any

    # Should the selected item be edited after rebuilding the editor list:
    edit = Bool(False)

    # The adapter from trait values to editor values:
    adapter = Instance(TabularAdapter)

    # The table model associated with the editor:
    model = Instance(TabularModel)

    # Dictionary mapping image names to QIcons
    images = Any({})

    # Dictionary mapping ImageResource objects to QIcons
    image_resources = Any({})

    # An image being converted:
    image = Image

    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------

    def init (self, parent):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        factory = self.factory
        adapter = self.adapter = factory.adapter
        self.model = TabularModel(editor=self)

        # Create the control
        control = self.control = _TableView(self)

        # Set up the selection listener
        if factory.multi_select:
            self.sync_value(factory.selected, 'multi_selected', 'both',
                            is_list=True)
            self.sync_value(factory.selected_row, 'multi_selected_rows','both',
                            is_list=True)
        else:
            self.sync_value(factory.selected, 'selected', 'both')
            self.sync_value(factory.selected_row, 'selected_row', 'both')

        # Connect to the mode specific selection handler
        if factory.multi_select:
            slot = self._on_rows_selection
        else:
            slot = self._on_row_selection
        signal = 'selectionChanged(QItemSelection,QItemSelection)'
        QtCore.QObject.connect(self.control.selectionModel(), 
                               QtCore.SIGNAL(signal), slot)

        # Synchronize other interesting traits as necessary:
        self.sync_value(factory.update, 'update', 'from')
        self.sync_value(factory.activated,     'activated',     'to')
        self.sync_value(factory.activated_row, 'activated_row', 'to')
        self.sync_value(factory.clicked,  'clicked',  'to')
        self.sync_value(factory.dclicked, 'dclicked', 'to')
        self.sync_value(factory.right_clicked,  'right_clicked',  'to')
        self.sync_value(factory.right_dclicked, 'right_dclicked', 'to')
        self.sync_value(factory.column_clicked, 'column_clicked', 'to')

        # Connect other signals as necessary
        signal = QtCore.SIGNAL('activated(QModelIndex)')
        QtCore.QObject.connect(control, signal, self._on_activate)
        signal = QtCore.SIGNAL('clicked(QModelIndex)')
        QtCore.QObject.connect(control, signal, self._on_click)
        signal = QtCore.SIGNAL('doubleClicked(QModelIndex)')
        QtCore.QObject.connect(control, signal, self._on_dclick)
        signal = QtCore.SIGNAL('sectionClicked(int)')
        QtCore.QObject.connect(control.horizontalHeader(), signal,
                               self._on_column_click)

        # Make sure we listen for 'items' changes as well as complete list
        # replacements:
        try:
            self.context_object.on_trait_change(self.update_editor,
                                self.extended_name + '_items', dispatch = 'ui')
        except:
            pass

        # If the user has requested automatic update, attempt to set up the
        # appropriate listeners:
        if factory.auto_update:
            self.context_object.on_trait_change(self.update_editor,
                                self.extended_name + '.-', dispatch='ui')

        # Create the mapping from user supplied images to wx.ImageList indices:
        for image_resource in factory.images:
            self._add_image(image_resource)

        # Refresh the editor whenever the adapter changes:
        self.on_trait_change(self.update_editor, 'adapter.+update',
                             dispatch='ui')

        # Rebuild the editor columns and headers whenever the adapter's
        # 'columns' changes:
        self.on_trait_change(self.update_editor, 'adapter.columns', 
                             dispatch='ui')

    #---------------------------------------------------------------------------
    #  Disposes of the contents of an editor:
    #---------------------------------------------------------------------------

    def dispose (self):
        """ Disposes of the contents of an editor.
        """
        self.context_object.on_trait_change(self.update_editor,
                                  self.extended_name + '_items', remove=True)

        if self.factory.auto_update:
            self.context_object.on_trait_change(self.update_editor,
                                self.extended_name + '.-', remove=True)

        self.on_trait_change(self.update_editor, 'adapter.+update', remove=True)
        self.on_trait_change(self.update_editor, 'adapter.columns',
                             remove=True)

        super(TabularEditor, self).dispose()

    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------

    def update_editor(self):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        self.model.reset()

    #---------------------------------------------------------------------------
    #  UI preference save/restore interface:
    #---------------------------------------------------------------------------

    def restore_prefs(self, prefs):
        """ Restores any saved user preference information associated with the
            editor.
        """
        cws = prefs.get('cached_widths')
        num_columns = len(self.adapter.columns)
        if cws is not None and num_columns == len(cws):
            for column in xrange(num_columns):
                self.control.setColumnWidth(column, cws[column])

    def save_prefs(self):
        """ Returns any user preference information associated with the editor.
        """
        widths = [ self.control.columnWidth(column) for column
                   in xrange(len(self.adapter.columns)) ]
        return { 'cached_widths': widths }

    #---------------------------------------------------------------------------
    #  Private methods:
    #---------------------------------------------------------------------------

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
        if isinstance(image, basestring):
            self.image = image
            image = self.image

        if isinstance(image, ImageResource):
            result = self.image_resources.get(image)
            if result is not None:
                return result
            return self._add_image(image)

        return self.images.get(image)

    def _mouse_click(self, index, trait):
        """ Generate a TabularEditorEvent event for a specified model index and
            editor trait name.
        """
        event = TabularEditorEvent(editor=self, row=index.row(), 
                                   column=index.column())
        setattr(self, trait, event)

    #-- Trait Event Handlers ---------------------------------------------------

    def _update_changed(self):
        self.update_editor()

    def _selected_changed(self, new):
        if not self._no_update:
            try:
                self._selected_row_changed(self, self.value.index(new))
            except:
                pass

    def _selected_row_changed(self, selected_row):
        if not self._no_update:
            smodel = self.control.selectionModel()
            if selected is None:
                smodel.clearSelection()
            else:
                smodel.select(self.model.index(row, 0), 
                              QtGui.QItemSelectionModel.ClearAndSelect |
                              QtGui.QItemSelectionModel.Rows)

    def _multi_selected_changed(self, new):
        if not self._no_update:
            values = self.value
            try:
                rows = [ values.index(i) for i in new]
                self._multi_selected_rows_changed(row)
            except:
                pass

    def _multi_selected_items_changed(self, event):
        values = self.values
        try:
            added = [ values.index(item) for item in event.added ]
            removed = [ values.index(item) for item in event.removed ]
            new_event = TraitListEvent(0, added, removed)
            self._multi_selected_rows_items_changed(new_event)
        except:
            pass

    def _multi_selected_rows_changed(self, selected_rows):
        if not self._no_update:
            smodel = self.control.selectionModel()
            smodel.clearSelection()
            for row in selected_rows:
                smodel.select(self.model.index(row, 0),
                              QtGui.QItemSelectionModel.Select |
                              QtGui.QItemSelectionModel.Rows)

    def _multi_selected_rows_items_changed(self, event):
        smodel = self.control.selectionModel()
        for row in event.removed:
            smodel.select(self.model.index(row, 0),
                          QtGui.QItemSelectionModel.Deselect |
                          QtGui.QItemSelectionModel.Rows)
        for row in event.added:
            smodel.select(self.model.index(row, 0),
                          QtGui.QItemSelectionModel.Select |
                          QtGui.QItemSelectionModel.Rows)

    #-- Table Control Event Handlers -------------------------------------------

    def _on_activate(self, index):
        """ Handle a cell being activated.
        """
        self._mouse_click(index, 'activated')

    def _on_click(self, index):
        """ Handle a cell being clicked.
        """
        self._mouse_click(index, 'clicked')

    def _on_dclick(self, index):
        """ Handle a cell being double clicked.
        """
        self._mouse_click(index, 'dclicked')

    def _on_column_click(self, column):
        event = TabularEditorEvent(editor=self, row=0, column=column)
        setattr(self, 'column_clicked', event)

    def _on_row_selection(self, added, removed):
        """ Handle the row selection being changed.
        """
        self._no_update = True
        try:
            indexes = self.control.selectionModel().selectedRows()
            if len(indexes):
                self.selected_row = indexes[0].row()
                self.selected = self.adapter.get_item(self.object, self.name,
                                                      self.selected_row)
            else:
                self.selected_row = -1
                self.selected = None
        finally:
            self._no_update = False

    def _on_rows_selection(self, added, removed):
        """ Handle the rows selection being changed.
        """
        self._no_update = True
        try:
            indexes = self.control.selectionModel().selectedRows()
            selected_rows = []
            selected = []
            for index in indexes:
                row = index.row()
                selected_rows.append(row)
                selected.append(self.adapter.get_item(self.object, self.name, 
                                                      row))
            self.multi_selected_rows = selected_rows
            self.multi_selected = selected
        finally:
            self._no_update = False

#-------------------------------------------------------------------------------
#  'TabularEditorEvent' class:
#-------------------------------------------------------------------------------

class TabularEditorEvent(HasStrictTraits):

    # The index of the row:
    row = Int

    # The id of the column (either a string or an integer):
    column = Any

    # The row item:
    item = Property

    #-- Private Traits ---------------------------------------------------------

    # The editor the event is associated with:
    editor = Instance(TabularEditor)

    #-- Property Implementations -----------------------------------------------

    def _get_item(self):
        editor = self.editor
        return editor.adapter.get_item(editor.object, editor.name, self.row)

#-------------------------------------------------------------------------------
#  Qt widgets that have been configured to behave as expected by Traits UI:
#-------------------------------------------------------------------------------

class _ItemDelegate(QtGui.QStyledItemDelegate):
    """ A QStyledItemDelegate which draws its owns gridlines so that we can 
        choose to draw only the horizontal or only the vertical gridlines if 
        necessary.
    """

    def __init__(self, table_view):
        """ Store which grid lines to draw.
        """
        QtGui.QStyledItemDelegate.__init__(self)
        self._table_view = table_view
        self._horizontal_lines = table_view._editor.factory.horizontal_lines
        self._vertical_lines = table_view._editor.factory.vertical_lines

    def paint(self, painter, option, index):
        """ Overrident to draw gridlines.
        """
        QtGui.QStyledItemDelegate.paint(self, painter, option, index)
        painter.save()

        # FIXME: 'styleHint' is returning bogus (negative) values. Why?
        #style = self._table_view.style()
        #color = style.styleHint(QtGui.QStyle.SH_Table_GridLineColor, option,
        #                        self._table_view)
        #painter.setPen(QtGui.QColor(color))
        painter.setPen(option.palette.color(QtGui.QPalette.Dark))

        if self._horizontal_lines:
            painter.drawLine(option.rect.topLeft(), option.rect.topRight())
            if index.row() == index.model().rowCount(index)-1:
                painter.drawLine(option.rect.bottomLeft(), 
                                 option.rect.bottomRight())
        if self._vertical_lines:
            painter.drawLine(option.rect.topLeft(), option.rect.bottomLeft())

        painter.restore()

class _TableView(QtGui.QTableView):
    """ A QTableView configured to behave as expected by TraitsUI.
    """

    def __init__(self, editor):
        """ Initialise the object.
        """
        QtGui.QTableView.__init__(self)

        self._editor = editor
        self.setModel(editor.model)
        factory = editor.factory
        
        # Configure the row headings
        self.verticalHeader().hide()

        # Configure the column headings.
        hheader = self.horizontalHeader()
        hheader.setStretchLastSection(True)
        if factory.show_titles:
            hheader.setHighlightSections(False)
        else:
            hheader.hide()
        self.resizeColumnsToContents()

        # Turn off the grid lines--we'll draw our own
        self.setShowGrid(False)
        self.setItemDelegate(_ItemDelegate(self))

        # Configure the selection behaviour.
        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        if factory.multi_select:
            mode = QtGui.QAbstractItemView.ExtendedSelection
        else:
            mode = QtGui.QAbstractItemView.SingleSelection
        self.setSelectionMode(mode)

        # Set column widths according to the adapter's requested width
        for column in xrange(len(editor.adapter.columns)):
            width = editor.adapter.get_width(editor.object, editor.name, column)
            if width != -1:
                self.setColumnWidth(column, width)

    def sizeHint(self):
        """ Reimplemented to define an appropriate size hint.
        """
        sh = QtGui.QTableView.sizeHint(self)
        
        w = 0
        for column in xrange(len(self._editor.adapter.columns)):
            w += self.sizeHintForColumn(column)
        sh.setWidth(w)

        return sh
