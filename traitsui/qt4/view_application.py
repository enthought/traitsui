#------------------------------------------------------------------------------
# Copyright (c) 2007, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD license.
# However, when used with the GPL version of PyQt the additional terms described in the PyQt GPL exception also apply

#
# Author: Riverbank Computing Limited
#------------------------------------------------------------------------------

""" Creates a PyQt specific modal dialog user interface that runs as a
complete application, using information from the specified UI object.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

# Standard library imports.
import os

# System library imports.
from pyface.qt import QtGui

# ETS imports.
from pyface.util.guisupport import is_event_loop_running_qt4, \
    start_event_loop_qt4

#-------------------------------------------------------------------------------
#  Creates a 'stand-alone' PyQt application to display a specified traits UI
#  View:
#-------------------------------------------------------------------------------

def view_application ( context, view, kind, handler, id, scrollable, args ):
    """ Creates a stand-alone PyQt application to display a specified traits UI
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
    if (kind is None) and (view.kind == 'live'):
        kind = 'livemodal'

    app = QtGui.QApplication.instance()
    if app is None or not is_event_loop_running_qt4(app):
        return ViewApplication( context, view, kind, handler, id,
                                scrollable, args ).ui.result

    return view.ui( context,
                    kind       = kind,
                    handler    = handler,
                    id         = id,
                    scrollable = scrollable,
                    args       = args ).result

#-------------------------------------------------------------------------------
#  'ViewApplication' class:
#-------------------------------------------------------------------------------

class ViewApplication ( object ):
    """ Modal window that contains a stand-alone application.
    """
    #---------------------------------------------------------------------------
    #  Initializes the object:
    #---------------------------------------------------------------------------

    def __init__ ( self, context, view, kind, handler, id, scrollable, args ):
        """ Initializes the object.
        """
        self.context    = context
        self.view       = view
        self.kind       = kind
        self.handler    = handler
        self.id         = id
        self.scrollable = scrollable
        self.args       = args

        # FIXME: fbi is wx specific at the moment.
        if os.environ.get( 'ENABLE_FBI' ) is not None:
            try:
                from etsdevtools.developer.helper.fbi import enable_fbi
                enable_fbi()
            except:
                pass

        self.ui = self.view.ui( self.context,
                                kind       = self.kind,
                                handler    = self.handler,
                                id         = self.id,
                                scrollable = self.scrollable,
                                args       = self.args )

        start_event_loop_qt4()
