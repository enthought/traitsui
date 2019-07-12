#------------------------------------------------------------------------------
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
#  Date:   11/10/2004
#
#------------------------------------------------------------------------------

""" Creates a wxPython specific modal dialog user interface that runs as a
    complete application, using information from the specified UI object.
"""

#-------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------

# Standard library imports.
from __future__ import absolute_import
import os
import sys

# System library imports.
import wx

# ETS imports.
from pyface.util.guisupport import is_event_loop_running_wx, \
    start_event_loop_wx

#-------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------

# File to redirect output to. If '', output goes to stdout.
redirect_filename = ''

KEEP_ALIVE_UIS = set()


def on_ui_destroyed(object, name, old, destroyed):
    """ Remove the UI object from KEEP_ALIVE_UIS.
    """
    assert name == 'destroyed'
    if destroyed:
        assert object in KEEP_ALIVE_UIS
        KEEP_ALIVE_UIS.remove(object)
        object.on_trait_change(on_ui_destroyed, 'destroyed', remove=True)


#-------------------------------------------------------------------------
#  Creates a 'stand-alone' wx Application to display a specified traits UI View:
#-------------------------------------------------------------------------

def view_application(context, view, kind, handler, id, scrollable, args):
    """ Creates a stand-alone wx Application to display a specified traits UI
        View.

    Parameters
    ----------
    context : object or dictionary
        A single object or a dictionary of string/object pairs, whose trait
        attributes are to be edited. If not specified, the current object is
        used.
    view : view object
        A View object that defines a user interface for editing trait attribute
        values.
    kind : string
        The type of user interface window to create. See the
        **traitsui.view.kind_trait** trait for values and
        their meanings. If *kind* is unspecified or None, the **kind**
        attribute of the View object is used.
    handler : Handler object
        A handler object used for event handling in the dialog box. If
        None, the default handler for Traits UI is used.
    scrollable : Boolean
        Indicates whether the dialog box should be scrollable. When set to
        True, scroll bars appear on the dialog box if it is not large enough
        to display all of the items in the view at one time.
    """
    if (kind == 'panel') or ((kind is None) and (view.kind == 'panel')):
        kind = 'modal'

    app = wx.GetApp()
    if app is None or not is_event_loop_running_wx(app):
        return ViewApplication(context, view, kind, handler, id,
                               scrollable, args).ui.result

    ui = view.ui(context,
                 kind=kind,
                 handler=handler,
                 id=id,
                 scrollable=scrollable,
                 args=args)

    # If the UI has not been closed yet, we need to keep a reference to
    # it until it does close.
    if not ui.destroyed:
        KEEP_ALIVE_UIS.add(ui)
        ui.on_trait_change(on_ui_destroyed, 'destroyed')
    return ui.result

#-------------------------------------------------------------------------
#  'ViewApplication' class:
#-------------------------------------------------------------------------


class ViewApplication(wx.App):
    """ Modal window that contains a stand-alone application.
    """
    #-------------------------------------------------------------------------
    #  Initializes the object:
    #-------------------------------------------------------------------------

    def __init__(self, context, view, kind, handler, id, scrollable, args):
        """ Initializes the object.
        """
        self.context = context
        self.view = view
        self.kind = kind
        self.handler = handler
        self.id = id
        self.scrollable = scrollable
        self.args = args

        if redirect_filename.strip() != '':
            super(ViewApplication, self).__init__(1, redirect_filename)
        else:
            super(ViewApplication, self).__init__(0)

        # Start the event loop in an IPython-conforming manner.
        start_event_loop_wx(self)

    #-------------------------------------------------------------------------
    #  Handles application initialization:
    #-------------------------------------------------------------------------

    def OnInit(self):
        """ Handles application initialization.
        """
        self.ui = self.view.ui(self.context,
                               kind=self.kind,
                               handler=self.handler,
                               id=self.id,
                               scrollable=self.scrollable,
                               args=self.args)
        return True
