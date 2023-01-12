# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Defines an editor for playing animated GIF files.
"""


from wx.adv import Animation, GenericAnimationCtrl

from traits.api import Bool, Str

from traitsui.wx.editor import Editor

from traitsui.basic_editor_factory import BasicEditorFactory


class _AnimatedGIFEditor(Editor):
    """Editor that displays an animated GIF file."""

    # -------------------------------------------------------------------------
    #  Trait definitions:
    # -------------------------------------------------------------------------

    #: Is the animated GIF file currently playing?
    playing = Bool(True)

    def init(self, parent):
        """Finishes initializing the editor by creating the underlying toolkit
        widget.
        """
        self._animate = Animation(self.value)
        self.control = GenericAnimationCtrl(parent, -1, self._animate)
        self.control.SetUseWindowBackgroundColour()
        self.sync_value(self.factory.playing, "playing", "from")
        self.set_tooltip()

    def update_editor(self):
        """Updates the editor when the object trait changes externally to the
        editor.
        """
        if not self.playing:
            self.control.Stop()

        self.control.LoadFile(self.value)
        self._file_loaded = True

        if self.playing:
            self.control.Play()

    def _playing_changed(self):
        if self._file_loaded:
            if self.playing:
                self.control.Play()
            else:
                self.control.Stop()


# -------------------------------------------------------------------------
#  Create the editor factory object:
# -------------------------------------------------------------------------

# wxPython editor factory for animated GIF editors:


class AnimatedGIFEditor(BasicEditorFactory):

    #: The editor class to be created:
    klass = _AnimatedGIFEditor

    #: The optional trait used to control whether the animated GIF file is
    #: playing or not:
    playing = Str()
