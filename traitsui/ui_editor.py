# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!


""" Defines the BasicUIEditor class, which allows creating editors that define
    their function by creating an embedded Traits UI.
"""

from traits.api import Instance

from .ui import UI

from .editor import Editor

# -------------------------------------------------------------------------
#  'UIEditor' base class:
# -------------------------------------------------------------------------


class UIEditor(Editor):
    """An editor that creates an embedded Traits UI."""

    # -------------------------------------------------------------------------
    #  Trait definitions:
    # -------------------------------------------------------------------------

    #: The Traits UI created by the editor
    editor_ui = Instance(UI)

    def init(self, parent):
        """Finishes initializing the editor by creating the underlying toolkit
        widget.
        """
        self.editor_ui = self.init_ui(parent).trait_set(parent=self.ui)
        self.control = self.editor_ui.control

    def init_ui(self, parent):
        """Creates the traits UI for the editor."""
        return self.value.edit_traits(
            view=self.trait_view(),
            context={"object": self.value, "editor": self},
            parent=parent,
        )

    def update_editor(self):
        """Updates the editor when the object trait changes external to the
        editor.
        """
        # Do nothing, since the embedded traits UI should handle the updates
        # itself, without our meddling:
        pass

    def dispose(self):
        """Disposes of the contents of an editor."""
        # Make sure the embedded traits UI is disposed of properly:
        if self.editor_ui is not None:
            self.editor_ui.dispose()

        super().dispose()

    def get_error_control(self):
        """Returns the editor's control for indicating error status."""
        return self.editor_ui.get_error_controls()

    # -- UI preference save/restore interface ---------------------------------

    def restore_prefs(self, prefs):
        """Restores any saved user preference information associated with the
        editor.
        """
        self.editor_ui.set_prefs(prefs)

    def save_prefs(self):
        """Returns any user preference information associated with the editor."""
        return self.editor_ui.get_prefs()
