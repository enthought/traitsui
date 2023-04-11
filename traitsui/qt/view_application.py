# (C) Copyright 2008-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

# ------------------------------------------------------------------------------
# Copyright (c) 2007, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD license.
# However, when used with the GPL version of PyQt the additional terms
# described in the PyQt GPL exception also apply

#
# Author: Riverbank Computing Limited
# ------------------------------------------------------------------------------

""" Creates a PyQt specific modal dialog user interface that runs as a
complete application, using information from the specified UI object.
"""


# Standard library imports.
import os

# System library imports.
from pyface.qt import QtGui

# ETS imports.
from pyface.util.guisupport import (
    is_event_loop_running_qt4,
    start_event_loop_qt4,
)


KEEP_ALIVE_UIS = set()


def on_ui_destroyed(object, name, old, destroyed):
    """Remove the UI object from KEEP_ALIVE_UIS."""
    assert name == "destroyed"
    if destroyed:
        assert object in KEEP_ALIVE_UIS
        KEEP_ALIVE_UIS.remove(object)
        object.on_trait_change(on_ui_destroyed, "destroyed", remove=True)


# -------------------------------------------------------------------------
#  Creates a 'stand-alone' PyQt application to display a specified traits UI
#  View:
# -------------------------------------------------------------------------


def view_application(context, view, kind, handler, id, scrollable, args):
    """Creates a stand-alone PyQt application to display a specified traits UI
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
    if (kind == "panel") or ((kind is None) and (view.kind == "panel")):
        kind = "modal"

    app = QtGui.QApplication.instance()
    if app is None or not is_event_loop_running_qt4(app):
        return ViewApplication(
            context, view, kind, handler, id, scrollable, args
        ).ui.result

    ui = view.ui(
        context,
        kind=kind,
        handler=handler,
        id=id,
        scrollable=scrollable,
        args=args,
    )

    # If the UI has not been closed yet, we need to keep a reference to
    # it until it does close.
    if not ui.destroyed:
        KEEP_ALIVE_UIS.add(ui)
        ui.on_trait_change(on_ui_destroyed, "destroyed")
    return ui.result


class ViewApplication(object):
    """Modal window that contains a stand-alone application."""

    def __init__(self, context, view, kind, handler, id, scrollable, args):
        """Initializes the object."""
        self.context = context
        self.view = view
        self.kind = kind
        self.handler = handler
        self.id = id
        self.scrollable = scrollable
        self.args = args

        # this will block for modal dialogs, but not non-modals
        self.ui = self.view.ui(
            self.context,
            kind=self.kind,
            handler=self.handler,
            id=self.id,
            scrollable=self.scrollable,
            args=self.args,
        )

        # only non-modal UIs need to have an event loop started for them
        if kind not in {"modal", "livemodal"}:
            start_event_loop_qt4()
