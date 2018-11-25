#
#  Copyright (c) 2017, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Author: Corran Webster
#  Date:   Aug 2017
#

from __future__ import absolute_import
from unittest import TestCase

from pyface.action.api import ActionEvent
from traits.api import HasTraits, Bool
from traitsui.api import (
    Action, CloseAction, Handler, HelpAction, RedoAction, RevertAction, UI,
    UndoAction
)


class PyfaceAction(Action):

    name = 'Test Action'

    performed = Bool

    def perform(self, event):
        self.performed = True


class TraitsUIAction(Action):

    name = 'Test Action'

    performed = Bool

    def perform(self):
        self.performed = True


class SampleHandler(Handler):

    action_performed = Bool

    info_action_performed = Bool

    click_performed = Bool

    undo_performed = Bool

    redo_performed = Bool

    revert_performed = Bool

    apply_performed = Bool

    close_performed = Bool

    help_performed = Bool

    def action_handler(self):
        self.action_performed = True

    def info_action_handler(self, info):
        self.info_action_performed = True

    def revert(self, info):
        self.revert_perfomed = True

    def apply(self, info):
        self.apply_perfomed = True

    def show_help(self, info, control=None):
        self.help_performed = True

    def _action_clicked(self):
        self.click_performed = True

    def _on_undo(self, info):
        super(SampleHandler, self)._on_undo(info)
        self.undo_performed = True

    def _on_redo(self, info):
        super(SampleHandler, self)._on_redo(info)
        self.redo_performed = True

    def _on_revert(self, info):
        super(SampleHandler, self)._on_revert(info)
        self.revert_performed = True

    def _on_close(self, info):
        super(SampleHandler, self)._on_close(info)
        self.close_performed = True


class SampleObject(HasTraits):

    object_action_performed = Bool

    action_performed = Bool

    info_action_performed = Bool

    click_performed = Bool

    def object_action_handler(self):
        self.object_action_performed = True

    def action_handler(self):
        self.action_performed = True

    def info_action_handler(self, info):
        self.info_action_performed = True

    def _action_click(self):
        self.click_performed = True


class TestHandler(TestCase):

    def test_perform_pyface_action(self):
        object = SampleObject()
        handler = SampleHandler()
        action = PyfaceAction()
        event = ActionEvent()
        ui = UI(handler=handler, context={'object': object})
        info = ui.info

        handler.perform(info, action, event)

        self.assertTrue(action.performed)

    def test_perform_traitsui_action(self):
        object = SampleObject()
        handler = SampleHandler()
        action = TraitsUIAction()
        event = ActionEvent()
        ui = UI(handler=handler, context={'object': object})
        info = ui.info

        handler.perform(info, action, event)

        self.assertTrue(action.performed)
        self.assertFalse(handler.action_performed)
        self.assertFalse(handler.info_action_performed)
        self.assertFalse(handler.click_performed)
        self.assertFalse(object.action_performed)
        self.assertFalse(object.info_action_performed)
        self.assertFalse(object.click_performed)

    def test_perform_action_handler(self):
        object = SampleObject()
        handler = SampleHandler()
        action = TraitsUIAction(name='action', action='action_handler')
        event = ActionEvent()
        ui = UI(handler=handler, context={'object': object})
        info = ui.info

        handler.perform(info, action, event)

        self.assertTrue(handler.action_performed)
        self.assertFalse(handler.info_action_performed)
        self.assertFalse(handler.click_performed)
        self.assertFalse(object.action_performed)
        self.assertFalse(object.info_action_performed)
        self.assertFalse(object.click_performed)
        self.assertFalse(action.performed)

    def test_perform_info_action_handler(self):
        object = SampleObject()
        handler = SampleHandler()
        action = TraitsUIAction(name='action', action='info_action_handler')
        event = ActionEvent()
        ui = UI(handler=handler, context={'object': object})
        info = ui.info

        handler.perform(info, action, event)

        self.assertTrue(handler.info_action_performed)
        self.assertFalse(handler.action_performed)
        self.assertFalse(handler.click_performed)
        self.assertFalse(object.action_performed)
        self.assertFalse(object.info_action_performed)
        self.assertFalse(object.click_performed)
        self.assertFalse(action.performed)

    def test_perform_click_handler(self):
        object = SampleObject()
        handler = SampleHandler()
        action = TraitsUIAction(name='action', action='')
        event = ActionEvent()
        ui = UI(handler=handler, context={'object': object})
        info = ui.info

        handler.perform(info, action, event)

        self.assertTrue(handler.click_performed)
        self.assertFalse(handler.action_performed)
        self.assertFalse(handler.info_action_performed)
        self.assertFalse(object.action_performed)
        self.assertFalse(object.info_action_performed)
        self.assertFalse(object.click_performed)
        self.assertFalse(action.performed)

    def test_perform_object_handler(self):
        object = SampleObject()
        handler = SampleHandler()
        action = TraitsUIAction(name='action', action='object_action_handler')
        event = ActionEvent()
        ui = UI(handler=handler, context={'object': object})
        info = ui.info

        handler.perform(info, action, event)

        self.assertTrue(object.object_action_performed)
        self.assertFalse(action.performed)

    def test_undo_handler(self):
        object = SampleObject()
        handler = SampleHandler()
        action = UndoAction
        event = ActionEvent()
        ui = UI(handler=handler, context={'object': object})
        info = ui.info

        handler.perform(info, action, event)

        self.assertTrue(handler.undo_performed)

    def test_redo_handler(self):
        object = SampleObject()
        handler = SampleHandler()
        action = RedoAction
        event = ActionEvent()
        ui = UI(handler=handler, context={'object': object})
        info = ui.info

        handler.perform(info, action, event)

        self.assertTrue(handler.redo_performed)

    def test_revert_handler(self):
        object = SampleObject()
        handler = SampleHandler()
        action = RevertAction
        event = ActionEvent()
        ui = UI(handler=handler, context={'object': object})
        info = ui.info

        handler.perform(info, action, event)

        self.assertTrue(handler.revert_performed)

    def test_close_handler(self):
        object = SampleObject()
        handler = SampleHandler()
        action = CloseAction
        event = ActionEvent()
        ui = UI(handler=handler, context={'object': object})
        info = ui.info

        handler.perform(info, action, event)

        self.assertTrue(handler.close_performed)

    def test_help_handler(self):
        object = SampleObject()
        handler = SampleHandler()
        action = HelpAction
        event = ActionEvent()
        ui = UI(handler=handler, context={'object': object})
        info = ui.info

        handler.perform(info, action, event)

        self.assertTrue(handler.help_performed)
