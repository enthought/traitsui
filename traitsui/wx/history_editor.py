#-------------------------------------------------------------------------
#
#  Copyright (c) 2005, Enthought, Inc.
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
#  Date:   10/21/2004
#
#-------------------------------------------------------------------------

""" Defines a text editor which displays a text field and maintains a history
    of previously entered values.
"""

#-------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------

from __future__ import absolute_import
from traits.api \
    import Any, on_trait_change

from pyface.timer.api \
    import do_later

from .editor \
    import Editor

from .history_control \
    import HistoryControl

#-------------------------------------------------------------------------
#  '_HistoryEditor' class:
#-------------------------------------------------------------------------


class _HistoryEditor(Editor):
    """ Simple style text editor, which displays a text field and maintains a
        history of previously entered values, the maximum number of which is
        specified by the 'entries' trait of the HistoryEditor factory.
    """

    #-------------------------------------------------------------------------
    #  Trait definitions:
    #-------------------------------------------------------------------------

    # The history control:
    history = Any

    #-------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #-------------------------------------------------------------------------

    def init(self, parent):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.history = history = HistoryControl(
            value=self.value,
            entries=self.factory.entries,
            auto_set=self.factory.auto_set)
        self.control = history.create_control(parent)

        self.set_tooltip()

    def dispose(self):
        """ Disposes of the contents of an editor.
        """
        self.history.dispose()
        self.history = None

        super(_HistoryEditor, self).dispose()

    #-------------------------------------------------------------------------
    #  Handles the user entering input data in the edit control:
    #-------------------------------------------------------------------------

    @on_trait_change('history:value')
    def _value_changed(self, value):
        """ Handles the history object's 'value' trait being changed.
        """
        if not self._dont_update:
            history = self.history
            try:
                self._dont_update = True
                self.value = history.value
                history.error = False
            except:
                history.error = True

            do_later(self.trait_set, _dont_update=False)

    #-------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #-------------------------------------------------------------------------

    def update_editor(self):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        if not self._dont_update:
            self._dont_update = True
            self.history.value = self.value
            self.history.error = False
            self._dont_update = False

    #-------------------------------------------------------------------------
    #  Handles an error that occurs while setting the object's trait value:
    #-------------------------------------------------------------------------

    def error(self, excp):
        """ Handles an error that occurs while setting the object's trait value.
        """
        pass

    #-- UI preference save/restore interface ---------------------------------

    #-------------------------------------------------------------------------
    #  Restores any saved user preference information associated with the
    #  editor:
    #-------------------------------------------------------------------------

    def restore_prefs(self, prefs):
        """ Restores any saved user preference information associated with the
            editor.
        """
        self.history.history = \
            prefs.get('history', [])[: self.factory.entries]

    #-------------------------------------------------------------------------
    #  Returns any user preference information associated with the editor:
    #-------------------------------------------------------------------------

    def save_prefs(self):
        """ Returns any user preference information associated with the editor.
        """
        # If the view closed successfully, try to update the history with the
        # current value:
        if self.ui.result:
            self._dont_update = True
            self.history.set_value(self.value)
            self._dont_update = False

        return {'history': self.history.history[:]}

# EOF #########################################################################
