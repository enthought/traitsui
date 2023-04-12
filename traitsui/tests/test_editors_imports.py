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


class TestEditorsImports(unittest.TestCase):

    def test_editors_import_warns(self):
        # Importing from traitsui.editors is deprecated
        with self.assertWarns(DeprecationWarning):
            from traitsui.editors import BooleanEditor
