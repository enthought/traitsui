# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" This file provides tests for the demo of the same name located in the
directory one level up.
"""
import os
import runpy
import unittest

#: Filename of the demo script
FILENAME = "Image_editor_demo.py"

#: Path of the demo script
DEMO_PATH = os.path.join(os.path.dirname(__file__), "..", FILENAME)


class TestImageEditorDemo(unittest.TestCase):
    def test_image_path_exists(self):
        (search_path,) = runpy.run_path(DEMO_PATH)["search_path"]
        self.assertTrue(os.path.exists(search_path))


# Run the test(s)
unittest.TextTestRunner().run(
    unittest.TestLoader().loadTestsFromTestCase(TestImageEditorDemo)
)
