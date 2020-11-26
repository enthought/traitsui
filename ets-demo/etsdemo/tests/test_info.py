# (C) Copyright 2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Test the EAM app metadata.
"""

import os
import subprocess
import unittest

try:
    import eam   # noqa: #F401
except ImportError:
    EAM_EXISTS = False
else:
    EAM_EXISTS = True

from etsdemo.info import info


class TestInfoForEAM(unittest.TestCase):

    @unittest.skipUnless(EAM_EXISTS, "eam is not available.")
    def test_etsdemo_info(self):
        output = subprocess.check_output(
            ["eam", "info"],
        )
        output = output.decode("utf-8")
        self.assertIn("etsdemo", output)

    def test_etsdemo_icon_exists(self):
        metadata = info()
        command, = metadata["commands"]
        icon = command["icon"]
        self.assertTrue(
            os.path.exists(icon), "Expected icon file to exist. Not found."
        )
