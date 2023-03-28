# (C) Copyright 2008-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

# ------------------------------------------------------------------------------
# Copyright (c) 2007, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD license.
# However, when used with the GPL version of PyQt the additional terms
# described in the PyQt GPL exception also apply

#
# Author: Riverbank Computing Limited
# ------------------------------------------------------------------------------

""" Defines the tree editor for the PyQt user interface toolkit.
"""


import copy
import collections.abc
from functools import partial
from itertools import zip_longest
import logging

from pyface.qt import QtCore, QtGui, is_qt5

from pyface.api import ImageResource
from pyface.ui_traits import convert_image
from pyface.timer.api import do_later
from traits.api import Any, Event, Int
from traitsui.editors.tree_editor import (
    CopyAction,
    CutAction,
    DeleteAction,
    NewAction,
    PasteAction,
    RenameAction,
)
from traitsui.tree_node import (
    ITreeNodeAdapterBridge,
    MultiTreeNode,
    ObjectTreeNode,
    TreeNode,
)
from traitsui.menu import Menu, Action, Separator
from traitsui.ui_traits import SequenceTypes
from traitsui.undo import ListUndoItem

from .clipboard import clipboard, PyMimeData
from .editor import Editor
from .helper import pixmap_cache, qobject_is_valid
from .tree_node_renderers import WordWrapRenderer


logger = logging.getLogger(__name__)


# The renderer to use when word_wrap is True.
DEFAULT_WRAP_RENDERER = WordWrapRenderer()


