import os
import unittest
from unittest.mock import patch

from pyface.gui import GUI

from traits.api import Enum, HasTraits, List
from traitsui.api import ImageEnumEditor, UItem, View
from traitsui.tests._tools import (
    is_current_backend_qt4,
    is_current_backend_wx,
    skip_if_null,
    skip_if_not_qt4,
    skip_if_not_wx,
    store_exceptions_on_all_threads,
)

# Import needed bitmap/pixmap cache and prepare for patching
if is_current_backend_wx():
    from traitsui.wx.helper import bitmap_cache as image_cache
    cache_to_patch = "traitsui.wx.image_enum_editor.bitmap_cache"
elif is_current_backend_qt4():
    from traitsui.qt4.helper import pixmap_cache as image_cache
    cache_to_patch = "traitsui.qt4.image_enum_editor.pixmap_cache"
else:
    image_cache = None
    cache_to_patch = "traitsui.null"


class EnumModel(HasTraits):

    value = Enum('top left', 'top right', 'bottom left', 'bottom right')


def get_view(style):
    return View(
        UItem(
            'value',
            editor=ImageEnumEditor(
                values=[
                    'top left', 'top right', 'bottom left', 'bottom right'
                ],
                prefix='@icons:',
                suffix='_origin',
                path=os.getcwd(),
            ),
            style=style,
        ),
        resizable=True,
    )


def click_on_image(image_control):
    """ Click on the image controlled by given image_control."""
    if is_current_backend_wx():
        import wx

        event = wx.MouseEvent(wx.EVT_LEFT_UP.typeId)
        event.SetX(0)
        event.SetY(0)
        wx.PostEvent(image_control, event)

    elif is_current_backend_qt4():
        image_control.click()

    else:
        raise unittest.SkipTest("Test not implemented for this toolkit")


def get_button_strings(control):
    """ Return the list of strings associated with the buttons under given
    control. Assumes all sizer children (wx) or layout items (qt) are buttons.
    """
    button_strings = []

    if is_current_backend_wx():
        for item in control.GetSizer().GetChildren():
            button = item.GetWindow()
            button_strings.append(button.value)

    elif is_current_backend_qt4():
        layout = control.layout()
        for i in range(layout.count()):
            button = layout.itemAt(i).widget()
            button_strings.append(button.value)

    else:
        raise unittest.SkipTest("Test not implemented for this toolkit")

    return button_strings


def get_all_button_selected_status(control):
    """ Return a list with selected (wx) or checked (qt) button status under
    given control. Assumes all sizer children (wx) or layout items (qt) are
    buttons.
    """
    button_status = []

    if is_current_backend_wx():
        for item in control.GetSizer().GetChildren():
            button_status.append(item.GetWindow().Selected())

    elif is_current_backend_qt4():
        layout = control.layout()
        for i in range(layout.count()):
            button_status.append(layout.itemAt(i).widget().isChecked())

    else:
        raise unittest.SkipTest("Test not implemented for this toolkit")

    return button_status


def get_button_control(control, button_idx):
    """ Get button control from a specified parent control given a button index.
    Assumes all sizer children (wx) or layout items (qt) are buttons.
    """
    if is_current_backend_wx():
        return control.GetSizer().GetChildren()[button_idx].GetWindow()

    elif is_current_backend_qt4():
        return control.layout().itemAt(button_idx).widget()

    else:
        raise unittest.SkipTest("Test not implemented for this toolkit")


