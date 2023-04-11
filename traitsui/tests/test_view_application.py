# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import unittest

from pyface.timer.api import CallbackTimer
from traits.api import HasTraits, Instance, Int
from traitsui.api import Handler, Item, UIInfo, View, toolkit

from traitsui.tests._tools import (
    BaseTestMixin,
    GuiTestAssistant,
    is_qt,
    no_gui_test_assistant,
)


class SimpleModel(HasTraits):
    cell = Int()


class ClosableHandler(Handler):

    info = Instance(UIInfo)

    def init(self, info):
        self.info = info
        return True

    def test_close(self):
        self.info.ui.dispose()


simple_view = View(
    Item("cell"), title="Enter IDs and conditions", buttons=["OK", "Cancel"]
)


@unittest.skipIf(no_gui_test_assistant, "No GuiTestAssistant")
class TestViewApplication(BaseTestMixin, GuiTestAssistant, unittest.TestCase):
    def setUp(self):
        BaseTestMixin.setUp(self)
        GuiTestAssistant.setUp(self)
        self.model = SimpleModel()
        self.handler = ClosableHandler()
        self.event_loop_timeout = False
        self.closed = False

        if is_qt():
            if len(self.qt_app.topLevelWidgets()) > 0:
                with self.event_loop_with_timeout(repeat=5):
                    self.gui.invoke_later(self.qt_app.closeAllWindows)

    def tearDown(self):
        GuiTestAssistant.tearDown(self)
        BaseTestMixin.tearDown(self)

    def view_application(self, kind, button=None):
        if button is None:
            self.gui.invoke_later(self.close_dialog)
        else:
            self.gui.invoke_later(self.click_button, text=button)

        timer = CallbackTimer.single_shot(
            callback=self.stop_event_loop, interval=1.0
        )
        try:
            self.result = toolkit().view_application(
                context=self.model,
                view=simple_view,
                kind=kind,
                handler=self.handler,
            )
        finally:
            timer.stop()

    def view_application_event_loop(self, kind):
        with self.event_loop_until_condition(lambda: self.closed):
            self.gui.invoke_later(
                toolkit().view_application,
                context=self.model,
                view=simple_view,
                kind=kind,
                handler=self.handler,
            )
            self.gui.invoke_after(100, self.close_dialog)

    def close_dialog(self):
        if is_qt():
            self.handler.info.ui.control.close()
            self.closed = True
        else:
            raise NotImplementedError("Can't close current backend")

    def click_button(self, text):
        if is_qt():
            from pyface.qt.QtGui import QPushButton
            from pyface.ui.qt.util.testing import find_qt_widget

            button = find_qt_widget(
                self.handler.info.ui.control,
                QPushButton,
                lambda widget: widget.text() == text,
            )
            if button is None:
                raise RuntimeError("Can't find {} button".format(text))
            button.click()
            self.closed = True
        else:
            raise NotImplementedError("Can't click current backend")

    def stop_event_loop(self):
        self.gui.stop_event_loop()
        self.event_loop_timeout = True

    def test_modal_view_application_close(self):
        self.view_application("modal")

        self.assertTrue(self.closed)
        self.assertFalse(self.event_loop_timeout)
        self.assertFalse(self.result)

    def test_nonmodal_view_application_close(self):
        self.view_application("nonmodal")

        self.assertTrue(self.closed)
        self.assertFalse(self.event_loop_timeout)
        self.assertTrue(self.result)

    def test_livemodal_view_application_close(self):
        self.view_application("livemodal")

        self.assertTrue(self.closed)
        self.assertFalse(self.event_loop_timeout)
        self.assertFalse(self.result)

    def test_live_view_application_close(self):
        self.view_application("live")

        self.assertTrue(self.closed)
        self.assertFalse(self.event_loop_timeout)
        self.assertTrue(self.result)

    def test_modal_view_application_ok(self):
        self.view_application("modal", button="OK")

        self.assertTrue(self.closed)
        self.assertFalse(self.event_loop_timeout)
        self.assertTrue(self.result)

    def test_nonmodal_view_application_ok(self):
        self.view_application("nonmodal", button="OK")

        self.assertTrue(self.closed)
        self.assertFalse(self.event_loop_timeout)
        self.assertTrue(self.result)

    def test_livemodal_view_application_ok(self):
        self.view_application("livemodal", button="OK")

        self.assertTrue(self.closed)
        self.assertFalse(self.event_loop_timeout)
        self.assertTrue(self.result)

    def test_live_view_application_ok(self):
        self.view_application("live", button="OK")

        self.assertTrue(self.closed)
        self.assertFalse(self.event_loop_timeout)
        self.assertTrue(self.result)

    def test_modal_view_application_cancel(self):
        self.view_application("modal", button="Cancel")

        self.assertTrue(self.closed)
        self.assertFalse(self.event_loop_timeout)
        self.assertFalse(self.result)

    def test_nonmodal_view_application_cancel(self):
        self.view_application("nonmodal", button="Cancel")

        self.assertTrue(self.closed)
        self.assertFalse(self.event_loop_timeout)
        self.assertFalse(self.result)

    def test_livemodal_view_application_cancel(self):
        self.view_application("livemodal", button="Cancel")

        self.assertTrue(self.closed)
        self.assertFalse(self.event_loop_timeout)
        self.assertFalse(self.result)

    def test_live_view_application_cancel(self):
        self.view_application("live", button="Cancel")

        self.assertTrue(self.closed)
        self.assertFalse(self.event_loop_timeout)
        self.assertFalse(self.result)

    def test_modal_view_application_eventloop_close(self):
        self.view_application_event_loop("modal")

        self.assertTrue(self.closed)
        self.assertFalse(self.event_loop_timeout)

    def test_nonmodal_view_application_eventloop_close(self):
        self.view_application_event_loop("nonmodal")

        self.assertTrue(self.closed)
        self.assertFalse(self.event_loop_timeout)

    def test_livemodal_view_application_eventloop_close(self):
        self.view_application_event_loop("livemodal")

        self.assertTrue(self.closed)
        self.assertFalse(self.event_loop_timeout)

    def test_live_view_application_eventloop_close(self):
        self.view_application_event_loop("live")

        self.assertTrue(self.closed)
        self.assertFalse(self.event_loop_timeout)
