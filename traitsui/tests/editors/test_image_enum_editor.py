# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import contextlib
import sys
import unittest
from unittest.mock import patch

from traits.api import Enum, HasTraits, List
from traitsui.api import ImageEnumEditor, UItem, View
from traitsui.tests._tools import (
    BaseTestMixin,
    create_ui,
    is_qt,
    is_wx,
    process_cascade_events,
    requires_toolkit,
    reraise_exceptions,
    ToolkitName,
)

# Import needed bitmap/pixmap cache and prepare for patching
if is_wx():
    from traitsui.wx.helper import bitmap_cache as image_cache

    cache_to_patch = "traitsui.wx.image_enum_editor.bitmap_cache"
elif is_qt():
    from traitsui.qt.helper import pixmap_cache as image_cache

    cache_to_patch = "traitsui.qt.image_enum_editor.pixmap_cache"

is_linux = sys.platform == 'linux'


class EnumModel(HasTraits):

    value = Enum('top left', 'top right', 'bottom left', 'bottom right')


def get_view(style):
    return View(
        UItem(
            'value',
            editor=ImageEnumEditor(
                values=[
                    'top left',
                    'top right',
                    'bottom left',
                    'bottom right',
                ],
                prefix='@icons:',
                suffix='_origin',
                path='dummy_path',
            ),
            style=style,
        ),
        resizable=True,
    )


def click_on_image(image_control):
    """Click on the image controlled by given image_control."""
    if is_wx():
        import wx

        event_down = wx.MouseEvent(wx.EVT_LEFT_DOWN.typeId)
        wx.PostEvent(image_control, event_down)
        event_up = wx.MouseEvent(wx.EVT_LEFT_UP.typeId)
        event_up.SetX(0)
        event_up.SetY(0)
        wx.PostEvent(image_control, event_up)

    elif is_qt():
        image_control.click()

    else:
        raise unittest.SkipTest("Test not implemented for this toolkit")


def get_button_strings(control):
    """Return the list of strings associated with the buttons under given
    control. Assumes all sizer children (wx) or layout items (qt) are buttons.
    """
    button_strings = []

    if is_wx():
        for item in control.GetSizer().GetChildren():
            button = item.GetWindow()
            button_strings.append(button.value)

    elif is_qt():
        layout = control.layout()
        for i in range(layout.count()):
            button = layout.itemAt(i).widget()
            button_strings.append(button.value)

    else:
        raise unittest.SkipTest("Test not implemented for this toolkit")

    return button_strings


def get_all_button_selected_status(control):
    """Return a list with selected (wx) or checked (qt) button status under
    given control. Assumes all sizer children (wx) or layout items (qt) are
    buttons.
    """
    button_status = []

    if is_wx():
        for item in control.GetSizer().GetChildren():
            button_status.append(item.GetWindow().Selected())

    elif is_qt():
        layout = control.layout()
        for i in range(layout.count()):
            button_status.append(layout.itemAt(i).widget().isChecked())

    else:
        raise unittest.SkipTest("Test not implemented for this toolkit")

    return button_status


def get_button_control(control, button_idx):
    """Get button control from a specified parent control given a button index.
    Assumes all sizer children (wx) or layout items (qt) are buttons.
    """
    if is_wx():
        return control.GetSizer().GetChildren()[button_idx].GetWindow()

    elif is_qt():
        return control.layout().itemAt(button_idx).widget()

    else:
        raise unittest.SkipTest("Test not implemented for this toolkit")


