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

from pyface.toolkit import toolkit_object
from traits.api import (
    Any,
    Bool,
    Event,
    Float,
    HasTraits,
    Int,
    List,
    Range,
    Undefined,
)
from traits.trait_base import xgetattr

from traitsui.context_value import ContextValue, CVFloat, CVInt
from traitsui.editor import Editor
from traitsui.editor_factory import EditorFactory
from traitsui.handler import default_handler
from traitsui.ui import UI
from traitsui.testing.api import KeyClick, KeySequence, Textbox, UITester
from traitsui.tests._tools import (
    BaseTestMixin,
    GuiTestAssistant,
    no_gui_test_assistant,
    requires_toolkit,
    ToolkitName,
)

ModalDialogTester = toolkit_object(
    "util.modal_dialog_tester:ModalDialogTester"
)
no_modal_dialog_tester = ModalDialogTester.__name__ == "Unimplemented"


class FakeControl(HasTraits):
    """A pure Traits object that fakes being a control.

    It can aither hold a value (mimicking a field), or have an event
    which is listened to (mimicking a button or similar control).
    """

    #: The value stored in the control.
    control_value = Any()

    #: An event which also can be fired.
    control_event = Event()

    #: The tooltip text for the control.
    tooltip = Any()


class StubEditorFactory(EditorFactory):
    """A minimal editor factory

    This simply holds state that may or may not be copied to the
    editor.  No attempt is made to handle custom/readonly/etc.
    variation.
    """

    #: Whether or not the traits are events.
    is_event = Bool()

    #: Whether or not the traits are events.
    auxiliary_value = Any(sync_value=True)

    #: Whether or not the traits are events.
    auxiliary_cv_int = CVInt

    #: Whether or not the traits are events.
    auxiliary_cv_float = CVFloat

    def _auxiliary_cv_int_default(self):
        return 0

    def _auxiliary_cv_float_default(self):
        return 0.0


class StubEditor(Editor):
    """A minimal editor implementaton for a StubEditorFactory.

    The editor creates a FakeControl instance as its control object
    and keeps values synchronized either to `control_value` or
    `control_event` (if `is_event` is True).
    """

    #: Whether or not the traits are events.
    is_event = Bool()

    #: An auxiliary value we want to synchronize.
    auxiliary_value = Any()

    #: An auxiliary list we want to synchronize.
    auxiliary_list = List()

    #: An auxiliary event we want to synchronize.
    auxiliary_event = Event()

    #: An auxiliary int we want to synchronize with a context value.
    auxiliary_cv_int = Int(sync_value="from")

    #: An auxiliary float we want to synchronize with a context value.
    auxiliary_cv_float = Float()

    def init(self, parent):
        self.control = FakeControl()
        self.is_event = self.factory.is_event
        if self.is_event:
            self.control.on_trait_change(self.update_object, "control_event")
        else:
            self.control.on_trait_change(self.update_object, "control_value")
        self.set_tooltip()

    def dispose(self):
        if self.is_event:
            self.control.on_trait_change(
                self.update_object, "control_event", remove=True
            )
        else:
            self.control.on_trait_change(
                self.update_object, "control_value", remove=True
            )
        super().dispose()

    def update_editor(self):
        if self.is_event:
            self.control.control_event = True
        else:
            self.control.control_value = self.value

    def update_object(self, new):
        if self.control is not None:
            if not self._no_update:
                self._no_update = True
                try:
                    self.value = new
                finally:
                    self._no_update = False

    def set_tooltip_text(self, control, text):
        control.tooltip = text

    def set_focus(self, parent):
        pass


class UserObject(HasTraits):
    """A simple HasTraits class with a variety of state."""

    #: The value being edited.
    user_value = Any("test")

    #: An auxiliary user value
    user_auxiliary = Any(10)

    #: A list user value
    user_list = List(["one", "two", "three"])

    #: A trait with desc metadata.
    user_desc = Any("test", desc="a trait with desc metadata")

    #: A trait with tooltip metadata.
    user_tooltip = Any("test", tooltip="a tooltip")

    #: An event user value
    user_event = Event()

    #: A state that is to be synchronized with the editor.
    invalid_state = Bool()


