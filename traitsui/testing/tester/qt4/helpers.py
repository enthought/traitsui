#  Copyright (c) 2005-2020, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#


from pyface.qt import QtCore
from pyface.qt.QtTest import QTest


def mouse_click_qwidget(wrapper, action):
    """ Performs a mouce click on a Qt widget.

    Parameters
    ----------
    wrapper : UIWrapper
        The wrapper object wrapping the Qt widget.
    interaction : instance of traitsui.testing.tester.command.MouseClick
        interaction is unused here, but it is included so that the function
        matches the expected format for a handler.  Note this handler is
        intended to be used with an interaction_class of a MouseClick.
    """
    QTest.mouseClick(
        wrapper.target,
        QtCore.Qt.LeftButton,
        delay=wrapper.delay,
    )