@requires_toolkit([ToolkitName.qt])
class TestImageEnumEditorMapping(BaseTestMixin, unittest.TestCase):
    def setUp(self):
        BaseTestMixin.setUp(self)

    def tearDown(self):
        BaseTestMixin.tearDown(self)

    @contextlib.contextmanager
    def setup_ui(self, model, view):
        with create_ui(model, dict(view=view)) as ui:
            yield ui.get_editors("value")[0]

    def check_enum_mappings_value_change(self, style):

        image_enum_editor_factory = ImageEnumEditor(
            values=['top left', 'top right'],
            format_func=lambda v: v.upper(),
            prefix='@icons:',
            suffix='_origin',
            path='dummy_path',
        )
        formatted_view = View(
            UItem(
                "value",
                editor=image_enum_editor_factory,
                style=style,
            )
        )

        with reraise_exceptions(), self.setup_ui(
            EnumModel(), formatted_view
        ) as editor:

            self.assertEqual(editor.names, ["TOP LEFT", "TOP RIGHT"])
            self.assertEqual(
                editor.mapping,
                {"TOP LEFT": "top left", "TOP RIGHT": "top right"},
            )
            self.assertEqual(
                editor.inverse_mapping,
                {"top left": "TOP LEFT", "top right": "TOP RIGHT"},
            )

            image_enum_editor_factory.values = ["top right", "top left"]

            self.assertEqual(editor.names, ["TOP RIGHT", "TOP LEFT"])
            self.assertEqual(
                editor.mapping,
                {"TOP RIGHT": "top right", "TOP LEFT": "top left"},
            )
            self.assertEqual(
                editor.inverse_mapping,
                {"top right": "TOP RIGHT", "top left": "TOP LEFT"},
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
                    path='dummy_path',
                ),
                style=style,
            )
        )
        model = PossibleEnumModel()

        with reraise_exceptions(), self.setup_ui(
            model, formatted_view
        ) as editor:

            self.assertEqual(editor.names, ["TOP LEFT", "TOP RIGHT"])
            self.assertEqual(
                editor.mapping,
                {"TOP LEFT": "top left", "TOP RIGHT": "top right"},
            )
            self.assertEqual(
                editor.inverse_mapping,
                {"top left": "TOP LEFT", "top right": "TOP RIGHT"},
            )

            model.possible_values = ["top right", "top left"]

            self.assertEqual(editor.names, ["TOP RIGHT", "TOP LEFT"])
            self.assertEqual(
                editor.mapping,
                {"TOP RIGHT": "top right", "TOP LEFT": "top left"},
            )
            self.assertEqual(
                editor.inverse_mapping,
                {"top right": "TOP RIGHT", "top left": "TOP LEFT"},
            )

    def test_simple_editor_mapping_values(self):
        self.check_enum_mappings_value_change("simple")

    def test_simple_editor_mapping_name(self):
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
                    path='dummy_path',
                ),
                style="readonly",
            )
        )
        model = PossibleEnumModel()

        with reraise_exceptions(), self.setup_ui(
            model, formatted_view
        ) as editor:

            # Readonly editor doesn't set up full mapping, only check that
            # str_value is mapped as expected
            self.assertEqual(model.value, "top left")
            self.assertEqual(editor.str_value, "TOP LEFT")


class TestSimpleImageEnumEditor(BaseTestMixin, unittest.TestCase):
    def setUp(self):
        BaseTestMixin.setUp(self)

    def tearDown(self):
        BaseTestMixin.tearDown(self)

    @contextlib.contextmanager
    def setup_gui(self, model, view):
        with create_ui(model, dict(view=view)) as ui:
            process_cascade_events()
            yield ui.get_editors("value")[0]

    @requires_toolkit([ToolkitName.qt, ToolkitName.wx])
    def test_simple_editor_more_cols(self):
        # Smoke test for setting up an editor with more than one column
        enum_edit = EnumModel()
        view = View(
            UItem(
                'value',
                editor=ImageEnumEditor(
                    values=[
                        'top left',
                        'top right',
                        'bottom left',
                        'bottom right',
                    ],
                    prefix='@icons:',
                    suffix='_origin',
                    path='dummy_path',
                    cols=4,
                ),
                style="simple",
            ),
            resizable=True,
        )

        with reraise_exceptions():
            self.setup_gui(enum_edit, view)

    @requires_toolkit([ToolkitName.wx])
    def test_simple_editor_popup_editor(self):
        enum_edit = EnumModel()

        with reraise_exceptions(), self.setup_gui(
            enum_edit, get_view("simple")
        ) as editor:

            self.assertEqual(enum_edit.value, 'top left')

            # Set up ImageEnumDialog
            click_on_image(editor.control)
            process_cascade_events()

            # Check created buttons
            image_grid_control = editor.control.GetChildren()[0].GetChildren()[
                0
            ]
            self.assertEqual(
                get_button_strings(image_grid_control),
                ['top left', 'top right', 'bottom left', 'bottom right'],
            )

            # Select new image
            click_on_image(get_button_control(image_grid_control, 1))
            process_cascade_events()

            self.assertEqual(enum_edit.value, 'top right')

            # Check that dialog window is closed
            self.assertEqual(list(editor.control.GetChildren()), [])

    @requires_toolkit([ToolkitName.qt])
    def test_simple_editor_combobox(self):
        enum_edit = EnumModel()

        with reraise_exceptions(), self.setup_gui(
            enum_edit, get_view("simple")
        ) as editor:

            self.assertEqual(enum_edit.value, 'top left')

            # Smoke test for ImageEnumItemDelegate painting
            editor.control.showPopup()
            process_cascade_events()

            editor.control.setCurrentIndex(1)
            editor.control.hidePopup()
            process_cascade_events()

            self.assertEqual(enum_edit.value, 'top right')


