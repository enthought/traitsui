import unittest

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
    traits_view = View(Item("inst", style="simple"), buttons=["OK"])


class TestInstanceEditor(unittest.TestCase):

    @requires_toolkit([ToolkitName.qt])
    def test_simple_editor(self):
        obj = NonmodalInstanceEditor()
        tester=UITester()
        with tester.create_ui(obj) as ui:
            instance = tester.find_by_name(ui, "inst")
            editor = instance.locate(locator.NestedUI())
            # the below code requires ui_base implementation to work
            #ok_button = editor.find_by_id("OK")
            #ok_button.perform(command.MouseClick())
            press_ok_button(editor.target)

    @requires_toolkit([ToolkitName.qt])
    def test_simple_editor_parent_closed(self):
        obj = NonmodalInstanceEditor()
        with reraise_exceptions(), create_ui(obj) as ui:
            editor = ui.get_editors("inst")[0]

            # make the dialog appear
            editor._button.click()
