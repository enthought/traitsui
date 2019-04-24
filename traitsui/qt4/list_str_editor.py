#-------------------------------------------------------------------------
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
#  Date:   08/05/2009
#
#-------------------------------------------------------------------------

""" Traits UI editor for editing lists of strings.
"""

#-------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------

from __future__ import absolute_import
from pyface.qt import QtCore, QtGui
import collections

from pyface.image_resource import ImageResource
from traits.api import Any, Bool, Event, Int, Instance, List, \
    Property, Str, TraitListEvent, NO_COMPARE
from traitsui.list_str_adapter import ListStrAdapter

from .editor import Editor
from .list_str_model import ListStrModel
from traitsui.menu import Menu


is_qt5 = (QtCore.__version_info__[0] >= 5)

#-------------------------------------------------------------------------
#  '_ListStrEditor' class:
#-------------------------------------------------------------------------


class _ListStrEditor(Editor):
    """ Traits UI editor for editing lists of strings.
    """

    #-------------------------------------------------------------------------
    #  Trait definitions:
    #-------------------------------------------------------------------------

    # The list view control associated with the editor:
    list_view = Any

    # The list model associated the editor:
    model = Instance(ListStrModel)

    # The title of the editor:
    title = Str

    # The current set of selected items (which one is used depends upon the
    # initial state of the editor factory 'multi_select' trait):
    selected = Any
    multi_selected = List

    # The current set of selected item indices (which one is used depends upon
    # the initial state of the editor factory 'multi_select' trait):
    selected_index = Int(-1)
    multi_selected_indices = List(Int)

    # The most recently actived item and its index.
    # Always trigger change notification.
    activated = Any(comparison_mode=NO_COMPARE)
    activated_index = Int(comparison_mode=NO_COMPARE)

    # The most recently right_clicked item and its index:
    right_clicked = Event
    right_clicked_index = Event

    # Is the list editor scrollable? This value overrides the default.
    scrollable = True

    # Should the selected item be edited after rebuilding the editor list:
    edit = Bool(False)

    # The adapter from list items to editor values:
    adapter = Instance(ListStrAdapter)

    # Dictionary mapping image names to QIcons
    images = Any({})

    # Dictionary mapping ImageResource objects to QIcons
    image_resources = Any({})

    # The current number of item currently in the list:
    item_count = Property

    # The current search string:
    search = Str

    #-------------------------------------------------------------------------
    #  Editor interface:
    #-------------------------------------------------------------------------

    def init(self, parent):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        factory = self.factory

        # Set up the adapter to use:
        self.adapter = factory.adapter
        self.sync_value(factory.adapter_name, 'adapter', 'from')

        # Create the list model and accompanying controls:
        self.model = ListStrModel(editor=self)

        self.control = QtGui.QWidget()
        layout = QtGui.QVBoxLayout(self.control)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        if factory.title or factory.title_name:
            header_view = QtGui.QHeaderView(QtCore.Qt.Horizontal, self.control)
            header_view.setModel(self.model)
            header_view.setMaximumHeight(header_view.sizeHint().height())
            if is_qt5:
                header_view.setSectionResizeMode(QtGui.QHeaderView.Stretch)
            else:
                header_view.setResizeMode(QtGui.QHeaderView.Stretch)
            layout.addWidget(header_view)

        self.list_view = _ListView(self)
        layout.addWidget(self.list_view)

        # Set up the list control's event handlers:
        if factory.multi_select:
            slot = self._on_rows_selection
        else:
            slot = self._on_row_selection
        selection_model = self.list_view.selectionModel()
        selection_model.selectionChanged.connect(slot)

        self.list_view.activated.connect(self._on_activate)

        # Initialize the editor title:
        self.title = factory.title
        self.sync_value(factory.title_name, 'title', 'from')

        # Set up the selection listener
        if factory.multi_select:
            self.sync_value(factory.selected, 'multi_selected', 'both',
                            is_list=True)
            self.sync_value(factory.selected_index, 'multi_selected_indices',
                            'both', is_list=True)
        else:
            self.sync_value(factory.selected, 'selected', 'both')
            self.sync_value(factory.selected_index, 'selected_index', 'both')

        # Synchronize other interesting traits as necessary:
        self.sync_value(factory.activated, 'activated', 'to')
        self.sync_value(factory.activated_index, 'activated_index', 'to')

        self.sync_value(factory.right_clicked, 'right_clicked', 'to')
        self.sync_value(
            factory.right_clicked_index,
            'right_clicked_index',
            'to')

        # Make sure we listen for 'items' changes as well as complete list
        # replacements:
        self.context_object.on_trait_change(
            self.update_editor, self.extended_name + '_items', dispatch='ui')

        # Create the mapping from user supplied images to QIcons:
        for image_resource in factory.images:
            self._add_image(image_resource)

        # Refresh the editor whenever the adapter changes:
        self.on_trait_change(
            self.refresh_editor, 'adapter.+update', dispatch='ui')

        # Set the list control's tooltip:
        self.set_tooltip()

    def dispose(self):
        """ Disposes of the contents of an editor.
        """
        self.context_object.on_trait_change(
            self.update_editor, self.extended_name + '_items', remove=True)

        self.on_trait_change(
            self.refresh_editor, 'adapter.+update', remove=True)

        super(Editor, self).dispose()

    def update_editor(self):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        if not self._no_update:
            self.model.beginResetModel()
            self.model.endResetModel()
            # restore selection back
            if self.factory.multi_select:
                self._multi_selected_changed(self.multi_selected)
            else:
                self._selected_changed(self.selected)

    #-------------------------------------------------------------------------
    #  ListStrEditor interface:
    #-------------------------------------------------------------------------

    def refresh_editor(self):
        """ Requests that the underlying list widget to redraw itself.
        """
        self.list_view.viewport().update()

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

    def get_image(self, image):
        """ Converts a user specified image to a QIcon.
        """
        if isinstance(image, ImageResource):
            result = self.image_resources.get(image)
            if result is not None:
                return result

            return self._add_image(image)

        return self.images.get(image)

    def is_auto_add(self, index):
        """ Returns whether or not the index is the special 'auto add' item at
            the end of the list.
        """
        return (self.factory.auto_add and
                (index >= self.adapter.len(self.object, self.name)))

    #-------------------------------------------------------------------------
    #  Private interface:
    #-------------------------------------------------------------------------

    def _add_image(self, image_resource):
        """ Adds a new image to the image map.
        """
        image = image_resource.create_icon()

        self.image_resources[image_resource] = image
        self.images[image_resource.name] = image

        return image

    #-- Property Implementations ---------------------------------------------

    def _get_item_count(self):
        return (self.model.rowCount(None) - self.factory.auto_add)

    #-- Trait Event Handlers -------------------------------------------------

    def _selected_changed(self, selected):
        """ Handles the editor's 'selected' trait being changed.
        """
        if not self._no_update:
            try:
                selected_index = self.value.index(selected)
            except ValueError:
                pass
            else:
                self._selected_index_changed(selected_index)

    def _selected_index_changed(self, selected_index):
        """ Handles the editor's 'selected_index' trait being changed.
        """
        if not self._no_update:
            smodel = self.list_view.selectionModel()
            if selected_index == -1:
                smodel.clearSelection()
            else:
                mi = self.model.index(selected_index)
                smodel.select(mi, QtGui.QItemSelectionModel.ClearAndSelect)
                self.list_view.scrollTo(mi)

    def _multi_selected_changed(self, selected):
        """ Handles the editor's 'multi_selected' trait being changed.
        """
        if not self._no_update:
            indices = []
            for item in selected:
                try:
                    indices.append(self.value.index(item))
                except ValueError:
                    pass
            self._multi_selected_indices_changed(indices)

    def _multi_selected_items_changed(self, event):
        """ Handles the editor's 'multi_selected' trait being modified.
        """
        if not self._no_update:
            try:
                added = [self.value.index(item) for item in event.added]
                removed = [self.value.index(item) for item in event.removed]
            except ValueError:
                pass
            else:
                event = TraitListEvent(0, added, removed)
                self._multi_selected_indices_items_changed(event)

    def _multi_selected_indices_changed(self, selected_indices):
        """ Handles the editor's 'multi_selected_indices' trait being changed.
        """
        if not self._no_update:
            smodel = self.list_view.selectionModel()
            smodel.clearSelection()
            for selected_index in selected_indices:
                smodel.select(self.model.index(selected_index),
                              QtGui.QItemSelectionModel.Select)
            if selected_indices:
                self.list_view.scrollTo(self.model.index(selected_indices[-1]))

    def _multi_selected_indices_items_changed(self, event):
        """ Handles the editor's 'multi_selected_indices' trait being modified.
        """
        if not self._no_update:
            smodel = self.list_view.selectionModel()
            for selected_index in event.removed:
                smodel.select(self.model.index(selected_index),
                              QtGui.QItemSelectionModel.Deselect)
            for selected_index in event.added:
                smodel.select(self.model.index(selected_index),
                              QtGui.QItemSelectionModel.Select)

    #-- List Control Event Handlers ------------------------------------------

    def _on_activate(self, mi):
        """ Handle a cell being activated.
        """
        self.activated_index = index = mi.row()
        self.activated = self.adapter.get_item(self.object, self.name, index)

    def _on_context_menu(self, point):
        """ Handle a context menu request.
        """
        mi = self.list_view.indexAt(point)
        if mi.isValid():
            self.right_clicked_index = index = mi.row()
            self.right_clicked = self.adapter.get_item(
                self.object, self.name, index)

    def _on_row_selection(self, added, removed):
        """ Handle the row selection being changed.
        """
        self._no_update = True
        try:
            indices = self.list_view.selectionModel().selectedRows()
            if len(indices):
                self.selected_index = indices[0].row()
                self.selected = self.adapter.get_item(self.object, self.name,
                                                      self.selected_index)
            else:
                self.selected_index = -1
                self.selected = None
        finally:
            self._no_update = False

    def _on_rows_selection(self, added, removed):
        """ Handle the rows selection being changed.
        """
        self._no_update = True
        try:
            indices = self.list_view.selectionModel().selectedRows()
            self.multi_selected_indices = indices = [i.row() for i in indices]
            self.multi_selected = [self.adapter.get_item(self.object,
                                                         self.name, i)
                                   for i in self.multi_selected_indices]
        finally:
            self._no_update = False

    def _on_context_menu(self, pos):
        menu = self.factory.menu

        index = self.list_view.indexAt(pos).row()

        if isinstance(menu, str):
            menu = getattr(self.object, menu, None)

        if isinstance(menu, collections.Callable):
            menu = menu(index)

        if menu is not None:
            qmenu = menu.create_menu(self.list_view, self)

            self._menu_context = {'selection': self.object,
                                  'object': self.object,
                                  'editor': self,
                                  'index': index,
                                  'info': self.ui.info,
                                  'handler': self.ui.handler}

            qmenu.exec_(self.list_view.mapToGlobal(pos))

            self._menu_context = None

