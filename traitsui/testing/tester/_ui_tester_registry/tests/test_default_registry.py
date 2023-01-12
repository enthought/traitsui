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

from traitsui.testing.tester._abstract_target_registry import (
    AbstractTargetRegistry,
)
from traitsui.testing.tester._ui_tester_registry.default_registry import (
    get_default_registries,
)


class TestDefaultRegistry(unittest.TestCase):
    def test_load_default_registries(self):
        registries = get_default_registries()
        for registry in registries:
            self.assertIsInstance(registry, AbstractTargetRegistry)

        self.assertGreaterEqual(len(registries), 1)
