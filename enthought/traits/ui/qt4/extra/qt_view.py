#------------------------------------------------------------------------------
# Copyright (c) 2009, Enthought, Inc.
# All rights reserved.
# 
# This software is provided without warranty under the terms of the BSD
# license included in enthought/LICENSE.txt and may be redistributed only
# under the conditions described in the aforementioned license.  The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
# Thanks for using Enthought open source!
# 
# Author: Evan Patterson
# Date: 07/21/09
#------------------------------------------------------------------------------

""" Defines a Traits UI View that allows for the customization of Qt-specific
    widget properties.
"""

# ETS imports
from enthought.traits.api import Str, File
from enthought.traits.ui.view import View


class QtView(View):
    """ A View that allows the specification of Qt style sheets.
    """
    
    # An optional string containing a Qt style sheet
    style_sheet = Str

    # An optional path to a Qt style sheet
    style_sheet_path = File

    #---------------------------------------------------------------------------
    #  Creates a UI user interface object:
    #---------------------------------------------------------------------------
    
    def ui(self, context, parent=None, kind=None, view_elements=None, 
           handler=None, id='', scrollable=None, args=None):
        """ Reimplemented to set style sheets.
        """
        ui = super(QtView, self).ui(context, parent, kind, view_elements,
                                    handler, id, scrollable, args)
        
        if self.style_sheet:
            ui.control.setStyleSheet(self.style_sheet)

        if self.style_sheet_path:
            try:
                f = open(self.style_sheet_path, 'r')
                try:
                    ui.control.setStyleSheet(f.read())
                finally:
                    f.close()
            except IOError, error:
                print "Error loading Qt style sheet:", error

        return ui
