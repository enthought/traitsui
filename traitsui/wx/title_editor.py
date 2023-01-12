# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Define an editor that displays a string value as a title.
"""


from .editor import Editor

from pyface.api import HeadingText

# FIXME: TitleEditor (the editor factory for title editors) is a proxy class
# defined here just for backward compatibility. The class has been moved to
# traitsui.editors.title_editor.
from traitsui.editors.title_editor import TitleEditor


# -------------------------------------------------------------------------
#  '_TitleEditor' class:
# -------------------------------------------------------------------------


class _TitleEditor(Editor):

    def init(self, parent):
        """Finishes initializing the editor by creating the underlying toolkit
        widget.
        """
        self._control = HeadingText(parent=parent, create=False)
        self._control.create()
        self.control = self._control.control
        self.set_tooltip()

    def update_editor(self):
        """Updates the editor when the object trait changes external to the
        editor.
        """
        self._control.text = self.str_value

    def dispose(self):
        """Cleanly dispose of the editor.

        This ensures that the wrapped Pyface Widget is cleaned-up.
        """
        if self._control is not None:
            self._control.destroy()
        super().dispose()


SimpleEditor = _TitleEditor
CustomEditor = _TitleEditor
ReadonlyEditor = _TitleEditor
TextEditor = _TitleEditor
