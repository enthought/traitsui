import unittest

from pyface.toolkit import toolkit_object
from traits.api import HasTraits, Instance, Str
from traitsui.api import InstanceEditor, Item, View
from traitsui.tests._tools import (
    BaseTestMixin,
    requires_toolkit,
    ToolkitName,
)

from traitsui.testing.api import (
    DisplayedText,
    KeySequence,
    MouseClick,
    UITester
)

ModalDialogTester = toolkit_object(
    "util.modal_dialog_tester:ModalDialogTester"
)
no_modal_dialog_tester = ModalDialogTester.__name__ == "Unimplemented"


class EditedInstance(HasTraits):
    value = Str()
    traits_view = View(Item("value"), buttons=["OK"])


class ObjectWithInstance(HasTraits):
    inst = Instance(EditedInstance, ())


def get_view(style):
    return View(Item("inst", style=style), buttons=["OK"])


@requires_toolkit([ToolkitName.qt, ToolkitName.wx])
class TestInstanceEditor(BaseTestMixin, unittest.TestCase):

    def setUp(self):
        BaseTestMixin.setUp(self)

    def tearDown(self):
        BaseTestMixin.tearDown(self)

    def test_simple_editor(self):
        obj = ObjectWithInstance()
        tester = UITester()
        with tester.create_ui(obj, dict(view=get_view("simple"))) as ui:
            instance = tester.find_by_name(ui, "inst")
            instance.perform(MouseClick())
            value_txt = instance.find_by_name("value")
            value_txt.perform(KeySequence("abc"))
            self.assertEqual(obj.inst.value, "abc")

    def test_custom_editor(self):
        obj = ObjectWithInstance()
        tester = UITester()
        with tester.create_ui(obj, dict(view=get_view("custom"))) as ui:
            value_txt = tester.find_by_name(ui, "inst").find_by_name("value")
            value_txt.perform(KeySequence("abc"))
            self.assertEqual(obj.inst.value, "abc")

    def test_custom_editor_resynch_editor(self):
        edited_inst = EditedInstance(value='hello')
        obj = ObjectWithInstance(inst=edited_inst)
        tester = UITester()
        with tester.create_ui(obj, dict(view=get_view("custom"))) as ui:
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
        with tester.create_ui(obj, dict(view=get_view("simple"))) as ui:
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
        with tester.create_ui(obj, dict(view=get_view('simple'))) as ui:
            instance = tester.find_by_name(ui, "inst")
            instance.perform(MouseClick())

    @unittest.skipIf(no_modal_dialog_tester, "ModalDialogTester unavailable")
    def test_simple_editor_modal(self):
        # Test launching the instance editor with kind set to 'modal'
        obj = ObjectWithInstance()
        ui_tester = UITester()
        view = View(
            Item("inst", style="simple", editor=InstanceEditor(kind="modal"))
        )

        with ui_tester.create_ui(obj, dict(view=view)) as ui:

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
