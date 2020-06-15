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

from functools import partial
import time
import types
import unittest

from pyface.gui import GUI
from pyface.window import Window
from traitsui.tests._tools import (
    is_current_backend_qt4,
    is_current_backend_wx,
    process_events,
)


def resize_window(control, length):
    """ Post a resize event for the given window control.

    Parameters
    ----------
    control : any
        Toolkit-specific control, e.g. QWindow for Qt
    length : int
        New size event. Used for both width and height.
    """

    if is_current_backend_qt4():

        from pyface.qt import QtCore, QtGui
        old_size = QtCore.QSize(length, length + 1)
        size = QtCore.QSize(length, length)
        event = QtGui.QResizeEvent(size, old_size)
        QtCore.QCoreApplication.postEvent(
            control, event
        )

    elif is_current_backend_wx():

        import wx
        size = wx.Size(length, length)
        event = wx.SizeEvent(size)
        wx.PostEvent(control, event)

    else:
        raise unittest.SkipTest("Not implemented.")


def get_width(event):
    """ Get the width for a given resize event.

    Parameters
    ----------
    event : any
        Toolkit-specific event object, e.g. QResizeEvent for Qt

    Returns
    -------
    width : int
    """
    if is_current_backend_qt4():
        return event.size().width()
    else:
        return event.GetSize().GetWidth()
    raise unittest.SkipTest("Not implemented")


def new_on_resize(event, window, max_length, sleep):
    """ New method for overriding handlers for resize events so that
    we can record the last size seen. The event is then considered handled and
    the window is not actually resized.

    This method if the current event size length is less than the given
    maximum length, this method will emit another resize event.
    This imitates a cascade of events being posted to the event queue.

    Used for patching objects in tests.

    Parameters
    ----------
    event : any
        Toolkit-specific event object.
    window : pyface.window.Window
        The window to be resized.
    max_length : int
        Maximum length of the resize event.
    sleep : float
        Call time.sleep for the given amount of second.
    """
    length = get_width(event)
    window._size = (length, length)
    time.sleep(sleep)
    if length < max_length:
        resize_window(window.control, length + 1)


def modify_resize(window, max_length, sleep):
    """ Modify / bind event handler for the resize event
    such that we get more events into the event queue from
    processing events.

    Parameters
    ----------
    window : pyface.window.Window
        The window to be resized.
    max_length : int
        Maximum length of the resize event.
    sleep : float
        Call time.sleep for the given amount of second.
    """

    if is_current_backend_qt4():
        window.control.resizeEvent =  partial(
            new_on_resize, window=window, max_length=max_length,
            sleep=sleep,
        )

    elif is_current_backend_wx():
        import wx
        window.control.Bind(
            wx.EVT_SIZE,
            partial(
                new_on_resize, window=window, max_length=max_length,
                sleep=sleep,
            ),
        )

    else:
        raise unittest.SkipTest("Not implemented.")


class TestProcessEventsRepeated(unittest.TestCase):
    """ Test process_events actually processes all events, including the events
    posted by the processed events.
    """

    def get_window(self):
        window = Window()
        window.open()

        def cleanup():
            window.close()
            window.destroy()
            GUI.process_events()

        self.addCleanup(cleanup)
        return window

    def test_process_events_process_all(self):
        window = self.get_window()

        modify_resize(window, max_length=200, sleep=0)

        resize_window(window.control, 1)

        process_events()

        self.assertEqual(window._size, (200, 200))
