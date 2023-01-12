# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import unittest
from unittest import mock

from pyface.api import OK
from traits.api import Event, File, HasTraits

from traitsui.api import FileEditor, Item, View
from traitsui.tests._tools import (
    BaseTestMixin,
    requires_toolkit,
    ToolkitName,
)
from traitsui.testing.api import DisplayedText, KeyClick, KeySequence, UITester


class FileModel(HasTraits):

    filepath = File()

    reload_event = Event()

    existing_filepath = File(exists=True)


def trait_set_side_effect(**traits):

    def side_effect(self, *args, **kwargs):
        self.trait_set(**traits)
        return mock.DEFAULT

    return side_effect


@requires_toolkit([ToolkitName.qt, ToolkitName.wx])
class TestSimpleFileEditor(BaseTestMixin, unittest.TestCase):
    """Test FileEditor (simple style)."""

    def setUp(self):
        BaseTestMixin.setUp(self)

    def tearDown(self):
        BaseTestMixin.tearDown(self)

    # Behavior on wx may not be quite the same on other platforms.
    @requires_toolkit([ToolkitName.qt])
    def test_simple_editor_set_text_to_nonexisting_path(self):
        # Test setting the editor to a nonexisting filepath
        # e.g. use case for creating a new file.
        view = View(Item("filepath", editor=FileEditor()))
        obj = FileModel()
        tester = UITester()
        with tester.create_ui(obj, dict(view=view)) as ui:
            filepath_field = tester.find_by_name(ui, "filepath")

            filepath_field.perform(KeySequence("some_file.txt"))
            filepath_field.perform(KeyClick("Enter"))

            self.assertEqual(obj.filepath, "some_file.txt")

    def test_simple_editor_display_path(self):
        # Test the filepath widget is updated to show path
        view = View(Item("filepath", editor=FileEditor()))
        obj = FileModel()
        tester = UITester()
        with tester.create_ui(obj, dict(view=view)) as ui:
            filepath_field = tester.find_by_name(ui, "filepath")
            self.assertEqual(filepath_field.inspect(DisplayedText()), "")

            obj.filepath = "some_file.txt"
            self.assertEqual(
                filepath_field.inspect(DisplayedText()), "some_file.txt"
            )

    # Behavior on wx may not be quite the same on other platforms.
    @requires_toolkit([ToolkitName.qt])
    def test_simple_editor_auto_set_text(self):
        # Test with auto_set set to True.
        view = View(Item("filepath", editor=FileEditor(auto_set=True)))
        obj = FileModel()
        tester = UITester()
        with tester.create_ui(obj, dict(view=view)) as ui:
            filepath_field = tester.find_by_name(ui, "filepath")
            filepath_field.perform(KeySequence("some_file.txt"))
            self.assertEqual(obj.filepath, "some_file.txt")

    def test_simple_editor_reset_text_if_validation_error(self):
        # Test when the trait validates file existence.
        view = View(Item("existing_filepath", editor=FileEditor()))
        obj = FileModel()
        tester = UITester()
        with tester.create_ui(obj, dict(view=view)) as ui:
            filepath_field = tester.find_by_name(ui, "existing_filepath")

            # when
            filepath_field.perform(KeySequence("some_file.txt"))
            filepath_field.perform(KeyClick("Enter"))

            # then
            # the file does not exist, the trait is not set.
            self.assertEqual(obj.existing_filepath, "")

            # the widget is synchronized to the trait value.
            self.assertEqual(filepath_field.inspect(DisplayedText()), "")

    @mock.patch(
        "pyface.api.FileDialog.open",
        autospec=True,
        side_effect=trait_set_side_effect(
            return_code=OK,
            path="some_file.txt",
        ),
    )
    def test_show_file_dialog(self, mock_open):
        view = View(Item("filepath", editor=FileEditor()))
        obj = FileModel()
        tester = UITester()
        with tester.create_ui(obj, dict(view=view)) as ui:
            editor = ui.get_editors("filepath")[0]
            editor.show_file_dialog()

            self.assertEqual(editor.value, "some_file.txt")

    @mock.patch(
        "pyface.api.FileDialog.open",
        autospec=True,
        side_effect=trait_set_side_effect(
            return_code=OK,
            path="some_file.txt",
        ),
    )
    def test_show_file_dialog_truncate_ext(self, mock_open):
        view = View(Item("filepath", editor=FileEditor(truncate_ext=True)))
        obj = FileModel()
        tester = UITester()
        with tester.create_ui(obj, dict(view=view)) as ui:
            editor = ui.get_editors("filepath")[0]
            editor.show_file_dialog()

            self.assertEqual(editor.value, "some_file")


# Run this against wx too when enthought/traitsui#752 is also fixed.
@requires_toolkit([ToolkitName.qt])
class TestCustomFileEditor(BaseTestMixin, unittest.TestCase):
    """Test FileEditor (custom style)."""

    def setUp(self):
        BaseTestMixin.setUp(self)

    def tearDown(self):
        BaseTestMixin.tearDown(self)

    def test_custom_editor_init_and_dispose(self):
        # Test init and dispose by opening and closing the UI
        view = View(Item("filepath", editor=FileEditor(), style="custom"))
        obj = FileModel()
        with UITester().create_ui(obj, dict(view=view)):
            pass

    def test_custom_editor_reload_changed_after_dispose(self):
        # Test firing reload event on the model after the UI is disposed.
        view = View(
            Item(
                "filepath",
                editor=FileEditor(reload_name="reload_event"),
                style="custom",
            ),
        )
        obj = FileModel()
        with UITester().create_ui(obj, dict(view=view)):
            pass
        # should not fail.
        obj.reload_event = True
