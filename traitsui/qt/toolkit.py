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
# However, when used with the GPL version of PyQt the additional terms described
# in the PyQt GPL exception also apply.
#
# Author: Riverbank Computing Limited
# ------------------------------------------------------------------------------

""" Defines the concrete implementations of the traits Toolkit interface for
the PyQt user interface toolkit.
"""


# Make sure that importing from this backend is OK:
from traitsui.toolkit import assert_toolkit_import

assert_toolkit_import(["qt4", "qt"])

# Ensure that we can import Pyface backend.  This starts App as a side-effect.
from pyface.toolkit import toolkit_object as pyface_toolkit

_app = pyface_toolkit("init:_app")

from traits.trait_notifiers import set_ui_handler
from pyface.api import SystemMetrics
from pyface.qt import QtCore, QtGui, qt_api

from traitsui.toolkit import Toolkit


# -------------------------------------------------------------------------
#  Handles UI notification handler requests that occur on a thread other than
#  the UI thread:
# -------------------------------------------------------------------------

_QT_TRAITS_EVENT = QtCore.QEvent.Type(QtCore.QEvent.registerEventType())


class _CallAfter(QtCore.QObject):
    """This class dispatches a handler so that it executes in the main GUI
    thread (similar to the wx function).
    """

    # The list of pending calls.
    _calls = []

    # The mutex around the list of pending calls.
    _calls_mutex = QtCore.QMutex()

    def __init__(self, handler, *args, **kwds):
        """Initialise the call."""
        QtCore.QObject.__init__(self)

        # Save the details of the call.
        self._handler = handler
        self._args = args
        self._kwds = kwds

        # Add this to the list.
        self._calls_mutex.lock()
        self._calls.append(self)
        self._calls_mutex.unlock()

        # Move to the main GUI thread.
        self.moveToThread(QtGui.QApplication.instance().thread())

        # Post an event to be dispatched on the main GUI thread. Note that
        # we do not call QTimer.singleShot, which would be simpler, because
        # that only works on QThreads. We want regular Python threads to work.
        event = QtCore.QEvent(_QT_TRAITS_EVENT)
        QtGui.QApplication.instance().postEvent(self, event)

    def event(self, event):
        """QObject event handler."""
        if event.type() == _QT_TRAITS_EVENT:
            # Invoke the handler
            self._handler(*self._args, **self._kwds)

            # We cannot remove from self._calls here. QObjects don't like being
            # garbage collected during event handlers (there are tracebacks,
            # plus maybe a memory leak, I think).
            QtCore.QTimer.singleShot(0, self._finished)

            return True
        else:
            return QtCore.QObject.event(self, event)

    def _finished(self):
        """Remove the call from the list, so it can be garbage collected."""
        self._calls_mutex.lock()
        del self._calls[self._calls.index(self)]
        self._calls_mutex.unlock()


def ui_handler(handler, *args, **kwds):
    """Handles UI notification handler requests that occur on a thread other
    than the UI thread.
    """
    _CallAfter(handler, *args, **kwds)


# Tell the traits notification handlers to use this UI handler
set_ui_handler(ui_handler)


class _KeyEventHook(QtCore.QObject):
    """
    Event hook for handling Qt key events.
    """

    def __init__(self, handler):
        super().__init__()
        self._handler = handler

    def eventFilter(self, object, event):
        if event.type() == QtCore.QEvent.Type.KeyPress:
            return self._handler(event)
        else:
            return QtCore.QObject.eventFilter(self, object, event)