@requires_toolkit([ToolkitName.qt, ToolkitName.wx])
class TestCustomImageEnumEditor(BaseTestMixin, unittest.TestCase):
    def setUp(self):
        BaseTestMixin.setUp(self)

    def tearDown(self):
        BaseTestMixin.tearDown(self)

    @contextlib.contextmanager
    def setup_gui(self, model, view):
        with create_ui(model, dict(view=view)) as ui:
            process_cascade_events()
            yield ui.get_editors("value")[0]

    def test_custom_editor_more_cols(self):
        # Smoke test for setting up an editor with more than one column
        enum_edit = EnumModel()
        view = View(
            UItem(
                'value',
                editor=ImageEnumEditor(
                    values=[
                        'top left',
                        'top right',
                        'bottom left',
                        'bottom right',
                    ],
                    prefix='@icons:',
                    suffix='_origin',
                    path='dummy_path',
                    cols=4,
                ),
                style="custom",
            ),
            resizable=True,
        )

        with reraise_exceptions(), self.setup_gui(enum_edit, view):
            pass

    def test_custom_editor_selection(self):
        enum_edit = EnumModel()

        with reraise_exceptions(), self.setup_gui(
            enum_edit, get_view("custom")
        ) as editor:
            self.assertEqual(
                get_button_strings(editor.control),
                ['top left', 'top right', 'bottom left', 'bottom right'],
            )

            self.assertEqual(enum_edit.value, 'top left')
            self.assertEqual(
                get_all_button_selected_status(editor.control),
                [True, False, False, False],
            )

            click_on_image(get_button_control(editor.control, 1))
            process_cascade_events()

            self.assertEqual(enum_edit.value, 'top right')

    def test_custom_editor_value_changed(self):
        enum_edit = EnumModel()

        with reraise_exceptions(), self.setup_gui(
            enum_edit, get_view("custom")
        ) as editor:
            self.assertEqual(
                get_button_strings(editor.control),
                ['top left', 'top right', 'bottom left', 'bottom right'],
            )

            self.assertEqual(enum_edit.value, 'top left')
            self.assertEqual(
                get_all_button_selected_status(editor.control),
                [True, False, False, False],
            )

            enum_edit.value = 'top right'
            process_cascade_events()

            self.assertEqual(
                get_all_button_selected_status(editor.control),
                [False, True, False, False],
            )


@requires_toolkit([ToolkitName.qt, ToolkitName.wx])
class TestReadOnlyImageEnumEditor(BaseTestMixin, unittest.TestCase):
    def setUp(self):
        BaseTestMixin.setUp(self)

    def tearDown(self):
        BaseTestMixin.tearDown(self)

    def test_readonly_editor_value_changed(self):
        enum_edit = EnumModel()

        with reraise_exceptions():
            with patch(
                cache_to_patch, wraps=image_cache
            ) as patched_cache, create_ui(
                enum_edit, dict(view=get_view("readonly"))
            ):

                self.assertEqual(enum_edit.value, 'top left')
                self.assertEqual(
                    patched_cache.call_args[0][0], "@icons:top left_origin"
                )

                enum_edit.value = 'top right'
                process_cascade_events()

                self.assertEqual(
                    patched_cache.call_args[0][0], "@icons:top right_origin"
                )
