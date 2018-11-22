#-------------------------------------------------------------------------
#  Copyright (c) 20011, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
#  Author: Evan Patterson
#-------------------------------------------------------------------------

# System library imports
from __future__ import absolute_import
from pyface.qt import QtCore, QtGui

# ETS imports
from .editor import Editor
import six


class SearchWidget(QtGui.QLineEdit):

    # FIXME: This widget needs a search button and a cancel button like the
    #        wxWidgets SearchControl.

    def __init__(self, desc):
        """ Store the descriptive text for the widget.
        """
        super(SearchWidget, self).__init__()
        self._desc = six.text_type(desc)
        self._set_descriptive_text()

    def focusInEvent(self, event):
        """ Handles accepting focus.

        If the text box contains the default description string, reset the text
        color and clear the box.
        """
        palette = QtGui.QApplication.instance().palette()
        self.setPalette(palette)

        if self.text() == self._desc:
            self.setText('')
            self.update()

        super(SearchWidget, self).focusInEvent(event)

    def focusOutEvent(self, event):
        """ Handles losing focus.

        When focus is lost, if the user had typed something, keep that text,
        otherwise replace it with the default description string.
        """
        if len(self.text()) == 0:
            self._set_descriptive_text()

        super(SearchWidget, self).focusOutEvent(event)

    def _set_descriptive_text(self):
        """ Sets the greyed-out descriptive text.
        """
        palette = QtGui.QApplication.instance().palette()
        palette.setColor(QtGui.QPalette.Text,
                         palette.color(QtGui.QPalette.Dark))
        self.setPalette(palette)
        self.setText(self._desc)
        self.update()


class SearchEditor(Editor):

    def init(self, parent):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        if QtCore.__version_info__ < (4, 7, 0):
            control = self.control = SearchWidget(self.factory.text)
        else:
            control = self.control = QtGui.QLineEdit()
            control.setPlaceholderText(self.factory.text)

        if self.factory.auto_set:
            control.textEdited.connect(self.update_object)
        if self.factory.enter_set:
            control.editingFinished.connect(self.update_object)

    def update_object(self, event=None):
        """ Handles the user entering input data in the edit control.
        """
        if not self._no_update:
            self.value = str(self.control.text())
            if self.factory.search_event_trait != '':
                setattr(self.object, self.factory.search_event_trait, True)

    def update_editor(self):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        if str(self.control.text()) != self.value:
            self._no_update = True
            self.control.setText(self.str_value)
            self._no_update = False
