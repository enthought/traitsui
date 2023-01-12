# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Module containing GUI event processing utility for testing purposes.
"""

from traits.etsconfig.api import ETSConfig


def process_cascade_events():
    """Process all posted events, and attempt to process new events posted by
    the processed events.

    Cautions:
    - An infinite cascade of events will cause this function to enter an
      infinite loop.
    - There still exists technical difficulties with Qt. On Qt4 + OSX,
      QEventLoop.processEvents may report false saying it had found no events
      to process even though it actually had processed some.
      Consequently the internal loop breaks too early such that there are
      still cascaded events unprocessed. Problems are also observed on
      Qt5 + Appveyor occasionally. At the very least, events that are already
      posted prior to calling this function will be processed.
      See enthought/traitsui#951
    """
    if ETSConfig.toolkit.startswith("qt"):
        from pyface.qt import QtCore

        event_loop = QtCore.QEventLoop()
        while event_loop.processEvents(QtCore.QEventLoop.ProcessEventsFlag.AllEvents):
            pass
    else:
        from pyface.api import GUI

        GUI.process_events()