@skip_if_not_qt4
class TestImageEnumEditorMapping(unittest.TestCase):

    def setup_ui(self, model, view):
        ui = model.edit_traits(view=view)
        self.addCleanup(ui.dispose)
        return ui.get_editors("value")[0]

    def check_enum_mappings_value_change(self, style):

        image_enum_editor_factory = ImageEnumEditor(
            values=['top left', 'top right'],
            format_func=lambda v: v.upper(),
            prefix='@icons:',
            suffix='_origin',
            path=os.getcwd(),
        )
        formatted_view = View(
            UItem(
                "value",
                editor=image_enum_editor_factory,
                style=style,
            )
        )

        with store_exceptions_on_all_threads():
            editor = self.setup_ui(EnumModel(), formatted_view)

            # FIXME issue enthought/traitsui#782
            with self.assertRaises(AssertionError):
                self.assertEqual(editor.names, ["TOP LEFT", "TOP RIGHT"])
                self.assertEqual(
                    editor.mapping,
                    {"TOP LEFT": "top left", "TOP RIGHT": "top right"}
                )
                self.assertEqual(
                    editor.inverse_mapping,
                    {"top left": "TOP LEFT", "top right": "TOP RIGHT"}
                )
            self.assertEqual(editor.names, ["top left", "top right"])
            self.assertEqual(
                editor.mapping,
                {"top left": "top left", "top right": "top right"}
            )
            self.assertEqual(
                editor.inverse_mapping,
                {"top left": "top left", "top right": "top right"}
            )

            image_enum_editor_factory.values = ["top right", "top left"]

            self.assertEqual(editor.names, ["TOP RIGHT", "TOP LEFT"])
            self.assertEqual(
                editor.mapping,
                {"TOP RIGHT": "top right", "TOP LEFT": "top left"}
            )
            self.assertEqual(
                editor.inverse_mapping,
                {"top right": "TOP RIGHT", "top left": "TOP LEFT"}
            )

    def check_enum_mappings_name_change(self, style):
        class PossibleEnumModel(HasTraits):
            value = value = Enum('top left', 'top right')
            possible_values = List(['top left', 'top right'])

        formatted_view = View(
            UItem(
                'value',
                editor=ImageEnumEditor(
                    name="object.possible_values",
                    format_func=lambda v: v.upper(),
                    prefix='@icons:',
                    suffix='_origin',
                    path=os.getcwd(),
                ),
                style=style,
            )
        )
        model = PossibleEnumModel()

        with store_exceptions_on_all_threads():
            editor = self.setup_ui(model, formatted_view)

            self.assertEqual(editor.names, ["TOP LEFT", "TOP RIGHT"])
            self.assertEqual(
                editor.mapping,
                {"TOP LEFT": "top left", "TOP RIGHT": "top right"}
                )
            self.assertEqual(
                editor.inverse_mapping,
                {"top left": "TOP LEFT", "top right": "TOP RIGHT"}
            )

            model.possible_values = ["top right", "top left"]

            self.assertEqual(editor.names, ["TOP RIGHT", "TOP LEFT"])
            self.assertEqual(
                editor.mapping,
                {"TOP RIGHT": "top right", "TOP LEFT": "top left"}
            )
            self.assertEqual(
                editor.inverse_mapping,
                {"top right": "TOP RIGHT", "top left": "TOP LEFT"}
            )

    def test_simple_editor_mapping_values(self):
        # FIXME issue enthought/traitsui#844
        error_msg = "'ImageEnumModel' object has no attribute 'reset'"
        with self.assertRaisesRegex(AttributeError, error_msg):
            self.check_enum_mappings_value_change("simple")

    def test_simple_editor_mapping_name(self):
        # FIXME issue enthought/traitsui#844
        error_msg = "'ImageEnumModel' object has no attribute 'reset'"
        with self.assertRaisesRegex(AttributeError, error_msg):
            self.check_enum_mappings_name_change("simple")

    def test_custom_editor_mapping_values(self):
        self.check_enum_mappings_value_change("custom")

    def test_custom_editor_mapping_name(self):
        self.check_enum_mappings_name_change("custom")

    def test_readonly_editor_mapping_values(self):
        self.check_enum_mappings_value_change("readonly")

    def test_readonly_editor_name(self):
        class PossibleEnumModel(HasTraits):
            value = value = Enum('top left', 'top right')
            possible_values = List(['top left', 'top right'])

        formatted_view = View(
            UItem(
                'value',
                editor=ImageEnumEditor(
                    name="object.possible_values",
                    format_func=lambda v: v.upper(),
                    prefix='@icons:',
                    suffix='_origin',
                    path=os.getcwd(),
                ),
                style="readonly",
            )
        )
        model = PossibleEnumModel()

        with store_exceptions_on_all_threads():
            editor = self.setup_ui(model, formatted_view)

            # Readonly editor doesn't set up full mapping, only check that
            # str_value is mapped as expected
            self.assertEqual(model.value, "top left")
            self.assertEqual(editor.str_value, "TOP LEFT")


