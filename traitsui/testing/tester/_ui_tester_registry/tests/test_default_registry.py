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

from traitsui.testing.tester._ui_tester_registry.default_registry import (
    get_default_registries
)
from traitsui.testing.api import TargetRegistry
from traitsui.tests._tools import is_null


class TestDefaultRegistry(unittest.TestCase):

    def test_load_default_registries(self):
        registry = get_default_registries()
        self.assertIsInstance(registry, TargetRegistry)
        if not is_null():
            self.assertGreaterEqual(
                len(registry._interaction_registry._target_to_key_to_value),
                1,
            )
