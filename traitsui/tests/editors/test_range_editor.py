import unittest

from traits.api import HasTraits, Int, Range
from traitsui.api import Item, RangeEditor, UItem, View
from traitsui.testing.tester import command, locator, query
from traitsui.testing.tester.ui_tester import UITester
from traitsui.tests._tools import (
    create_ui,
    requires_toolkit,
    reraise_exceptions,
    ToolkitName,
)


class RangeModel(HasTraits):

    value = Int()

class stuff(HasTraits):
    value = Range(0, 12)

@requires_toolkit([ToolkitName.qt, ToolkitName.wx])
class TestRangeEditor(unittest.TestCase):

    def check_range_enum_editor_format_func(self, style):
        # RangeEditor with enum mode doesn't support format_func
        obj = RangeModel()
        view = View(
            UItem(
                "value",
                editor=RangeEditor(
                    low=1, high=3,
                    format_func=lambda v: "{:02d}".format(v),
                    mode="enum"
                ),
                style=style,
            )
        )

        tester = UITester()
        with tester.create_ui(obj, dict(view=view)) as ui:
            editor = ui.get_editors("value")[0]

            # No formatting - simple strings
            self.assertEqual(editor.names[:3], ["1", "2", "3"])
            self.assertEqual(editor.mapping, {"1": 1, "2": 2, "3": 3})
            self.assertEqual(
                editor.inverse_mapping, {1: "1", 2: "2", 3: "3"}
            )

    def test_simple_editor_format_func(self):
        self.check_range_enum_editor_format_func("simple")

    def test_custom_editor_format_func(self):
        self.check_range_enum_editor_format_func("custom")

    """def test_set_with_text(self):
        model = stuff()
        view = View(Item("value", style='simple'))
        tester = UITester()
        with tester.create_ui(model, dict(view=view)) as ui:
            number_field = tester.find_by_name(ui, "value")
            text = number_field.locate(locator.WidgetType.textbox)
            text.perform(command.KeySequence("\b\b\b\b4"))
            text.perform(command.KeyClick("Tab"))
            display = text.inspect(query.DisplayedText())
            print("________-")
            print(display)
            self.assertEqual(model.value, 4)
            text.perform(command.KeySequence("\b4"))"""

    @requires_toolkit([ToolkitName.qt])
    def check_set_with_text(self, mode):
        model = RangeModel()
        view = View(Item("value", editor=RangeEditor(low=0.0, high=12.0, mode=mode)), buttons=["OK"])
        tester = UITester()
        with tester.create_ui(model, dict(view=view)) as ui:
            number_field = tester.find_by_name(ui, "value")
            text = number_field.locate(locator.WidgetType.textbox)
            text.perform(command.KeySequence("\b\b\b\b\b4"))
            #ok_button = tester.find_by_name(ui, 'OK')
            #ok_button.perform(command.MouseClick)
            text.perform(command.KeyClick("Enter"))
            self.assertEqual(model.value, 4)
            #text.perform(command.KeySequence("\b4"))

    def test_simple_slider_editor_set_with_text(self):
        return self.check_set_with_text(mode='slider')

    def test_large_range_slider_editor_set_with_text(self):
        return self.check_set_with_text(mode='xslider')

    """def test_log_range_slider_editor_set_with_text(self):
        return self.check_set_with_text(mode='logslider')"""

    def test_range_text_editor_set_with_text(self):
        return self.check_set_with_text(mode='text')