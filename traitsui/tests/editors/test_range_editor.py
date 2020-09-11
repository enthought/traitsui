import platform
import unittest

from traits.api import HasTraits, Float, Int
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
    float_value = Float(0.1)


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

    @requires_toolkit([ToolkitName.qt])
    def test_simple_spin_editor_set_with_text_valid(self):
        return self.check_set_with_text_valid(mode='spinner')

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

    @requires_toolkit([ToolkitName.qt])
    def test_simple_spin_editor_set_with_text_after_empty(self):
        return self.check_set_with_text_after_empty(mode='spinner')

    def test_large_range_slider_editor_set_with_text_after_empty(self):
        return self.check_set_with_text_after_empty(mode='xslider')

    def test_log_range_slider_editor_set_with_text_after_empty(self):
        return self.check_set_with_text_after_empty(mode='logslider')

    # on wx the text style editor gives an error whenever the textbox
    # is empty, even if enter has not been pressed.
    @requires_toolkit([ToolkitName.qt])
    def test_range_text_editor_set_with_text_after_empty(self):
        return self.check_set_with_text_after_empty(mode='text')
    
    def check_modify_slider(self, mode):
        model = RangeModel(value=0)
        view = View(
            Item(
                "value",
                editor=RangeEditor(low=0, high=10, mode=mode)
            )
        )
        tester = UITester()
        with tester.create_ui(model, dict(view=view)) as ui:
            number_field = tester.find_by_name(ui, "value")
            slider = number_field.locate(locator.WidgetType.slider)
            text = number_field.locate(locator.WidgetType.textbox)
            # slider values are converted to a [0, 10000] scale.  A single 
            # step is a change of 100 on that scale and a page step is 1000.
            # Our range in [0, 10] so these correspond to changes of .1 and 1.
            for _ in range(10):
                slider.perform(command.KeyClick("Right"))
            displayed = text.inspect(query.DisplayedText())
            self.assertEqual(model.value, 1)
            self.assertEqual(displayed, str(model.value))
            slider.perform(command.KeyClick("Page Up"))
            displayed = text.inspect(query.DisplayedText())
            self.assertEqual(model.value, 2)
            self.assertEqual(displayed, str(model.value))

    def test_modify_slider_simple_slider(self):
        return self.check_modify_slider('slider')

    def test_modify_slider_large_range_slider(self):
        return self.check_modify_slider('xslider')

    def test_modify_slider_log_range_slider(self):
        model = RangeModel()
        view = View(
            Item(
                "float_value",
                editor=RangeEditor(low=.1, high=1000000000, mode='logslider')
            )
        )
        tester = UITester()
        with tester.create_ui(model, dict(view=view)) as ui:
            number_field = tester.find_by_name(ui, "float_value")
            slider = number_field.locate(locator.WidgetType.slider)
            text = number_field.locate(locator.WidgetType.textbox)
            # 10 steps is equivalent to 1 page step
            # on this scale either of those is equivalent to increasing the
            # trait's value from 10^n to 10^(n+1)
            for _ in range(10):
                slider.perform(command.KeyClick("Right"))
            displayed = text.inspect(query.DisplayedText())
            self.assertEqual(model.float_value, 1.0)
            self.assertEqual(displayed, str(model.float_value))
            slider.perform(command.KeyClick("Page Up"))
            displayed = text.inspect(query.DisplayedText())
            self.assertEqual(model.float_value, 10.0)
            self.assertEqual(displayed, str(model.float_value))