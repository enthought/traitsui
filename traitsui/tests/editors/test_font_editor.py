#  Copyright (c) 2005-2020, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
""" Test FontEditor
"""
import unittest

from traits.api import HasTraits
from traitsui.api import Font, Item, View
from traitsui.tests._tools import (
    is_wx,
    requires_toolkit,
    ToolkitName,
)
from traitsui.testing.tester import command
from traitsui.testing.tester.ui_tester import UITester
from traitsui.testing.tester.registry import TargetRegistry


class ObjectWithFont(HasTraits):
    font_trait = Font()


# A local registry of interaction handlers for testing purposes.
LOCAL_TARGET_REGISTRY = TargetRegistry()

if is_wx():
    from traitsui.wx.font_editor import TextEditor
    LOCAL_TARGET_REGISTRY.register_handler(
        target_class=TextEditor,
        interaction_class=command.MouseClick,
        handler=lambda wrapper, _: wrapper.target.control.SetFocus()
    )


@requires_toolkit([ToolkitName.wx])
class TestFontEditor(unittest.TestCase):

    def test_create_and_dispose_text_style(self):
        # Setting focus on the widget and then disposing the widget
        # should not cause errors.
        view = View(Item("font_trait", style="text"))
        tester = UITester([LOCAL_TARGET_REGISTRY])
        with tester.create_ui(ObjectWithFont(), dict(view=view)) as ui:
            wrapper = tester.find_by_name(ui, "font_trait")
            wrapper.perform(command.MouseClick())
