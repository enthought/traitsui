# (C) Copyright 2004-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

# from traits.etsconfig.api import ETSConfig
# ETSConfig.toolkit = 'wx'

import platform
import unittest

from traits.api import HasTraits, Float, Int
from traitsui.api import Item, RangeEditor, UItem, View
from traitsui.testing.api import (
    DisplayedText,
    KeyClick,
    KeySequence,
    Slider,
    Textbox,
    UITester,
)
from traitsui.tests._tools import (
    BaseTestMixin,
    is_wx,
    requires_toolkit,
    ToolkitName,
)

is_windows = platform.system() == "Windows"


class RangeModel(HasTraits):

    value = Int(1)
    float_value = Float(0.1)


@requires_toolkit([ToolkitName.qt, ToolkitName.wx])
class TestRangeEditor(BaseTestMixin, unittest.TestCase):
    def setUp(self):
        BaseTestMixin.setUp(self)

    def tearDown(self):
        BaseTestMixin.tearDown(self)

    def check_range_enum_editor_format_func(self, style):
        # RangeEditor with enum mode doesn't support format_func
        obj = RangeModel()
        view = View(
            UItem(
                "value",
                editor=RangeEditor(
                    low=1,
                    high=3,
                    format_func=lambda v: "{:02d}".format(v),
                    mode="enum",
                    show_error_dialog=False
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
            self.assertEqual(editor.inverse_mapping, {1: "1", 2: "2", 3: "3"})

    def test_simple_editor_format_func(self):
        self.check_range_enum_editor_format_func("simple")

    def test_custom_editor_format_func(self):
        self.check_range_enum_editor_format_func("custom")

    def check_slider_set_with_text_valid(self, mode):
        model = RangeModel()
        view = View(
            Item("value", editor=RangeEditor(low=1, high=12, mode=mode))
        )
        tester = UITester()
        with tester.create_ui(model, dict(view=view)) as ui:
            # sanity check
            self.assertEqual(model.value, 1)
            number_field = tester.find_by_name(ui, "value")
            text = number_field.locate(Textbox())
            text.perform(KeyClick("0"))
            text.perform(KeyClick("Enter"))
            displayed = text.inspect(DisplayedText())
            self.assertEqual(model.value, 10)
            self.assertEqual(displayed, str(model.value))

    def test_simple_slider_editor_set_with_text_valid(self):
        return self.check_slider_set_with_text_valid(mode='slider')

    def test_large_range_slider_editor_set_with_text_valid(self):
        return self.check_slider_set_with_text_valid(mode='xslider')

    def test_log_range_slider_editor_set_with_text_valid(self):
        return self.check_slider_set_with_text_valid(mode='logslider')

    def test_range_text_editor_set_with_text_valid(self):
        model = RangeModel()
        view = View(
            Item("value", editor=RangeEditor(low=1, high=12, mode="text"))
        )
        tester = UITester()
        with tester.create_ui(model, dict(view=view)) as ui:
            # sanity check
            self.assertEqual(model.value, 1)
            number_field_text = tester.find_by_name(ui, "value")
            if is_windows and is_wx():
                # For RangeTextEditor on wx and windows, the textbox
                # automatically gets focus and the full content is selected.
                # Insertion point is moved to keep the test consistent
                number_field_text.perform(KeyClick("End"))
            number_field_text.perform(KeyClick("0"))
            number_field_text.perform(KeyClick("Enter"))
            displayed = number_field_text.inspect(DisplayedText())
            self.assertEqual(model.value, 10)
            self.assertEqual(displayed, str(model.value))

    @requires_toolkit([ToolkitName.qt, ToolkitName.wx])
    def test_simple_spin_editor_set_with_text_valid(self):
        model = RangeModel()
        view = View(
            Item("value", editor=RangeEditor(low=1, high=12, mode="spinner"))
        )

        tester = UITester()
        with tester.create_ui(model, dict(view=view)) as ui:
            # sanity check
            self.assertEqual(model.value, 1)
            number_field = tester.find_by_name(ui, "value")
            # For whatever reason, "End" was not working here
            number_field.perform(KeyClick("Right"))
            number_field.perform(KeyClick("0"))
            number_field.perform(KeyClick("Enter"))
            displayed = number_field.inspect(DisplayedText())
            self.assertEqual(model.value, 10)
            self.assertEqual(displayed, str(model.value))

    def check_slider_set_with_text_after_empty(self, mode):
        model = RangeModel()
        view = View(
            Item("value", editor=RangeEditor(low=1, high=12, mode=mode, show_error_dialog=False))
        )
        tester = UITester()
        with tester.create_ui(model, dict(view=view)) as ui:
            number_field = tester.find_by_name(ui, "value")
            text = number_field.locate(Textbox())
            # Delete all contents of textbox
            for _ in range(5):
                text.perform(KeyClick("Backspace"))
            text.perform(KeySequence("11"))
            text.perform(KeyClick("Enter"))
            displayed = text.inspect(DisplayedText())
            self.assertEqual(model.value, 11)
            self.assertEqual(displayed, str(model.value))

    def test_simple_slider_editor_set_with_text_after_empty(self):
        return self.check_slider_set_with_text_after_empty(mode='slider')

    def test_large_range_slider_editor_set_with_text_after_empty(self):
        return self.check_slider_set_with_text_after_empty(mode='xslider')

    def test_log_range_slider_editor_set_with_text_after_empty(self):
        return self.check_slider_set_with_text_after_empty(mode='logslider')

    @requires_toolkit([ToolkitName.qt, ToolkitName.wx])
    def test_range_text_editor_set_with_text_after_empty(self):
        model = RangeModel()
        view = View(
            Item("value", editor=RangeEditor(low=1, high=12, mode="text",
                                             show_error_dialog=False))
        )
        tester = UITester()
        with tester.create_ui(model, dict(view=view)) as ui:
            number_field_text = tester.find_by_name(ui, "value")
            # Delete all contents of textbox
            for _ in range(5):
                number_field_text.perform(KeyClick("Backspace"))
            number_field_text.perform(KeySequence("11"))
            number_field_text.perform(KeyClick("Enter"))
            displayed = number_field_text.inspect(DisplayedText())
            self.assertEqual(model.value, 11)
            self.assertEqual(displayed, str(model.value))

    @requires_toolkit([ToolkitName.qt, ToolkitName.wx])
    def test_simple_spin_editor_set_with_text_after_empty(self):
        model = RangeModel()
        view = View(
            Item("value", editor=RangeEditor(low=1, high=12, mode="spinner",
                                             show_error_dialog=False))
        )

        tester = UITester()
        with tester.create_ui(model, dict(view=view)) as ui:
            number_field_text = tester.find_by_name(ui, "value")
            number_field_text.perform(KeyClick("Right"))
            # Delete all contents of textbox
            for _ in range(5):
                number_field_text.perform(KeyClick("Backspace"))
            number_field_text.perform(KeySequence("11"))
            number_field_text.perform(KeyClick("Enter"))
            displayed = number_field_text.inspect(DisplayedText())
            self.assertEqual(model.value, 11)
            self.assertEqual(displayed, str(model.value))

    def check_modify_slider(self, mode):
        model = RangeModel(value=0)
        view = View(
            Item("value", editor=RangeEditor(low=0, high=10, mode=mode))
        )
        tester = UITester()
        with tester.create_ui(model, dict(view=view)) as ui:
            number_field = tester.find_by_name(ui, "value")
            slider = number_field.locate(Slider())
            text = number_field.locate(Textbox())
            # slider values are converted to a [0, 10000] scale.  A single
            # step is a change of 100 on that scale and a page step is 1000.
            # Our range in [0, 10] so these correspond to changes of .1 and 1.
            # Note: when tested manually, the step size seen on OSX and Wx is
            # different.
            for _ in range(10):
                slider.perform(KeyClick("Right"))
            displayed = text.inspect(DisplayedText())
            self.assertEqual(model.value, 1)
            self.assertEqual(displayed, str(model.value))
            slider.perform(KeyClick("Page Up"))
            displayed = text.inspect(DisplayedText())
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
                editor=RangeEditor(low=0.1, high=1000000000, mode='logslider'),
            )
        )
        tester = UITester()
        with tester.create_ui(model, dict(view=view)) as ui:
            number_field = tester.find_by_name(ui, "float_value")
            slider = number_field.locate(Slider())
            text = number_field.locate(Textbox())
            # 10 steps is equivalent to 1 page step
            # on this scale either of those is equivalent to increasing the
            # trait's value from 10^n to 10^(n+1)
            for _ in range(10):
                slider.perform(KeyClick("Right"))
            displayed = text.inspect(DisplayedText())
            self.assertEqual(model.float_value, 1.0)
            self.assertEqual(displayed, str(model.float_value))
            slider.perform(KeyClick("Page Up"))
            displayed = text.inspect(DisplayedText())
            self.assertEqual(model.float_value, 10.0)
            self.assertEqual(displayed, str(model.float_value))

    def test_format_func(self):
        def num_to_time(num):
            minutes = int(num / 60)
            if minutes < 10:
                minutes_str = '0' + str(minutes)
            else:
                minutes_str = str(minutes)
            seconds = num % 60
            if seconds < 10:
                seconds_str = '0' + str(seconds)
            else:
                seconds_str = str(seconds)
            return minutes_str + ':' + seconds_str

        model = RangeModel()
        view = View(
            Item("float_value", editor=RangeEditor(format_func=num_to_time,
                                                   show_error_dialog=False))
        )
        tester = UITester()
        with tester.create_ui(model, dict(view=view)) as ui:
            float_value_field = tester.find_by_name(ui, "float_value")
            float_value_text = float_value_field.locate(Textbox())
            self.assertEqual(
                float_value_text.inspect(DisplayedText()), "00:00.1"
            )

    def test_editor_factory_format(self):
        """
        format trait on RangeEditor editor factory has been deprecated in
        favor of format_str. However, behavior should be unchanged.
        """
        model = RangeModel()
        with self.assertWarns(DeprecationWarning):
            view = View(
                Item("float_value", editor=RangeEditor(format="%s ...",
                                                       show_error_dialog=False))
            )
        tester = UITester()
        with tester.create_ui(model, dict(view=view)) as ui:
            float_value_field = tester.find_by_name(ui, "float_value")
            float_value_text = float_value_field.locate(Textbox())
            self.assertEqual(
                float_value_text.inspect(DisplayedText()), "0.1 ..."
            )

    def test_editor_format(self):
        """
        The format trait on an Editor instance previously potentially
        could override the factory. Now that is not the case.
        """
        model = RangeModel()
        with self.assertWarns(DeprecationWarning):
            view = View(
                Item("float_value", editor=RangeEditor(format="%s ...",
                                                       show_error_dialog=False))
            )
        tester = UITester()
        with tester.create_ui(model, dict(view=view)) as ui:
            float_value_field = tester.find_by_name(ui, "float_value")
            float_value_field._target.format = "%s +++"
            model.float_value = 0.2
            float_value_text = float_value_field.locate(Textbox())
            self.assertEqual(
                float_value_text.inspect(DisplayedText()), "0.2 ..."
            )

    # regression test for enthought/traitsui#737
    def test_set_text_out_of_range(self):
        model = RangeModel()
        view = View(
            Item(
                'float_value', editor=RangeEditor(mode='text', low=0.0, high=1,
                                                  show_error_dialog=False)
            ),
        )
        tester = UITester()
        with tester.create_ui(model, dict(view=view)) as ui:
            float_value_field = tester.find_by_name(ui, "float_value")
            for _ in range(3):
                float_value_field.perform(KeyClick("Backspace"))

            # set a value out of the range [0.0, 1]
            float_value_field.perform(KeySequence("2.0"))
            float_value_field.perform(KeyClick("Enter"))

            self.assertTrue(0.0 <= model.float_value <= 1)
