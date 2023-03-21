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
from traits.api import Button, HasTraits, Instance, List, observe, Str, String
from traitsui.api import InstanceEditor, Item, View
from traitsui.tests._tools import (
    BaseTestMixin,
    requires_toolkit,
    ToolkitName,
)

from traitsui.testing.api import (
    DisplayedText,
    Index,
    IsEnabled,
    KeyClick,
    KeySequence,
    MouseClick,
    SelectedText,
    TargetByName,
    UITester,
)

ModalDialogTester = toolkit_object(
    "util.modal_dialog_tester:ModalDialogTester"
)
no_modal_dialog_tester = ModalDialogTester.__name__ == "Unimplemented"


class EditedInstance(HasTraits):
    value = Str()
    traits_view = View(Item("value"), buttons=["OK"])


class NamedInstance(HasTraits):
    name = Str()
    value = Str()
    traits_view = View(Item("name"), Item("value"), buttons=["OK"])


class ObjectWithInstance(HasTraits):
    inst = Instance(EditedInstance, args=())


class ObjectWithList(HasTraits):
    inst_list = List(Instance(NamedInstance))
    inst = Instance(NamedInstance, args=())
    reset_to_none = Button()
    change_options = Button()

    def _inst_list_default(self):
        return [
            NamedInstance(name=value, value=value)
            for value in ['one', 'two', 'three']
        ]

    @observe('reset_to_none')
    def _reset_inst_to_none(self, event):
        self.inst = None

    @observe('change_options')
    def _modify_inst_list(self, event):
        self.inst_list = [NamedInstance(name='one', value='one')]


simple_view = View(Item("inst"), buttons=["OK"])
custom_view = View(Item("inst", style='custom'), buttons=["OK"])
selection_view = View(
    Item(
        "inst",
        editor=InstanceEditor(name='inst_list'),
        style='custom',
    ),
    buttons=["OK"],
)
none_view = View(
    Item(
        "inst",
        editor=InstanceEditor(name='inst_list'),
        style='custom',
    ),
    Item('reset_to_none'),
    Item('change_options'),
    buttons=["OK"],
)
non_editable_droppable_view = View(
    Item(
        "inst",
        editor=InstanceEditor(
            editable=False,
            droppable=True,
        ),
        style='custom',
    ),
    buttons=["OK"],
)
non_editable_droppable_selectable_view = View(
    Item(
        "inst",
        editor=InstanceEditor(
            name='inst_list',
            editable=False,
            droppable=True,
        ),
        style='custom',
    ),
    buttons=["OK"],
)
modal_view = View(
    Item("inst", style="simple", editor=InstanceEditor(kind="modal"))
)


class ValidatedEditedInstance(HasTraits):
    some_string = String("A", maxlen=3)

    traits_view = View(Item('some_string'))


class ObjectWithValidatedInstance(HasTraits):
    something = Instance(ValidatedEditedInstance, args=())

    traits_view = View(
        Item('something', editor=InstanceEditor(), style='custom'),
        buttons=["OK", "Cancel"],
    )


class ObjectWithValidatedList(HasTraits):
    inst_list = List(Instance(HasTraits))
    inst = Instance(HasTraits, ())

    def _inst_list_default(self):
        return [
            ValidatedEditedInstance(some_string=value)
            for value in ['a', 'b', 'c']
        ]


