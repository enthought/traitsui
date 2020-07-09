import unittest

from traits.api import HasTraits, Int
from traitsui.api import RangeEditor, UItem, View
from traitsui.tests._tools import (
    create_ui,
    skip_if_null,
    store_exceptions_on_all_threads,
)


class RangeModel(HasTraits):

    value = Int()


@skip_if_null
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

        with store_exceptions_on_all_threads(),\
                create_ui(obj, dict(view=view)) as ui:
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
