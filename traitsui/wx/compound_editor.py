# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Defines the compound editor and the compound editor factory for the
    wxPython user interface toolkit.
"""


import wx

from traits.api import Str

from .editor import Editor

from .helper import TraitsUIPanel

# -------------------------------------------------------------------------
#  'CompoundEditor' class:
# -------------------------------------------------------------------------


class CompoundEditor(Editor):
    """Editor for compound traits, which displays editors for each of the
    combined traits, in the appropriate style.
    """

    # -------------------------------------------------------------------------
    #  Trait definitions:
    # -------------------------------------------------------------------------

    #: The kind of editor to create for each list item
    kind = Str()

    def init(self, parent):
        """Finishes initializing the editor by creating the underlying toolkit
        widget.
        """
        # Create a panel to hold all of the component trait editors:
        self.control = panel = TraitsUIPanel(parent, -1)
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Add all of the component trait editors:
        self._editors = editors = []
        for factory in self.factory.editors:
            editor = getattr(factory, self.kind)(
                self.ui, self.object, self.name, self.description, panel
            )
            editor.prepare(panel)
            sizer.Add(
                editor.control, 1, wx.TOP | wx.BOTTOM | editor.layout_style, 3
            )
            editors.append(editor)

        # Set-up the layout:
        panel.SetSizerAndFit(sizer)

        self.set_tooltip()

    def update_editor(self):
        """Updates the editor when the object trait changes externally to the
        editor.
        """
        pass

    def dispose(self):
        """Disposes of the contents of an editor."""
        for editor in self._editors:
            editor.dispose()

        super().dispose()


class SimpleEditor(CompoundEditor):

    #: The kind of editor to create for each list item. This value overrides
    #: the default.
    kind = "simple_editor"


class CustomEditor(CompoundEditor):

    #: The kind of editor to create for each list item. This value overrides
    #: the default.

    kind = "custom_editor"
