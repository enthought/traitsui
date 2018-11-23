#-------------------------------------------------------------------------
#
#  Copyright (c) 2007, Enthought, Inc.
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
#  Date:   03/02/2007
#
#-------------------------------------------------------------------------

""" Defines an editor for playing animated GIF files.
"""

#-------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------

from __future__ import absolute_import
from wx.animate \
    import Animation, AnimationCtrl

from traits.api \
    import Bool, Str

from traitsui.wx.editor \
    import Editor

from traitsui.basic_editor_factory \
    import BasicEditorFactory

#-------------------------------------------------------------------------
#  '_AnimatedGIFEditor' class:
#-------------------------------------------------------------------------


class _AnimatedGIFEditor(Editor):
    """ Editor that displays an animated GIF file.
    """

    #-------------------------------------------------------------------------
    #  Trait definitions:
    #-------------------------------------------------------------------------

    # Is the animated GIF file currently playing?
    playing = Bool(True)

    #-------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #-------------------------------------------------------------------------

    def init(self, parent):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self._animate = Animation(self.value)
        self.control = AnimationCtrl(parent, -1, self._animate)
        self.control.SetUseWindowBackgroundColour()
        self.sync_value(self.factory.playing, 'playing', 'from')
        self.set_tooltip()

    #-------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #-------------------------------------------------------------------------

    def update_editor(self):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        if not self.playing:
            self.control.Stop()

        self.control.LoadFile(self.value)
        self._file_loaded = True

        if self.playing:
            self.control.Play()

    #-------------------------------------------------------------------------
    #  Handles the editor 'playing' trait being changed:
    #-------------------------------------------------------------------------

    def _playing_changed(self):
        if self._file_loaded:
            if self.playing:
                self.control.Play()
            else:
                self.control.Stop()

#-------------------------------------------------------------------------
#  Create the editor factory object:
#-------------------------------------------------------------------------

# wxPython editor factory for animated GIF editors:


class AnimatedGIFEditor(BasicEditorFactory):

    # The editor class to be created:
    klass = _AnimatedGIFEditor

    # The optional trait used to control whether the animated GIF file is
    # playing or not:
    playing = Str
