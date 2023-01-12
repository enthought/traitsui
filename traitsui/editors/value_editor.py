# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Defines the tree-based Python value editor and the value editor factory.
"""

from traits.api import Bool, Instance, Int

from traitsui.editor import Editor
from traitsui.editor_factory import EditorFactory
from traitsui.editors.tree_editor import TreeEditor
from traitsui.item import Item
from traitsui.value_tree import RootNode, value_tree_nodes
from traitsui.view import View

# -------------------------------------------------------------------------
#  'SimpleEditor' class:
# -------------------------------------------------------------------------


class _ValueEditor(Editor):
    """Simple style of editor for values, which displays a tree."""

    # -------------------------------------------------------------------------
    #  Trait definitions:
    # -------------------------------------------------------------------------

    #: Is the editor read only?
    readonly = Bool(False)

    #: The root node of the value tree
    root = Instance(RootNode)

    #: Is the value editor scrollable? This values overrides the default.
    scrollable = True

    def init(self, parent):
        """Finishes initializing the editor by creating the underlying toolkit
        widget.
        """
        self.update_editor()
        editor = TreeEditor(
            auto_open=self.factory.auto_open,
            hide_root=True,
            editable=False,
            nodes=value_tree_nodes,
        )
        self._ui = self.edit_traits(
            parent=parent,
            view=View(
                Item("root", show_label=False, editor=editor), kind="subpanel"
            ),
        )
        self._ui.parent = self.ui
        self.control = self._ui.control

    def update_editor(self):
        """Updates the editor when the object trait changes external to the
        editor.
        """
        self.root = RootNode(name="", value=self.value, readonly=self.readonly)

    def dispose(self):
        """Disposes of the contents of an editor."""
        self._ui.dispose()

        super().dispose()

    def get_error_control(self):
        """Returns the editor's control for indicating error status."""
        return self._ui.get_error_controls()


class ValueEditor(EditorFactory):
    """Editor factory for tree-based value editors."""

    # -------------------------------------------------------------------------
    #  Trait definitions:
    # -------------------------------------------------------------------------

    #: Number of tree levels to automatically open
    auto_open = Int(2)


# This alias is deprecated and will be removed in TraitsUI 8.
ToolkitEditorFactory = ValueEditor