#-------------------------------------------------------------------------
#  Qt widgets that have been configured to behave as expected by Traits UI:
#-------------------------------------------------------------------------


class _ItemDelegate(QtGui.QStyledItemDelegate):
    """ A QStyledItemDelegate which optionally draws horizontal gridlines.
        (QListView does not support gridlines).
    """

    def __init__(self, editor, parent=None):
        """ Save the editor
        """
        QtGui.QStyledItemDelegate.__init__(self, parent)
        self._editor = editor

    def paint(self, painter, option, index):
        """ Overrident to draw gridlines.
        """
        QtGui.QStyledItemDelegate.paint(self, painter, option, index)
        if self._editor.factory.horizontal_lines:
            painter.save()
            painter.setPen(option.palette.color(QtGui.QPalette.Dark))
            painter.drawLine(
                option.rect.bottomLeft(),
                option.rect.bottomRight())
            painter.restore()


class _ListView(QtGui.QListView):
    """ A QListView configured to behave as expected by TraitsUI.
    """

    def __init__(self, editor):
        """ Initialise the object.
        """
        QtGui.QListView.__init__(self)

        self._editor = editor
        self.setItemDelegate(_ItemDelegate(editor, self))
        self.setModel(editor.model)
        factory = editor.factory

        # Configure the selection behavior
        if factory.multi_select:
            mode = QtGui.QAbstractItemView.ExtendedSelection
        else:
            mode = QtGui.QAbstractItemView.SingleSelection
        self.setSelectionMode(mode)

        # Configure drag and drop behavior
        self.setDragEnabled(True)
        self.setDragDropOverwriteMode(True)
        self.setDragDropMode(QtGui.QAbstractItemView.InternalMove)
        self.setDropIndicatorShown(True)

        if editor.factory.menu is False:
            self.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        elif editor.factory.menu is not False:
            self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

        self.customContextMenuRequested.connect(editor._on_context_menu)

        # Configure context menu behavior
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

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
                indices = editor.multi_selected_indices
                row = indices[0] if len(indices) == 1 else -1
            else:
                row = editor.selected_index

            if row != -1:
                event.accept()
                self.edit(editor.model.index(row))

        elif (event.key() in (QtCore.Qt.Key_Backspace, QtCore.Qt.Key_Delete) and
              factory.editable and 'delete' in factory.operations):
            event.accept()

            if factory.multi_select:
                for row in reversed(sorted(editor.multi_selected_indices)):
                    editor.model.removeRow(row)
            elif editor.selected_index != -1:
                # Deleting the selected item will reset cause the ListView's
                # selection model to select the next item before removing the
                # originally selected rows. Visually, this looks fine because
                # the next item is then placed where the deleted item used to
                # be. However, some internal state is kept which makes the
                # selected item seem off by one. So we'll reset it manually
                # here.
                row = editor.selected_index
                editor.model.removeRow(row)
                # Handle the case of deleting the last item in the list.
                editor.selected_index = min(
                    row, editor.adapter.len(editor.object, editor.name) - 1)

        elif (event.key() == QtCore.Qt.Key_Insert and
              factory.editable and 'insert' in factory.operations):
            event.accept()

            if factory.multi_select:
                indices = sorted(editor.multi_selected_indices)
                row = indices[0] if len(indices) else -1
            else:
                row = editor.selected_index
            if row == -1:
                row = editor.adapter.len(editor.object, editor.name)
            editor.model.insertRow(row)
            self.setCurrentIndex(editor.model.index(row))

        else:
            QtGui.QListView.keyPressEvent(self, event)
