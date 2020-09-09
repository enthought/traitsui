import platform

from traits.api import HasTraits, Int
from traitsui.api import Item, RangeEditor, UItem, View
from traitsui.testing.tester import command, locator, query
from traitsui.testing.tester.ui_tester import UITester
from traitsui.tests._tools import is_wx
is_windows = platform.system() == "Windows"

class RangeModel(HasTraits):

    value = Int(1)


def get_view(mode):
    return View(
        Item(
            "value",
            editor=RangeEditor(low=1, high=12, mode=mode)
        )
    )


model = RangeModel()

if __name__ == '__main__':
    tester = UITester(delay = 500)
    for mode in ['slider', 'xslider', 'logslider', 'text']:
        with tester.create_ui(model, dict(view=get_view(mode))) as ui:
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
            assert model.value == 10
            assert displayed == str(model.value)
            text.perform(command.KeyClick("Backspace"))
            text.perform(command.KeyClick("Enter"))