class SimpleEditor(Editor):
    """Simple style of tree editor."""

    # -------------------------------------------------------------------------
    #  Trait definitions:
    # -------------------------------------------------------------------------

    #: Is the tree editor is scrollable? This value overrides the default.
    scrollable = True

    #: Allows an external agent to set the tree selection
    selection = Event()

    #: The currently selected object
    selected = Any()

    #: The event fired when a tree node is activated by double clicking or
    #: pressing the Enter key on a node.
    activated = Event()

    #: The event fired when a tree node is clicked on:
    click = Event()

    #: The event fired when a tree node is double-clicked on:
    dclick = Event()

    #: The event fired when the application wants to veto an operation:
    veto = Event()

    #: The vent fired when the application wants to refresh the viewport.
    refresh = Event()

    def init(self, parent):
        """Finishes initializing the editor by creating the underlying toolkit
        widget.
        """
        factory = self.factory

        self._editor = None

        if factory.editable:

            # Check to see if the tree view is based on a shared trait editor:
            if factory.shared_editor:
                factory_editor = factory.editor

                # If this is the editor that defines the trait editor panel:
                if factory_editor is None:

                    # Remember which editor has the trait editor in the
                    # factory:
                    factory._editor = self

                    # Create the trait editor panel:
                    self.control = sa = QtGui.QScrollArea()
                    sa.setFrameShape(QtGui.QFrame.Shape.NoFrame)
                    sa.setWidgetResizable(True)
                    self.control._node_ui = self.control._editor_nid = None

                    # Check to see if there are any existing editors that are
                    # waiting to be bound to the trait editor panel:
                    editors = factory._shared_editors
                    if editors is not None:
                        for editor in factory._shared_editors:

                            # If the editor is part of this UI:
                            if editor.ui is self.ui:

                                # Then bind it to the trait editor panel:
                                editor._editor = self.control

                        # Indicate all pending editors have been processed:
                        factory._shared_editors = None

                    # We only needed to build the trait editor panel, so exit:
                    return

                # Check to see if the matching trait editor panel has been
                # created yet:
                editor = factory_editor._editor
                if (editor is None) or (editor.ui is not self.ui):
                    # If not, add ourselves to the list of pending editors:
                    shared_editors = factory_editor._shared_editors
                    if shared_editors is None:
                        factory_editor._shared_editors = shared_editors = []
                    shared_editors.append(self)
                else:
                    # Otherwise, bind our trait editor panel to the shared one:
                    self._editor = editor.control

                # Finally, create only the tree control:
                self.control = self._tree = _TreeWidget(self)
            else:
                # If editable, create a tree control and an editor panel:
                self._tree = _TreeWidget(self)

                self._editor = sa = QtGui.QScrollArea()
                sa.setFrameShape(QtGui.QFrame.Shape.NoFrame)
                sa.setWidgetResizable(True)
                sa._node_ui = sa._editor_nid = None

                if factory.orientation == "horizontal":
                    orient = QtCore.Qt.Orientation.Horizontal
                else:
                    orient = QtCore.Qt.Orientation.Vertical

                self.control = splitter = QtGui.QSplitter(orient)
                splitter.setSizePolicy(
                    QtGui.QSizePolicy.Policy.Expanding, QtGui.QSizePolicy.Policy.Expanding
                )
                splitter.addWidget(self._tree)
                splitter.addWidget(sa)
        else:
            # Otherwise, just create the tree control:
            self.control = self._tree = _TreeWidget(self)

        # Create our item delegate
        delegate = TreeItemDelegate()
        delegate.editor = self
        self._tree.setItemDelegate(delegate)
        # From Qt Docs: QAbstractItemView does not take ownership of `delegate`
        self._item_delegate = delegate

        # Set up the mapping between objects and tree id's:
        self._map = {}

        # Initialize the 'undo state' stack:
        self._undoable = []

        # Synchronize external object traits with the editor:
        self.sync_value(factory.refresh, "refresh")
        self.sync_value(factory.selected, "selected")
        self.sync_value(factory.activated, "activated", "to")
        self.sync_value(factory.click, "click", "to")
        self.sync_value(factory.dclick, "dclick", "to")
        self.sync_value(factory.veto, "veto", "from")

    def _selection_changed(self, selection):
        """Handles the **selection** event."""
        try:
            tree = self._tree
            if not isinstance(selection, str) and isinstance(
                selection, collections.abc.Iterable
            ):

                item_selection = QtGui.QItemSelection()
                for sel in selection:
                    item = self._object_info(sel)[2]
                    idx = tree.indexFromItem(item)
                    item_selection.append(QtGui.QItemSelectionRange(idx))

                tree.selectionModel().select(
                    item_selection, QtGui.QItemSelectionModel.SelectionFlag.ClearAndSelect
                )
            else:
                tree.setCurrentItem(self._object_info(selection)[2])
        except:
            from traitsui.api import raise_to_debug

            raise_to_debug()

    def _selected_changed(self, selected):
        """Handles the **selected** trait being changed."""
        if not self._no_update_selected:
            self._selection_changed(selected)

    def _veto_changed(self):
        """Handles the 'veto' event being fired."""
        self._veto = True

    def _refresh_changed(self):
        """Update the viewport."""
        self._tree.viewport().update()

    def dispose(self):
        """Disposes of the contents of an editor."""
        if self._tree is not None:
            # Stop the chatter (specifically about the changing selection).
            self._tree.blockSignals(True)

            self._delete_node(self._tree.invisibleRootItem())

            self._tree = None

        super().dispose()

    def expand_levels(self, nid, levels, expand=True):
        """Expands from the specified node the specified number of sub-levels."""
        if levels > 0:
            try:
                expanded, node, object = self._get_node_data(nid)
            except Exception:
                # node is either not ready or has been deleted
                return
            if self._has_children(node, object):
                self._expand_node(nid)
                if expand:
                    nid.setExpanded(True)
                for cnid in self._nodes_for(nid):
                    self.expand_levels(cnid, levels - 1)

    def expand_all(self):
        """Expands all expandable nodes in the tree.

        Warning: If the Tree contains a large number of items, this function
        will be very slow.
        """
        # For more info on the QtGui.QTreeWidgetItemIterator object,
        # see https://doc.qt.io/qt-5/qtreewidgetitemiterator.html
        iterator = QtGui.QTreeWidgetItemIterator(self._tree)
        while iterator.value():
            item = iterator.value()
            try:
                expanded, node, object = self._get_node_data(item)
            except Exception:
                # node is either not ready or has been deleted
                continue
            if self._has_children(node, object):
                self._expand_node(item)
                item.setExpanded(True)
            iterator += 1

    def update_editor(self):
        """Updates the editor when the object trait changes externally to the
        editor.
        """
        tree = self._tree
        if tree is None:
            return
        saved_state = {}

        object, node = self._node_for(self.old_value)
        old_nid = self._get_object_nid(object, node.get_children_id(object))
        if old_nid:
            self._delete_node(old_nid)

        object, node = self._node_for(self.old_value)
        old_nid = self._get_object_nid(object, node.get_children_id(object))
        if old_nid:
            self._delete_node(old_nid)

        tree.clear()
        self._map = {}

        object, node = self._node_for(self.value)
        if node is not None:
            if self.factory.hide_root:
                nid = tree.invisibleRootItem()
            else:
                nid = self._create_item(tree, node, object)

            self._map[id(object)] = [(node.get_children_id(object), nid)]
            self._add_listeners(node, object)
            self._set_node_data(nid, (False, node, object))
            if self.factory.hide_root or self._has_children(node, object):
                self._expand_node(nid)
                if not self.factory.hide_root:
                    nid.setExpanded(True)
                    tree.setCurrentItem(nid)

            self.expand_levels(nid, self.factory.auto_open, False)
        ncolumns = self._tree.columnCount()
        if ncolumns > 1:
            for i in range(ncolumns):
                self._tree.resizeColumnToContents(i)
        # FIXME: Clear the current editor (if any)...

    def get_error_control(self):
        """Returns the editor's control for indicating error status."""
        return self._tree

    def _get_brush(self, color):
        if isinstance(color, SequenceTypes):
            q_color = QtGui.QColor(*color)
        else:
            q_color = QtGui.QColor(color)
        return QtGui.QBrush(q_color)

    def _set_column_labels(self, nid, node, object):
        """Set the column labels."""
        column_labels = node.get_column_labels(object)

        for i, (header, label) in enumerate(
            zip_longest(self.factory.column_headers[1:], column_labels), 1
        ):
            renderer = node.get_renderer(object, i)
            handles_text = renderer.handles_text if renderer else False
            if header is None or label is None or handles_text:
                nid.setText(i, "")
            else:
                nid.setText(i, label)

    def _create_item(self, nid, node, object, index=None):
        """Create  a new TreeWidgetItem as per word_wrap policy.

        Index is the index of the new node in the parent:
            None implies append the child to the end."""
        if index is None:
            cnid = QtGui.QTreeWidgetItem(nid)
        else:
            cnid = QtGui.QTreeWidgetItem()
            nid.insertChild(index, cnid)

        renderer = node.get_renderer(object)
        handles_text = getattr(renderer, "handles_text", False)
        handles_icon = getattr(renderer, "handles_icon", False)
        if not (self.factory.word_wrap or handles_text):
            cnid.setText(0, node.get_label(object))
        if not handles_icon:
            cnid.setIcon(0, self._get_icon(node, object))
        cnid.setToolTip(0, node.get_tooltip(object))

        self._set_column_labels(cnid, node, object)

        color = node.get_background(object)
        if color:
            cnid.setBackground(0, self._get_brush(color))
        color = node.get_foreground(object)
        if color:
            cnid.setForeground(0, self._get_brush(color))

        return cnid

    def _set_label(self, nid, col=0):
        """Set the label of the specified item"""
        if col != 0:
            # these are handled by _set_column_labels
            return
        try:
            expanded, node, object = self._get_node_data(nid)
        except Exception:
            # node is either not ready or has been deleted
            return
        renderer = node.get_renderer(object)
        handles_text = getattr(renderer, "handles_text", False)
        if self.factory.word_wrap or handles_text:
            nid.setText(col, "")
        else:
            nid.setText(col, node.get_label(object))

    def _append_node(self, nid, node, object):
        """Appends a new node to the specified node."""
        return self._insert_node(nid, None, node, object)

    def _insert_node(self, nid, index, node, object):
        """Inserts a new node before a specified index into the children of the
        specified node.
        """

        cnid = self._create_item(nid, node, object, index)

        has_children = self._has_children(node, object)
        self._set_node_data(cnid, (False, node, object))
        self._map.setdefault(id(object), []).append(
            (node.get_children_id(object), cnid)
        )
        self._add_listeners(node, object)

        # Automatically expand the new node (if requested):
        if has_children:
            if node.can_auto_open(object):
                cnid.setExpanded(True)
            else:
                # Qt only draws the control that expands the tree if there is a
                # child.  As the tree is being populated lazily we create a
                # dummy that will be removed when the node is expanded for the
                # first time.
                cnid._dummy = QtGui.QTreeWidgetItem(cnid)

        # Return the newly created node:
        return cnid

    def _delete_node(self, nid):
        """Deletes a specified tree node and all its children."""

        for cnid in self._nodes_for(nid):
            self._delete_node(cnid)

        # See if it is a dummy.
        pnid = nid.parent()
        if pnid is not None and getattr(pnid, "_dummy", None) is nid:
            pnid.removeChild(nid)
            del pnid._dummy
            return

        try:
            expanded, node, object = self._get_node_data(nid)
        except Exception:
            # The node has already been deleted.
            pass
        else:
            id_object = id(object)
            object_info = self._map[id_object]
            for i, info in enumerate(object_info):
                # QTreeWidgetItem does not have an equal operator, so use id()
                if id(nid) == id(info[1]):
                    del object_info[i]
                    break

            if len(object_info) == 0:
                self._remove_listeners(node, object)
                del self._map[id_object]

        if pnid is None:
            self._tree.takeTopLevelItem(self._tree.indexOfTopLevelItem(nid))
        else:
            pnid.removeChild(nid)

        # If the deleted node had an active editor panel showing, remove it:
        # Note: QTreeWidgetItem does not have an equal operator, so use id()
        if (self._editor is not None) and (
            id(nid) == id(self._editor._editor_nid)
        ):
            self._clear_editor()

    def _expand_node(self, nid):
        """Expands the contents of a specified node (if required)."""
        try:
            expanded, node, object = self._get_node_data(nid)
        except Exception:
            # The node has already been deleted.
            return

        # Lazily populate the item's children:
        if not expanded:
            # Remove any dummy node.
            dummy = getattr(nid, "_dummy", None)
            if dummy is not None:
                nid.removeChild(dummy)
                del nid._dummy

            for child in node.get_children(object):
                child, child_node = self._node_for(child)
                if child_node is not None:
                    self._append_node(nid, child_node, child)

            # Indicate the item is now populated:
            self._set_node_data(nid, (True, node, object))

    def _nodes_for(self, nid):
        """Returns all child node ids of a specified node id."""
        return [nid.child(i) for i in range(nid.childCount())]

    def _node_index(self, nid):
        pnid = nid.parent()
        if pnid is None:
            if self.factory.hide_root:
                pnid = self._tree.invisibleRootItem()
            if pnid is None:
                return (None, None, None)

        for i in range(pnid.childCount()):
            if pnid.child(i) is nid:
                try:
                    _, pnode, pobject = self._get_node_data(pnid)
                except Exception:
                    continue
                return (pnode, pobject, i)
        else:
            # doesn't match any node, so return None
            return (None, None, None)

    def _has_children(self, node, object):
        """Returns whether a specified object has any children."""
        return node.allows_children(object) and node.has_children(object)

    # -------------------------------------------------------------------------
    #  Returns the icon index for the specified object:
    # -------------------------------------------------------------------------

    STD_ICON_MAP = {
        "<item>": QtGui.QStyle.StandardPixmap.SP_FileIcon,
        "<group>": QtGui.QStyle.StandardPixmap.SP_DirClosedIcon,
        "<open>": QtGui.QStyle.StandardPixmap.SP_DirOpenIcon,
    }

    def _get_icon(self, node, object, is_expanded=False):
        """Returns the index of the specified object icon."""
        if not self.factory.show_icons:
            return QtGui.QIcon()

        icon_name = node.get_icon(object, is_expanded)
        if isinstance(icon_name, str):
            if icon_name.startswith("@"):
                image_resource = convert_image(icon_name, 4)
                return image_resource.create_icon()
            elif icon_name in self.STD_ICON_MAP:
                icon = self.STD_ICON_MAP[icon_name]
                return self._tree.style().standardIcon(icon)

            path = node.get_icon_path(object)
            if isinstance(path, str):
                path = [path, node]
            else:
                path = path + [node]

            image_resource = ImageResource(icon_name, path)

        elif isinstance(icon_name, ImageResource):
            image_resource = icon_name

        elif isinstance(icon_name, tuple):
            if max(icon_name) <= 1.0:
                # rgb(a) color tuple between 0.0 and 1.0
                color = QtGui.QColor.fromRgbF(*icon_name)
            else:
                # rgb(a) color tuple between 0 and 255
                color = QtGui.QColor.fromRgb(*icon_name)
            return self._icon_from_color(color)

        elif isinstance(icon_name, QtGui.QColor):
            return self._icon_from_color(icon_name)

        else:
            raise ValueError(
                "Icon value must be a string or color or color tuple or "
                + "IImageResource instance: "
                + "given {!r}".format(icon_name)
            )

        file_name = image_resource.absolute_path
        return QtGui.QIcon(pixmap_cache(file_name))

    def _icon_from_color(self, color):
        """Create a square icon filled with the given color."""
        pixmap = QtGui.QPixmap(self._tree.iconSize())
        pixmap.fill(color)
        return QtGui.QIcon(pixmap)

    def _add_listeners(self, node, object):
        """Adds the event listeners for a specified object."""

        if node.allows_children(object):
            node.when_children_replaced(object, self._children_replaced, False)
            node.when_children_changed(object, self._children_updated, False)

        node.when_label_changed(object, self._label_updated, False)
        node.when_column_labels_change(
            object, self._column_labels_updated, False
        )

    def _remove_listeners(self, node, object):
        """Removes any event listeners from a specified object."""

        if node.allows_children(object):
            node.when_children_replaced(object, self._children_replaced, True)
            node.when_children_changed(object, self._children_updated, True)

        node.when_label_changed(object, self._label_updated, True)
        node.when_column_labels_change(
            object, self._column_labels_updated, True
        )

    def _object_info(self, object, name=""):
        """Returns the tree node data for a specified object in the form
        ( expanded, node, nid ).
        """
        info = self._map[id(object)]
        for name2, nid in info:
            if name == name2:
                break
        else:
            nid = info[0][1]

        expanded, node, ignore = self._get_node_data(nid)

        return (expanded, node, nid)

    def _object_info_for(self, object, name=""):
        """Returns the tree node data for a specified object as a list of the
        form: [ ( expanded, node, nid ), ... ].
        """
        result = []
        for name2, nid in self._map[id(object)]:
            if name == name2:
                try:
                    expanded, node, object = self._get_node_data(nid)
                except Exception:
                    # The node has already been deleted.
                    continue
                result.append((expanded, node, nid))

        return result

    def _node_for(self, object):
        """Returns the TreeNode associated with a specified object."""
        if (
            (isinstance(object, tuple))
            and (len(object) == 2)
            and isinstance(object[1], TreeNode)
        ):
            return object

        # Select all nodes which understand this object:
        factory = self.factory
        nodes = [node for node in factory.nodes if node.is_node_for(object)]

        # If only one found, we're done, return it:
        if len(nodes) == 1:
            return (object, nodes[0])

        # If none found, give up:
        if len(nodes) == 0:
            return (object, ITreeNodeAdapterBridge(adapter=object))

        # Use all selected nodes that have the same 'node_for' list as the
        # first selected node:
        base = nodes[0].node_for
        nodes = [node for node in nodes if base == node.node_for]

        # If only one left, then return that node:
        if len(nodes) == 1:
            return (object, nodes[0])

        # Otherwise, return a MultiTreeNode based on all selected nodes...

        # Use the node with no specified children as the root node. If not
        # found, just use the first selected node as the 'root node':
        root_node = None
        for i, node in enumerate(nodes):
            if node.children == "":
                root_node = node
                del nodes[i]
                break
        else:
            root_node = nodes[0]

        # If we have a matching MultiTreeNode already cached, return it:
        key = (root_node,) + tuple(nodes)
        if key in factory.multi_nodes:
            return (object, factory.multi_nodes[key])

        # Otherwise create one, cache it, and return it:
        factory.multi_nodes[key] = multi_node = MultiTreeNode(
            root_node=root_node, nodes=nodes
        )

        return (object, multi_node)

    def _node_for_class(self, klass):
        """Returns the TreeNode associated with a specified class."""
        for node in self.factory.nodes:
            if issubclass(klass, tuple(node.node_for)):
                return node
        return None

    def _update_icon(self, nid):
        """Updates the icon for a specified node."""
        try:
            expanded, node, object = self._get_node_data(nid)
        except Exception:
            # The node has already been deleted.
            return
        renderer = node.get_renderer(object)
        if renderer is None or not renderer.handles_icon:
            nid.setIcon(0, self._get_icon(node, object, expanded))
        else:
            nid.setIcon(0, QtGui.QIcon())

    def _begin_undo(self):
        """Begins an "undoable" transaction."""
        ui = self.ui
        self._undoable.append(ui._undoable)
        if (ui._undoable == -1) and (ui.history is not None):
            ui._undoable = ui.history.now

    def _end_undo(self):
        if self._undoable.pop() == -1:
            self.ui._undoable = -1

    def _get_undo_item(self, object, name, event):
        return ListUndoItem(
            object=object,
            name=name,
            index=event.index,
            added=event.added,
            removed=event.removed,
        )

    def _undoable_append(self, node, object, data, make_copy=True):
        """Performs an undoable append operation."""
        try:
            self._begin_undo()
            if make_copy:
                data = copy.deepcopy(data)
            node.append_child(object, data)
        finally:
            self._end_undo()

    def _undoable_insert(self, node, object, index, data, make_copy=True):
        """Performs an undoable insert operation."""
        try:
            self._begin_undo()
            if make_copy:
                data = copy.deepcopy(data)
            node.insert_child(object, index, data)
        finally:
            self._end_undo()

    def _undoable_delete(self, node, object, index):
        """Performs an undoable delete operation."""
        try:
            self._begin_undo()
            node.delete_child(object, index)
        finally:
            self._end_undo()

    def _get_object_nid(self, object, name=""):
        """Gets the ID associated with a specified object (if any)."""
        info = self._map.get(id(object))
        if info is None:
            return None
        for name2, nid in info:
            if name == name2:
                return nid
        else:
            return info[0][1]

    def _clear_editor(self):
        """Clears the current editor pane (if any)."""
        editor = self._editor
        if editor._node_ui is not None:
            editor.setWidget(None)
            editor._node_ui.dispose()
            editor._node_ui = editor._editor_nid = None

    # -------------------------------------------------------------------------
    #  Gets/Sets the node specific data:
    # -------------------------------------------------------------------------

    @staticmethod
    def _get_node_data(nid):
        """Gets the node specific data."""
        if not qobject_is_valid(nid):
            raise RuntimeError(f"Qt object {nid} for node nolonger exists.")
        return nid._py_data

    @staticmethod
    def _set_node_data(nid, data):
        """Sets the node specific data."""
        nid._py_data = data

    # ----- User callable methods: --------------------------------------------

    def get_object(self, nid):
        """Gets the object associated with a specified node."""
        return self._get_node_data(nid)[2]

    def get_parent(self, object, name=""):
        """Returns the object that is the immmediate parent of a specified
        object in the tree.
        """
        nid = self._get_object_nid(object, name)
        if nid is not None:
            pnid = nid.parent()
            if pnid is not self._tree.invisibleRootItem():
                return self.get_object(pnid)
        return None

    def get_node(self, object, name=""):
        """Returns the node associated with a specified object."""
        nid = self._get_object_nid(object, name)
        if nid is not None:
            return self._get_node_data(nid)[1]
        return None

    # ----- Tree event handlers: ----------------------------------------------

    def _on_item_expanded(self, nid):
        """Handles a tree node being expanded."""
        try:
            _, node, object = self._get_node_data(nid)
        except Exception:
            # The node has already been deleted.
            return

        # If 'auto_close' requested for this node type, close all of the node's
        # siblings:
        if node.can_auto_close(object):
            parent = nid.parent()

            if parent is not None:
                for snid in self._nodes_for(parent):
                    if snid is not nid:
                        snid.setExpanded(False)

        # Expand the node (i.e. populate its children if they are not there
        # yet):
        self._expand_node(nid)

        self._update_icon(nid)

    def _on_item_collapsed(self, nid):
        """Handles a tree node being collapsed."""
        self._update_icon(nid)

    def _on_item_clicked(self, nid, col):
        """Handles a tree item being clicked."""
        try:
            _, node, object = self._get_node_data(nid)
        except Exception:
            # The node has already been deleted.
            return

        if node.click(object) is True and self.factory.on_click is not None:
            self.ui.evaluate(self.factory.on_click, object)

        # Fire the 'click' event with the object as its value:
        self.click = object

    def _on_item_dclicked(self, nid, col):
        """Handles a tree item being double-clicked."""
        try:
            _, node, object = self._get_node_data(nid)
        except Exception:
            # The node has already been deleted.
            return

        if node.dclick(object) is True:
            if self.factory.on_dclick is not None:
                self.ui.evaluate(self.factory.on_dclick, object)
                self._veto = True
        else:
            self._veto = True

        # Fire the 'dclick' event with the clicked on object as value:
        self.dclick = object

    def _on_item_activated(self, nid, col):
        """Handles a tree item being activated."""
        try:
            _, node, object = self._get_node_data(nid)
        except Exception:
            # The node has already been deleted.
            return

        if node.activated(object) is True:
            if self.factory.on_activated is not None:
                self.ui.evaluate(self.factory.on_activated, object)
                self._veto = True
        else:
            self._veto = True

        # Fire the 'activated' event with the clicked on object as value:
        self.activated = object

    def _on_tree_sel_changed(self):
        """Handles a tree node being selected."""
        # Get the new selection:
        nids = self._tree.selectedItems()

        selected = []
        first = True
        for nid in nids:
            try:
                node = self._get_node_data(nid)[2]
            except Exception:
                continue
            selected.append(node)
        for nid in nids:
            # If there is a real selection, get the associated object:
            try:
                expanded, sel_node, sel_object = self._get_node_data(nid)
            except Exception:
                continue

            # Try to inform the node specific handler of the selection, if
            # there are multiple selections, we only care about the first
            if first:
                node = sel_node
                object = sel_object
                not_handled = node.select(sel_object)
                first = False

        if len(selected) == 0:
            nid = None
            object = None
            not_handled = True

        # Set the value of the new selection:
        if self.factory.selection_mode == "single":
            self._no_update_selected = True
            self.selected = object
            self._no_update_selected = False
        else:
            self._no_update_selected = True
            self.selected = selected
            self._no_update_selected = False

        # If no one has been notified of the selection yet, inform the editor's
        # select handler (if any) of the new selection:
        if not_handled is True:
            self.ui.evaluate(self.factory.on_select, object)

        # Check to see if there is an associated node editor pane:
        editor = self._editor
        if editor is not None:
            # If we already had a node editor, destroy it:
            editor.setUpdatesEnabled(False)
            self._clear_editor()

            # If there is a selected object, create a new editor for it:
            if object is not None:
                # Try to chain the undo history to the main undo history:
                view = node.get_view(object)
                if view is None or isinstance(view, str):
                    view = object.trait_view(view)

                if (self.ui.history is not None) or (view.kind == "subpanel"):
                    ui = object.edit_traits(
                        parent=editor, view=view, kind="subpanel"
                    )
                else:
                    # Otherwise, just set up our own new one:
                    ui = object.edit_traits(
                        parent=editor, view=view, kind="panel"
                    )

                # Make our UI the parent of the new UI:
                ui.parent = self.ui

                # Remember the new editor's UI and node info:
                editor._node_ui = ui
                editor._editor_nid = nid

                # Finish setting up the editor:
                if ui.control.layout() is not None:
                    ui.control.layout().setContentsMargins(0, 0, 0, 0)
                editor.setWidget(ui.control)

            # Allow the editor view to show any changes that have occurred:
            editor.setUpdatesEnabled(True)

    def _on_context_menu(self, pos):
        """Handles the user requesting a context menu on a tree node."""
        nid = self._tree.itemAt(pos)

        if nid is None:
            return

        try:
            _, node, object = self._get_node_data(nid)
        except Exception:
            return

        self._data = (node, object, nid)
        self._context = {
            "object": object,
            "editor": self,
            "node": node,
            "info": self.ui.info,
            "handler": self.ui.handler,
        }

        # Try to get the parent node of the node clicked on:
        pnid = nid.parent()
        if pnid is None or pnid is self._tree.invisibleRootItem():
            parent_node = parent_object = None
        else:
            _, parent_node, parent_object = self._get_node_data(pnid)

        self._menu_node = node
        self._menu_parent_node = parent_node
        self._menu_parent_object = parent_object

        menu = node.get_menu(object)

        if menu is None:
            # Use the standard, default menu:
            menu = self._standard_menu(node, object)

        elif isinstance(menu, Menu):
            # Use the menu specified by the node:
            group = menu.find_group(NewAction)
            if group is not None:
                # Reset the group for the current usage in case it is shared
                # - the call to `node.get_add()` is potentially dynamic and
                # the callback `_menu_new_node()` captures state about this
                # particular TreeEditor instance
                group.clear()
                actions = self._new_actions(node, object)
                if len(actions) > 0:
                    group.insert(0, Menu(name="New", *actions))

        else:
            # All other values mean no menu should be displayed:
            menu = None

        # Only display the menu if a valid menu is defined:
        if menu is not None:
            qmenu = menu.create_menu(self._tree, self)
            qmenu.exec_(self._tree.mapToGlobal(pos))

        # Reset all menu related cached values:
        self._data = (
            self._context
        ) = (
            self._menu_node
        ) = self._menu_parent_node = self._menu_parent_object = None

    def _standard_menu(self, node, object):
        """Returns the standard contextual pop-up menu."""
        actions = [
            CutAction,
            CopyAction,
            PasteAction,
            Separator(),
            DeleteAction,
            Separator(),
            RenameAction,
        ]

        # See if the 'New' menu section should be added:
        items = self._new_actions(node, object)
        if len(items) > 0:
            actions[0:0] = [Menu(name="New", *items), Separator()]

        return Menu(*actions)

    def _new_actions(self, node, object):
        """Returns a list of Actions that will create new objects."""
        object = self._data[1]
        items = []
        add = node.get_add(object)
        # return early if there are no items to be added in the tree
        if len(add) == 0:
            return items

        for klass in add:
            prompt = False
            factory = None
            if isinstance(klass, tuple):
                if len(klass) == 2:
                    klass, prompt = klass
                elif len(klass) == 3:
                    klass, prompt, factory = klass
            add_node = self._node_for_class(klass)
            if add_node is None:
                continue
            class_name = klass.__name__
            name = add_node.get_name(object)
            if name == "":
                name = class_name
            if factory is None:
                factory = klass

            def perform_add(object, factory, prompt):
                self._menu_new_node(factory, prompt)

            on_perform = partial(perform_add, factory=factory, prompt=prompt)
            items.append(Action(name=name, on_perform=on_perform))
        return items

    # -------------------------------------------------------------------------
    #  Menu action helper methods:
    # -------------------------------------------------------------------------

    def _is_copyable(self, object):
        parent = self._menu_parent_node
        if isinstance(parent, ObjectTreeNode):
            return parent.can_copy(self._menu_parent_object)
        return (parent is not None) and parent.can_copy(object)

    def _is_cutable(self, object):
        parent = self._menu_parent_node
        if isinstance(parent, ObjectTreeNode):
            can_cut = parent.can_copy(
                self._menu_parent_object
            ) and parent.can_delete(self._menu_parent_object)
        else:
            can_cut = (
                (parent is not None)
                and parent.can_copy(object)
                and parent.can_delete(object)
            )
        return can_cut and self._menu_node.can_delete_me(object)

    def _is_pasteable(self, object):
        return self._menu_node.can_add(object, clipboard.instance_type)

    def _is_deletable(self, object):
        parent = self._menu_parent_node
        if isinstance(parent, ObjectTreeNode):
            can_delete = parent.can_delete(self._menu_parent_object)
        else:
            can_delete = (parent is not None) and parent.can_delete(object)
        return can_delete and self._menu_node.can_delete_me(object)

    def _is_renameable(self, object):
        parent = self._menu_parent_node
        if isinstance(parent, ObjectTreeNode):
            can_rename = parent.can_rename(self._menu_parent_object)
        else:
            can_rename = (parent is not None) and parent.can_rename(object)

        can_rename = can_rename and self._menu_node.can_rename_me(object)

        # Set the widget item's editable flag appropriately.
        nid = self._get_object_nid(object)
        flags = nid.flags()
        if can_rename:
            flags |= QtCore.Qt.ItemFlag.ItemIsEditable
        else:
            flags &= ~QtCore.Qt.ItemFlag.ItemIsEditable
        nid.setFlags(flags)

        return can_rename

    def _is_droppable(self, node, object, add_object, for_insert):
        """Returns whether a given object is droppable on the node."""
        if for_insert and (not node.can_insert(object)):
            return False

        return node.can_add(object, add_object)

    def _drop_object(self, node, object, dropped_object, make_copy=True):
        """Returns a droppable version of a specified object."""
        new_object = node.drop_object(object, dropped_object)
        if (new_object is not dropped_object) or (not make_copy):
            return new_object

        return copy.deepcopy(new_object)

    # ----- pyface.action 'controller' interface implementation: --------------

    def add_to_menu(self, menu_item):
        """Adds a menu item to the menu bar being constructed."""
        action = menu_item.item.action
        self.eval_when(action.enabled_when, menu_item, "enabled")
        self.eval_when(action.checked_when, menu_item, "checked")

    def add_to_toolbar(self, toolbar_item):
        """Adds a toolbar item to the toolbar being constructed."""
        self.add_to_menu(toolbar_item)

    def can_add_to_menu(self, action):
        """Returns whether the action should be defined in the user interface."""
        if action.defined_when != "":
            if not eval(action.defined_when, globals(), self._context):
                return False

        if action.visible_when != "":
            if not eval(action.visible_when, globals(), self._context):
                return False

        return True

    def can_add_to_toolbar(self, action):
        """Returns whether the toolbar action should be defined in the user
        interface.
        """
        return self.can_add_to_menu(action)

    def perform(self, action, action_event=None):
        """Performs the action described by a specified Action object."""
        self.ui.do_undoable(self._perform, action)

    def _perform(self, action):
        node, object, nid = self._data
        method_name = action.action
        info = self.ui.info
        handler = self.ui.handler

        if method_name.find(".") >= 0:
            if method_name.find("(") < 0:
                method_name += "()"
            try:
                eval(
                    method_name,
                    globals(),
                    {
                        "object": object,
                        "editor": self,
                        "node": node,
                        "info": info,
                        "handler": handler,
                    },
                )
            except Exception:
                from traitsui.api import raise_to_debug

                raise_to_debug()
            return

        method = getattr(handler, method_name, None)
        if method is not None:
            method(info, object)
            return

        if action.on_perform is not None:
            action.on_perform(object)

    # ----- Menu support methods: ---------------------------------------------

    def eval_when(self, condition, object, trait):
        """Evaluates a condition within a defined context, and sets a
        specified object trait based on the result, which is assumed to be a
        Boolean.
        """
        if condition != "":
            value = True
            try:
                if not eval(condition, globals(), self._context):
                    value = False
            except Exception as e:
                logger.warning(
                    "Exception (%s) raised when evaluating the "
                    "condition %s. Returning True." % (e, condition)
                )
            setattr(object, trait, value)

    # ----- Menu event handlers: ----------------------------------------------

    def _menu_copy_node(self):
        """Copies the current tree node object to the paste buffer."""
        clipboard.instance = self._data[1]
        self._data = None

    def _menu_cut_node(self):
        """Cuts the current tree node object into the paste buffer."""
        node, object, nid = self._data
        clipboard.instance = object
        self._data = None
        self._undoable_delete(*self._node_index(nid))

    def _menu_paste_node(self):
        """Pastes the current contents of the paste buffer into the current
        node.
        """
        node, object, nid = self._data
        self._data = None
        self._undoable_append(node, object, clipboard.instance, True)

    def _menu_delete_node(self):
        """Deletes the current node from the tree."""
        node, object, nid = self._data
        self._data = None
        rc = node.confirm_delete(object)
        if rc is not False:
            if rc is not True:
                if self.ui.history is None:
                    # If no undo history, ask user to confirm the delete:
                    butn = QtGui.QMessageBox.question(
                        self._tree,
                        "Confirm Deletion",
                        "Are you sure you want to delete %s?"
                        % node.get_label(object),
                        QtGui.QMessageBox.StandardButton.Yes | QtGui.QMessageBox.StandardButton.No,
                    )
                    if butn != QtGui.QMessageBox.StandardButton.Yes:
                        return

            self._undoable_delete(*self._node_index(nid))

    def _menu_rename_node(self):
        """Rename the current node."""
        _, _, nid = self._data
        self._data = None
        self._tree.editItem(nid)

    def _on_nid_changed(self, nid, col):
        """Handle changes to a widget item."""
        # The node data may not have been set up for the nid yet.  Ignore it if
        # it hasn't.
        try:
            _, node, object = self._get_node_data(nid)
        except Exception:
            return

        new_label = str(nid.text(col))
        old_label = node.get_label(object)

        if new_label != old_label:
            if new_label != "":
                node.set_label(object, new_label)
            else:
                self._set_label(nid, col)

    def _menu_new_node(self, factory, prompt=False):
        """Adds a new object to the current node."""
        node, object, nid = self._data
        self._data = None
        new_object = factory()
        if new_object is None:
            return  # support None-type returns from factory
        if (not prompt) or new_object.edit_traits(
            parent=self.control, kind="livemodal"
        ).result:
            self._undoable_append(node, object, new_object, False)

            # Automatically select the new object if editing is being
            # performed:
            if self.factory.editable:
                self._tree.setCurrentItem(nid.child(nid.childCount() - 1))

    # ----- Model event handlers: ---------------------------------------------

    def _children_replaced(self, object, name="", new=None):
        """Handles the children of a node being completely replaced."""
        tree = self._tree
        for expanded, node, nid in self._object_info_for(object, name):
            children = node.get_children(object)

            # Only add/remove the changes if the node has already been
            # expanded:
            if expanded:
                # Delete all current child nodes:
                for cnid in self._nodes_for(nid):
                    self._delete_node(cnid)

                # Add all of the children back in as new nodes:
                for child in children:
                    child, child_node = self._node_for(child)
                    if child_node is not None:
                        self._append_node(nid, child_node, child)
            else:
                dummy = getattr(nid, "_dummy", None)
                if dummy is None and len(children) > 0:
                    # if model now has children add dummy child
                    nid._dummy = QtGui.QTreeWidgetItem(nid)
                elif dummy is not None and len(children) == 0:
                    # if model no longer has children remove dummy child
                    nid.removeChild(dummy)
                    del nid._dummy

            # Try to expand the node (if requested):
            if node.can_auto_open(object):
                nid.setExpanded(True)

    def _children_updated(self, object, name, event):
        """Handles the children of a node being changed."""
        # Log the change that was made made (removing '_items' from the end of
        # the name):
        name = name[:-6]
        self.log_change(self._get_undo_item, object, name, event)

        # Get information about the node that was changed:
        start = event.index
        n = len(event.added)
        end = start + len(event.removed)
        tree = self._tree

        for expanded, node, nid in self._object_info_for(object, name):
            children = node.get_children(object)

            # If the new children aren't all at the end, remove/add them all:
            # if (n > 0) and ((start + n) != len( children )):
            #    self._children_replaced( object, name, event )
            #    return

            # Only add/remove the changes if the node has already been
            # expanded:
            if expanded:
                # Remove all of the children that were deleted:
                for cnid in self._nodes_for(nid)[start:end]:
                    self._delete_node(cnid)

                remaining = len(children) - len(event.removed)
                child_index = 0
                # Add all of the children that were added:
                for child in event.added:
                    child, child_node = self._node_for(child)
                    if child_node is not None:
                        insert_index = (
                            (start + child_index)
                            if (start <= remaining)
                            else None
                        )
                        self._insert_node(nid, insert_index, child_node, child)
                        child_index += 1
            else:
                dummy = getattr(nid, "_dummy", None)
                if dummy is None and len(children) > 0:
                    # if model now has children add dummy child
                    nid._dummy = QtGui.QTreeWidgetItem(nid)
                elif dummy is not None and len(children) == 0:
                    # if model no longer has children remove dummy child
                    nid.removeChild(dummy)
                    del nid._dummy

            # Try to expand the node (if requested):
            if node.can_auto_open(object):
                nid.setExpanded(True)

    def _label_updated(self, object, name, label):
        """Handles the label of an object being changed."""
        # Prevent the itemChanged() signal from being emitted.
        blk = self._tree.blockSignals(True)
        try:
            # Have to use a list rather than a set because nids for PyQt
            # on Python 3 (QTreeWidgetItem instances) aren't hashable.
            # This means potentially quadratic behaviour, but the number of
            # nodes for a particular object shouldn't be high
            nids = []
            for name2, nid in self._map[id(object)]:
                if nid not in nids:
                    try:
                        node = self._get_node_data(nid)[1]
                    except Exception:
                        # node is either not ready or has been deleted
                        continue
                    nids.append(nid)
                    self._set_label(nid, 0)
                    self._update_icon(nid)
        finally:
            self._tree.blockSignals(blk)

    def _column_labels_updated(self, object, name, new):
        """Handles the column labels of an object being changed."""
        # Prevent the itemChanged() signal from being emitted.
        blk = self._tree.blockSignals(True)
        try:
            nids = []
            for name2, nid in self._map[id(object)]:
                if nid not in nids:
                    try:
                        node = self._get_node_data(nid)[1]
                    except Exception:
                        # node is either not ready or has been deleted
                        continue
                    nids.append(nid)
                    self._set_column_labels(nid, node, object)
        finally:
            self._tree.blockSignals(blk)

    # -- UI preference save/restore interface ---------------------------------

    def restore_prefs(self, prefs):
        """Restores any saved user preference information associated with the
        editor.
        """
        if isinstance(self.control, QtGui.QSplitter):
            if isinstance(prefs, dict):
                structure = prefs.get("structure")
            else:
                structure = prefs

            self.control.restoreState(structure)
        header = self._tree.header()
        self.control.setExpandsOnDoubleClick(self.factory.expands_on_dclick)

        if header is not None and "column_state" in prefs:
            header.restoreState(prefs["column_state"])

    def save_prefs(self):
        """Returns any user preference information associated with the editor."""
        prefs = {}
        if isinstance(self.control, QtGui.QSplitter):
            prefs["structure"] = self.control.saveState().data()
        header = self._tree.header()
        if header is not None:
            prefs["column_state"] = header.saveState().data()

        return prefs


