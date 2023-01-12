# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Defines the tree editor for the wxPython user interface toolkit.
"""


import copy
from functools import partial
import os

import wx

try:
    from pyface.wx.drag_and_drop import PythonDropSource, PythonDropTarget
except:
    PythonDropSource = PythonDropTarget = None

from pyface.ui.wx.image_list import ImageList
from traits.api import HasStrictTraits, Any, Str, Event, TraitError
from traitsui.api import View, TreeNode, ObjectTreeNode, MultiTreeNode

from traitsui.editors.tree_editor import (
    CopyAction,
    CutAction,
    DeleteAction,
    NewAction,
    PasteAction,
    RenameAction,
)
from traitsui.undo import ListUndoItem
from traitsui.tree_node import ITreeNodeAdapterBridge
from traitsui.menu import Menu, Action, Separator

from pyface.api import ImageResource
from pyface.ui_traits import convert_image
from pyface.dock.api import (
    DockWindow,
    DockSizer,
    DockSection,
    DockRegion,
    DockControl,
)

from .constants import OKColor
from .editor import Editor
from .helper import TraitsUIPanel, TraitsUIScrolledPanel

# -------------------------------------------------------------------------
#  Global data:
# -------------------------------------------------------------------------

# Paste buffer for copy/cut/paste operations
paste_buffer = None


# -------------------------------------------------------------------------
#  'SimpleEditor' class:
# -------------------------------------------------------------------------


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
    #: pressing the enter key on a node.
    activated = Event()

    #: The event fired when a tree node is clicked on:
    click = Event()

    #: The event fired when a tree node is double-clicked on:
    dclick = Event()

    #: The event fired when the application wants to veto an operation:
    veto = Event()

    def init(self, parent):
        """Finishes initializing the editor by creating the underlying toolkit
        widget.
        """
        factory = self.factory
        style = self._get_style()

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
                    self.control = TraitsUIPanel(parent, -1)
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
                self.control = self._tree = tree = wx.TreeCtrl(
                    parent, -1, style=style
                )
            else:
                # If editable, create a tree control and an editor panel:
                self._is_dock_window = True
                theme = factory.dock_theme or self.item.container.dock_theme
                self.control = splitter = DockWindow(
                    parent, theme=theme
                ).control
                self._tree = tree = wx.TreeCtrl(splitter, -1, style=style)
                self._editor = editor = TraitsUIScrolledPanel(splitter)
                editor.SetSizer(wx.BoxSizer(wx.VERTICAL))
                editor.SetScrollRate(16, 16)
                editor.SetMinSize(wx.Size(100, 100))

                self._editor._node_ui = self._editor._editor_nid = None
                item = self.item
                hierarchy_name = editor_name = ""
                style = "fixed"
                name = item.label
                if name != "":
                    hierarchy_name = name + " Hierarchy"
                    editor_name = name + " Editor"
                    style = item.dock

                splitter.SetSizer(
                    DockSizer(
                        contents=DockSection(
                            contents=[
                                DockRegion(
                                    contents=[
                                        DockControl(
                                            name=hierarchy_name,
                                            id="tree",
                                            control=tree,
                                            style=style,
                                        )
                                    ]
                                ),
                                DockRegion(
                                    contents=[
                                        DockControl(
                                            name=editor_name,
                                            id="editor",
                                            control=self._editor,
                                            style=style,
                                        )
                                    ]
                                ),
                            ],
                            is_row=(factory.orientation == "horizontal"),
                        )
                    )
                )
        else:
            # Otherwise, just create the tree control:
            self.control = self._tree = tree = wx.TreeCtrl(
                parent, -1, style=style
            )

        # Set up to show tree node icon (if requested):
        if factory.show_icons:
            self._image_list = ImageList(*factory.icon_size)
            tree.AssignImageList(self._image_list)

        # Set up the mapping between objects and tree id's:
        self._map = {}

        # Initialize the 'undo state' stack:
        self._undoable = []

        # Set up the mouse event handlers:
        tree.Bind(wx.EVT_LEFT_DOWN, self._on_left_down)
        tree.Bind(wx.EVT_RIGHT_DOWN, self._on_right_down)
        tree.Bind(wx.EVT_LEFT_DCLICK, self._on_left_dclick)

        # Set up the tree event handlers:
        tree.Bind(wx.EVT_TREE_ITEM_EXPANDING, self._on_tree_item_expanding)
        tree.Bind(wx.EVT_TREE_ITEM_EXPANDED, self._on_tree_item_expanded)
        tree.Bind(wx.EVT_TREE_ITEM_COLLAPSING, self._on_tree_item_collapsing)
        tree.Bind(wx.EVT_TREE_ITEM_COLLAPSED, self._on_tree_item_collapse)
        tree.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self._on_tree_item_activated)
        tree.Bind(wx.EVT_TREE_SEL_CHANGED, self._on_tree_sel_changed)
        tree.Bind(wx.EVT_TREE_BEGIN_DRAG, self._on_tree_begin_drag)
        tree.Bind(wx.EVT_TREE_BEGIN_LABEL_EDIT, self._on_tree_begin_label_edit)
        tree.Bind(wx.EVT_TREE_END_LABEL_EDIT, self._on_tree_end_label_edit)
        tree.Bind(wx.EVT_TREE_ITEM_GETTOOLTIP, self._on_tree_item_gettooltip)

        # Set up general mouse events
        tree.Bind(wx.EVT_MOTION, self._on_hover)

        # Synchronize external object traits with the editor:
        self.sync_value(factory.selected, "selected")
        self.sync_value(factory.activated, "activated", "to")
        self.sync_value(factory.click, "click", "to")
        self.sync_value(factory.dclick, "dclick", "to")
        self.sync_value(factory.veto, "veto", "from")

        # Set up the drag and drop target:
        if PythonDropTarget is not None:
            tree.SetDropTarget(PythonDropTarget(self))

    def dispose(self):
        """Disposes of the contents of an editor."""
        tree = self._tree
        if tree is not None:
            tree.Unbind(wx.EVT_LEFT_DOWN)
            tree.Unbind(wx.EVT_RIGHT_DOWN)
            tree.Unbind(wx.EVT_LEFT_DCLICK)

            tree.Unbind(wx.EVT_TREE_ITEM_EXPANDING)
            tree.Unbind(wx.EVT_TREE_ITEM_EXPANDED)
            tree.Unbind(wx.EVT_TREE_ITEM_COLLAPSING)
            tree.Unbind(wx.EVT_TREE_ITEM_COLLAPSED)
            tree.Unbind(wx.EVT_TREE_ITEM_ACTIVATED)
            tree.Unbind(wx.EVT_TREE_SEL_CHANGED)
            tree.Unbind(wx.EVT_TREE_BEGIN_DRAG)
            tree.Unbind(wx.EVT_TREE_BEGIN_LABEL_EDIT)
            tree.Unbind(wx.EVT_TREE_END_LABEL_EDIT)
            tree.Unbind(wx.EVT_TREE_ITEM_GETTOOLTIP)

            tree.Unbind(wx.EVT_MOTION)

            nid = self._tree.GetRootItem()
            if nid.IsOk():
                self._delete_node(nid)

        self._tree = None
        super().dispose()

    def _selection_changed(self, selection):
        """Handles the **selection** event."""
        try:
            self._tree.SelectItem(self._object_info(selection)[2])
        except Exception:
            pass

    def _selected_changed(self, selected):
        """Handles the **selected** trait being changed."""
        if not self._no_update_selected:
            self._selection_changed(selected)

    def _veto_changed(self):
        """Handles the 'veto' event being fired."""
        self._veto = True

    def _get_style(self):
        """Returns the style settings used for displaying the wx tree."""
        factory = self.factory
        style = wx.TR_EDIT_LABELS | wx.TR_HAS_BUTTONS | wx.CLIP_CHILDREN

        # Turn lines off if explicit or for appearance on *nix:
        if (factory.lines_mode == "off") or (
            (factory.lines_mode == "appearance") and (os.name == "posix")
        ):
            style |= wx.TR_NO_LINES

        if factory.hide_root:
            style |= wx.TR_HIDE_ROOT | wx.TR_LINES_AT_ROOT

        if factory.selection_mode != "single":
            style |= wx.TR_MULTIPLE | wx.TR_EXTENDED

        return style

    def update_object(self, event):
        """Handles the user entering input data in the edit control."""
        try:
            self.value = self._get_value()
            self.control.SetBackgroundColour(OKColor)
            self.control.Refresh()
        except TraitError:
            pass

    def _save_state(self):
        tree = self._tree
        nid = tree.GetRootItem()
        state = {}
        if nid.IsOk():
            nodes_to_do = [nid]
            while nodes_to_do:
                node = nodes_to_do.pop()
                data = self._get_node_data(node)
                try:
                    is_expanded = tree.IsExpanded(node)
                except:
                    is_expanded = True
                state[hash(data[-1])] = (data[0], is_expanded)
                for cnid in self._nodes(node):
                    nodes_to_do.append(cnid)
        return state

    def _restore_state(self, state):
        if not state:
            return
        tree = self._tree
        nid = tree.GetRootItem()
        if nid.IsOk():
            nodes_to_do = [nid]
            while nodes_to_do:
                node = nodes_to_do.pop()
                for cnid in self._nodes(node):
                    data = self._get_node_data(cnid)
                    key = hash(data[-1])
                    if key in state:
                        was_expanded, current_state = state[key]
                        if was_expanded:
                            self._expand_node(cnid)
                            if current_state:
                                tree.Expand(cnid)
                            nodes_to_do.append(cnid)

    def expand_all(self):
        """Expands all nodes, starting from the selected node."""
        tree = self._tree

        def _do_expand(nid):
            expanded, node, object = self._get_node_data(nid)
            if self._has_children(node, object):
                tree.SetItemHasChildren(nid, True)
                self._expand_node(nid)
                tree.Expand(nid)

        nid = tree.GetSelection()
        if nid.IsOk():
            nodes_to_do = [nid]
            while nodes_to_do:
                node = nodes_to_do.pop()
                _do_expand(node)
                for n in self._nodes(node):
                    _do_expand(n)
                    nodes_to_do.append(n)

    def expand_levels(self, nid, levels, expand=True):
        """Expands from the specified node the specified number of sub-levels."""
        if levels > 0:
            expanded, node, object = self._get_node_data(nid)
            if self._has_children(node, object):
                self._tree.SetItemHasChildren(nid, True)
                self._expand_node(nid)
                if expand:
                    self._tree.Expand(nid)
                for cnid in self._nodes(nid):
                    self.expand_levels(cnid, levels - 1)

    def update_editor(self):
        """Updates the editor when the object trait changes externally to the
        editor.
        """
        tree = self._tree
        saved_state = {}
        if tree is not None:
            nid = tree.GetRootItem()
            if nid.IsOk():
                self._delete_node(nid)
            object, node = self._node_for(self.value)
            if node is not None:
                icon = self._get_icon(node, object)
                self._root_nid = nid = tree.AddRoot(
                    node.get_label(object), icon, icon
                )
                self._map[id(object)] = [(node.get_children_id(object), nid)]
                self._add_listeners(node, object)
                self._set_node_data(nid, (False, node, object))
                if self.factory.hide_root or self._has_children(node, object):
                    tree.SetItemHasChildren(nid, True)
                    self._expand_node(nid)
                    if not self.factory.hide_root:
                        tree.Expand(nid)
                        tree.SelectItem(nid)
                        self._on_tree_sel_changed()

                self.expand_levels(nid, self.factory.auto_open, False)

                # It seems like in some cases, an explicit Refresh is needed to
                # trigger a screen update:
                tree.Refresh()

            # fixme: Clear the current editor (if any)...

    def get_error_control(self):
        """Returns the editor's control for indicating error status."""
        return self._tree

    def _append_node(self, nid, node, object):
        """Appends a new node to the specified node."""
        return self._insert_node(nid, None, node, object)

    def _insert_node(self, nid, index, node, object):
        """Inserts a new node before a specified index into the children of the
        specified node.
        """
        tree = self._tree
        icon = self._get_icon(node, object)
        label = node.get_label(object)
        if index is None:
            cnid = tree.AppendItem(nid, label, icon, icon)
        else:
            cnid = tree.InsertItem(nid, index, label, icon, icon)
        has_children = self._has_children(node, object)
        tree.SetItemHasChildren(cnid, has_children)
        self._set_node_data(cnid, (False, node, object))
        self._map.setdefault(id(object), []).append(
            (node.get_children_id(object), cnid)
        )
        self._add_listeners(node, object)

        # Automatically expand the new node (if requested):
        if has_children and node.can_auto_open(object):
            tree.Expand(cnid)

        # Return the newly created node:
        return cnid

    def _delete_node(self, nid):
        """Deletes a specified tree node and all of its children."""
        for cnid in self._nodes_for(nid):
            self._delete_node(cnid)

        expanded, node, object = self._get_node_data(nid)
        id_object = id(object)
        object_info = self._map[id_object]
        for i, info in enumerate(object_info):
            if nid == info[1]:
                del object_info[i]
                break

        if len(object_info) == 0:
            self._remove_listeners(node, object)
            del self._map[id_object]

        # We set the '_locked' flag here because wx seems to generate a
        # 'node selected' event when the node is deleted. This can lead to
        # some bad side effects. So the 'node selected' event handler exits
        # immediately if the '_locked' flag is set:
        self._locked = True
        self._tree.Delete(nid)
        self._locked = False

        # If the deleted node had an active editor panel showing, remove it:
        if (self._editor is not None) and (nid == self._editor._editor_nid):
            self._clear_editor()

    def _expand_node(self, nid):
        """Expands the contents of a specified node (if required)."""
        expanded, node, object = self._get_node_data(nid)

        # Lazily populate the item's children:
        if not expanded:
            for child in node.get_children(object):
                child, child_node = self._node_for(child)
                if child_node is not None:
                    self._append_node(nid, child_node, child)

            # Indicate the item is now populated:
            self._set_node_data(nid, (True, node, object))

    def _nodes(self, nid):
        """Returns each of the child nodes of a specified node."""
        tree = self._tree
        cnid, cookie = tree.GetFirstChild(nid)
        while cnid.IsOk():
            yield cnid
            cnid, cookie = tree.GetNextChild(nid, cookie)

    def _nodes_for(self, nid):
        """Returns all child node ids of a specified node id."""
        return [cnid for cnid in self._nodes(nid)]

    def _node_index(self, nid):
        pnid = self._tree.GetItemParent(nid)
        if not pnid.IsOk():
            return (None, None, None)

        for i, cnid in enumerate(self._nodes(pnid)):
            if cnid == nid:
                ignore, pnode, pobject = self._get_node_data(pnid)

                return (pnode, pobject, i)

    def _has_children(self, node, object):
        """Returns whether a specified object has any children."""
        return node.allows_children(object) and node.has_children(object)

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

    def _get_icon(self, node, object, is_expanded=False):
        """Returns the index of the specified object icon."""
        if self._image_list is None:
            return -1

        icon_name = node.get_icon(object, is_expanded)
        if isinstance(icon_name, str):
            if icon_name.startswith("@"):
                image = convert_image(icon_name, 3)
                if image is None:
                    return -1
            else:
                if icon_name[:1] == "<":
                    icon_name = icon_name[1:-1]
                    path = self
                else:
                    path = node.get_icon_path(object)
                    if isinstance(path, str):
                        path = [path, node]
                    else:
                        path.append(node)
                image = ImageResource(icon_name, path).absolute_path
        elif isinstance(icon_name, ImageResource):
            image = icon_name.absolute_path
        else:
            raise ValueError(
                "Icon value must be a string or IImageResource instance: "
                + "given {!r}".format(icon_name)
            )

        return self._image_list.GetIndex(image)

    def _add_listeners(self, node, object):
        """Adds the event listeners for a specified object."""
        if node.allows_children(object):
            node.when_children_replaced(object, self._children_replaced, False)
            node.when_children_changed(object, self._children_updated, False)

        node.when_label_changed(object, self._label_updated, False)

    def _remove_listeners(self, node, object):
        """Removes any event listeners from a specified object."""
        if node.allows_children(object):
            node.when_children_replaced(object, self._children_replaced, True)
            node.when_children_changed(object, self._children_updated, True)

        node.when_label_changed(object, self._label_updated, True)

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
                expanded, node, ignore = self._get_node_data(nid)
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
        nodes = [
            node
            for node in factory.nodes
            if object is not None and node.is_node_for(object)
        ]

        # If only one found, we're done, return it:
        if len(nodes) == 1:
            return (object, nodes[0])

        # If none found, try to create an adapted node for the object:
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
            if node.get_children_id(object) == "":
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

    def _update_icon(self, event, is_expanded):
        """Updates the icon for a specified node."""
        self._update_icon_for_nid(event.GetItem())

    def _update_icon_for_nid(self, nid):
        """Updates the icon for a specified node ID."""
        if self._image_list is not None:
            expanded, node, object = self._get_node_data(nid)
            icon = self._get_icon(node, object, expanded)
            self._tree.SetItemImage(nid, icon, wx.TreeItemIcon_Normal)
            self._tree.SetItemImage(nid, icon, wx.TreeItemIcon_Selected)

    def _unpack_event(self, event):
        """Unpacks an event to see whether a tree item was involved."""
        try:
            point = event.GetPosition()
        except:
            point = event.GetPoint()

        nid = None
        if hasattr(event, "GetItem"):
            nid = event.GetItem()

        if (nid is None) or (not nid.IsOk()):
            nid, flags = self._tree.HitTest(point)

        if nid.IsOk():
            return self._get_node_data(nid) + (nid, point)

        return (None, None, None, nid, point)

    def _hit_test(self, point):
        """Returns information about the node at a specified point."""
        nid, flags = self._tree.HitTest(point)
        if nid.IsOk():
            return self._get_node_data(nid) + (nid, point)
        return (None, None, None, nid, point)

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
            editor.SetSizer(None)
            editor._node_ui.dispose()
            editor._node_ui = editor._editor_nid = None

    def _get_node_data(self, nid):
        """Gets the node specific data."""
        if nid == self._root_nid:
            return self._root_nid_data

        return self._tree.GetItemData(nid)

    def _set_node_data(self, nid, data):
        """Sets the node specific data."""
        if nid == self._root_nid:
            self._root_nid_data = data
        else:
            self._tree.SetItemData(nid, data)

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
            pnid = self._tree.GetItemParent(nid)
            if pnid.IsOk():
                return self.get_object(pnid)

        return None

    def get_node(self, object, name=""):
        """Returns the node associated with a specified object."""
        nid = self._get_object_nid(object, name)
        if nid is not None:
            return self._get_node_data(nid)[1]

        return None

    # -- Tree Event Handlers: -------------------------------------------------

    def _on_tree_item_expanding(self, event):
        """Handles a tree node expanding."""
        if self._veto:
            self._veto = False
            event.Veto()
            return

        nid = event.GetItem()
        tree = self._tree
        expanded, node, object = self._get_node_data(nid)

        # If 'auto_close' requested for this node type, close all of the node's
        # siblings:
        if node.can_auto_close(object):
            snid = nid
            while True:
                snid = tree.GetPrevSibling(snid)
                if not snid.IsOk():
                    break
                tree.Collapse(snid)
            snid = nid
            while True:
                snid = tree.GetNextSibling(snid)
                if not snid.IsOk():
                    break
                tree.Collapse(snid)

        # Expand the node (i.e. populate its children if they are not there
        # yet):
        self._expand_node(nid)

    def _on_tree_item_expanded(self, event):
        """Handles a tree node being expanded."""
        self._update_icon(event, True)

    def _on_tree_item_collapsing(self, event):
        """Handles a tree node collapsing."""
        if self._veto:
            self._veto = False
            event.Veto()

    def _on_tree_item_collapsed(self, event):
        """Handles a tree node being collapsed."""
        self._update_icon(event, False)

    def _on_tree_sel_changed(self, event=None):
        """Handles a tree node being selected."""
        if self._locked:
            return

        # Get the new selection:
        object = None
        not_handled = True
        nids = self._tree.GetSelections()

        selected = [self._get_node_data(nid)[2] for nid in nids if nid.IsOk()]
        first = True
        for nid in nids:
            if not nid.IsOk():
                continue

            # If there is a real selection, get the associated object:
            expanded, sel_node, sel_object = self._get_node_data(nid)

            # Try to inform the node specific handler of the selection,
            # if there are multiple selections, we only care about the
            # first (or maybe the last makes more sense?)
            if first:
                node = sel_node
                object = sel_object
                not_handled = node.select(object)
                first = False

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
            editor.Freeze()
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
                sizer = wx.BoxSizer(wx.VERTICAL)
                sizer.Add(ui.control, 1, wx.EXPAND)
                editor.SetSizer(sizer)
                editor.Layout()

            # fixme: The following is a hack needed to make the editor window
            # (which is a wx.ScrolledWindow) recognize that its contents have
            # been changed:
            dx, dy = editor.GetSize()
            editor.SetSize(wx.Size(dx, dy + 1))
            editor.SetSize(wx.Size(dx, dy))

            # Allow the editor view to show any changes that have occurred:
            editor.Thaw()

    def _on_hover(self, event):
        """Handles the mouse moving over a tree node"""
        id, flags = self._tree.HitTest(event.GetPosition())
        if flags & wx.TREE_HITTEST_ONITEMLABEL:
            expanded, node, object = self._get_node_data(id)
            if self.factory.on_hover is not None:
                self.ui.evaluate(self.factory.on_hover, object)
                self._veto = True
        elif self.factory and self.factory.on_hover is not None:
            self.ui.evaluate(self.factory.on_hover, None)

        # allow other events to be processed
        event.Skip(True)

    def _on_tree_item_activated(self, event):
        """Handles a tree item being activated."""
        expanded, node, object = self._get_node_data(event.GetItem())

        if node.activated(object) is True:
            if self.factory.on_activated is not None:
                self.ui.evaluate(self.factory.on_activated, object)
                self._veto = True
        else:
            self._veto = True

        # Fire the 'activated' event with the clicked on object as value:
        self.activated = object

        # FIXME: Firing the dclick event also for backward compatibility on wx.
        # Change it occur on mouse double click only.
        self.dclick = object

    def _on_tree_begin_label_edit(self, event):
        """Handles the user starting to edit a tree node label."""
        item = event.GetItem()
        parent = self._tree.GetItemParent(item)
        can_rename = True
        if parent.IsOk():
            expanded, node, object = self._get_node_data(parent)
            can_rename = node.can_rename(object)

        if can_rename:
            expanded, node, object = self._get_node_data(item)
            if node.can_rename_me(object):
                return

        event.Veto()

    def _on_tree_end_label_edit(self, event):
        """Handles the user completing tree node label editing."""
        label = event.GetLabel()
        if len(label) > 0:
            expanded, node, object = self._get_node_data(event.GetItem())
            # Tell the node to change the label. If it raises an exception,
            # that means it didn't like the label, so veto the tree node
            # change:
            try:
                node.set_label(object, label)
                return
            except:
                pass
        event.Veto()

    def _on_tree_begin_drag(self, event):
        """Handles a drag operation starting on a tree node."""
        if PythonDropSource is not None:
            expanded, node, object, nid, point = self._unpack_event(event)
            if node is not None:
                try:
                    self._dragging = nid
                    PythonDropSource(self._tree, node.get_drag_object(object))
                finally:
                    self._dragging = None

    def _on_tree_item_gettooltip(self, event):
        """Handles a tooltip request on a tree node."""
        nid = event.GetItem()
        if nid.IsOk():
            node_data = self._get_node_data(nid)
            if node_data is not None:
                expanded, node, object = node_data
                tooltip = node.get_tooltip(object)
                if tooltip != "":
                    event.SetToolTip(tooltip)

        event.Skip()

    def _on_left_dclick(self, event):
        """Handle left mouse dclick to emit dclick event for associated node."""
        # Determine what node (if any) was clicked on:
        expanded, node, object, nid, point = self._unpack_event(event)

        # If the mouse is over a node, then process the click:
        if node is not None:
            if node.dclick(object) is True:
                if self.factory.on_dclick is not None:
                    self.ui.evaluate(self.factory.on_dclick, object)
                    self._veto = True
            else:
                self._veto = True

            # Fire the 'dclick' event with the object as its value:
            # FIXME: This is instead done in _on_item_activated for backward
            # compatibility only on wx toolkit.
            # self.dclick = object

        # Allow normal mouse event processing to occur:
        event.Skip()

    def _on_left_down(self, event):
        """Handles the user right clicking on a tree node."""
        # Determine what node (if any) was clicked on:
        expanded, node, object, nid, point = self._unpack_event(event)

        # If the mouse is over a node, then process the click:
        if node is not None:
            if (node.click(object) is True) and (
                self.factory.on_click is not None
            ):
                self.ui.evaluate(self.factory.on_click, object)

            # Fire the 'click' event with the object as its value:
            self.click = object

        # Allow normal mouse event processing to occur:
        event.Skip()

    def _on_right_down(self, event):
        """Handles the user right clicking on a tree node."""
        expanded, node, object, nid, point = self._unpack_event(event)

        if node is not None:
            self._data = (node, object, nid)
            self._context = {
                "object": object,
                "editor": self,
                "node": node,
                "info": self.ui.info,
                "handler": self.ui.handler,
            }

            # Try to get the parent node of the node clicked on:
            pnid = self._tree.GetItemParent(nid)
            if pnid.IsOk():
                ignore, parent_node, parent_object = self._get_node_data(pnid)
            else:
                parent_node = parent_object = None

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
                    # Reset the group for the current usage in case it is
                    # shared - the call to `node.get_add()` is potentially
                    # dynamic and the callback `_menu_new_node()` captures
                    # state about this particular TreeEditor instance
                    group.clear()
                    actions = self._new_actions(node, object)
                    if len(actions) > 0:
                        group.insert(0, Menu(name="New", *actions))

            else:
                # All other values mean no menu should be displayed:
                menu = None

            # Only display the menu if a valid menu is defined:
            if menu is not None:
                wxmenu = menu.create_menu(self._tree, self)
                self._tree.PopupMenu(wxmenu, point[0] - 10, point[1] - 10)
                wxmenu.Destroy()

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
            if not factory:
                factory = klass

            def perform_add(object, factory, prompt):
                self._menu_new_node(factory, prompt)

            on_perform = partial(perform_add, factory=factory, prompt=prompt)
            items.append(Action(name=name, on_perform=on_perform))
        return items

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
        from pyface.wx.clipboard import clipboard

        return self._menu_node.can_add(object, clipboard.object_type)

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
        elif parent is not None:
            can_rename = parent.can_rename(object)
        else:
            can_rename = True
        return can_rename and self._menu_node.can_rename_me(object)

    # ----- Drag and drop event handlers: -------------------------------------

    def wx_dropped_on(self, x, y, data, drag_result):
        """Handles a Python object being dropped on the tree."""
        if isinstance(data, list):
            rc = wx.DragNone
            for item in data:
                rc = self.wx_dropped_on(x, y, item, drag_result)
            return rc

        expanded, node, object, nid, point = self._hit_test(wx.Point(x, y))
        if node is not None:
            if drag_result == wx.DragMove:
                if not self._is_droppable(node, object, data, False):
                    return wx.DragNone

                if self._dragging is not None:
                    data = self._drop_object(node, object, data, False)
                    if data is not None:
                        try:
                            self._begin_undo()
                            self._undoable_delete(
                                *self._node_index(self._dragging)
                            )
                            self._undoable_append(node, object, data, False)
                        finally:
                            self._end_undo()
                else:
                    data = self._drop_object(node, object, data)
                    if data is not None:
                        self._undoable_append(node, object, data, False)

                return drag_result

            to_node, to_object, to_index = self._node_index(nid)
            if to_node is not None:
                if self._dragging is not None:
                    data = self._drop_object(node, to_object, data, False)
                    if data is not None:
                        from_node, from_object, from_index = self._node_index(
                            self._dragging
                        )
                        if (to_object is from_object) and (
                            to_index > from_index
                        ):
                            to_index -= 1
                        try:
                            self._begin_undo()
                            self._undoable_delete(
                                from_node, from_object, from_index
                            )
                            self._undoable_insert(
                                to_node, to_object, to_index, data, False
                            )
                        finally:
                            self._end_undo()
                else:
                    data = self._drop_object(to_node, to_object, data)
                    if data is not None:
                        self._undoable_insert(
                            to_node, to_object, to_index, data, False
                        )

                return drag_result

        return wx.DragNone

    def wx_drag_over(self, x, y, data, drag_result):
        """Handles a Python object being dragged over the tree."""
        expanded, node, object, nid, point = self._hit_test(wx.Point(x, y))
        insert = False

        if (node is not None) and (drag_result == wx.DragCopy):
            node, object, index = self._node_index(nid)
            insert = True

        if (self._dragging is not None) and (
            not self._is_drag_ok(self._dragging, data, object)
        ):
            return wx.DragNone

        if (node is not None) and self._is_droppable(
            node, object, data, insert
        ):
            return drag_result

        return wx.DragNone

    def _is_drag_ok(self, snid, source, target):
        if (snid is None) or (target is source):
            return False

        for cnid in self._nodes(snid):
            if not self._is_drag_ok(
                cnid, self._get_node_data(cnid)[2], target
            ):
                return False

        return True

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
            except:
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
            if not eval(condition, globals(), self._context):
                value = False
            setattr(object, trait, value)

    # ----- Menu event handlers: ----------------------------------------------

    def _menu_copy_node(self):
        """Copies the current tree node object to the paste buffer."""
        from pyface.wx.clipboard import clipboard

        clipboard.data = self._data[1]
        self._data = None

    def _menu_cut_node(self):
        """Cuts the current tree node object into the paste buffer."""
        from pyface.wx.clipboard import clipboard

        node, object, nid = self._data
        clipboard.data = object
        self._data = None
        self._undoable_delete(*self._node_index(nid))

    def _menu_paste_node(self):
        """Pastes the current contents of the paste buffer into the current
        node.
        """
        from pyface.wx.clipboard import clipboard

        node, object, nid = self._data
        self._data = None
        self._undoable_append(node, object, clipboard.object_data, False)

    def _menu_delete_node(self):
        """Deletes the current node from the tree."""
        node, object, nid = self._data
        self._data = None
        rc = node.confirm_delete(object)
        if rc is not False:
            if rc is not True:
                if self.ui.history is None:
                    # If no undo history, ask user to confirm the delete:
                    dlg = wx.MessageDialog(
                        self._tree,
                        "Are you sure you want to delete %s?"
                        % node.get_label(object),
                        "Confirm Deletion",
                        style=wx.OK | wx.CANCEL | wx.ICON_EXCLAMATION,
                    )
                    if dlg.ShowModal() != wx.ID_OK:
                        return

            self._undoable_delete(*self._node_index(nid))

    def _menu_rename_node(self):
        """Renames the current tree node."""
        node, object, nid = self._data
        self._data = None
        object_label = ObjectLabel(label=node.get_label(object))
        if object_label.edit_traits().result:
            label = object_label.label.strip()
            if label != "":
                node.set_label(object, label)

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
                self._tree.SelectItem(self._tree.GetLastChild(nid))

    # -- Model event handlers -------------------------------------------------

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

            # Indicate whether the node has any children now:
            tree.SetItemHasChildren(nid, len(children) > 0)

            # Try to expand the node (if requested):
            if node.can_auto_open(object):
                tree.Expand(nid)

    def _children_updated(self, object, name, event):
        """Handles the children of a node being changed."""
        # Log the change that was made (removing '_items' from the end of the
        # name):
        name = name[:-6]
        self.log_change(self._get_undo_item, object, name, event)

        start = event.index
        end = start + len(event.removed)
        tree = self._tree

        for expanded, node, nid in self._object_info_for(object, name):
            n = len(node.get_children(object))

            # Only add/remove the changes if the node has already been
            # expanded:
            if expanded:
                # Remove all of the children that were deleted:
                for cnid in self._nodes_for(nid)[start:end]:
                    self._delete_node(cnid)

                # Add all of the children that were added:
                remaining = n - len(event.removed)
                child_index = 0
                for child in event.added:
                    child, child_node = self._node_for(child)
                    if child_node is not None:
                        insert_index = (
                            (start + child_index)
                            if (start < remaining)
                            else None
                        )
                        self._insert_node(nid, insert_index, child_node, child)
                        child_index += 1

            # Indicate whether the node has any children now:
            tree.SetItemHasChildren(nid, n > 0)

            # Try to expand the node (if requested):
            root = tree.GetRootItem()
            if node.can_auto_open(object):
                if (nid != root) or not self.factory.hide_root:
                    tree.Expand(nid)

    def _label_updated(self, object, name, label):
        """Handles the label of an object being changed."""
        nids = {}
        for name2, nid in self._map[id(object)]:
            if nid not in nids:
                nids[nid] = None
                node = self._get_node_data(nid)[1]
                self._tree.SetItemText(nid, node.get_label(object))
                self._update_icon_for_nid(nid)

    # -- UI preference save/restore interface ---------------------------------

    def restore_prefs(self, prefs):
        """Restores any saved user preference information associated with the
        editor.
        """
        if self._is_dock_window:
            if isinstance(prefs, dict):
                structure = prefs.get("structure")
            else:
                structure = prefs
            self.control.GetSizer().SetStructure(self.control, structure)

    def save_prefs(self):
        """Returns any user preference information associated with the editor."""
        if self._is_dock_window:
            return {"structure": self.control.GetSizer().GetStructure()}

        return None


# -- End UI preference save/restore interface -----------------------------


class ObjectLabel(HasStrictTraits):
    """An editable label for an object."""

    # -------------------------------------------------------------------------
    #  Trait definitions:
    # -------------------------------------------------------------------------

    #: Label to be edited
    label = Str()

    # -------------------------------------------------------------------------
    #  Traits view definition:
    # -------------------------------------------------------------------------

    traits_view = View(
        "label", title="Edit Label", kind="modal", buttons=["OK", "Cancel"]
    )
