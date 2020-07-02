import unittest

from pyface.gui import GUI

from traits.api import Button, HasTraits, List, Str
from traitsui.api import ButtonEditor, Item, UItem, View
from traitsui.tests._tools import (
    create_ui,
    is_current_backend_qt4,
    is_current_backend_wx,
    process_cascade_events,
    skip_if_null,
    skip_if_not_qt4,
    store_exceptions_on_all_threads,
)


class ButtonTextEdit(HasTraits):

    play_button = Button("Play")

    play_button_label = Str("I'm a play button")

    values = List()

    traits_view = View(
        Item("play_button", style="simple"),
        Item("play_button", style="custom"),
        Item("play_button", style="readonly"),
        Item("play_button", style="text"),
    )


simple_view = View(
    UItem("play_button", editor=ButtonEditor(label_value="play_button_label")),
    Item("play_button_label"),
    resizable=True,
)


custom_view = View(
    UItem("play_button", editor=ButtonEditor(label_value="play_button_label")),
    Item("play_button_label"),
    resizable=True,
    style="custom",
)


def get_button_text(button):
    """ Return the button text given a button control """
    if is_current_backend_wx():
        return button.GetLabel()

    elif is_current_backend_qt4():
        return button.text()


class TestButtonEditor(unittest.TestCase):
    def check_button_text_update(self, view):
        button_text_edit = ButtonTextEdit()

        with store_exceptions_on_all_threads(), \
                create_ui(button_text_edit, dict(view=view)) as ui:

            process_cascade_events()
            editor, = ui.get_editors("play_button")
            button = editor.control

            self.assertEqual(get_button_text(button), "I'm a play button")

            button_text_edit.play_button_label = "New Label"
            self.assertEqual(get_button_text(button), "New Label")

    @skip_if_null
    def test_styles(self):
        # simple smoke test of buttons
        button_text_edit = ButtonTextEdit()
        with store_exceptions_on_all_threads(), create_ui(button_text_edit):
            pass

    @skip_if_null
    def test_simple_button_editor(self):
        self.check_button_text_update(simple_view)

    @skip_if_null
    def test_custom_button_editor(self):
        self.check_button_text_update(custom_view)


@skip_if_not_qt4
class TestButtonEditorValuesTrait(unittest.TestCase):
    """ The values_trait is only supported by Qt.

    See discussion enthought/traitsui#879
    """

    def get_view(self, style):
        return View(
            Item(
                "play_button",
                editor=ButtonEditor(values_trait="values"),
                style=style,
            ),
        )

    def check_editor_values_trait_init_and_dispose(self, style):
        # Smoke test to check init and dispose when values_trait is used.
        instance = ButtonTextEdit(values=["Item1", "Item2"])
        view = self.get_view(style=style)
        with store_exceptions_on_all_threads():
            with create_ui(instance, dict(view=view)):
                pass

            # It is okay to mutate trait after the GUI is disposed.
            instance.values = ["Item3"]

    def test_simple_editor_values_trait_init_and_dispose(self):
        # Smoke test to check init and dispose when values_trait is used.
        self.check_editor_values_trait_init_and_dispose(style="simple")

    def test_custom_editor_values_trait_init_and_dispose(self):
        # Smoke test to check init and dispose when values_trait is used.
        self.check_editor_values_trait_init_and_dispose(style="custom")
