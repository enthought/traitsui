import unittest

from traits.api import HasTraits, Instance, Str
from traitsui.item import Item
from traitsui.view import View
from traitsui.tests._tools import (
    create_ui,
    press_ok_button,
    skip_if_not_qt4,
    store_exceptions_on_all_threads,
)


class EditedInstance(HasTraits):
    value = Str()
    traits_view = View(Item("value"), buttons=["OK"])


class NonmodalInstanceEditor(HasTraits):
    inst = Instance(EditedInstance, ())
    traits_view = View(Item("inst", style="simple"), buttons=["OK"])


class TestInstanceEditor(unittest.TestCase):

    @skip_if_not_qt4
    def test_simple_editor(self):
        obj = NonmodalInstanceEditor()
        with store_exceptions_on_all_threads(), create_ui(obj) as ui:
            editor = ui.get_editors("inst")[0]

            # make the dialog appear
            editor._button.click()

            # close the ui dialog
            press_ok_button(editor._dialog_ui)

            # close the main ui
            press_ok_button(ui)

    @skip_if_not_qt4
    def test_simple_editor_parent_closed(self):
        obj = NonmodalInstanceEditor()
        with store_exceptions_on_all_threads(), create_ui(obj) as ui:
            editor = ui.get_editors("inst")[0]

            # make the dialog appear
            editor._button.click()

            # close the main ui
            press_ok_button(ui)
