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

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import os

from pyface.qt import QtCore, QtGui

from pyface.image_resource import ImageResource

from traits.api import (Any, Bool, Callable, Event, HasStrictTraits, Instance,
    Int, List, NO_COMPARE, Property, TraitListEvent)

from traitsui.tabular_adapter import TabularAdapter
from traitsui.ui_traits import Image

from editor import Editor
from tabular_model import TabularModel


TRAITS_DEBUG = (os.getenv('TRAITS_DEBUG') is not None)


class HeaderEventFilter(QtCore.QObject) :
    def __init__(self, editor) :
        super(HeaderEventFilter, self).__init__()
        self.editor = editor

    def eventFilter(self, obj, event) :
        if event.type() == QtCore.QEvent.ContextMenu :
            self.editor._on_column_context_menu(event.pos())
            return True
        return False


class TabularEditor(Editor):
    """ A traits UI editor for editing tabular data (arrays, list of tuples,
        lists of objects, etc).
    """

    #-- Trait Definitions ------------------------------------------------------

    # The event fired when a table update is needed:
    update = Event

    # The event fired when a simple repaint is needed:
    refresh = Event

    # The current set of selected items (which one is used depends upon the
    # initial state of the editor factory 'multi_select' trait):
    selected       = Any
    multi_selected = List

    # The current set of selected item indices (which one is used depends upon
    # the initial state of the editor factory 'multi_select' trait):
    selected_row        = Int(-1)
    multi_selected_rows = List(Int)

    # The most recently actived item and its index:
    activated     = Any(comparison_mode=NO_COMPARE)
    activated_row = Int(comparison_mode=NO_COMPARE)

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

    # The most recent column click data:
    column_right_clicked = Instance('TabularEditorEvent')

    # The event triggering scrolling.
    scroll_to_row = Event(Int)

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

    header_event_filter = Any()

    widget_factory = Callable(lambda *args, **kwds: _TableView(*args, **kwds))

    #---------------------------------------------------------------------------
    #  Editor interface:
    #---------------------------------------------------------------------------

    def init (self, parent):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        factory = self.factory
        adapter = self.adapter = factory.adapter
        self.model = TabularModel(editor=self)

        # Create the control
        control = self.control = self.widget_factory(self)

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
        self.sync_value(factory.refresh, 'refresh', 'from')
        self.sync_value(factory.activated,     'activated',     'to')
        self.sync_value(factory.activated_row, 'activated_row', 'to')
        self.sync_value(factory.clicked,  'clicked',  'to')
        self.sync_value(factory.dclicked, 'dclicked', 'to')
        self.sync_value(factory.right_clicked,  'right_clicked',  'to')
        self.sync_value(factory.right_dclicked, 'right_dclicked', 'to')
        self.sync_value(factory.column_clicked, 'column_clicked', 'to')
        self.sync_value(factory.column_right_clicked, 'column_right_clicked', 'to')
        self.sync_value(factory.scroll_to_row, 'scroll_to_row', 'from')

        # Connect other signals as necessary
        signal = QtCore.SIGNAL('activated(QModelIndex)')
        QtCore.QObject.connect(control, signal, self._on_activate)
        signal = QtCore.SIGNAL('clicked(QModelIndex)')
        QtCore.QObject.connect(control, signal, self._on_click)
        signal = QtCore.SIGNAL('clicked(QModelIndex)')
        QtCore.QObject.connect(control, signal, self._on_right_click)
        signal = QtCore.SIGNAL('doubleClicked(QModelIndex)')
        QtCore.QObject.connect(control, signal, self._on_dclick)
        signal = QtCore.SIGNAL('sectionClicked(int)')
        QtCore.QObject.connect(control.horizontalHeader(), signal, self._on_column_click)

        control.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        signal = QtCore.SIGNAL('customContextMenuRequested(QPoint)')
        QtCore.QObject.connect(control, signal, self._on_context_menu)

        self.header_event_filter = HeaderEventFilter(self)
        control.horizontalHeader().installEventFilter(self.header_event_filter)

        # Make sure we listen for 'items' changes as well as complete list
        # replacements:
        try:
            self.context_object.on_trait_change(
                self.update_editor, self.extended_name+'_items', dispatch='ui')
        except:
            pass

        # If the user has requested automatic update, attempt to set up the
        # appropriate listeners:
        if factory.auto_update:
            self.context_object.on_trait_change(
                self.refresh_editor, self.extended_name + '.-', dispatch='ui')

        # Create the mapping from user supplied images to QImages:
        for image_resource in factory.images:
            self._add_image(image_resource)

        # Refresh the editor whenever the adapter changes:
        self.on_trait_change(self.refresh_editor, 'adapter.+update',
                             dispatch='ui')

        # Rebuild the editor columns and headers whenever the adapter's
        # 'columns' changes:
        self.on_trait_change(self.update_editor, 'adapter.columns',
                             dispatch='ui')

    def dispose (self):
        """ Disposes of the contents of an editor.
        """
        self.context_object.on_trait_change(
            self.update_editor, self.extended_name + '_items', remove=True)

        if self.factory.auto_update:
            self.context_object.on_trait_change(
                self.refresh_editor, self.extended_name + '.-', remove=True)

        self.on_trait_change(self.refresh_editor, 'adapter.+update',
                             remove=True)
        self.on_trait_change(self.update_editor, 'adapter.columns',
                             remove=True)

        self.adapter.cleanup()

        super(TabularEditor, self).dispose()

    def update_editor(self):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        if not self._no_update:
            self.model.reset()
            if self.factory.multi_select:
                self._multi_selected_changed(self.multi_selected)
            else :
                self._selected_changed(self.selected)

    #---------------------------------------------------------------------------
    #  TabularEditor interface:
    #---------------------------------------------------------------------------

    def refresh_editor(self):
        """ Requests the table view to redraw itself.
        """
        self.control.viewport().update()

    def callx(self, func, *args, **kw):
        """ Call a function without allowing the editor to update.
        """
        old = self._no_update
        self._no_update = True
        try:
            func(*args, **kw)
        finally:
            self._no_update = old

    def setx(self, **keywords):
        """ Set one or more attributes without allowing the editor to update.
        """
        old = self._no_notify
        self._no_notify = True
        try:
            for name, value in keywords.items():
                setattr(self, name, value)
        finally:
            self._no_notify = old

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
        widths = [ self.control.columnWidth(column)
                   for column in xrange(len(self.adapter.columns)) ]
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

    def _refresh_changed(self):
        self.refresh_editor()

    def _selected_changed(self, new):
        if not self._no_update:
            try:
                selected_row = self.value.index(new)
            except Exception as e:
                if TRAITS_DEBUG:
                    from traits.api import raise_to_debug
                    raise_to_debug()
            else:
                self._selected_row_changed(selected_row)

    def _selected_row_changed(self, selected_row):
        if not self._no_update:
            smodel = self.control.selectionModel()
            if selected_row == -1:
                smodel.clearSelection()
            else:
                smodel.select(self.model.index(selected_row, 0),
                              QtGui.QItemSelectionModel.ClearAndSelect |
                              QtGui.QItemSelectionModel.Rows)

    def _multi_selected_changed(self, new):
        if not self._no_update:
            values = self.value
            try:
                rows = [ values.index(i) for i in new]
            except:
                pass
            else:
                self._multi_selected_rows_changed(rows)

    def _multi_selected_items_changed(self, event):
        values = self.value
        try:
            added = [ values.index(item) for item in event.added ]
            removed = [ values.index(item) for item in event.removed ]
        except:
            pass
        else:
            list_event = TraitListEvent(0, added, removed)
            self._multi_selected_rows_items_changed(list_event)

    def _multi_selected_rows_changed(self, selected_rows):
        if not self._no_update:
            smodel = self.control.selectionModel()
            selection = QtGui.QItemSelection()
            for row in selected_rows:
                selection.select(self.model.index(row, 0), self.model.index(row, 0))
            smodel.clearSelection()
            smodel.select(selection,
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

    scroll_to_row_hint_map = {
        'center'  : QtGui.QTableView.PositionAtCenter,
        'top'     : QtGui.QTableView.PositionAtTop,
        'bottom'  : QtGui.QTableView.PositionAtBottom,
        'visible' : QtGui.QTableView.EnsureVisible,
    }

    def _scroll_to_row_changed(self, row):
        """ Scroll to the given row.
        """
        scroll_hint = self.scroll_to_row_hint_map.get(self.factory.scroll_to_row_hint, self.control.PositionAtCenter)
        self.control.scrollTo(self.model.index(row, 0), scroll_hint)

    #-- Table Control Event Handlers -------------------------------------------

    def _on_activate(self, index):
        """ Handle a cell being activated.
        """
        self.activated_row = row = index.row()
        self.activated = self.adapter.get_item(self.object, self.name, row)

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

    def _on_right_click(self, column):
        event = TabularEditorEvent(editor=self, row=0, column=column)
        setattr(self, 'right_clicked', event)

    def _on_column_right_click(self, column):
        event = TabularEditorEvent(editor=self, row=0, column=column)
        setattr(self, 'column_right_clicked', event)

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

    def _on_context_menu(self, pos) :
        column, row = self.control.columnAt(pos.x()), self.control.rowAt(pos.y())
        menu = self.adapter.get_menu(self.object, self.name, row, column)
        if menu :
            self._menu_context = {'selection' : self.object,
                             'object':  self.object,
                             'editor':  self,
                             'column':  column,
                             'row':     row,
                             'item':    self.adapter.get_item(self.object, self.name, row),
                             'info':    self.ui.info,
                             'handler': self.ui.handler }
            qmenu = menu.create_menu( self.control, self )
            qmenu.exec_(self.control.mapToGlobal(pos))
            self._menu_context = None

    def _on_column_context_menu(self, pos) :
        column = self.control.columnAt(pos.x())
        menu = self.adapter.get_column_menu(self.object, self.name, -1, column)
        if menu :
            self._menu_context = {'selection' : self.object, 'object':  self.object,
                             'editor':  self,
                             'column':  column,
                             'info':    self.ui.info,
                             'handler': self.ui.handler }
            qmenu = menu.create_menu( self.control, self )
            qmenu.exec_(self.control.mapToGlobal(pos))
            self._menu_context = None
        else:
            #If no menu is defined on the adapter, just trigger a click event.
            self._on_column_right_click(column)


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
        appropriate.
    """

    def __init__(self, table_view):
        """ Store which grid lines to draw.
        """
        QtGui.QStyledItemDelegate.__init__(self, table_view)
        self._horizontal_lines = table_view._editor.factory.horizontal_lines
        self._vertical_lines = table_view._editor.factory.vertical_lines

    def paint(self, painter, option, index):
        """ Overrident to draw gridlines.
        """
        QtGui.QStyledItemDelegate.paint(self, painter, option, index)
        painter.save()

        # FIXME: 'styleHint' is returning bogus (negative) values. Why?
        #style = QtGui.QApplication.instance().style()
        #color = style.styleHint(QtGui.QStyle.SH_Table_GridLineColor, option)
        #painter.setPen(QtGui.QColor(color))
        painter.setPen(option.palette.color(QtGui.QPalette.Dark))

        if self._horizontal_lines:
            painter.drawLine(option.rect.bottomLeft(),option.rect.bottomRight())
        if self._vertical_lines:
            painter.drawLine(option.rect.topRight(), option.rect.bottomRight())

        painter.restore()

class _TableView(QtGui.QTableView):
    """ A QTableView configured to behave as expected by TraitsUI.
    """

    def __init__(self, editor):
        """ Initialise the object.
        """
        QtGui.QTableView.__init__(self)

        self._initial_size = False
        self._editor = editor
        self.setModel(editor.model)
        factory = editor.factory

        # Configure the row headings
        vheader = self.verticalHeader()
        if factory.show_row_titles:
            vheader.setHighlightSections(False)
        else:
            vheader.hide()

        if factory.show_row_titles and factory.auto_resize_rows:
            vheader.setResizeMode(QtGui.QHeaderView.ResizeToContents)
        else:
            # Set a default height for rows. Although setting the resize mode to
            # ResizeToContents would provide the best sizes, this is far too
            # expensive when the TabularEditor has a large amount of data. Instead,
            # we make a reasonable guess based on the minimum size hint and the font
            # of the first row.
            size = vheader.minimumSectionSize()
            font = editor.adapter.get_font(editor.object, editor.name, 0)
            if font is not None:
                size = max(size, QtGui.QFontMetrics(QtGui.QFont(font)).height())
            vheader.setDefaultSectionSize(size)

        # Configure the column headings.
        hheader = self.horizontalHeader()
        hheader.setStretchLastSection(factory.stretch_last_section)
        if factory.show_titles:
            hheader.setHighlightSections(False)
        else:
            hheader.hide()

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

        # Configure drag and drop behavior
        self.setDragEnabled(True)
        if factory.editable:
            self.viewport().setAcceptDrops(True)
        if factory.drag_move:
            self.setDragDropMode(QtGui.QAbstractItemView.InternalMove)
        self.setDropIndicatorShown(True)

    def keyPressEvent(self, event):
        """ Reimplemented to support edit, insert, and delete by keyboard.
        """
        editor = self._editor
        factory = editor.factory

        # Note that setting 'EditKeyPressed' as an edit trigger does not work on
        # most platforms, which is why we do this here.
        if (event.key() in (QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return) and
            self.state() != QtGui.QAbstractItemView.EditingState and
            factory.editable and 'edit' in factory.operations):
            if factory.multi_select:
                rows = editor.multi_selected_rows
                row = rows[0] if len(rows) == 1 else -1
            else:
                row = editor.selected_row

            if row != -1:
                event.accept()
                self.edit(editor.model.index(row, 0))

        elif (event.key() in (QtCore.Qt.Key_Backspace, QtCore.Qt.Key_Delete) and
              factory.editable and 'delete' in factory.operations):
            event.accept()

            if factory.multi_select:
                for row in reversed(sorted(editor.multi_selected_rows)):
                    editor.model.removeRow(row)
            elif editor.selected_row != -1:
                editor.model.removeRow(editor.selected_row)

        elif (event.key() == QtCore.Qt.Key_Insert and
              factory.editable and 'insert' in factory.operations):
            event.accept()

            if factory.multi_select:
                rows = sorted(editor.multi_selected_rows)
                row = rows[0] if len(rows) else -1
            else:
                row = editor.selected_row
            if row == -1:
                row = editor.adapter.len(editor.object, editor.name)
            editor.model.insertRow(row)
            self.setCurrentIndex(editor.model.index(row, 0))

        else:
            QtGui.QTableView.keyPressEvent(self, event)

    def sizeHint(self):
        """ Reimplemented to define a reasonable size hint.
        """
        sh = QtGui.QTableView.sizeHint(self)

        width = 0
        for column in xrange(len(self._editor.adapter.columns)):
            width += self.sizeHintForColumn(column)
        sh.setWidth(width)

        return sh

    def resizeEvent(self, event):
        """ Reimplemented to size the table columns when the size of the table
            changes. Because the layout algorithm requires that the available
            space be known, we have to wait until the UI that contains this
            table gives it its initial size.
        """
        QtGui.QTableView.resizeEvent(self, event)

        parent = self.parent()
        if (not self._initial_size and parent and
            (self.isVisible() or isinstance(parent, QtGui.QMainWindow))):
            self._initial_size = True
            self.resizeColumnsToContents()

    def sizeHintForColumn(self, column):
        """ Reimplemented to support absolute width specification via
            TabularAdapters and to avoid scanning all data to determine the size
            hint. (TabularEditor, unlike TableEditor, is expected to handle very
            large data sets.)
        """
        editor = self._editor
        if editor.factory.auto_resize:
            # Use the default implementation.
            return super(_TableView, self).sizeHintForColumn(column)

        width = editor.adapter.get_width(editor.object, editor.name, column)
        if width > 1:
            return width
        else:
            return self.horizontalHeader().sectionSizeHint(column)

    def resizeColumnsToContents(self):
        """ Reimplemented to support proportional column width specifications.
            For information about the layout algorithm, see
            https://svn.enthought.com/enthought/wiki/Traits_3_0_tabular_editor.
        """
        editor = self._editor
        if editor.factory.auto_resize:
            # Use the default implementation.
            return super(_TableView, self).resizeColumnsToContents()
        available_space = self.viewport().width()
        hheader = self.horizontalHeader()

        # Assign sizes for columns with absolute size requests
        percent_vals, percent_cols = [], []
        for column in xrange(len(editor.adapter.columns)):
            width = editor.adapter.get_width(editor.object, editor.name, column)
            if width > 1:
                available_space -= width
                hheader.resizeSection(column, width)
            else:
                if width <= 0:
                    width = 0.1
                percent_vals.append(width)
                percent_cols.append(column)

        # Now use the remaining space for columns with proportional or no width
        # requests.
        percent_total = sum(percent_vals)
        for i, column in enumerate(percent_cols):
            percent = percent_vals[i] / percent_total
            width = max(30, int(percent * available_space))
            hheader.resizeSection(column, width)