def create_editor(
    context=None,
    object_name="object",
    name="user_value",
    factory=None,
    is_event=False,
    description="",
):
    if context is None:
        user_object = UserObject()
        context = {"object": user_object}
    elif "." in object_name:
        context_name, xname = object_name.split(".", 1)
        context_object = context[context_name]
        user_object = xgetattr(context_object, xname)
    else:
        user_object = context[object_name]
    ui = UI(context=context, handler=default_handler())

    if factory is None:
        factory = StubEditorFactory()
    factory.is_event = is_event

    editor = StubEditor(
        parent=None,
        ui=ui,
        object_name=object_name,
        name=name,
        factory=factory,
        object=user_object,
        description=description,
    )
    return editor


@unittest.skipIf(no_gui_test_assistant, "No GuiTestAssistant")
class TestEditor(BaseTestMixin, GuiTestAssistant, unittest.TestCase):
    def setUp(self):
        BaseTestMixin.setUp(self)
        GuiTestAssistant.setUp(self)

    def tearDown(self):
        GuiTestAssistant.tearDown(self)
        BaseTestMixin.tearDown(self)

    def change_user_value(self, editor, object, name, value):
        if editor.is_event:
            control_name = "control_event"
        else:
            control_name = "control_value"

        # test the value in the control changes
        with self.assertTraitChanges(editor.control, control_name, count=1):
            self.gui.set_trait_later(object, name, value)
            self.event_loop_helper.event_loop_with_timeout(repeat=6)

    def change_control_value(self, editor, object, name, value):
        if editor.is_event:
            control_name = "control_event"
        else:
            control_name = "control_value"

        # test the value in the user object changes
        with self.assertTraitChanges(object, name, count=1):
            self.gui.set_trait_later(editor.control, control_name, value)
            self.event_loop_helper.event_loop_with_timeout(repeat=6)

    def test_lifecycle(self):
        editor = create_editor()

        self.assertEqual(editor.old_value, "test")
        self.assertEqual(editor.name, "user_value")
        self.assertEqual(editor.extended_name, "user_value")
        self.assertEqual(editor.value, "test")
        self.assertEqual(editor.str_value, "test")
        self.assertIs(editor.value_trait, editor.object.trait("user_value"))
        self.assertIs(editor.context_object, editor.ui.context["object"])

        editor.prepare(None)

        # preparation creates the control and sets the control value
        self.assertEqual(editor.value, "test")
        self.assertEqual(editor.control.control_value, "test")

        with self.assertTraitChanges(editor.ui, "modified", count=1):
            self.change_user_value(
                editor, editor.object, "user_value", "new test"
            )

        self.assertEqual(editor.value, "new test")
        self.assertEqual(editor.control.control_value, "new test")
        self.assertTrue(editor.ui.modified)

        self.change_control_value(
            editor, editor.object, "user_value", "even newer test"
        )

        self.assertEqual(editor.value, "even newer test")
        self.assertEqual(editor.object.user_value, "even newer test")

        editor.dispose()

        self.assertIsNone(editor.object)
        self.assertIsNone(editor.factory)
        self.assertIsNone(editor.control)

    def test_context_object(self):
        user_object = UserObject(user_value="other_test")
        context = {"object": UserObject(), "other_object": user_object}
        editor = create_editor(context=context, object_name="other_object")

        self.assertEqual(editor.old_value, "other_test")
        self.assertEqual(editor.name, "user_value")
        self.assertEqual(editor.extended_name, "user_value")
        self.assertIs(editor.context_object, editor.ui.context["other_object"])

        editor.prepare(None)

        # preparation creates the control and sets the control value
        self.assertEqual(editor.value, "other_test")
        self.assertEqual(editor.control.control_value, "other_test")

        self.change_user_value(editor, user_object, "user_value", "new test")

        self.assertEqual(editor.value, "new test")
        self.assertEqual(editor.control.control_value, "new test")

        self.change_control_value(
            editor, user_object, "user_value", "even newer test"
        )

        self.assertEqual(editor.value, "even newer test")
        self.assertEqual(editor.object.user_value, "even newer test")

        editor.dispose()

    def test_event_trait(self):
        editor = create_editor(name="user_event", is_event=True)
        user_object = editor.object

        self.assertEqual(editor.name, "user_event")
        self.assertEqual(editor.extended_name, "user_event")
        self.assertIs(editor.context_object, editor.ui.context["object"])

        editor.prepare(None)

        # preparation creates the control and sets the control value
        self.assertIs(editor.value, Undefined)

        self.change_user_value(editor, user_object, "user_event", True)
        self.change_control_value(editor, user_object, "user_event", True)

        editor.dispose()

    def test_chained_object(self):
        context = {
            "object": UserObject(
                user_auxiliary=UserObject(user_value="other_test")
            )
        }
        user_object = context["object"].user_auxiliary
        editor = create_editor(
            context=context, object_name="object.user_auxiliary"
        )

        self.assertEqual(editor.old_value, "other_test")
        self.assertEqual(editor.name, "user_value")
        self.assertEqual(editor.extended_name, "user_auxiliary.user_value")
        self.assertIs(editor.context_object, editor.ui.context["object"])

        editor.prepare(None)

        # preparation creates the control and sets the control value
        self.assertEqual(editor.value, "other_test")
        self.assertEqual(editor.control.control_value, "other_test")

        self.change_user_value(editor, user_object, "user_value", "new test")

        self.assertEqual(editor.value, "new test")
        self.assertEqual(editor.control.control_value, "new test")

        self.change_control_value(
            editor, user_object, "user_value", "even newer test"
        )

        self.assertEqual(editor.value, "even newer test")
        self.assertEqual(editor.object.user_value, "even newer test")

        # test changing the chained object
        new_user_object = UserObject(user_value="new object")
        with self.assertTraitChanges(editor, "object", count=1):
            self.change_user_value(
                editor, context["object"], "user_auxiliary", new_user_object
            )

        self.assertEqual(editor.value, "new object")
        self.assertIs(editor.object, new_user_object)
        self.assertEqual(editor.object.user_value, "new object")

        editor.dispose()

    def test_factory_sync_simple(self):
        factory = StubEditorFactory(auxiliary_value="test")
        editor = create_editor(factory=factory)
        editor.prepare(None)

        # preparation copies the auxiliary value from the factory
        self.assertIs(editor.auxiliary_value, "test")

        editor.dispose()

    def test_factory_sync_cv_simple(self):
        factory = StubEditorFactory()
        editor = create_editor(factory=factory)
        editor.prepare(None)

        # preparation copies the auxiliary CV int value from the factory
        self.assertIs(editor.auxiliary_cv_int, 0)

        editor.dispose()

    def test_parse_extended_name(self):
        context = {
            "object": UserObject(
                user_auxiliary=UserObject(user_value="other_test")
            ),
            "other_object": UserObject(user_value="another_test"),
        }
        editor = create_editor(context=context)
        editor.prepare(None)

        # test simple name
        object, name, getter = editor.parse_extended_name("user_value")
        value = getter()

        self.assertIs(object, context["object"])
        self.assertEqual(name, "user_value")
        self.assertEqual(value, "test")

        # test different context object name
        object, name, getter = editor.parse_extended_name(
            "other_object.user_value"
        )
        value = getter()

        self.assertIs(object, context["other_object"])
        self.assertEqual(name, "user_value")
        self.assertEqual(value, "another_test")

        # test chained name
        object, name, getter = editor.parse_extended_name(
            "object.user_auxiliary.user_value"
        )
        value = getter()

        self.assertIs(object, context["object"])
        self.assertEqual(name, "user_auxiliary.user_value")
        self.assertEqual(value, "other_test")

        editor.dispose()

    def test_tooltip_default(self):
        context = {
            "object": UserObject(),
        }
        editor = create_editor(context=context)
        editor.prepare(None)

        # test tooltip text
        try:
            self.assertIsNone(editor.control.tooltip)

            tooltip_text = editor.tooltip_text()
            self.assertIsNone(tooltip_text)

            set_tooltip_result = editor.set_tooltip()
            self.assertFalse(set_tooltip_result)
        except Exception:
            editor.dispose()
            raise

    def test_tooltip_from_description(self):
        context = {
            "object": UserObject(),
        }
        editor = create_editor(context=context, description="a tooltip")
        editor.prepare(None)

        # test tooltip text
        try:
            self.assertEqual(editor.control.tooltip, "a tooltip")

            tooltip_text = editor.tooltip_text()
            self.assertEqual(tooltip_text, "a tooltip")

            set_tooltip_result = editor.set_tooltip()
            self.assertTrue(set_tooltip_result)
        except Exception:
            editor.dispose()
            raise

    def test_tooltip_text_with_tooltip(self):
        context = {
            "object": UserObject(),
        }
        editor = create_editor(context=context, name='user_tooltip')
        editor.prepare(None)

        # test tooltip text
        try:
            self.assertEqual(editor.control.tooltip, "a tooltip")

            tooltip_text = editor.tooltip_text()
            self.assertEqual(tooltip_text, "a tooltip")

            set_tooltip_result = editor.set_tooltip()
            self.assertTrue(set_tooltip_result)
        except Exception:
            editor.dispose()
            raise

    def test_tooltip_text_with_desc(self):
        context = {
            "object": UserObject(),
        }
        editor = create_editor(context=context, name='user_desc')
        editor.prepare(None)

        # test tooltip text
        try:
            self.assertEqual(
                editor.control.tooltip,
                "Specifies a trait with desc metadata",
            )

            tooltip_text = editor.tooltip_text()
            self.assertEqual(
                tooltip_text,
                "Specifies a trait with desc metadata",
            )

            set_tooltip_result = editor.set_tooltip()
            self.assertTrue(set_tooltip_result)
        except Exception:
            editor.dispose()
            raise

    def test_tooltip_other_control(self):
        context = {
            "object": UserObject(),
        }
        editor = create_editor(context=context, description="a tooltip")
        editor.prepare(None)

        # test tooltip text
        try:
            other_control = FakeControl()
            set_tooltip_result = editor.set_tooltip(other_control)

            self.assertTrue(set_tooltip_result)
            self.assertEqual(other_control.tooltip, "a tooltip")
        except Exception:
            editor.dispose()
            raise

    # Test synchronizing built-in trait values between factory
    # and editor.

    def test_factory_sync_invalid_state(self):
        # Test when object's trait that sets the invalid state changes,
        # the invalid state on the editor changes
        factory = StubEditorFactory(invalid="invalid_state")
        user_object = UserObject(invalid_state=False)
        context = {
            "object": user_object,
        }
        editor = create_editor(context=context, factory=factory)
        editor.prepare(None)
        self.addCleanup(editor.dispose)

        with self.assertTraitChanges(editor, "invalid", count=1):
            user_object.invalid_state = True

        self.assertTrue(editor.invalid)

        with self.assertTraitChanges(editor, "invalid", count=1):
            user_object.invalid_state = False

        self.assertFalse(editor.invalid)

    # Testing sync_value "from" ---------------------------------------------

    def test_sync_value_from(self):
        editor = create_editor()
        user_object = editor.object
        editor.prepare(None)

        with self.assertTraitChanges(editor, "auxiliary_value", count=1):
            editor.sync_value(
                "object.user_auxiliary", "auxiliary_value", "from"
            )

        self.assertEqual(editor.auxiliary_value, 10)

        with self.assertTraitChanges(editor, "auxiliary_value", count=1):
            user_object.user_auxiliary = 11

        self.assertEqual(editor.auxiliary_value, 11)

        editor.dispose()

        with self.assertTraitDoesNotChange(editor, "auxiliary_value"):
            user_object.user_auxiliary = 12

    def test_sync_value_from_object(self):
        editor = create_editor()
        user_object = editor.object
        editor.prepare(None)

        with self.assertTraitChanges(editor, "auxiliary_value", count=1):
            editor.sync_value("user_auxiliary", "auxiliary_value", "from")

        self.assertEqual(editor.auxiliary_value, 10)

        with self.assertTraitChanges(editor, "auxiliary_value", count=1):
            user_object.user_auxiliary = 11

        self.assertEqual(editor.auxiliary_value, 11)

        editor.dispose()

        with self.assertTraitDoesNotChange(editor, "auxiliary_value"):
            user_object.user_auxiliary = 12

    def test_sync_value_from_context(self):
        # set up the editor
        user_object = UserObject()
        other_object = UserObject(user_auxiliary=20)
        context = {"object": user_object, "other_object": other_object}
        editor = create_editor(context=context)
        editor.prepare(None)

        with self.assertTraitChanges(editor, "auxiliary_value", count=1):
            editor.sync_value(
                "other_object.user_auxiliary", "auxiliary_value", "from"
            )

        self.assertEqual(editor.auxiliary_value, 20)

        with self.assertTraitChanges(editor, "auxiliary_value", count=1):
            other_object.user_auxiliary = 11

        self.assertEqual(editor.auxiliary_value, 11)

        editor.dispose()

        with self.assertTraitDoesNotChange(editor, "auxiliary_value"):
            other_object.user_auxiliary = 12

    def test_sync_value_from_chained(self):
        # set up the editor
        user_object = UserObject(user_auxiliary=UserObject(user_value=20))
        context = {"object": user_object}
        editor = create_editor(context=context)
        editor.prepare(None)

        with self.assertTraitChanges(editor, "auxiliary_value", count=1):
            editor.sync_value(
                "object.user_auxiliary.user_value", "auxiliary_value", "from"
            )

        self.assertEqual(editor.auxiliary_value, 20)

        with self.assertTraitChanges(editor, "auxiliary_value", count=1):
            user_object.user_auxiliary.user_value = 11

        self.assertEqual(editor.auxiliary_value, 11)

        with self.assertTraitChanges(editor, "auxiliary_value", count=1):
            user_object.user_auxiliary = UserObject(user_value=12)

        self.assertEqual(editor.auxiliary_value, 12)

        editor.dispose()

        with self.assertTraitDoesNotChange(editor, "auxiliary_value"):
            user_object.user_auxiliary.user_value = 13

    def test_sync_value_from_list(self):
        editor = create_editor()
        user_object = editor.object
        editor.prepare(None)

        with self.assertTraitChanges(editor, "auxiliary_list", count=1):
            editor.sync_value(
                "object.user_list", "auxiliary_list", "from", is_list=True
            )

        self.assertEqual(editor.auxiliary_list, ["one", "two", "three"])

        with self.assertTraitChanges(editor, "auxiliary_list", count=1):
            user_object.user_list = ["one", "two"]

        self.assertEqual(editor.auxiliary_list, ["one", "two"])

        with self.assertTraitChanges(editor, "auxiliary_list_items", count=1):
            user_object.user_list[1:] = ["four", "five"]

        self.assertEqual(editor.auxiliary_list, ["one", "four", "five"])

        editor.dispose()

        with self.assertTraitDoesNotChange(editor, "auxiliary_list"):
            user_object.user_list = ["one", "two", "three"]

    def test_sync_value_from_event(self):
        editor = create_editor()
        user_object = editor.object
        editor.prepare(None)

        with self.assertTraitDoesNotChange(editor, "auxiliary_event"):
            editor.sync_value(
                "object.user_event", "auxiliary_event", "from", is_event=True
            )

        with self.assertTraitChanges(editor, "auxiliary_event", count=1):
            user_object.user_event = True

        editor.dispose()

        with self.assertTraitDoesNotChange(editor, "auxiliary_event"):
            user_object.user_event = True

    def test_sync_value_from_cv(self):
        factory = StubEditorFactory(
            auxiliary_cv_int=ContextValue("object.user_auxiliary")
        )
        editor = create_editor(factory=factory)
        user_object = editor.object

        with self.assertTraitChanges(editor, "auxiliary_cv_int", count=1):
            editor.prepare(None)

        self.assertEqual(editor.auxiliary_cv_int, 10)

        with self.assertTraitChanges(editor, "auxiliary_cv_int", count=1):
            user_object.user_auxiliary = 11

        self.assertEqual(editor.auxiliary_cv_int, 11)

        editor.dispose()

        with self.assertTraitDoesNotChange(editor, "auxiliary_cv_int"):
            user_object.user_auxiliary = 12

    # Testing sync_value "to" -----------------------------------------------

    def test_sync_value_to(self):
        editor = create_editor()
        user_object = editor.object
        editor.prepare(None)
        editor.auxiliary_value = 20

        with self.assertTraitChanges(user_object, "user_auxiliary", count=1):
            editor.sync_value("object.user_auxiliary", "auxiliary_value", "to")

        self.assertEqual(user_object.user_auxiliary, 20)

        with self.assertTraitChanges(user_object, "user_auxiliary", count=1):
            editor.auxiliary_value = 11

        self.assertEqual(user_object.user_auxiliary, 11)

        editor.dispose()

        with self.assertTraitDoesNotChange(user_object, "user_auxiliary"):
            editor.auxiliary_value = 12

    def test_sync_value_to_object(self):
        editor = create_editor()
        user_object = editor.object
        editor.prepare(None)
        editor.auxiliary_value = 20

        with self.assertTraitChanges(user_object, "user_auxiliary", count=1):
            editor.sync_value("user_auxiliary", "auxiliary_value", "to")

        self.assertEqual(user_object.user_auxiliary, 20)

        with self.assertTraitChanges(user_object, "user_auxiliary", count=1):
            editor.auxiliary_value = 11

        self.assertEqual(user_object.user_auxiliary, 11)

        editor.dispose()

        with self.assertTraitDoesNotChange(user_object, "user_auxiliary"):
            editor.auxiliary_value = 12

    def test_sync_value_to_context(self):
        # set up the editor
        user_object = UserObject()
        other_object = UserObject()
        context = {"object": user_object, "other_object": other_object}
        editor = create_editor(context=context)
        editor.prepare(None)
        editor.auxiliary_value = 20

        with self.assertTraitChanges(other_object, "user_auxiliary", count=1):
            editor.sync_value(
                "other_object.user_auxiliary", "auxiliary_value", "to"
            )

        self.assertEqual(other_object.user_auxiliary, 20)

        with self.assertTraitChanges(other_object, "user_auxiliary", count=1):
            editor.auxiliary_value = 11

        self.assertEqual(other_object.user_auxiliary, 11)

        editor.dispose()

        with self.assertTraitDoesNotChange(other_object, "user_auxiliary"):
            editor.auxiliary_value = 12

    def test_sync_value_to_chained(self):
        user_object = UserObject(user_auxiliary=UserObject())
        context = {"object": user_object}
        editor = create_editor(context=context)
        editor.prepare(None)
        editor.auxiliary_value = 20

        with self.assertTraitChanges(
            user_object.user_auxiliary, "user_value", count=1
        ):
            editor.sync_value(
                "object.user_auxiliary.user_value", "auxiliary_value", "to"
            )

        self.assertEqual(user_object.user_auxiliary.user_value, 20)

        with self.assertTraitChanges(
            user_object.user_auxiliary, "user_value", count=1
        ):
            editor.auxiliary_value = 11

        self.assertEqual(user_object.user_auxiliary.user_value, 11)

        editor.dispose()

        with self.assertTraitDoesNotChange(
            user_object.user_auxiliary, "user_value"
        ):
            editor.auxiliary_value = 12

    def test_sync_value_to_list(self):
        editor = create_editor()
        user_object = editor.object
        editor.prepare(None)

        with self.assertTraitChanges(user_object, "user_list", count=1):
            editor.sync_value(
                "object.user_list", "auxiliary_list", "to", is_list=True
            )

        self.assertEqual(user_object.user_list, [])

        with self.assertTraitChanges(user_object, "user_list", count=1):
            editor.auxiliary_list = ["one", "two"]

        self.assertEqual(user_object.user_list, ["one", "two"])

        with self.assertTraitChanges(user_object, "user_list_items", count=1):
            editor.auxiliary_list[1:] = ["four", "five"]

        self.assertEqual(user_object.user_list, ["one", "four", "five"])

        editor.dispose()

        with self.assertTraitDoesNotChange(user_object, "user_list"):
            editor.auxiliary_list = ["one", "two", "three"]

    def test_sync_value_to_event(self):
        editor = create_editor()
        user_object = editor.object
        editor.prepare(None)

        with self.assertTraitDoesNotChange(user_object, "user_event"):
            editor.sync_value(
                "object.user_event", "auxiliary_event", "to", is_event=True
            )

        with self.assertTraitChanges(user_object, "user_event", count=1):
            editor.auxiliary_event = True

        editor.dispose()

        with self.assertTraitDoesNotChange(user_object, "user_event"):
            editor.auxiliary_event = True

    def test_sync_value_to_cv(self):
        factory = StubEditorFactory(
            auxiliary_cv_float=ContextValue("object.user_auxiliary")
        )
        editor = create_editor(factory=factory)
        user_object = editor.object
        editor.auxiliary_cv_float = 20.0

        with self.assertTraitChanges(user_object, "user_auxiliary", count=1):
            editor.prepare(None)

        self.assertEqual(user_object.user_auxiliary, 20)

        with self.assertTraitChanges(user_object, "user_auxiliary", count=1):
            editor.auxiliary_cv_float = 11.0

        self.assertEqual(user_object.user_auxiliary, 11)

        editor.dispose()

        with self.assertTraitDoesNotChange(user_object, "user_auxiliary"):
            editor.auxiliary_cv_float = 12.0

    # Testing sync_value "both" -----------------------------------------------

    def test_sync_value_both(self):
        editor = create_editor()
        user_object = editor.object
        editor.prepare(None)

        with self.assertTraitChanges(editor, "auxiliary_value", count=1):
            editor.sync_value(
                "object.user_auxiliary", "auxiliary_value", "both"
            )

        self.assertEqual(editor.auxiliary_value, 10)

        with self.assertTraitChanges(editor, "auxiliary_value", count=1):
            user_object.user_auxiliary = 11

        self.assertEqual(editor.auxiliary_value, 11)

        with self.assertTraitChanges(user_object, "user_auxiliary", count=1):
            editor.auxiliary_value = 12

        self.assertEqual(user_object.user_auxiliary, 12)

        editor.dispose()

        with self.assertTraitDoesNotChange(editor, "auxiliary_value"):
            user_object.user_auxiliary = 13

        with self.assertTraitDoesNotChange(user_object, "user_auxiliary"):
            editor.auxiliary_value = 14

    # regression test for enthought/traitsui#1543
    @requires_toolkit([ToolkitName.qt])
    @unittest.skipIf(no_modal_dialog_tester, "ModalDialogTester unavailable")
    def test_editor_error_msg(self):
        from pyface.qt import QtCore, QtGui

        class Foo(HasTraits):
            x = Range(low=0.0, high=1.0, value=0.5, exclude_low=True)

        foo = Foo()
        tester = UITester(auto_process_events=False)
        with tester.create_ui(foo) as ui:

            x_range = tester.find_by_name(ui, "x")
            x_range_textbox = x_range.locate(Textbox())

            x_range_textbox.perform(KeyClick('Backspace'))
            x_range_textbox.perform(KeySequence('0'))

            def trigger_error():
                x_range_textbox.perform(KeyClick('Enter'))

            def check_and_close(mdtester):
                try:
                    with mdtester.capture_error():
                        self.assertTrue(
                            mdtester.has_widget(
                                text="The 'x' trait of a Foo instance must be "
                                "0.0 < a floating point number <= 1.0, "
                                "but a value of 0.0 <class 'float'> was "
                                "specified.",
                                type_=QtGui.QMessageBox,
                            )
                        )
                        self.assertEqual(
                            mdtester.get_dialog_widget().textFormat(),
                            QtCore.Qt.TextFormat.PlainText,
                        )
                finally:
                    mdtester.close(accept=True)
                    self.assertTrue(mdtester.dialog_was_opened)

            mdtester = ModalDialogTester(trigger_error)
            mdtester.open_and_run(check_and_close)
            self.assertTrue(mdtester.dialog_was_opened)

    def test_get_control_widget(self):
        user_object = UserObject(user_auxiliary=UserObject())
        context = {"object": user_object}
        editor = create_editor(context=context)
        editor.prepare(None)

        control = editor.get_control_widget()
        try:
            self.assertIsNotNone(control)
        finally:
            editor.dispose()
