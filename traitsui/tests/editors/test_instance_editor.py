import unittest

from traits.api import HasTraits, Instance, Str
from traitsui.item import Item
from traitsui.view import View
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


class EditedInstance(HasTraits):
    value = Str()
    traits_view = View(Item("value"), buttons=["OK"])


class NonmodalInstanceEditor(HasTraits):
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
        obj = NonmodalInstanceEditor()
        tester = UITester()
        with tester.create_ui(obj, dict(view=get_view("simple"))) as ui:
            instance = tester.find_by_name(ui, "inst")
            instance.perform(MouseClick())
            value_txt = instance.find_by_name("value")
            value_txt.perform(KeySequence("abc"))
            self.assertEqual(obj.inst.value, "abc")

    def test_custom_editor(self):
        obj = NonmodalInstanceEditor()
        tester = UITester()
        with tester.create_ui(obj, dict(view=get_view("custom"))) as ui:
            value_txt = tester.find_by_name(ui, "inst").find_by_name("value")
            value_txt.perform(KeySequence("abc"))
            self.assertEqual(obj.inst.value, "abc")

    def test_custom_editor_resynch_editor(self):
        edited_inst = EditedInstance(value='hello')
        obj = NonmodalInstanceEditor(inst=edited_inst)
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
        obj = NonmodalInstanceEditor(inst=edited_inst)
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
        obj = NonmodalInstanceEditor()
        tester = UITester()
        with tester.create_ui(obj, dict(view=get_view('simple'))) as ui:
            instance = tester.find_by_name(ui, "inst")
            instance.perform(MouseClick())
