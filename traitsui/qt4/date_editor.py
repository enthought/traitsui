#------------------------------------------------------------------------------
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
#  Date:   08/03/2009
#
#------------------------------------------------------------------------------

""" A Traits UI editor for datetime.date objects.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import datetime

from pyface.qt import QtCore, QtGui

from editor import Editor
from editor_factory import ReadonlyEditor as BaseReadonlyEditor

#-------------------------------------------------------------------------------
#  'SimpleEditor' class:
#-------------------------------------------------------------------------------

class SimpleEditor(Editor):
    """ Simple Traits UI date editor that wraps QDateEdit.
    """

    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------

    def init(self, parent):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.control = QtGui.QDateEdit()
        if hasattr(self.factory, 'qt_date_format'):
            self.control.setDisplayFormat(self.factory.qt_date_format)

        if not self.factory.allow_future:
            self.control.setMaximumDate(QtCore.QDate.currentDate())

        if getattr(self.factory, 'maximum_date_name', None):
            obj, extended_name, func = self.parse_extended_name(self.factory.maximum_date_name)
            self.factory.maximum_date = func()

        if getattr(self.factory, 'minimum_date_name', None):
            obj, extended_name, func = self.parse_extended_name(self.factory.minimum_date_name)
            self.factory.minimum_date = func()

        if getattr(self.factory, 'minimum_date', None):
            min_date = QtCore.QDate(self.factory.minimum_date.year,
                                    self.factory.minimum_date.month,
                                    self.factory.minimum_date.day)
            self.control.setMinimumDate(min_date)

        if getattr(self.factory, 'maximum_date', None):
            max_date = QtCore.QDate(self.factory.maximum_date.year,
                                    self.factory.maximum_date.month,
                                    self.factory.maximum_date.day)
            self.control.setMaximumDate(max_date)

        signal = QtCore.SIGNAL('dateChanged(QDate)')
        QtCore.QObject.connect(self.control, signal, self.update_object)

    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------

    def update_editor(self):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        value = self.value
        if value:
            q_date = QtCore.QDate(value.year, value.month, value.day)
            self.control.setDate(q_date)

    #---------------------------------------------------------------------------
    #  Handles the user entering input data in the edit control:
    #---------------------------------------------------------------------------

    def update_object(self, q_date):
        """ Handles the user entering input data in the edit control.
        """
        year = q_date.year()
        month = q_date.month()
        day = q_date.day()
        try:
            self.value = datetime.date(year, month, day)
        except ValueError:
            print 'Invalid date:', year, month, day
            raise

#-------------------------------------------------------------------------------
#  'CustomEditor' class:
#-------------------------------------------------------------------------------

class CustomEditor(Editor):
    """ Custom Traits UI date editor that wraps QCalendarWidget.
    """

    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------

    def init(self, parent):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.control = QtGui.QCalendarWidget()

        if not self.factory.allow_future:
            self.control.setMaximumDate(QtCore.QDate.currentDate())

        signal = QtCore.SIGNAL('clicked(QDate)')
        QtCore.QObject.connect(self.control, signal, self.update_object)

    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------

    def update_editor(self):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        value = self.value
        if value:
            q_date = QtCore.QDate(value.year, value.month, value.day)
            self.control.setSelectedDate(q_date)

    #---------------------------------------------------------------------------
    #  Handles the user entering input data in the edit control:
    #---------------------------------------------------------------------------

    def update_object(self, q_date):
        """ Handles the user entering input data in the edit control.
        """
        year = q_date.year()
        month = q_date.month()
        day = q_date.day()
        try:
            self.value = datetime.date(year, month, day)
        except ValueError:
            print 'Invalid date:', year, month, day
            raise

#------------------------------------------------------------------------------
# 'ReadonlyEditor' class:
#------------------------------------------------------------------------------

class ReadonlyEditor(BaseReadonlyEditor):
    """ Readonly Traits UI date editor that uses a QLabel for the view.
    """

    def _get_str_value(self):
        """ Replace the default string value with our own date verision.
        """
        if not self.value:
            return self.factory.message
        else:
            return self.value.strftime(self.factory.strftime)