@skip_if_null
class TestSimpleImageEnumEditor(unittest.TestCase):

    def setup_gui(self, model, view):
        gui = GUI()
        ui = model.edit_traits(view=view)
        self.addCleanup(ui.dispose)

        gui.process_events()
        editor = ui.get_editors("value")[0]
        control = editor.control

        return gui, control

    def test_simple_editor_more_cols(self):
        # Smoke test for setting up an editor with more than one column
        enum_edit = EnumModel()
        view = View(
            UItem(
                'value',
                editor=ImageEnumEditor(
                    values=[
                        'top left', 'top right', 'bottom left', 'bottom right'
                    ],
                    prefix='@icons:',
                    suffix='_origin',
                    path=os.getcwd(),
                    cols=4,
                ),
                style="simple",
            ),
            resizable=True,
        )

        with store_exceptions_on_all_threads():
            gui, combobox = self.setup_gui(enum_edit, view)

    @skip_if_not_wx
    @patch(cache_to_patch, wraps=image_cache)
    def test_simple_editor_popup_editor(self, patched_cache):
        enum_edit = EnumModel()

        with store_exceptions_on_all_threads():
            gui, control = self.setup_gui(enum_edit, get_view("simple"))

            self.assertEqual(enum_edit.value, 'top left')
            self.assertEqual(
                patched_cache.call_args[0][0], "@icons:top left_origin"
            )

            # Set up ImageEnumDialog
            click_on_image(control)
            gui.process_events()

            # Check created buttons
            image_grid_control = control.GetChildren()[0].GetChildren()[0]
            self.assertEqual(
                get_button_strings(image_grid_control),
                ['top left', 'top right', 'bottom left', 'bottom right']
            )

            # Select new image
            click_on_image(get_button_control(image_grid_control, 1))
            gui.process_events()

            self.assertEqual(enum_edit.value, 'top right')
            self.assertEqual(
                patched_cache.call_args[0][0], "@icons:top right_origin"
            )

            # Check that dialog window is closed
            self.assertEqual(list(control.GetChildren()), [])

    @skip_if_not_qt4
    @patch(cache_to_patch, wraps=image_cache)
    def test_simple_editor_combobox(self, patched_cache):
        enum_edit = EnumModel()

        with store_exceptions_on_all_threads():
            gui, combobox = self.setup_gui(enum_edit, get_view("simple"))

            self.assertEqual(enum_edit.value, 'top left')
            self.assertEqual(
                patched_cache.call_args[0][0], "@icons:top left_origin"
            )

            # Smoke test for ImageEnumItemDelegate painting
            combobox.showPopup()
            gui.process_events()

            combobox.setCurrentIndex(1)
            combobox.hidePopup()
            gui.process_events()

            self.assertEqual(enum_edit.value, 'top right')
            self.assertEqual(
                patched_cache.call_args[0][0], "@icons:top right_origin"
            )


@skip_if_null
class TestCustomImageEnumEditor(unittest.TestCase):

    def setup_gui(self, model, view):
        gui = GUI()
        ui = model.edit_traits(view=view)
        self.addCleanup(ui.dispose)

        gui.process_events()
        editor = ui.get_editors("value")[0]
        control = editor.control

        return gui, control

    def test_custom_editor_more_cols(self):
        # Smoke test for setting up an editor with more than one column
        enum_edit = EnumModel()
        view = View(
            UItem(
                'value',
                editor=ImageEnumEditor(
                    values=[
                        'top left', 'top right', 'bottom left', 'bottom right'
                    ],
                    prefix='@icons:',
                    suffix='_origin',
                    path=os.getcwd(),
                    cols=4,
                ),
                style="custom",
            ),
            resizable=True,
        )

        with store_exceptions_on_all_threads():
            gui, combobox = self.setup_gui(enum_edit, view)

    def test_custom_editor_selection(self):
        enum_edit = EnumModel()

        with store_exceptions_on_all_threads():
            gui, control = self.setup_gui(enum_edit, get_view("custom"))
            self.assertEqual(
                get_button_strings(control),
                ['top left', 'top right', 'bottom left', 'bottom right']
            )

            self.assertEqual(enum_edit.value, 'top left')
            self.assertEqual(
                get_all_button_selected_status(control),
                [True, False, False, False]
            )

            click_on_image(get_button_control(control, 1))
            gui.process_events()

            self.assertEqual(enum_edit.value, 'top right')
            self.assertEqual(
                get_all_button_selected_status(control),
                [False, True, False, False]
            )

    def test_custom_editor_value_changed(self):
        enum_edit = EnumModel()

        with store_exceptions_on_all_threads():
            gui, control = self.setup_gui(enum_edit, get_view("custom"))
            self.assertEqual(
                get_button_strings(control),
                ['top left', 'top right', 'bottom left', 'bottom right']
            )

            self.assertEqual(enum_edit.value, 'top left')
            self.assertEqual(
                get_all_button_selected_status(control),
                [True, False, False, False]
            )

            enum_edit.value = 'top right'
            gui.process_events()

            self.assertEqual(
                get_all_button_selected_status(control),
                [False, True, False, False]
            )


@skip_if_null
class TestReadOnlyImageEnumEditor(unittest.TestCase):

    def setup_gui(self, model, view):
        gui = GUI()
        ui = model.edit_traits(view=view)
        self.addCleanup(ui.dispose)

        gui.process_events()
        editor = ui.get_editors("value")[0]
        control = editor.control

        return gui, control

    @patch(cache_to_patch, wraps=image_cache)
    def test_readonly_editor_value_changed(self, patched_cache):
        enum_edit = EnumModel()

        with store_exceptions_on_all_threads():
            gui, control = self.setup_gui(enum_edit, get_view("readonly"))

            self.assertEqual(enum_edit.value, 'top left')
            self.assertEqual(
                patched_cache.call_args[0][0], "@icons:top left_origin"
            )

            enum_edit.value = 'top right'
            gui.process_events()

            self.assertEqual(
                patched_cache.call_args[0][0], "@icons:top right_origin"
            )
