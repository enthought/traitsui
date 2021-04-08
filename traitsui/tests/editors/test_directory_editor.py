# (C) Copyright 2004-2021 Enthought, Inc., Austin, TX
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
from traitsui.tests._tools import (
    BaseTestMixin,
    create_ui,
    requires_toolkit,
    reraise_exceptions,
    ToolkitName,
)


class DirectoryModel(HasTraits):

    dir_path = Directory()

    reload_event = Event()


# Run this against wx too when enthought/traitsui#752 is also fixed.
@requires_toolkit([ToolkitName.qt])
class TestDirectoryEditor(BaseTestMixin, unittest.TestCase):
    """ Test DirectoryEditor. """

    def setUp(self):
        BaseTestMixin.setUp(self)

    def tearDown(self):
        BaseTestMixin.tearDown(self)

    def check_init_and_dispose(self, style):
        # Test init and dispose by opening and closing the UI
        view = View(Item("dir_path", editor=DirectoryEditor(), style=style))
        obj = DirectoryModel()
        with reraise_exceptions(), \
                create_ui(obj, dict(view=view)):
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
        with reraise_exceptions():
            with create_ui(obj, dict(view=view)):
                pass
            # should not fail.
            obj.reload_event = True
