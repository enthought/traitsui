#-------------------------------------------------------------------------------
#
#  Copyright (c) 2009, Enthought, Inc.
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
#  Date:   06/25/09
#
#-------------------------------------------------------------------------------

# System library imports
from enthought.qt import QtCore, QtGui

# ETS imports
from editor import Editor


class SearchWidget(QtGui.QLineEdit):

    # FIXME: This widget needs a search button and a cancel button like the
    #        wxWidgets SearchControl.
    
    def __init__(self, desc):
        """ Store the descriptive text for the widget.
        """
        QtGui.QLineEdit.__init__(self)
        
        self._desc = unicode(desc)
        
    def paintEvent(self, event):
        """ Overloads the QLineEdit paintEvent handler. Sets the default text if
            the user has not modified it yet, then calls the parent paintEvent
        """
        if not self.isModified():
            self._set_default_text()
        super(SearchWidget, self).paintEvent(event)
                    
    def focusInEvent(self, event):
        """ Handles accepting focus.
        
            If the text box contains the default description string,
            change the text color back to the correct color and reset the 
            text string so the user doesn't have to select & delete it before
            typing in the box
        """
        palette = QtGui.QApplication.instance().palette()
        self.setPalette(palette)
        
        if self.text() == self._desc:
            # Set the text to an empty string, but make sure to set the modified
            # property because Qt will reset it when the text is an empty string
            self.setText('')
            self.setModified(True)
            self.update()
        
        super(SearchWidget, self).focusInEvent(event)
            

    def focusOutEvent(self, event):
        """ Handles accepting focus.
            
            When focus is lost, if the user had typed something, keep that text,
            otherwise replace it with the default description string.
        """
        if len(self.text()) == 0:
            self._set_default_text()

        super(SearchWidget, self).focusOutEvent(event)

    def _set_default_text(self):
        palette = QtGui.QApplication.instance().palette()
        palette.setColor(QtGui.QPalette.Text, 
                         palette.color(QtGui.QPalette.Dark))
        self.setPalette(palette)
        self.setText(self._desc)
        self.setModified(True)
        self.update()
            

class SearchEditor(Editor):
    
    def init(self, parent):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """

        control = self.control = SearchWidget(self.factory.text)
        
        if self.factory.auto_set:
            QtCore.QObject.connect(control, QtCore.SIGNAL('textEdited(QString)'),
                                   self.update_object)
        if self.factory.enter_set:
            QtCore.QObject.connect(control, QtCore.SIGNAL('editingFinished()'),
                                   self.update_object)

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
