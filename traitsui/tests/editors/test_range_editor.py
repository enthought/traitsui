# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import platform
import unittest

from pyface.constant import OK
from pyface.toolkit import toolkit_object
from traits.api import HasTraits, Float, Int, Range, TraitError
from traits.testing.api import UnittestTools
from traitsui.api import Item, RangeEditor, UItem, View
from traitsui.testing.api import (
    DisplayedText,
    KeyClick,
    KeySequence,
    Slider,
    TargetRegistry,
    Textbox,
    UITester,
)
from traitsui.tests._tools import (
    BaseTestMixin,
    is_wx,
    requires_toolkit,
    ToolkitName,
)

ModalDialogTester = toolkit_object(
    "util.modal_dialog_tester:ModalDialogTester"
)

is_windows = platform.system() == "Windows"


def _register_simple_spin(registry):
    """Register interactions for the given registry for a SimpleSpinEditor.

    If there are any conflicts, an error will occur.

    This is kept separate from the below register function because the
    SimpleSpinEditor is not yet implemented on wx.  This function can be used
    with a local reigstry for tests.

    Parameters
    ----------
    registry : TargetRegistry
        The registry being registered to.
    """
    from traitsui.testing.tester._ui_tester_registry.qt import (
        _registry_helper,
    )
    from traitsui.qt.range_editor import SimpleSpinEditor

    _registry_helper.register_editable_textbox_handlers(
        registry=registry,
        target_class=SimpleSpinEditor,
        widget_getter=lambda wrapper: wrapper._target.control.lineEdit(),
    )


class RangeModel(HasTraits):

    value = Int(1)
    float_value = Float(0.1)


class RangeExcludeLow(HasTraits):
    x = Range(low=0.0, high=1.0, value=0.1, exclude_low=True)


class ModelWithRangeTrait(HasTraits):
    value = Range(low=0, high=None, value=1)


