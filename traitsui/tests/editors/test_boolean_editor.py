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

from traits.api import HasTraits, Bool
from traitsui.api import BooleanEditor, Item, View
from traitsui.tests._tools import (
    BaseTestMixin,
    requires_toolkit,
    ToolkitName,
)

from traitsui.testing.api import (
    DisplayedText,
    IsChecked,
    KeyClick,
    KeySequence,
    MouseClick,
    UITester,
)


class BoolModel(HasTraits):

    true_or_false = Bool()


# Run this against wx once enthought/traitsui#752 is also fixed for
# BooleanEditor
@requires_toolkit([ToolkitName.qt, ToolkitName.wx])
class TestBooleanEditor(BaseTestMixin, unittest.TestCase):
    def setUp(self):
        BaseTestMixin.setUp(self)

    def tearDown(self):
        BaseTestMixin.tearDown(self)

    def check_click_boolean_changes_trait(self, style):
        view = View(Item("true_or_false", style=style, editor=BooleanEditor()))
        obj = BoolModel()

        tester = UITester()
        with tester.create_ui(obj, dict(view=view)) as ui:
            # sanity check
            self.assertEqual(obj.true_or_false, False)
            checkbox = tester.find_by_name(ui, "true_or_false")
            checkbox.perform(MouseClick())
            self.assertEqual(obj.true_or_false, True)

    def test_click_boolean_changes_trait_simple(self):
        self.check_click_boolean_changes_trait('simple')

    def test_click_boolean_changes_trait_custom(self):
        self.check_click_boolean_changes_trait('custom')

    def test_change_text_boolean_changes_trait(self):
        view = View(Item("true_or_false", style='text'))
        obj = BoolModel()

        tester = UITester()
        with tester.create_ui(obj, dict(view=view)) as ui:
            self.assertEqual(obj.true_or_false, False)
            text_field = tester.find_by_name(ui, 'true_or_false')
            for _ in range(5):
                text_field.perform(KeyClick("Backspace"))
            text_field.perform(KeySequence("True"))
            text_field.perform(KeyClick("Enter"))
            self.assertEqual(obj.true_or_false, True)

    def check_trait_change_shown_in_gui(self, style):
        view = View(Item("true_or_false", style=style))
        obj = BoolModel()

        tester = UITester()
        with tester.create_ui(obj, dict(view=view)) as ui:
            checkbox = tester.find_by_name(ui, "true_or_false")
            checked = checkbox.inspect(IsChecked())
            # sanity check
            self.assertEqual(checked, False)
            obj.true_or_false = True
            checked = checkbox.inspect(IsChecked())
            self.assertEqual(checked, True)

    def test_trait_change_shown_in_gui_simple(self):
        self.check_trait_change_shown_in_gui('simple')

    def test_trait_change_shown_in_gui_custom(self):
        self.check_trait_change_shown_in_gui('custom')

    def test_trait_change_shown_in_gui_readonly(self):
        view = View(Item("true_or_false", style='readonly'))
        obj = BoolModel()

        tester = UITester()
        with tester.create_ui(obj, dict(view=view)) as ui:
            readonly = tester.find_by_name(ui, "true_or_false")
            displayed = readonly.inspect(DisplayedText())
            # sanity check
            self.assertEqual(displayed, 'False')
            obj.true_or_false = True
            displayed = readonly.inspect(DisplayedText())
            self.assertEqual(displayed, 'True')

    def test_trait_change_shown_in_gui_text(self):
        view = View(Item("true_or_false", style='text'))
        obj = BoolModel()

        tester = UITester()
        with tester.create_ui(obj, dict(view=view)) as ui:
            text_field = tester.find_by_name(ui, "true_or_false")
            displayed = text_field.inspect(DisplayedText())
            # sanity check
            self.assertEqual(displayed, 'False')
            obj.true_or_false = True
            displayed = text_field.inspect(DisplayedText())
            self.assertEqual(displayed, 'True')
