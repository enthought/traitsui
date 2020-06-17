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

        q_object = DummyQObject(max_n_events=10)
        self.addCleanup(q_object.deleteLater)

        QtCore.QCoreApplication.postEvent(
            q_object, QtCore.QEvent(QtCore.QEvent.User)
        )

        # As a demonstration, check calling processEvents does not process
        # cascade of events.
        QtCore.QCoreApplication.processEvents(QtCore.QEventLoop.AllEvents)
        self.assertEqual(q_object.n_events, 1)

        # when
        process_cascade_events()

        # then
        self.assertEqual(q_object.n_events, 10)

    @skip_if_not_wx
    def test_wx_process_events_process_all(self):
        wx_handler = DummyWxHandler(max_n_events=10)
        wx_handler.post_event()

        # when
        process_cascade_events()

        # then
        self.assertEqual(wx_handler.n_events, 10)
