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
from PyQt4 import QtCore, QtGui

# ETS imports
from editor import Editor


class SearchWidget(QtGui.QLineEdit):

    # FIXME: This widget needs a search button and a cancel button like the
    #        wxWidgets SearchControl.
    
    def __init__(self, desc):
        """ Store the descriptive text for the widget.
        """
        QtGui.QLineEdit.__init__(self)
        self._desc = desc
        
    def paintEvent(self, event):
        """ Overidden to allow the drawing of description text.
        """

        draw_default = not (self.hasFocus() or self.text().length())
        
        palette = QtGui.QApplication.instance().palette()
        if draw_default:
            palette.setColor(QtGui.QPalette.Text, 
                             palette.color(QtGui.QPalette.Dark))
            self.setText(self._desc) 
        self.setPalette(palette)

        QtGui.QLineEdit.paintEvent(self, event)

        if draw_default:
            self.setText('')


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
