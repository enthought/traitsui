import platform
import unittest

from traits.api import HasTraits, Int
from traitsui.api import Item, RangeEditor, UItem, View
from traitsui.testing.tester import command, locator, query
from traitsui.testing.tester.ui_tester import UITester
from traitsui.tests._tools import (
    is_wx,
    requires_toolkit,
    ToolkitName,
)

is_windows = platform.system() == "Windows"


class RangeModel(HasTraits):

    value = Int(1)


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

    def check_set_with_text_valid(self, mode):
        model = RangeModel()
        view = View(
            Item(
                "value",
                editor=RangeEditor(low=1, high=12, mode=mode)
            )
        )
        tester = UITester()
        with tester.create_ui(model, dict(view=view)) as ui:
            # sanity check
            self.assertEqual(model.value, 1)
            number_field = tester.find_by_name(ui, "value")
            text = number_field.locate(locator.WidgetType.textbox)
            if is_windows and is_wx() and mode == 'text':
                # For RangeTextEditor on wx and windows, the textbox
                # automatically gets focus and the full content is selected.
                # Insertion point is moved to keep the test consistent
                text.target.textbox.SetInsertionPointEnd()
            text.perform(command.KeyClick("0"))
            text.perform(command.KeyClick("Enter"))
            displayed = text.inspect(query.DisplayedText())
            self.assertEqual(model.value, 10)
            self.assertEqual(displayed, str(model.value))

    def test_simple_slider_editor_set_with_text_valid(self):
        return self.check_set_with_text_valid(mode='slider')

    def test_large_range_slider_editor_set_with_text_valid(self):
        return self.check_set_with_text_valid(mode='xslider')

    def test_log_range_slider_editor_set_with_text_valid(self):
        return self.check_set_with_text_valid(mode='logslider')

    def test_range_text_editor_set_with_text_valid(self):
        return self.check_set_with_text_valid(mode='text')

    def check_set_with_text_after_empty(self, mode):
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
            # Delete all contents of textbox
            for _ in range(5):
                text.perform(command.KeyClick("Backspace"))
            text.perform(command.KeySequence("11"))
            text.perform(command.KeyClick("Enter"))
            displayed = text.inspect(query.DisplayedText())
            self.assertEqual(model.value, 11)
            self.assertEqual(displayed, str(model.value))

    def test_simple_slider_editor_set_with_text_after_empty(self):
        return self.check_set_with_text_after_empty(mode='slider')

    def test_large_range_slider_editor_set_with_text_after_empty(self):
        return self.check_set_with_text_after_empty(mode='xslider')

    def test_log_range_slider_editor_set_with_text_after_empty(self):
        return self.check_set_with_text_after_empty(mode='logslider')

    # on wx the text style editor gives an error whenever the textbox
    # is empty, even if enter has not been pressed.
    @requires_toolkit([ToolkitName.qt])
    def test_range_text_editor_set_with_text_after_empty(self):
        return self.check_set_with_text_after_empty(mode='text')
