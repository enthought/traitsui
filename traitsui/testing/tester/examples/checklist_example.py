""" Example for utilizing UI Tester on a checklist editor.
"""
import time

from traits.api import HasTraits, List
from traitsui.api import CheckListEditor, UItem, View
from traitsui.testing.tester.ui_tester import UITester
from traitsui.testing.tester import command, locator


class ListModel(HasTraits):
    """ Dummy class holding the list trait to interacted with. """
    value = List()


def get_view(style):
    """ Gets a view for the value trait that uses a CheckListEditor"""
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
        # added so last click can be seen (in real tests this would be removed)
        time.sleep(.5)
