#  Copyright (c) 2008-20, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#

""" Tests for traitsui.tests._tools """

import unittest

from pyface.api import GUI

from traitsui.tests._tools import (
    is_current_backend_qt4,
    is_current_backend_wx,
    skip_if_not_qt4,
    skip_if_not_wx,
    process_cascade_events,
)


if is_current_backend_qt4():

    # Create a QObject that will emit a new event to itself as long as
    # it has not received enough.

    from pyface.qt import QtCore

    class DummyQObject(QtCore.QObject):

        def __init__(self, max_n_events):
            super().__init__()
            self.max_n_events = max_n_events
            self.n_events = 0

        def event(self, event):
            if event.type() != QtCore.QEvent.User:
                return super().event(event)

            self.n_events += 1

            if self.n_events < self.max_n_events:
                new_event = QtCore.QEvent(QtCore.QEvent.User)
                QtCore.QCoreApplication.postEvent(self, new_event)
            return True


if is_current_backend_wx():

    # Create a wx.EvtHandler that will emit a new event to itself as long as
    # it has not received enough.

    import wx
    import wx.lib.newevent

    NewEvent, EVT_SOME_NEW_EVENT = wx.lib.newevent.NewEvent()

    class DummyWxHandler(wx.EvtHandler):

        def __init__(self, max_n_events):
            super().__init__()
            self.max_n_events = max_n_events
            self.n_events = 0

        def TryBefore(self, event):
            self.n_events += 1
            if self.n_events < self.max_n_events:
                self.post_event()
            return True

        def post_event(self):
            event = NewEvent()
            wx.PostEvent(self, event)


class TestProcessEventsRepeated(unittest.TestCase):
    """ Test process_events actually processes all events, including the events
    posted by the processed events.
    """

    @skip_if_not_qt4
    def test_qt_process_events_process_all(self):
        from pyface.qt import QtCore

        def cleanup(q_object):
            q_object.deleteLater()
            # If the test fails, run process events at least the same
            # number of times as max_n_events
            for _ in range(q_object.max_n_events):
                QtCore.QCoreApplication.processEvents(
                    QtCore.QEventLoop.AllEvents
                )

        max_n_events = 10
        q_object = DummyQObject(max_n_events=max_n_events)
        self.addCleanup(cleanup, q_object)

        QtCore.QCoreApplication.postEvent(
            q_object, QtCore.QEvent(QtCore.QEvent.User)
        )

        # sanity check calling processEvents does not process
        # cascade of events.
        QtCore.QCoreApplication.processEvents(QtCore.QEventLoop.AllEvents)
        self.assertEqual(q_object.n_events, 1)

        # when
        process_cascade_events()

        # then
        actual = q_object.n_events

        # If process_cascade_events did not do what it promises, then there
        # are still pending tasks left. Run process events at least the same
        # number of times as max_n_events to verify
        for _ in range(max_n_events):
            QtCore.QCoreApplication.processEvents(QtCore.QEventLoop.AllEvents)

        n_left_behind_events = q_object.n_events - actual
        msg = (
            "Expected {max_n_events} events processed on the objects after "
            "running process_cascade_events and zero events left. "
            "Found {actual} processed with {n_left_behind_events} left "
            "behind.".format(
                max_n_events=max_n_events,
                actual=actual,
                n_left_behind_events=n_left_behind_events,
            )
        )
        self.assertEqual(n_left_behind_events, 0, msg)

        # If the previous assertion passes but this one fails, that means some
        # events have gone missing, and that would likely be a problem for the
        # test setup, not for the process_cascade_events.
        self.assertEqual(actual, max_n_events, msg)

    @skip_if_not_wx
    def test_wx_process_events_process_all(self):

        def cleanup(wx_handler):
            # In case of test failure, always flush the GUI event queue.
            GUI.process_events()
            wx_handler.Destroy()

        max_n_events = 10
        wx_handler = DummyWxHandler(max_n_events=max_n_events)
        self.addCleanup(cleanup, wx_handler)

        wx_handler.post_event()

        # when
        process_cascade_events()

        # then
        self.assertEqual(wx_handler.n_events, max_n_events)
