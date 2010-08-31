#------------------------------------------------------------------------------
# Copyright (c) 2007, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD license.
# However, when used with the GPL version of PyQt the additional terms described in the PyQt GPL exception also apply

#
# Author: Riverbank Computing Limited
# Description: <Enthought pyface package component>
#------------------------------------------------------------------------------


# Standard library imports.
import logging

# Major package imports.
from PyQt4 import QtCore, QtGui

# Enthought library imports.
from enthought.traits.api import Bool, HasTraits, implements, Unicode
from enthought.util.guisupport import start_event_loop_qt4

# Local imports.
from enthought.pyface.i_gui import IGUI, MGUI


# Logging.
logger = logging.getLogger(__name__)


class GUI(MGUI, HasTraits):
    """ The toolkit specific implementation of a GUI.  See the IGUI interface
    for the API documentation.
    """

    implements(IGUI)

    #### 'GUI' interface ######################################################

    busy = Bool(False)

    started = Bool(False)

    state_location = Unicode

    ###########################################################################
    # 'object' interface.
    ###########################################################################

    def __init__(self, splash_screen=None):
        # Display the (optional) splash screen.
        self._splash_screen = splash_screen

        if self._splash_screen is not None:
            self._splash_screen.open()

    ###########################################################################
    # 'GUI' class interface.
    ###########################################################################

    def invoke_after(cls, millisecs, callable, *args, **kw):
        _FutureCall(millisecs, callable, *args, **kw)

    invoke_after = classmethod(invoke_after)

    def invoke_later(cls, callable, *args, **kw):
        _FutureCall(0, callable, *args, **kw)

    invoke_later = classmethod(invoke_later)

    def set_trait_after(cls, millisecs, obj, trait_name, new):
        _FutureCall(millisecs, setattr, obj, trait_name, new)

    set_trait_after = classmethod(set_trait_after)

    def set_trait_later(cls, obj, trait_name, new):
        _FutureCall(0, setattr, obj, trait_name, new)

    set_trait_later = classmethod(set_trait_later)

    def process_events(allow_user_events=True):
        if allow_user_events:
            events = QtCore.QEventLoop.AllEvents
        else:
            events = QtCore.QEventLoop.ExcludeUserInputEvents

        QtCore.QCoreApplication.processEvents(events)

    process_events = staticmethod(process_events)

    def set_busy(busy=True):
        if busy:
            QtGui.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        else:
            QtGui.QApplication.restoreOverrideCursor()

    set_busy = staticmethod(set_busy)

    ###########################################################################
    # 'GUI' interface.
    ###########################################################################

    def start_event_loop(self):
        # Make sure that SIGINTs actually stop the application event loop (Qt
        # sometimes swallows KeyboardInterrupt exceptions):
        import signal
        signal.signal(signal.SIGINT, signal.SIG_DFL)

        if self._splash_screen is not None:
            self._splash_screen.close()

        # Make sure that we only set the 'started' trait after the main loop
        # has really started.
        self.set_trait_later(self, "started", True)

        logger.debug("---------- starting GUI event loop ----------")
        start_event_loop_qt4()

        self.started = False

    def stop_event_loop(self):
        logger.debug("---------- stopping GUI event loop ----------")
        QtGui.QApplication.quit()

    ###########################################################################
    # Trait handlers.
    ###########################################################################

    def _state_location_default(self):
        """ The default state location handler. """

        return self._default_state_location()

    def _busy_changed(self, new):
        """ The busy trait change handler. """

        if new:
            QtGui.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        else:
            QtGui.QApplication.restoreOverrideCursor()


class _FutureCall(QtCore.QObject):
    """ This is a helper class that is similar to the wx FutureCall class. """

    # Keep a list of references so that they don't get garbage collected.
    _calls = []

    # Manage access to the list of instances.
    _calls_mutex = QtCore.QMutex()

    # A new Qt event type for _FutureCalls
    _pyface_event = QtCore.QEvent.Type(QtCore.QEvent.registerEventType())

    def __init__(self, ms, callable, *args, **kw):
        QtCore.QObject.__init__(self)

        # Save the arguments.
        self._ms = ms
        self._callable = callable
        self._args = args
        self._kw = kw

        # Save the instance.
        self._calls_mutex.lock()
        self._calls.append(self)
        self._calls_mutex.unlock()

        # Move to the main GUI thread.
        self.moveToThread(QtGui.QApplication.instance().thread())
        
        # Post an event to be dispatched on the main GUI thread. Note that 
        # we do not call QTimer.singleShot here, which would be simpler, because
        # that only works on QThreads. We want regular Python threads to work.
        event = QtCore.QEvent(self._pyface_event)
        QtGui.QApplication.postEvent(self, event)
        QtGui.QApplication.sendPostedEvents()

    def event(self, event):
        """ QObject event handler.
        """
        if event.type() == self._pyface_event:
            # Invoke the callable
            if self._ms:
                QtCore.QTimer.singleShot(self._ms, self._dispatch)
            else:
                self._callable(*self._args, **self._kw)

                # We cannot remove from self._calls here. QObjects don't like
                # being garbage collected during event handlers.
                QtCore.QTimer.singleShot(0, self._finished)

            return True
        else:
            return QtCore.QObject.event(self, event)

    def _dispatch(self):
        """ Invoke the callable.
        """
        self._callable(*self._args, **self._kw)
        self._finished()

    def _finished(self):
        """ Remove the call from the list, so it can be garbage collected.
        """
        self._calls_mutex.lock()
        del self._calls[self._calls.index(self)]
        self._calls_mutex.unlock()

#### EOF ######################################################################