# -- End UI preference save/restore interface -----------------------------


class _TreeWidget(QtGui.QTreeWidget):
    """The _TreeWidget class is a specialised QTreeWidget that reimplements
    the drag'n'drop support so that it hooks into the provided Traits
    support.
    """

    def __init__(self, editor, parent=None):
        """Initialise the tree widget."""
        QtGui.QTreeWidget.__init__(self, parent)

        self.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setIconSize(QtCore.QSize(*editor.factory.icon_size))

        # Set up headers if necessary.
        column_count = len(editor.factory.column_headers)
        if column_count > 0:
            self.setHeaderHidden(False)
            self.setColumnCount(column_count)
            self.setHeaderLabels(editor.factory.column_headers)
        else:
            self.setHeaderHidden(True)

        self.setAlternatingRowColors(editor.factory.alternating_row_colors)
        padding = editor.factory.vertical_padding
        if padding > 0:
            self.setStyleSheet(
                """
            QTreeView::item {
                padding-top: %spx;
                padding-bottom: %spx;
            }
            """
                % (padding, padding)
            )

        if editor.factory.selection_mode == "extended":
            self.setSelectionMode(QtGui.QAbstractItemView.SelectionMode.ExtendedSelection)

        self.itemExpanded.connect(editor._on_item_expanded)
        self.itemCollapsed.connect(editor._on_item_collapsed)
        self.itemClicked.connect(editor._on_item_clicked)
        self.itemDoubleClicked.connect(editor._on_item_dclicked)
        self.itemActivated.connect(editor._on_item_activated)
        self.itemSelectionChanged.connect(editor._on_tree_sel_changed)
        self.customContextMenuRequested.connect(editor._on_context_menu)
        self.itemChanged.connect(editor._on_nid_changed)

        self._editor = editor
        self._dragging = None

    def resizeEvent(self, event):
        """Overridden to emit sizeHintChanged() of items for word wrapping"""
        if self._editor.factory.word_wrap:
            for i in range(self.topLevelItemCount()):
                mi = self.indexFromItem(self.topLevelItem(i))
                id = self.itemDelegate(mi)
                id.sizeHintChanged.emit(mi)
        super(self.__class__, self).resizeEvent(event)

    def startDrag(self, actions):
        """Reimplemented to start the drag of a tree widget item."""
        nid = self.currentItem()
        if nid is None:
            return

        self._dragging = nid

        # Calculate the hotspot so that the pixmap appears on top of the
        # original item.
        nid_rect = self.visualItemRect(nid)
        hspos = (
            self.viewport().mapFromGlobal(QtGui.QCursor.pos())
            - nid_rect.topLeft()
        )

        _, node, object = self._editor._get_node_data(nid)

        # Convert the item being dragged to MIME data.
        drag_object = node.get_drag_object(object)
        md = PyMimeData.coerce(drag_object)

        # Render the item being dragged as a pixmap.
        rect = nid_rect.intersected(self.viewport().rect())
        pm = QtGui.QPixmap(rect.size())
        pm.fill(self.palette().base().color())
        painter = QtGui.QPainter(pm)

        if is_qt5:
            option = self.viewOptions()
        else:
            option = QtGui.QStyleOptionViewItem()
            self.initViewItemOption(option)
        option.state |= QtGui.QStyle.StateFlag.State_Selected
        option.rect = QtCore.QRect(
            nid_rect.topLeft() - rect.topLeft(), nid_rect.size()
        )
        self.itemDelegate().paint(painter, option, self.indexFromItem(nid))

        painter.end()

        # Start the drag.
        drag = QtGui.QDrag(self)
        drag.setMimeData(md)
        drag.setPixmap(pm)
        drag.setHotSpot(hspos)
        drag.exec_(actions)

    def dragEnterEvent(self, e):
        """Reimplemented to see if the current drag can be handled by the
        tree.
        """
        # Assume the drag is invalid.
        e.ignore()

        # Check if we have a python object instance, we might be interested
        data = PyMimeData.coerce(e.mimeData()).instance()
        if data is None:
            return

        # We might be able to handle it (but it depends on what the final
        # target is).
        e.acceptProposedAction()

    def dragMoveEvent(self, e):
        """Reimplemented to see if the current drag can be handled by the
        particular tree widget item underneath the cursor.
        """
        # Assume the drag is invalid.
        e.ignore()

        action, to_node, to_object, to_index, data = self._get_action(e)

        if action is not None:
            e.acceptProposedAction()

    def dropEvent(self, e):
        """Reimplemented to update the model and tree."""
        # Assume the drop is invalid.
        e.ignore()

        editor = self._editor

        dragging = self._dragging
        self._dragging = None

        action, to_node, to_object, to_index, data = self._get_action(e)

        if action == "append":
            if dragging is not None:
                data = self._editor._drop_object(
                    to_node, to_object, data, False
                )
                if data is not None:
                    try:
                        editor._begin_undo()
                        editor._undoable_delete(*editor._node_index(dragging))
                        editor._undoable_append(
                            to_node, to_object, data, False
                        )
                    finally:
                        editor._end_undo()
            else:
                data = editor._drop_object(to_node, to_object, data, True)
                if data is not None:
                    editor._undoable_append(to_node, to_object, data, False)
        elif action == "insert":
            if dragging is not None:
                data = editor._drop_object(to_node, to_object, data, False)
                if data is not None:
                    from_node, from_object, from_index = editor._node_index(
                        dragging
                    )
                    if (to_object is from_object) and (to_index > from_index):
                        to_index -= 1
                    try:
                        editor._begin_undo()
                        editor._undoable_delete(
                            from_node, from_object, from_index
                        )
                        editor._undoable_insert(
                            to_node, to_object, to_index, data, False
                        )
                    finally:
                        editor._end_undo()
            else:
                data = self._editor._drop_object(
                    to_node, to_object, data, True
                )
                if data is not None:
                    editor._undoable_insert(
                        to_node, to_object, to_index, data, False
                    )
        else:
            return

        e.acceptProposedAction()

    def _get_action(self, event):
        """Work out what action on what object to perform for a drop event"""
        # default values to return
        action = None
        to_node = None
        to_object = None
        to_index = None
        data = None

        editor = self._editor

        # Get the tree widget item under the cursor.
        nid = self.itemAt(event.pos())
        if nid is None:
            if editor.factory.hide_root:
                nid = self.invisibleRootItem()
            else:
                return (action, to_node, to_object, to_index, data)

        # Check that the target is not the source of a child of the source.
        if self._dragging is not None:
            pnid = nid
            while pnid is not None:
                if pnid is self._dragging:
                    return (action, to_node, to_object, to_index, data)

                pnid = pnid.parent()

        data = PyMimeData.coerce(event.mimeData()).instance()
        _, node, object = editor._get_node_data(nid)

        if (
            event.proposedAction() == QtCore.Qt.DropAction.MoveAction
            and editor._is_droppable(node, object, data, False)
        ):
            # append to node being dropped on
            action = "append"
            to_node = node
            to_object = object
            to_index = None
        else:
            # get parent of node being dropped on
            to_node, to_object, to_index = editor._node_index(nid)
            if to_node is None:
                # no parent, can't do anything
                action = None
            elif editor._is_droppable(to_node, to_object, data, True):
                # insert into the parent of the node being dropped on
                action = "insert"
            elif editor._is_droppable(to_node, to_object, data, False):
                # append to the parent of the node being dropped on
                action = "append"
            else:
                # parent can't be modified, can't do anything
                action = None

        return (action, to_node, to_object, to_index, data)


