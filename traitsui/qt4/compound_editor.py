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

""" Defines the compound editor and the compound editor factory for the
PyQt user interface toolkit.
"""


from pyface.qt import QtGui

from traits.api import Str

from .editor import Editor


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
        self.control = QtGui.QWidget()
        layout = QtGui.QVBoxLayout(self.control)
        layout.setContentsMargins(0, 0, 0, 0)

        # Add all of the component trait editors:
        self._editors = editors = []
        for factory in self.factory.editors:
            editor = getattr(factory, self.kind)(
                self.ui, self.object, self.name, self.description, None
            )
            editor.prepare(self.control)
            layout.addWidget(editor.control)
            editors.append(editor)

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