@requires_toolkit([ToolkitName.qt, ToolkitName.wx])
class TestInstanceEditor(BaseTestMixin, unittest.TestCase):
    def setUp(self):
        BaseTestMixin.setUp(self)

    def tearDown(self):
        BaseTestMixin.tearDown(self)

    def test_simple_editor(self):
        obj = ObjectWithInstance()
        tester = UITester()
        with tester.create_ui(obj, {'view': simple_view}) as ui:
            instance = tester.find_by_name(ui, "inst")
            instance.perform(MouseClick())
            value_txt = instance.find_by_name("value")
            value_txt.perform(KeySequence("abc"))
            self.assertEqual(obj.inst.value, "abc")

    def test_custom_editor(self):
        obj = ObjectWithInstance()
        tester = UITester()
        with tester.create_ui(obj, {'view': custom_view}) as ui:
            value_txt = tester.find_by_name(ui, "inst").find_by_name("value")
            value_txt.perform(KeySequence("abc"))
            self.assertEqual(obj.inst.value, "abc")

    def test_custom_editor_with_selection(self):
        obj = ObjectWithList()
        tester = UITester()
        with tester.create_ui(obj, {'view': selection_view}) as ui:
            # test that the current object is None
            self.assertIsNone(obj.inst)

            # test that the displayed text is empty
            instance = tester.find_by_name(ui, "inst")
            text = instance.inspect(SelectedText())
            self.assertEqual(text, '')

            # test that changing selection works
            instance.locate(Index(1)).perform(MouseClick())
            self.assertIs(obj.inst, obj.inst_list[1])

            # test that the displayed text is correct
            text = instance.inspect(SelectedText())
            self.assertEqual(text, obj.inst_list[1].name)

            # test editing the view works
            value_txt = instance.find_by_name("value")
            value_txt.perform(KeySequence("abc"))
            self.assertEqual(obj.inst.value, "twoabc")

    def test_custom_editor_with_selection_initialized(self):
        obj = ObjectWithList()
        obj.inst = obj.inst_list[1]
        tester = UITester()
        with tester.create_ui(obj, {'view': selection_view}) as ui:
            # test that the current object is the correct one
            self.assertIs(obj.inst, obj.inst_list[1])

            # test that the displayed text is correct
            instance = tester.find_by_name(ui, "inst")
            text = instance.inspect(SelectedText())
            self.assertEqual(text, obj.inst.name)

    # A regression test for issue enthought/traitsui#1725
    def test_custom_editor_with_selection_change_option_name(self):
        obj = ObjectWithList()
        tester = UITester()
        with tester.create_ui(obj, {'view': selection_view}) as ui:
            # test that the current object is None
            self.assertIsNone(obj.inst)

            # actually select the first item
            instance = tester.find_by_name(ui, "inst")
            instance.locate(Index(0)).perform(MouseClick())
            self.assertIs(obj.inst, obj.inst_list[0])

            # test that the displayed text is correct after change
            name_txt = instance.find_by_name("name")
            for _ in range(3):
                name_txt.perform(KeyClick("Backspace"))
            name_txt.perform(KeySequence("Something New"))
            text = instance.inspect(SelectedText())
            self.assertEqual(text, "Something New")
            self.assertEqual("Something New", obj.inst_list[0].name)

    def test_custom_editor_resynch_editor(self):
        edited_inst = EditedInstance(value='hello')
        obj = ObjectWithInstance(inst=edited_inst)
        tester = UITester()
        with tester.create_ui(obj, {'view': custom_view}) as ui:
            value_txt = tester.find_by_name(ui, "inst").find_by_name("value")
            displayed = value_txt.inspect(DisplayedText())
            self.assertEqual(displayed, "hello")
            edited_inst.value = "bye"
            displayed = value_txt.inspect(DisplayedText())
            self.assertEqual(displayed, "bye")

    def test_simple_editor_resynch_editor(self):
        edited_inst = EditedInstance(value='hello')
        obj = ObjectWithInstance(inst=edited_inst)
        tester = UITester()
        with tester.create_ui(obj, {'view': simple_view}) as ui:
            instance = tester.find_by_name(ui, "inst")
            instance.perform(MouseClick())

            value_txt = instance.find_by_name("value")
            displayed = value_txt.inspect(DisplayedText())
            self.assertEqual(displayed, "hello")
            edited_inst.value = "bye"
            displayed = value_txt.inspect(DisplayedText())
            self.assertEqual(displayed, "bye")

    def test_simple_editor_parent_closed(self):
        obj = ObjectWithInstance()
        tester = UITester()
        with tester.create_ui(obj, {'view': simple_view}) as ui:
            instance = tester.find_by_name(ui, "inst")
            instance.perform(MouseClick())

    @unittest.skipIf(no_modal_dialog_tester, "ModalDialogTester unavailable")
    def test_simple_editor_modal(self):
        # Test launching the instance editor with kind set to 'modal'
        obj = ObjectWithInstance()
        ui_tester = UITester()

        with ui_tester.create_ui(obj, dict(view=modal_view)) as ui:

            def click_button():
                ui_tester.find_by_name(ui, "inst").perform(MouseClick())

            def when_opened(tester):
                with tester.capture_error():
                    try:
                        dialog_ui = tester.get_dialog_widget()._ui
                        # If auto_process_events was not set to false, this
                        # will block due to deadlocks with ModalDialogTester.
                        ui_tester = UITester(auto_process_events=False)
                        value = ui_tester.find_by_name(dialog_ui, "value")
                        value.perform(KeySequence("Hello"))
                        self.assertEqual(obj.inst.value, "")
                        ok_button = ui_tester.find_by_id(dialog_ui, "OK")
                        ok_button.perform(MouseClick())
                    finally:
                        # If the block above fails, the dialog will block
                        # forever. Close it regardless.
                        if tester.get_dialog_widget() is not None:
                            tester.close(accept=True)

            mdtester = ModalDialogTester(click_button)
            mdtester.open_and_run(when_opened=when_opened)
            self.assertTrue(mdtester.dialog_was_opened)
            self.assertEqual(obj.inst.value, "Hello")

    # A regression test for issue enthought/traitsui#1501
    def test_propagate_errors(self):
        obj = ObjectWithValidatedInstance()
        ui_tester = UITester()
        with ui_tester.create_ui(obj) as ui:
            something_ui = ui_tester.find_by_name(ui, "something")
            some_string_field = something_ui.locate(
                TargetByName('some_string')
            )
            some_string_field.perform(KeySequence("abcd"))
            some_string_field.perform(KeyClick("Enter"))

            ok_button = ui_tester.find_by_id(ui, "OK")

            instance_editor_ui = something_ui._target._ui
            instance_editor_ui_parent = something_ui._target._ui.parent
            self.assertNotEqual(instance_editor_ui, ui)
            self.assertEqual(instance_editor_ui_parent, ui)

            self.assertEqual(instance_editor_ui.errors, ui.errors)
            self.assertFalse(ok_button.inspect(IsEnabled()))

    def test_propagate_errors_switch_selection(self):
        obj = ObjectWithValidatedList()
        ui_tester = UITester()
        with ui_tester.create_ui(obj, {'view': selection_view}) as ui:
            something_ui = ui_tester.find_by_name(ui, "inst")

            something_ui.locate(Index(0)).perform(MouseClick())

            some_string_field = something_ui.locate(
                TargetByName('some_string')
            )
            some_string_field.perform(KeySequence("bcde"))
            some_string_field.perform(KeyClick("Enter"))

            ok_button = ui_tester.find_by_id(ui, "OK")

            instance_editor_ui = something_ui._target._ui
            instance_editor_ui_parent = something_ui._target._ui.parent
            self.assertNotEqual(instance_editor_ui, ui)
            self.assertEqual(instance_editor_ui_parent, ui)

            self.assertEqual(instance_editor_ui.errors, ui.errors)
            self.assertFalse(ok_button.inspect(IsEnabled()))

            # change to a different selected that is not in an error state
            something_ui.locate(Index(1)).perform(MouseClick())

            self.assertTrue(ok_button.inspect(IsEnabled()))

    # regression test for enthought/traitsui#1134
    def test_none_selected(self):
        obj = ObjectWithList()
        tester = UITester()
        with tester.create_ui(obj, {'view': none_view}) as ui:
            # test that the current object is None
            self.assertIsNone(obj.inst)

            # test that the displayed text is empty to start
            instance = tester.find_by_name(ui, "inst")
            text = instance.inspect(SelectedText())
            self.assertEqual(text, '')

            # test that changing selection works and displayed text is correct
            instance.locate(Index(1)).perform(MouseClick())
            self.assertIs(obj.inst, obj.inst_list[1])
            text = instance.inspect(SelectedText())
            self.assertEqual(text, obj.inst_list[1].name)

            # test resetting selection to None
            reset_to_none_button = tester.find_by_name(ui, "reset_to_none")
            reset_to_none_button.perform(MouseClick())
            self.assertIsNone(obj.inst)
            text = instance.inspect(SelectedText())
            self.assertEqual(text, '')

            # change selection again
            instance.locate(Index(1)).perform(MouseClick())
            self.assertIs(obj.inst, obj.inst_list[1])
            text = instance.inspect(SelectedText())
            self.assertEqual(text, obj.inst_list[1].name)

            # test modifying list of selectable options returns current object
            # to None
            change_options_button = tester.find_by_name(ui, "change_options")
            change_options_button.perform(MouseClick())
            self.assertIsNone(obj.inst)
            text = instance.inspect(SelectedText())
            self.assertEqual(text, '')

    # regression test for enthought/traitsui#1478
    def test_droppable(self):
        obj = ObjectWithInstance()
        obj_with_list = ObjectWithList()
        tester = UITester()

        with tester.create_ui(obj, {'view': non_editable_droppable_view}):
            pass

        with tester.create_ui(
            obj_with_list, {'view': non_editable_droppable_selectable_view}
        ):
            pass
