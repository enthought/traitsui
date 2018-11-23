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
    import GIFAnimationCtrl

from traits.api \
    import Bool, Str

from traitsui.wx.editor \
    import Editor

from traitsui.basic_editor_factory \
    import BasicEditorFactory

from pyface.timer.api \
    import do_after

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
        self.control = GIFAnimationCtrl(parent, -1)
        self.control.GetPlayer().UseBackgroundColour(True)
        self.sync_value(self.factory.playing, 'playing', 'from')
        self.set_tooltip()

    #-------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #-------------------------------------------------------------------------

    def update_editor(self):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        control = self.control
        if self.playing:
            control.Stop()

        control.LoadFile(self.value)
        self._file_loaded = True

        # Note: It seems to be necessary to Play/Stop the control to avoid a
        # hard wx crash when 'PlayNextFrame' is called the first time (must be
        # some kind of internal initialization issue):
        control.Play()
        control.Stop()

        if self.playing or self._not_first:
            self._playing_changed()
        else:
            do_after(300, self._frame_changed)

        self._not_first = True

    #-------------------------------------------------------------------------
    #  Handles the editor 'playing' trait being changed:
    #-------------------------------------------------------------------------

    def _playing_changed(self):
        """ Handles the editor 'playing' trait being changed.
        """
        if self._file_loaded:
            try:
                if self.playing:
                    self.control.Play()
                else:
                    player = self.control.GetPlayer()
                    player.SetCurrentFrame(0)
                    player.PlayNextFrame()
                    player.Stop()
            except:
                pass

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
