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


class TestShellEditor(BaseTestMixin, unittest.TestCase):

    def setUp(self):
        BaseTestMixin.setUp(self)

    def tearDown(self):
        BaseTestMixin.tearDown(self)

    def test_no_share_dict(self):
        shell_test = ShellTest()
        tester = UITester()
        with tester.create_ui(shell_test, dict(view=get_dict_view())):
            pass

    def test_share_dict(self):
        shell_test = ShellTest()
        tester = UITester()
        with tester.create_ui(shell_test, dict(view=get_dict_view(True))):
            pass

    def test_no_share_str(self):
        shell_test = ShellTest()
        tester = UITester()
        with tester.create_ui(shell_test, dict(view=get_str_view())):
            pass

    def test_share_str(self):
        shell_test = ShellTest()
        tester = UITester()
        with tester.create_ui(shell_test, dict(view=get_str_view(True))):
            pass
