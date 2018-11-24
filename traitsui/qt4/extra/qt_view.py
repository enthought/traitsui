#------------------------------------------------------------------------------
# Copyright (c) 2011, Enthought, Inc.
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in enthought/LICENSE.txt and may be redistributed only
# under the conditions described in the aforementioned license.  The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
# Thanks for using Enthought open source!
#
# Author: Evan Patterson
#------------------------------------------------------------------------------

""" Defines a Traits UI View that allows for the customization of Qt-specific
    widget properties.
"""

# Standard library imports.
from __future__ import absolute_import
import logging

# System library imports.
from pyface.qt import QtGui

# Enthought library imports.
from traits.api import File, List, Str
from traitsui.view import View
from io import open

# Logger.
logger = logging.getLogger(__name__)


class QtView(View):
    """ A View that allows the specification of Qt style sheets.
    """

    # An optional string containing a Qt style sheet.
    style_sheet = Str

    # An optional file path for a Qt style sheet.
    style_sheet_path = File

    # A list of trait names that defines the order for focus switching via
    # Tab/Shift+Tab. If the view contains multiple items for a specified trait
    # name, the order is undefined.
    tab_order = List(Str)

    #-------------------------------------------------------------------------
    #  Creates a UI user interface object:
    #-------------------------------------------------------------------------

    def ui(self, context, parent=None, kind=None, view_elements=None,
           handler=None, id='', scrollable=None, args=None):
        ui = super(QtView, self).ui(context, parent, kind, view_elements,
                                    handler, id, scrollable, args)

        if self.style_sheet:
            ui.control.setStyleSheet(self.style_sheet)

        if self.style_sheet_path:
            try:
                with open(self.style_sheet_path, 'r', encoding='utf8') as f:
                    ui.control.setStyleSheet(f.read())
            except IOError:
                logger.exception("Error loading Qt style sheet")

        if len(self.tab_order) >= 2:
            previous = self._get_editor_control(ui, self.tab_order[0])
            for i in range(1, len(self.tab_order)):
                current = self._get_editor_control(ui, self.tab_order[i])
                QtGui.QWidget.setTabOrder(previous, current)
                previous = current

        return ui

    #-------------------------------------------------------------------------
    #  Private interface:
    #-------------------------------------------------------------------------

    def _get_editor_control(self, ui, name):
        control = None
        editors = ui.get_editors(name)
        if editors:
            control = editors[0].control
        else:
            logger.warning("No item for '%s' trait" % name)
        return control
