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

from traits.api import Directory, Event, HasTraits
from traitsui.api import DirectoryEditor, Item, View
from traitsui.testing.api import DisplayedText, KeyClick, KeySequence, UITester
from traitsui.tests._tools import (
    BaseTestMixin,
    requires_toolkit,
    ToolkitName,
)


class DirectoryModel(HasTraits):

    dir_path = Directory()

    reload_event = Event()


# Run this against wx too when enthought/traitsui#752 is also fixed.
@requires_toolkit([ToolkitName.qt])
class TestDirectoryEditor(BaseTestMixin, unittest.TestCase):
    """Test DirectoryEditor."""

    def setUp(self):
        BaseTestMixin.setUp(self)

    def tearDown(self):
        BaseTestMixin.tearDown(self)

    def check_init_and_dispose(self, style):
        # Test init and dispose by opening and closing the UI
        view = View(Item("dir_path", editor=DirectoryEditor(), style=style))
        obj = DirectoryModel()
        with UITester().create_ui(obj, dict(view=view)):
            pass

    def test_simple_editor_init_and_dispose(self):
        # This may fail on wx, see enthought/traitsui#889
        self.check_init_and_dispose("simple")

    def test_custom_editor_init_and_dispose(self):
        self.check_init_and_dispose("custom")

    def test_custom_editor_reload_changed_after_dispose(self):
        # Test firing reload event on the model after the UI is disposed.
        view = View(
            Item(
                "dir_path",
                editor=DirectoryEditor(reload_name="reload_event"),
                style="custom",
            ),
        )
        obj = DirectoryModel()
        with UITester().create_ui(obj, dict(view=view)):
            pass
        # should not fail.
        obj.reload_event = True

    # Behavior on wx may not be quite the same on other platforms.
    @requires_toolkit([ToolkitName.qt])
    def test_simple_editor_set_text_to_nonexisting_path(self):
        # Test setting the editor to a nonexisting dirpath
        # e.g. use case for creating a new file.
        view = View(Item("dir_path", editor=DirectoryEditor()))
        obj = DirectoryModel()
        tester = UITester()
        with tester.create_ui(obj, dict(view=view)) as ui:
            dirpath_field = tester.find_by_name(ui, "dir_path")

            dirpath_field.perform(KeySequence("some_dir"))
            dirpath_field.perform(KeyClick("Enter"))

            self.assertEqual(obj.dir_path, "some_dir")

    def test_simple_editor_display_path(self):
        # Test the filepath widget is updated to show path
        view = View(Item("dir_path", editor=DirectoryEditor()))
        obj = DirectoryModel()
        tester = UITester()
        with tester.create_ui(obj, dict(view=view)) as ui:
            dirpath_field = tester.find_by_name(ui, "dir_path")
            self.assertEqual(dirpath_field.inspect(DisplayedText()), "")

            obj.dir_path = "some_dir"
            self.assertEqual(
                dirpath_field.inspect(DisplayedText()), "some_dir"
            )

    # Behavior on wx may not be quite the same on other platforms.
    @requires_toolkit([ToolkitName.qt])
    def test_simple_editor_auto_set_text(self):
        # Test with auto_set set to True.
        view = View(Item("dir_path", editor=DirectoryEditor(auto_set=True)))
        obj = DirectoryModel()
        tester = UITester()
        with tester.create_ui(obj, dict(view=view)) as ui:
            dirpath_field = tester.find_by_name(ui, "dir_path")
            dirpath_field.perform(KeySequence("some_dir"))
            self.assertEqual(obj.dir_path, "some_dir")
