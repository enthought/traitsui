# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

from traitsui.testing.tester.command import MouseClick
from traitsui.testing.tester.locator import Index
from traitsui.testing.tester._ui_tester_registry._common_ui_targets import (
    BaseSourceWithLocation,
)
from traitsui.testing.tester._ui_tester_registry._traitsui_ui import (
    register_traitsui_ui_solvers,
)
from traitsui.testing.tester._ui_tester_registry.wx import _interaction_helpers
from traitsui.wx.list_editor import CustomEditor, NotebookEditor, SimpleEditor


class _IndexedNotebookEditor(BaseSourceWithLocation):
    """Wrapper for a ListEditor (Notebook) with an index."""

    source_class = NotebookEditor
    locator_class = Index
    handlers = [
        (
            MouseClick,
            (
                lambda wrapper, _: _interaction_helpers.mouse_click_notebook_tab_index(
                    control=wrapper._target.source.control,
                    index=wrapper._target.location.index,
                    delay=wrapper.delay,
                )
            ),
        ),
    ]

    @classmethod
    def register(cls, registry):
        """Class method to register interactions on a _IndexedNotebookEditor
        for the given registry.

        If there are any conflicts, an error will occur.

        Parameters
        ----------
        registry : TargetRegistry
            The registry being registered to.
        """
        super().register(registry)
        register_traitsui_ui_solvers(
            registry=registry,
            target_class=cls,
            traitsui_ui_getter=lambda target: target._get_nested_ui(),
        )

    def _get_nested_ui(self):
        """Method to get the nested ui corresponding to the List element at
        the given index.
        """
        return self.source._uis[self.location.index][0].dockable.ui


def _get_next_target(list_editor, index):
    """Gets the target at a given index from a Custom List Editor.

    Parameters
    ----------
    list_editor : CustomEditor
        The custom style list editor in which the target is contained.
    index : int
        the index of the target of interest in the list

    Returns
    -------
    traitsui.editor.Editor
        The obtained target.
    """
    # each list item gets a corresponding ImageControl item (allows one to
    # add items to the list before, after, delete, etc.) along with the
    # item itself.  Thus, index is actually an index over the odd elements
    # of the list of children corresponding to items in the list we would
    # want to interact with
    new_index = 2 * index + 1
    WindowList = list_editor.control.GetChildren()
    item = WindowList[new_index]
    return item._editor


def register(registry):
    """Register interactions for the given registry.

    If there are any conflicts, an error will occur.

    Parameters
    ----------
    registry : TargetRegistry
        The registry being registered to.
    """
    # NotebookEditor
    _IndexedNotebookEditor.register(registry)
    # CustomEditor
    registry.register_location(
        target_class=CustomEditor,
        locator_class=Index,
        solver=lambda wrapper, location: (
            _get_next_target(wrapper._target, location.index)
        ),
    )
    # SimpleEditor
    registry.register_location(
        target_class=SimpleEditor,
        locator_class=Index,
        solver=lambda wrapper, location: (
            _get_next_target(wrapper._target, location.index)
        ),
    )
