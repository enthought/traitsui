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

#-------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------

from __future__ import absolute_import, print_function

import datetime

from pyface.qt import QtCore, QtGui
from traits.api import Bool, Date, Dict, Instance, Set

from .editor import Editor
from .editor_factory import ReadonlyEditor as BaseReadonlyEditor
from traitsui.editors.date_editor import CellFormat

import six

#-------------------------------------------------------------------------
#  'SimpleEditor' class:
#-------------------------------------------------------------------------


class SimpleEditor(Editor):
    """ Simple Traits UI date editor that wraps QDateEdit.
    """

    #-------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #-------------------------------------------------------------------------

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
            obj, extended_name, func = self.parse_extended_name(
                self.factory.maximum_date_name)
            self.factory.maximum_date = func()

        if getattr(self.factory, 'minimum_date_name', None):
            obj, extended_name, func = self.parse_extended_name(
                self.factory.minimum_date_name)
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

        self.control.dateChanged.connect(self.update_object)

    #-------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #-------------------------------------------------------------------------

    def update_editor(self):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        value = self.value
        if value:
            q_date = QtCore.QDate(value.year, value.month, value.day)
            self.control.setDate(q_date)

    #-------------------------------------------------------------------------
    #  Handles the user entering input data in the edit control:
    #-------------------------------------------------------------------------

    def update_object(self, q_date):
        """ Handles the user entering input data in the edit control.
        """
        self.value = datetime.date(q_date.year(), q_date.month(), q_date.day())

#-------------------------------------------------------------------------
#  'CustomEditor' class:
#-------------------------------------------------------------------------


class CustomEditor(Editor):
    """ Custom Traits UI date editor that wraps QCalendarWidget.
    """

    # Style used for when a date is unselected.
    # Mapping from datetime.date to CellFormat
    _unselected_styles = Dict(Date, Instance(CellFormat))

    # Selected dates (used when multi_select is true)
    _selected = Set(Date)

    #-------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #-------------------------------------------------------------------------

    def init(self, parent):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.control = QtGui.QCalendarWidget()

        if not self.factory.allow_future:
            self.control.setMaximumDate(QtCore.QDate.currentDate())

        self.control.clicked.connect(self.update_object)

    #-------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #-------------------------------------------------------------------------

    def update_editor(self):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        value = self.value
        if value:
            if not self.factory.multi_select:
                q_date = QtCore.QDate(value.year, value.month, value.day)
                self.control.setSelectedDate(q_date)
            else:
                self.apply_unselected_style_to_all()
                for date in value:
                    self.apply_style(self.factory.selected_style, date)
                self._selected = set(value)

    #-------------------------------------------------------------------------
    #  Handles the user entering input data in the edit control:
    #-------------------------------------------------------------------------

    def update_object(self, q_date):
        """ Handles the user entering input data in the edit control.
        """
        value = datetime.date(q_date.year(), q_date.month(), q_date.day())
        if self.factory.multi_select:
            if value in self.value:
                self.unselect_date(value)
            else:
                self.select_date(value)

            self.value = sorted(self._selected)

        else:
            self.value = value

    def unselect_date(self, date):
        self._selected.remove(date)
        self.apply_unselected_style(date)

    def select_date(self, date):
        self._selected.add(date)
        self.apply_style(self.factory.selected_style, date)

    #-------------------------------------------------------------------------
    #  Helper methods for applying styling
    #-------------------------------------------------------------------------

    def set_unselected_style(self, style, date):
        """ Set the style used for a date when it is not selected."""
        self._unselected_styles[date] = style
        if self.factory.multi_select:
            if date not in self.value:
                self.apply_style(style, date)
        else:
            self.apply_style(style, date)

    def apply_style(self, style, date):
        """ Apply a given style to a given date."""
        qdt = QtCore.QDate(date)
        textformat = self.control.dateTextFormat(qdt)
        _apply_cellformat(style, textformat)
        self.control.setDateTextFormat(qdt, textformat)

    def apply_unselected_style(self, date):
        """ Apply the style for when a date is unselected."""
        # Resets the text format on the given dates
        textformat = QtGui.QTextCharFormat()
        if date in self._unselected_styles:
            _apply_cellformat(self._unselected_styles[date], textformat)
        qdt = QtCore.QDate(date)
        self.control.setDateTextFormat(qdt, textformat)

    def apply_unselected_style_to_all(self):
        """ Make all the selected dates appear unselected.
        """
        for date in self._selected:
            self.apply_unselected_style(date)

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


#------------------------------------------------------------------------
# Helper functions for styling
#------------------------------------------------------------------------


def _apply_cellformat(cf, textformat):
    """ Applies the formatting in the cellformat cf to the QTextCharFormat
    object provided.
    """
    if cf.italics is not None:
        textformat.setFontItalic(cf.italics)

    if cf.underline is not None:
        textformat.setFontUnderline(cf.underline)

    if cf.bold is not None:
        if cf.bold:
            weight = QtGui.QFont.Bold
        else:
            weight = QtGui.QFont.Normal
        textformat.setFontWeight(weight)

    if cf.bgcolor is not None:
        textformat.setBackground(_color_to_brush(cf.bgcolor))

    if cf.fgcolor is not None:
        textformat.setForeground(_color_to_brush(cf.fgcolor))


def _textformat_to_cellformat(textformat):
    """ Convert QTextCharFormat to a CellFormat """
    bg_brush = textformat.background()
    fg_brush = textformat.foreground()
    return CellFormat(
        italics=textformat.fontItalic(),
        underline=textformat.fontUnderline(),
        bold=textformat.fontWeight() == QtGui.QFont.Bold,
        bgcolor=_brush_to_color(bg_brush),
        fgcolor=_brush_to_color(fg_brush),
    )


def _color_to_brush(color):
    """ Returns a QBrush with the color specified in **color** """
    brush = QtGui.QBrush()
    if isinstance(color, six.string_types) and hasattr(QtCore.Qt, color):
        col = getattr(QtCore.Qt, color)
    elif isinstance(color, tuple):
        col = QtGui.QColor()
        col.setRgb(*color[:4])
    else:
        raise RuntimeError("Invalid color specification '%r'" % color)

    brush.setColor(col)
    return brush


def _brush_to_color(brush):
    if brush.style() == 0:   # Qt.BrushStyle.NoBrush
        return None

    color = brush.color()
    return (
        color.red(), color.green(), color.blue(), color.alpha()
    )

