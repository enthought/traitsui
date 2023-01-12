# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Test FontEditor
"""
import unittest

from traits.api import HasTraits
from traitsui.api import Font, Item, View
from traitsui.tests._tools import (
    requires_toolkit,
    ToolkitName,
)
from traitsui.testing.api import MouseClick, UITester


class ObjectWithFont(HasTraits):
    font_trait = Font()


@requires_toolkit([ToolkitName.qt, ToolkitName.wx])
class TestFontEditor(unittest.TestCase):
    def test_create_and_dispose_text_style(self):
        # Setting focus on the widget and then disposing the widget
        # should not cause errors.
        view = View(Item("font_trait", style="text"))
        tester = UITester()
        with tester.create_ui(ObjectWithFont(), dict(view=view)) as ui:
            wrapper = tester.find_by_name(ui, "font_trait")
            wrapper.perform(MouseClick())