class GUIToolkit(Toolkit):
    """Implementation class for PyQt toolkit."""

    def ui_panel(self, ui, parent):
        """Creates a PyQt panel-based user interface using information
        from the specified UI object.
        """
        from . import ui_panel

        ui_panel.ui_panel(ui, parent)

    def ui_subpanel(self, ui, parent):
        """Creates a PyQt subpanel-based user interface using information
        from the specified UI object.
        """
        from . import ui_panel

        ui_panel.ui_subpanel(ui, parent)

    def ui_livemodal(self, ui, parent):
        """Creates a PyQt modal "live update" dialog user interface using
        information from the specified UI object.
        """
        from . import ui_live

        ui_live.ui_livemodal(ui, parent)

    def ui_live(self, ui, parent):
        """Creates a PyQt non-modal "live update" window user interface
        using information from the specified UI object.
        """
        from . import ui_live

        ui_live.ui_live(ui, parent)

    def ui_modal(self, ui, parent):
        """Creates a PyQt modal dialog user interface using information
        from the specified UI object.
        """
        from . import ui_modal

        ui_modal.ui_modal(ui, parent)

    def ui_nonmodal(self, ui, parent):
        """Creates a PyQt non-modal dialog user interface using
        information from the specified UI object.
        """
        from . import ui_modal

        ui_modal.ui_nonmodal(ui, parent)

    def ui_wizard(self, ui, parent):
        """Creates a PyQt wizard dialog user interface using information
        from the specified UI object.
        """
        import ui_wizard

        ui_wizard.ui_wizard(ui, parent)

    def view_application(
        self,
        context,
        view,
        kind=None,
        handler=None,
        id="",
        scrollable=None,
        args=None,
    ):
        """Creates a PyQt modal dialog user interface that
            runs as a complete application, using information from the
            specified View object.

        Parameters
        ----------
        context : object or dictionary
            A single object or a dictionary of string/object pairs, whose trait
            attributes are to be edited. If not specified, the current object is
            used.
        view : view or string
            A View object that defines a user interface for editing trait
            attribute values.
        kind : string
            The type of user interface window to create. See the
            **traitsui.view.kind_trait** trait for values and
            their meanings. If *kind* is unspecified or None, the **kind**
            attribute of the View object is used.
        handler : Handler object
            A handler object used for event handling in the dialog box. If
            None, the default handler for Traits UI is used.
        id : string
            A unique ID for persisting preferences about this user interface,
            such as size and position. If not specified, no user preferences
            are saved.
        scrollable : Boolean
            Indicates whether the dialog box should be scrollable. When set to
            True, scroll bars appear on the dialog box if it is not large enough
            to display all of the items in the view at one time.

        """
        from . import view_application

        return view_application.view_application(
            context, view, kind, handler, id, scrollable, args
        )

    def position(self, ui):
        """Positions the associated dialog window on the display."""
        view = ui.view
        window = ui.control

        # Set up the default position of the window:
        parent = window.parent()
        if parent is None:
            px = 0
            py = 0
            pdx = SystemMetrics().screen_width
            pdy = SystemMetrics().screen_height
        else:
            pos = parent.pos()
            if int(parent.windowFlags()) & QtCore.Qt.WindowType.Window == 0:
                pos = parent.mapToGlobal(pos)
            px = pos.x()
            py = pos.y()
            pdx = parent.width()
            pdy = parent.height()

        # Get the window's prefered size.
        size_hint = window.sizeHint()

        # Calculate the correct width and height for the window:
        cur_width = size_hint.width()
        cur_height = size_hint.height()
        width = view.width
        height = view.height

        if width < 0.0:
            width = cur_width
        elif width <= 1.0:
            width = int(width * SystemMetrics().screen_width)
        else:
            width = int(width)

        if height < 0.0:
            height = cur_height
        elif height <= 1.0:
            height = int(height * SystemMetrics().screen_height)
        else:
            height = int(height)

        # Calculate the correct position for the window:
        x = view.x
        y = view.y

        if x < -99999.0:
            x = px + ((pdx - width) // 2)
        elif x <= -1.0:
            x = px + pdx - width + int(x) + 1
        elif x < 0.0:
            x = px + pdx - width + int(x * pdx)
        elif x <= 1.0:
            x = px + int(x * pdx)
        else:
            x = int(x)

        if y < -99999.0:
            y = py + ((pdy - height) // 2)
        elif y <= -1.0:
            y = py + pdy - height + int(y) + 1
        elif x < 0.0:
            y = py + pdy - height + int(y * pdy)
        elif y <= 1.0:
            y = py + int(y * pdy)
        else:
            y = int(y)

        # Position and size the window as requested:
        layout = window.layout()
        if layout.sizeConstraint() == QtGui.QLayout.SizeConstraint.SetFixedSize:
            layout.setSizeConstraint(QtGui.QLayout.SizeConstraint.SetDefaultConstraint)
            window.move(max(0, x), max(0, y))
            window.setFixedSize(QtCore.QSize(width, height))
        else:
            window.setGeometry(max(0, x), max(0, y), width, height)

    def show_help(self, ui, control):
        """Shows a help window for a specified UI and control."""
        from . import ui_panel

        ui_panel.show_help(ui, control)

    def save_window(self, ui):
        """Saves user preference information associated with a UI window."""
        from . import helper

        helper.save_window(ui)

    def rebuild_ui(self, ui):
        """Rebuilds a UI after a change to the content of the UI."""
        if ui.control is not None:
            ui.recycle()
            ui.info.ui = ui
        ui.rebuild(ui, ui.parent)

    def set_title(self, ui):
        """Sets the title for the UI window."""
        ui.control.setWindowTitle(ui.title)

    def set_icon(self, ui):
        """Sets the icon for the UI window."""
        from pyface.image_resource import ImageResource

        if isinstance(ui.icon, ImageResource):
            ui.control.setWindowIcon(ui.icon.create_icon())

    def key_event_to_name(self, event):
        """Converts a keystroke event into a corresponding key name."""
        from . import key_event_to_name

        return key_event_to_name.key_event_to_name(event)

    def hook_events(self, ui, control, events=None, handler=None):
        """Hooks all specified events for all controls in a UI so that they
        can be routed to the correct event handler.
        """
        if events is None:
            # FIXME: Implement drag and drop events ala toolkit.py for wx
            return

        elif events == "keys":
            # It's unsafe to parent the event filter with the object it's
            # filtering, so we store a reference to it here to ensure that it's
            # not garbage collected prematurely.
            ui._key_event_hook = _KeyEventHook(handler=handler)
            control.installEventFilter(ui._key_event_hook)

    def skip_event(self, event):
        """Indicates that an event should continue to be processed by the
        toolkit.
        """
        event.ignore()

    def destroy_control(self, control):
        """Destroys a specified GUI toolkit control."""
        # Block signals to prevent any editors from being updated (the control
        # will not be deleted immediately).
        control.blockSignals(True)

        # This may be called from within the finished() signal handler so we
        # need to do the delete after the handler has returned.
        control.hide()
        control.deleteLater()

    def destroy_children(self, control):
        """Destroys all of the child controls of a specified GUI toolkit
        control.
        """
        for w in control.children():
            # Only destroy widgets.
            if isinstance(w, QtGui.QWidget):
                # This may be called from within the finished() signal handler
                # so we need to do the delete after the handler has returned.
                w.deleteLater()

    def image_size(self, image):
        """Returns a ( width, height ) tuple containing the size of a
        specified toolkit image.
        """
        return (image.width(), image.height())

    def constants(self):
        """Returns a dictionary of useful constants.

        Currently, the dictionary should have the following key/value pairs:

        - 'WindowColor': the standard window background color in the toolkit
          specific color format.
        """
        return {
            "WindowColor": QtGui.QApplication.palette().color(
                QtGui.QPalette.ColorRole.Window
            )
        }

    def color_trait(self, *args, **traits):
        from . import color_trait as ct

        return ct.PyQtColor(*args, **traits)

    def rgb_color_trait(self, *args, **traits):
        from . import rgb_color_trait as rgbct

        return rgbct.RGBColor(*args, **traits)

    def font_trait(self, *args, **traits):
        from . import font_trait as ft

        return ft.PyQtFont(*args, **traits)
