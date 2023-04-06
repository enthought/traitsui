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

from traits.api import Any, Dict, HasTraits, Str
from traitsui.api import Item, ShellEditor, View
from traitsui.testing.api import UITester
from traitsui.tests._tools import (
    BaseTestMixin,
    requires_toolkit,
    ToolkitName,
)


class ShellTest(HasTraits):
    locals_str = Str()
    locals_dict = Dict(Str, Any)


def get_str_view(share=False):
    return View(
        Item(
            "locals_str",
            editor=ShellEditor(share=share),
        )
    )


def get_dict_view(share=False):
    return View(
        Item(
            "locals_dict",
            editor=ShellEditor(share=share),
        )
    )


@requires_toolkit([ToolkitName.qt, ToolkitName.wx])
class TestShellEditor(BaseTestMixin, unittest.TestCase):

    def setUp(self):
        BaseTestMixin.setUp(self)

    def tearDown(self):
        BaseTestMixin.tearDown(self)

    def smoke_test(self, locals_type, share):
        shell_test = ShellTest()
        tester = UITester()
        if locals_type == "str":
            with tester.create_ui(shell_test, dict(view=get_str_view(share))):
                pass
        else:
            with tester.create_ui(shell_test, dict(view=get_dict_view(share))):
                pass

    def test_no_share_dict(self):
        self.smoke_test("dict", False)

    def test_share_dict(self):
        self.smoke_test("dict", True)

    def test_no_share_str(self):
        self.smoke_test("str", False)

    def test_share_str(self):
        self.smoke_test("str", True)
