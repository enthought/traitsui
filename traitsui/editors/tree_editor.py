#------------------------------------------------------------------------------
#
#  Copyright (c) 2008, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
#  Author: David C. Morrill
#
#------------------------------------------------------------------------------
""" Defines the tree editor factory for all traits user interface toolkits.
"""

#-------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------

from __future__ import absolute_import

from traits.api import Any, Dict, Bool, Tuple, Int, List, Instance, Str, Enum

from ..menu import Action
from ..tree_node import TreeNode
from ..dock_window_theme import DockWindowTheme
from ..editor_factory import EditorFactory
from ..helper import Orientation

#-------------------------------------------------------------------------
#  Trait definitions:
#-------------------------------------------------------------------------

# Size of each tree node icon
IconSize = Tuple((16, 16), Int, Int)


#-------------------------------------------------------------------------
#  The core tree node menu actions:
#-------------------------------------------------------------------------


NewAction = 'NewAction'
CopyAction = Action(name='Copy',
                    action='editor._menu_copy_node',
                    enabled_when='editor._is_copyable(object)')
CutAction = Action(name='Cut',
                   action='editor._menu_cut_node',
                   enabled_when='editor._is_cutable(object)')
PasteAction = Action(name='Paste',
                     action='editor._menu_paste_node',
                     enabled_when='editor._is_pasteable(object)')
DeleteAction = Action(name='Delete',
                      action='editor._menu_delete_node',
                      enabled_when='editor._is_deletable(object)')
RenameAction = Action(name='Rename',
                      action='editor._menu_rename_node',
                      enabled_when='editor._is_renameable(object)')


#-------------------------------------------------------------------------
#  'ToolkitEditorFactory' class:
#-------------------------------------------------------------------------


class ToolkitEditorFactory(EditorFactory):
    """ Editor factory for tree editors.
    """
    #-------------------------------------------------------------------------
    #  Trait definitions:
    #-------------------------------------------------------------------------

    #: Supported TreeNode objects
    nodes = List(TreeNode)

    #: Mapping from TreeNode tuples to MultiTreeNodes
    multi_nodes = Dict

    #: The column header labels if any.
    column_headers = List(Str)

    #: Are the individual nodes editable?
    editable = Bool(True)

    #: Selection mode.
    selection_mode = Enum('single', 'extended')

    #: Is the editor shared across trees?
    shared_editor = Bool(False)

    #: Reference to a shared object editor
    editor = Instance(EditorFactory)

    # FIXME: Implemented only in wx backend.
    #: The DockWindow graphical theme
    dock_theme = Instance(DockWindowTheme)

    #: Show icons for tree nodes?
    show_icons = Bool(True)

    #: Hide the tree root node?
    hide_root = Bool(False)

    #: Layout orientation of the tree and the editor
    orientation = Orientation

    #: Number of tree levels (down from the root) that should be automatically
    #: opened
    auto_open = Int

    #: Size of the tree node icons
    icon_size = IconSize

    #: Called when a node is selected
    on_select = Any

    #: Called when a node is clicked
    on_click = Any

    #: Called when a node is double-clicked
    on_dclick = Any

    #: Called when a node is activated
    on_activated = Any

    #: Call when the mouse hovers over a node
    on_hover = Any

    #: The optional extended trait name of the trait to synchronize with the
    #: editor's current selection:
    selected = Str

    #: The optional extended trait name of the trait that should be assigned
    #: a node object when a tree node is activated, by double-clicking or
    #: pressing the Enter key when a node has focus (Note: if you want to
    #: receive repeated activated events on the same node, make sure the trait
    #: is defined as an Event):
    activated = Str

    #: The optional extended trait name of the trait that should be assigned
    #: a node object when a tree node is clicked on (Note: If you want to
    #: receive repeated clicks on the same node, make sure the trait is defined
    #: as an Event):
    click = Str

    #: The optional extended trait name of the trait that should be assigned
    #: a node object when a tree node is double-clicked on (Note: if you want to
    #: receive repeated double-clicks on the same node, make sure the trait is
    #: defined as an Event):
    dclick = Str

    #: The optional extended trait name of the trait event that is fired
    #: whenever the application wishes to veto a tree action in progress (e.g.
    #: double-clicking a non-leaf tree node normally opens or closes the node,
    #: but if you are handling the double-click event in your program, you may
    #: wish to veto the open or close operation). Be sure to fire the veto event
    #: in the event handler triggered by the operation (e.g. the 'dclick' event
    #: handler.
    veto = Str

    #: The optional extended trait name of the trait event that is fired when the
    #: application wishes the currently visible portion of the tree widget to
    #: repaint itself.
    refresh = Str

    #: Mode for lines connecting tree nodes
    #:
    #: * 'appearance': Show lines only when they look good.
    #: * 'on': Always show lines.
    #: * 'off': Don't show lines.
    lines_mode = Enum('appearance', 'on', 'off')

    # FIXME: Document as unimplemented or wx specific.
    #: Whether to alternate row colors or not.
    alternating_row_colors = Bool(False)

    #: Any extra vertical padding to add.
    vertical_padding = Int(0)

    #: Whether or not to expand on a double-click.
    expands_on_dclick = Bool(True)

    #: Whether the labels should be wrapped around, if not an ellipsis is shown
    #: This works only in the qt backend and if there is only one column in tree
    word_wrap = Bool(False)

#: Define the TreeEditor class.
TreeEditor = ToolkitEditorFactory
