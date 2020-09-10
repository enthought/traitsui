import unittest
import time

from traits.api import HasTraits, Instance, Str
from traitsui.item import Item
from traitsui.view import View
from traitsui.tests._tools import (
    create_ui,
    press_ok_button,
    requires_toolkit,
    reraise_exceptions,
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


    def check_editor_update_value(self, style):
        obj = NonmodalInstanceEditor()
        tester = UITester()
        with tester.create_ui(obj, dict(view=get_view(style))) as ui:
            instance = tester.find_by_name(ui, "inst")
            editor = instance.locate(locator.NestedUI())
            value_txt = editor.find_by_name("value")
            value_txt.perform(command.KeySequence("abc"))
            # the below code requires ui_base implementation to work
            #ok_button = editor.find_by_id("OK")
            #ok_button.perform(command.MouseClick())
            if style == 'simple':
                press_ok_button(editor.target)
            self.assertEqual(obj.inst.value, "abc")
    
    def test_simple_editor(self):
        return self.check_editor_update_value('simple')

    def test_custom_editor(self):
        return self.check_editor_update_value('custom')

    def check_resynch_editor(self, style):
        edited_inst = EditedInstance(value='hello')
        obj = NonmodalInstanceEditor(inst=edited_inst)
        tester= UITester()
        with tester.create_ui(obj, dict(view=get_view(style))) as ui: 
            instance = tester.find_by_name(ui, "inst")
            editor = instance.locate(locator.NestedUI())
            value_txt = editor.find_by_name("value")
            displayed = value_txt.inspect(query.DisplayedText())
            self.assertEqual(displayed, "hello")
            edited_inst.value = "bye"
            displayed = value_txt.inspect(query.DisplayedText())
            self.assertEqual(displayed, "bye")

    def test_custom_editor_resynch_editor(self):
        return self.check_resynch_editor('custom')

    def test_simple_editor_resynch_editor(self):
        return self.check_resynch_editor('simple')

    def test_simple_editor_parent_closed(self):
        obj = NonmodalInstanceEditor()
        tester = UITester()
        with tester.create_ui(obj, dict(view=get_view('simple'))) as ui:
            instance = tester.find_by_name(ui, "inst")
            instance.locate(locator.NestedUI())
