# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Tests for QWidget's DynamicTargetRegistry """

import unittest

from traitsui.testing.api import IsEnabled, IsVisible
from traitsui.testing.tester.exceptions import (
    LocationNotSupported,
)
from traitsui.testing.tester.ui_wrapper import UIWrapper
from traitsui.tests._tools import (
    is_qt,
    requires_toolkit,
    ToolkitName,
)

try:
    from pyface.qt import QtGui
except ImportError:
    if is_qt():
        raise
else:
    from traitsui.testing.tester._ui_tester_registry.qt._control_widget_registry import (  # noqa: E501
        get_widget_registry,
    )


class TargetWithControl:
    """An object holding a control attribute."""

    def __init__(self, control):
        self.control = control


@requires_toolkit([ToolkitName.qt])
class TestQtControlWidgetRegistry(unittest.TestCase):
    """Test the interface of AbstractTargetRegistry for QWidget's registry"""

    def setUp(self):
        self.widget = QtGui.QWidget()
        self.registry = get_widget_registry()
        self.target = TargetWithControl(self.widget)
        self.good_wrapper = UIWrapper(
            target=self.target,
            registries=[self.registry],
        )

    def test_is_enabled(self):
        self.assertTrue(self.good_wrapper.inspect(IsEnabled()))

    def test_is_disabled(self):
        self.widget.setEnabled(False)
        self.assertFalse(self.good_wrapper.inspect(IsEnabled()))

    def test_is_visible(self):
        self.widget.setVisible(True)
        self.assertTrue(self.good_wrapper.inspect(IsVisible()))

    def test_is_invisible(self):
        self.widget.setVisible(False)
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

    def test__get_locations(self):
        self.assertEqual(self.registry._get_locations(self.target), set())

    def test_error_get_location_doc(self):
        with self.assertRaises(LocationNotSupported):
            self.registry._get_location_doc(self.target, None)