@requires_toolkit([ToolkitName.qt, ToolkitName.wx])
class TestRangeEditor(BaseTestMixin, unittest.TestCase, UnittestTools):
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

    def test_range_text_editor_set_with_text_valid_and_none_bound(self):
        model = ModelWithRangeTrait()
        tester = UITester()
        with tester.create_ui(model) as ui:
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

    # the tester support code is not yet implemented for Wx SimpleSpinEditor
    @requires_toolkit([ToolkitName.qt])
    def test_simple_spin_editor_set_with_text_valid(self):
        model = RangeModel()
        view = View(
            Item("value", editor=RangeEditor(low=1, high=12, mode="spinner"))
        )
        LOCAL_REGISTRY = TargetRegistry()
        _register_simple_spin(LOCAL_REGISTRY)
        tester = UITester(registries=[LOCAL_REGISTRY])
        with tester.create_ui(model, dict(view=view)) as ui:
            # sanity check
            self.assertEqual(model.value, 1)
            number_field = tester.find_by_name(ui, "value")
            # For whatever reason, "End" was not working here
            number_field.perform(KeyClick("Right"))
            number_field.perform(KeyClick("0"))
            displayed = number_field.inspect(DisplayedText())
            self.assertEqual(model.value, 10)
            self.assertEqual(displayed, str(model.value))

    # the tester support code is not yet implemented for Wx SimpleSpinEditor
    @requires_toolkit([ToolkitName.qt])
    def test_simple_spin_editor_auto_set_false(self):
        model = RangeModel()
        view = View(
            Item(
                "value",
                editor=RangeEditor(
                    low=1,
                    high=12,
                    mode="spinner",
                    auto_set=False,
                )
            )
        )
        LOCAL_REGISTRY = TargetRegistry()
        _register_simple_spin(LOCAL_REGISTRY)
        tester = UITester(registries=[LOCAL_REGISTRY])
        with tester.create_ui(model, dict(view=view)) as ui:
            # sanity check
            self.assertEqual(model.value, 1)
            number_field = tester.find_by_name(ui, "value")
            # For whatever reason, "End" was not working here
            number_field.perform(KeyClick("Right"))
            with self.assertTraitDoesNotChange(model, "value"):
                number_field.perform(KeyClick("0"))
            displayed = number_field.inspect(DisplayedText())
            self.assertEqual(displayed, "10")
            with self.assertTraitChanges(model, "value"):
                number_field.perform(KeyClick("Enter"))
            self.assertEqual(model.value, 10)

    def check_slider_set_with_text_after_empty(self, mode):
        model = RangeModel()
        view = View(
            Item("value", editor=RangeEditor(low=1, high=12, mode=mode))
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

    # on wx the text style editor gives an error whenever the textbox
    # is empty, even if enter has not been pressed.
    @requires_toolkit([ToolkitName.qt])
    def test_range_text_editor_set_with_text_after_empty(self):
        model = RangeModel()
        view = View(
            Item("value", editor=RangeEditor(low=1, high=12, mode="text"))
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

    # the tester support code is not yet implemented for Wx SimpleSpinEditor
    @requires_toolkit([ToolkitName.qt])
    def test_simple_spin_editor_set_with_text_after_empty(self):
        model = RangeModel()
        view = View(
            Item("value", editor=RangeEditor(low=1, high=12, mode="spinner"))
        )
        LOCAL_REGISTRY = TargetRegistry()
        _register_simple_spin(LOCAL_REGISTRY)
        tester = UITester(registries=[LOCAL_REGISTRY])
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
            Item("float_value", editor=RangeEditor(format_func=num_to_time))
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
        format trait on RangeEditor editor factory has been removed in
        favor of format_str.
        """
        model = RangeModel()
        with self.assertRaises(TraitError):
            view = View(
                Item("float_value", editor=RangeEditor(format="%s ..."))
            )

    def test_editor_factory_format_str(self):
        """
        format trait on RangeEditor editor factory has been deprecated in
        favor of format_str. However, behavior should be unchanged.
        """
        model = RangeModel()
        view = View(
            Item("float_value", editor=RangeEditor(format_str="%s ..."))
        )
        tester = UITester()
        with tester.create_ui(model, dict(view=view)) as ui:
            float_value_field = tester.find_by_name(ui, "float_value")
            float_value_text = float_value_field.locate(Textbox())
            self.assertEqual(
                float_value_text.inspect(DisplayedText()), "0.1 ..."
            )

    def test_editor_format_str(self):
        """
        The format trait on an Editor instance has been removed.
        """
        model = RangeModel()
        view = View(
            Item("float_value", editor=RangeEditor(format_str="%s ..."))
        )
        tester = UITester()
        with tester.create_ui(model, dict(view=view)) as ui:
            float_value_field = tester.find_by_name(ui, "float_value")
            with self.assertRaises(TraitError):
                float_value_field._target.format = "%s +++"

    # regression test for enthought/traitsui#737. Hangs with a popup
    # dialog on wx. (xref: enthought/traitsui#1901)
    @requires_toolkit([ToolkitName.qt])
    def test_set_text_out_of_range(self):
        model = RangeModel()
        view = View(
            Item(
                'float_value', editor=RangeEditor(mode='text', low=0.0, high=1)
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

    # regression test for enthought/traitsui#1550
    @requires_toolkit([ToolkitName.qt])
    def test_modify_out_of_range(self):
        obj = RangeExcludeLow()
        tester = UITester(auto_process_events=False)
        with tester.create_ui(obj) as ui:
            number_field = tester.find_by_name(ui, "x")
            text = number_field.locate(Textbox())

            # should not fail
            def set_out_of_range():
                text.perform(KeyClick("Backspace"))
                text.perform(KeyClick("0"))
                text.perform(KeyClick("Enter"))

            mdtester = ModalDialogTester(set_out_of_range)
            mdtester.open_and_run(lambda x: x.close(accept=True))

    # regression test for enthought/traitsui#1550
    @requires_toolkit([ToolkitName.qt])
    def test_modify_out_of_range_with_slider(self):
        obj = RangeExcludeLow()
        tester = UITester(auto_process_events=False)
        with tester.create_ui(obj) as ui:
            number_field = tester.find_by_name(ui, "x")
            slider = number_field.locate(Slider())

            # slider values are converted to a [0, 10000] scale.  A single
            # step is a change of 100 on that scale and a page step is 1000.
            # Our range in [0, 10] so these correspond to changes of .1 and 1.
            # Note: when tested manually, the step size seen on OSX and Wx is
            # different.

            # should not fail
            def move_slider_out_of_range():
                slider.perform(KeyClick("Page Down"))

            mdtester = ModalDialogTester(move_slider_out_of_range)
            mdtester.open_and_run(lambda x: x.click_button(OK))
