# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Tests for wx.Window's DynamicTargetRegistry
"""

import unittest

from traitsui.testing.api import IsEnabled, IsVisible
from traitsui.testing.tester.exceptions import (
    LocationNotSupported,
)
from traitsui.testing.tester.ui_wrapper import UIWrapper
from traitsui.tests._tools import (
    is_wx,
    requires_toolkit,
    ToolkitName,
)

try:
    import wx
except ImportError:
    if is_wx():
        raise
else:
    from traitsui.testing.tester._ui_tester_registry.wx._control_widget_registry import (  # noqa: E501
        get_widget_registry,
    )


class TargetWithControl:
    """An object holding a control attribute."""

    def __init__(self, control):
        self.control = control


@requires_toolkit([ToolkitName.wx])
class TestWxControlWidgetRegistry(unittest.TestCase):
    def setUp(self):
        self.widget = wx.Window()
        self.registry = get_widget_registry()
        self.target = TargetWithControl(self.widget)
        self.good_wrapper = UIWrapper(
            target=self.target,
            registries=[self.registry],
        )

    def test_is_enabled(self):
        self.widget.Enable(True)
        self.assertTrue(self.good_wrapper.inspect(IsEnabled()))

    def test_is_visible(self):
        self.widget.Show(True)
        self.assertTrue(self.good_wrapper.inspect(IsVisible()))

    def test_is_invisible(self):
        self.widget.Hide()
        self.assertFalse(self.good_wrapper.inspect(IsVisible()))

    def test_get_interactions_good_target(self):
        self.assertEqual(
            self.registry._get_interactions(self.target),
            set([IsEnabled, IsVisible]),
        )

    def test_get_interactions_bad_target(self):
        self.assertEqual(self.registry._get_interactions(None), set())

    def test_get_interaction_doc(self):
        self.assertGreater(
            len(self.registry._get_interaction_doc(self.target, IsEnabled)), 0
        )
        self.assertGreater(
            len(self.registry._get_interaction_doc(self.target, IsVisible)), 0
        )

    def test_get_location_solver(self):
        # There are currently no solvers
        with self.assertRaises(LocationNotSupported):
            self.registry._get_solver(self.target, None)

    def test_get_locations(self):
        self.assertEqual(self.registry._get_locations(self.target), set())

    def test_error_get_location_doc(self):
        with self.assertRaises(LocationNotSupported):
            self.registry._get_location_doc(self.target, None)
