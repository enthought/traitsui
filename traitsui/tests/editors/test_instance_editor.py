import unittest

from traits.api import HasTraits, Instance, Str
from traitsui.api import InstanceEditor
from traitsui.item import Item
from traitsui.view import View
from traitsui.tests._tools import (
    press_ok_button,
    requires_toolkit,
    ToolkitName,
)

from traitsui.testing.tester import command, locator, query
from traitsui.testing.tester.ui_tester import UITester


class EditedInstance(HasTraits):
    value = Str()
    traits_view = View(Item("value"), buttons=["OK"])


class NonmodalInstanceEditor(HasTraits):
    inst = Instance(EditedInstance, ())


def get_view(style):
    return View(Item("inst", style=style), buttons=["OK"])


@requires_toolkit([ToolkitName.qt, ToolkitName.wx])
class TestInstanceEditor(unittest.TestCase):

    def test_simple_editor(self):
        obj = NonmodalInstanceEditor()
        tester = UITester()
        with tester.create_ui(obj, dict(view=get_view("simple"))) as ui:
            instance = tester.find_by_name(ui, "inst")
            instance.perform(command.MouseClick())
            value_txt = instance.find_by_name("value")
            value_txt.perform(command.KeySequence("abc"))
            self.assertEqual(obj.inst.value, "abc")

    def test_custom_editor(self):
        obj = NonmodalInstanceEditor()
        tester = UITester()
        with tester.create_ui(obj, dict(view=get_view("custom"))) as ui:
            value_txt = tester.find_by_name(ui, "inst").find_by_name("value")
            value_txt.perform(command.KeySequence("abc"))
            self.assertEqual(obj.inst.value, "abc")

    def test_custom_editor_resynch_editor(self):
        edited_inst = EditedInstance(value='hello')
        obj = NonmodalInstanceEditor(inst=edited_inst)
        tester = UITester()
        with tester.create_ui(obj, dict(view=get_view("custom"))) as ui:
            value_txt = tester.find_by_name(ui, "inst").find_by_name("value")
            displayed = value_txt.inspect(query.DisplayedText())
            self.assertEqual(displayed, "hello")
            edited_inst.value = "bye"
            displayed = value_txt.inspect(query.DisplayedText())
            self.assertEqual(displayed, "bye")

    def test_simple_editor_resynch_editor(self):
        edited_inst = EditedInstance(value='hello')
        obj = NonmodalInstanceEditor(inst=edited_inst)
        tester = UITester()
        with tester.create_ui(obj, dict(view=get_view("simple"))) as ui:
            instance = tester.find_by_name(ui, "inst")
            instance.perform(command.MouseClick())

            value_txt = tester.find_by_name(ui, "inst").find_by_name("value")
            displayed = value_txt.inspect(query.DisplayedText())
            self.assertEqual(displayed, "hello")
            edited_inst.value = "bye"
            displayed = value_txt.inspect(query.DisplayedText())
            self.assertEqual(displayed, "bye")

    def test_simple_editor_parent_closed(self):
        obj = NonmodalInstanceEditor()
        tester = UITester()
        with tester.create_ui(obj, dict(view=get_view('simple'))) as ui:
            instance = tester.find_by_name(ui, "inst")
            instance.perform(command.MouseClick())
