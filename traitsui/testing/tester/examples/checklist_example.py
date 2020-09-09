import time

from traits.api import HasTraits, List, Str
from traitsui.api import CheckListEditor, UItem, View
from traitsui.testing.tester.ui_tester import UITester
from traitsui.testing.tester import command, locator


class ListModel(HasTraits):

    value = List()


def get_view(style):
    return View(
        UItem(
            "value",
            editor=CheckListEditor(
                values=["one", "two", "three", "four"],
            ),
            style=style,
        ),
        resizable=True
    )

list_edit = ListModel()

if __name__ == '__main__':
    tester = UITester(delay=500)
    with tester.create_ui(list_edit, dict(view=get_view("custom"))) as ui:
        assert list_edit.value == []
        check_list = tester.find_by_name(ui, "value")
        item_1 = check_list.locate(locator.Index(1))
        item_1.perform(command.MouseClick())
        assert list_edit.value == ["two"]
        item_1.perform(command.MouseClick())
        assert list_edit.value == []
        time.sleep(.5)

    class StrModel(HasTraits):
            value = Str()

    str_edit = StrModel(value="alpha, \ttwo, three,\n lambda, one")

    tester = UITester(delay=500)
    with tester.create_ui(str_edit, dict(view=get_view("custom"))) as ui:

        assert str_edit.value == "two,three,one"

        check_list = tester.find_by_name(ui, "value")
        item_1 = check_list.locate(locator.Index(1))
        item_1.perform(command.MouseClick())
        time.sleep(.5)

        assert str_edit.value == "three,one"