class TreeItemDelegate(QtGui.QStyledItemDelegate):
    """A delegate class to draw wrapped text labels"""

    # FIXME: sizeHint() should return the size required by the label,
    # which is dependent on the width available, which is different for
    # each item due to the nested tree structure. However the option.rect
    # argument available to the sizeHint() is invalid (width=-1) so as a
    # hack sizeHintChanged is emitted in paint() and the size of drawn
    # text is returned, as paint() gets a valid option.rect argument.

    # TODO: add ability to override editor in item delegate

    def sizeHint(self, option, index):
        """returns area taken by the text."""
        column = index.column()
        item = self.editor._tree.itemFromIndex(index)
        expanded, node, instance = self.editor._get_node_data(item)
        column = index.column()

        renderer = node.get_renderer(object, column=column)
        if renderer is None:
            return super().sizeHint(option, index)

        size_context = (option, index)
        size = renderer.size(self.editor, node, column, instance, size_context)
        if size is None:
            return QtCore.QSize(1, 21)
        else:
            return QtCore.QSize(*size)

    def updateEditorGeometry(self, editor, option, index):
        """Update the editor's geometry."""
        editor.setGeometry(option.rect)

    def paint(self, painter, option, index):
        """Render the contents of the item."""
        item = self.editor._tree.itemFromIndex(index)
        expanded, node, instance = self.editor._get_node_data(item)
        column = index.column()

        renderer = node.get_renderer(object, column=column)
        if renderer is None and self.editor.factory.word_wrap:
            renderer = DEFAULT_WRAP_RENDERER
        if renderer is None:
            super().paint(painter, option, index)
        else:
            if not renderer.handles_all:
                # renderers background and selection highlights
                # will also render icon and text if flags are set
                super().paint(painter, option, index)
            paint_context = (painter, option, index)
            size = renderer.paint(
                self.editor, node, column, instance, paint_context
            )
            if size is not None:
                do_later(self.sizeHintChanged.emit, index)
