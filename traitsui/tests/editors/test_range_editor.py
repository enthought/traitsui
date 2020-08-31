import unittest

from traits.api import HasTraits, Int
from traitsui.api import Item, RangeEditor, UItem, View
from traitsui.testing.tester import command, locator, query
from traitsui.testing.tester.ui_tester import UITester
from traitsui.tests._tools import (
    requires_toolkit,
    ToolkitName,
)


class RangeModel(HasTraits):

    value = Int()


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

    @requires_toolkit([ToolkitName.qt])
    def check_set_with_text(self, mode):
        model = RangeModel()
        view = View(
            Item(
                "value",
                editor=RangeEditor(low=1, high=12, mode=mode)
            )
        )
        tester = UITester()
        with tester.create_ui(model, dict(view=view)) as ui:
            number_field = tester.find_by_name(ui, "value")
            text = number_field.locate(locator.WidgetType.textbox)
            text.perform(command.KeySequence("\b\b\b\b\b4"))
            text.perform(command.KeyClick("Enter"))
            displayed = text.inspect(query.DisplayedText())
            self.assertEqual(model.value, 4)
            self.assertEqual(displayed, str(model.value))

    def test_simple_slider_editor_set_with_text(self):
        return self.check_set_with_text(mode='slider')

    def test_large_range_slider_editor_set_with_text(self):
        return self.check_set_with_text(mode='xslider')

    def test_log_range_slider_editor_set_with_text(self):
        return self.check_set_with_text(mode='logslider')

    def test_range_text_editor_set_with_text(self):
        return self.check_set_with_text(mode='text')

    # There is a problem with KeySequence on wx.  trying to include the key
    # '\b' does not succesfully type a backspace.  Instead EmulateKeyPress
    # seems to literally type "\x08" which leads to errors.
    @requires_toolkit([ToolkitName.wx])
    def check_set_with_text_wx(self, mode):
        model = RangeModel()
        view = View(
            Item(
                "value",
                editor=RangeEditor(low=1, high=12, mode=mode)
            )
        )
        tester = UITester()
        with tester.create_ui(model, dict(view=view)) as ui:
            number_field = tester.find_by_name(ui, "value")
            text = number_field.locate(locator.WidgetType.textbox)
            for _ in range(5):
                text.perform(command.KeyClick("Backspace"))
            text.perform(command.KeySequence("10"))
            text.perform(command.KeyClick("Enter"))
            displayed = text.inspect(query.DisplayedText())
            self.assertEqual(model.value, 10)
            self.assertEqual(displayed, str(model.value))

    def test_simple_slider_editor_set_with_text_wx(self):
        return self.check_set_with_text_wx(mode='slider')

    def test_large_range_slider_editor_set_with_text_wx(self):
        return self.check_set_with_text_wx(mode='xslider')

    def test_log_range_slider_editor_set_with_text_wx(self):
        return self.check_set_with_text_wx(mode='logslider')

    def test_range_text_editor_set_with_text_wx(self):
        return self.check_set_with_text_wx(mode='text')
