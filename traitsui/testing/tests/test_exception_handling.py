# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Tests for traitsui.testing._exception_handling """

import unittest

from pyface.api import GUI

from traitsui.tests._tools import (
    requires_toolkit,
    ToolkitName,
)
from traitsui.testing._exception_handling import reraise_exceptions


class TestExceptionHandling(unittest.TestCase):
    @requires_toolkit([ToolkitName.qt, ToolkitName.wx])
    def test_error_from_gui_captured_and_raise(self):
        def raise_error_1():
            raise ZeroDivisionError()

        def raise_error_2():
            raise IndexError()

        # without the context manager:
        #   - with Qt5, the test run will be aborted prematurely.
        #   - with Qt4, the traceback is printed and the test passes.
        #   - with Wx, the traceback is printed and the test passes.
        # With the context manager, the exception is always reraised.
        gui = GUI()
        with self.assertRaises(
            RuntimeError
        ) as exception_context, self.assertLogs("traitsui") as watcher:
            with reraise_exceptions():
                gui.invoke_later(raise_error_1)
                gui.invoke_later(raise_error_2)
                gui.invoke_after(100, gui.stop_event_loop)
                gui.start_event_loop()

        error_msg = str(exception_context.exception)
        self.assertIn("ZeroDivisionError", error_msg)
        self.assertIn("IndexError", error_msg)
        log_content1, log_content2 = watcher.output
        self.assertIn("ZeroDivisionError", log_content1)
        self.assertIn("IndexError", log_content2)
