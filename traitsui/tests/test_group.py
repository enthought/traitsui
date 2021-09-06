# (C) Copyright 2004-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

"""
Test cases for the UI object.
"""

import contextlib
import unittest
import unittest.mock

from pyface.api import GUI
from traits.api import Property
from traits.has_traits import HasTraits, HasStrictTraits
from traits.trait_types import Str, Int

from traitsui.basic_editor_factory import BasicEditorFactory
from traitsui.api import Group, Include, Item, spring, View
from traitsui.group import ShadowGroup
from traitsui.tests._tools import (
    BaseTestMixin,
    count_calls,
    create_ui,
    is_qt,
    is_wx,
    process_cascade_events,
    requires_toolkit,
    reraise_exceptions,
    ToolkitName,
)
from traitsui.toolkit import toolkit, toolkit_object


class BaseWithInclude(HasTraits):

    x = Str()

    traits_view = View(
        Include('included_group'),
    )

class SubclassWithInclude(BaseWithInclude):

    included_group = Group('x')


class TestGroup(BaseTestMixin, unittest.TestCase):

    def test_get_shadow_item(self):
        """
        Given a group with an item
        When get_shadow is called
        Then it returns a shadow group with the same item
        """
        item = Item('x')
        group = Group(item)
        ui = unittest.mock.Mock()

        result = group.get_shadow(ui)

        self.assertIsInstance(result, ShadowGroup)
        self.assertIs(result.shadow, group)
        self.assertEqual(len(result.content), 1)
        self.assertIs(result.content[0], item)
        self.assertEqual(result.groups, 0)
        ui.find.assert_not_called()

    def test_get_shadow_item_defined_when_true(self):
        """
        Given a group with an item that has defined_when evaluate to True
        When get_shadow is called
        Then it returns a shadow group with the same item
        """
        item = Item('x', defined_when="True")
        group = Group(item)
        ui = unittest.mock.Mock(**{'eval_when.return_value': True})

        result = group.get_shadow(ui)

        self.assertIsInstance(result, ShadowGroup)
        self.assertIs(result.shadow, group)
        self.assertEqual(len(result.content), 1)
        self.assertIs(result.content[0], item)
        self.assertEqual(result.groups, 0)
        ui.find.assert_not_called()
        ui.eval_when.assert_called_once()

    def test_get_shadow_item_defined_when_false(self):
        """
        Given a group with an item that has defined_when evaluate to False
        When get_shadow is called
        Then it returns a shadow group with no items
        """
        item = Item('x', defined_when="False")
        group = Group(item)
        ui = unittest.mock.Mock(**{'eval_when.return_value': False})

        result = group.get_shadow(ui)

        self.assertIsInstance(result, ShadowGroup)
        self.assertIs(result.shadow, group)
        self.assertEqual(len(result.content), 0)
        self.assertEqual(result.groups, 0)
        ui.find.assert_not_called()
        ui.eval_when.assert_called_once()

    def test_get_shadow_sub_group(self):
        """
        Given a group with a sub-group
        When get_shadow is called
        Then it returns a shadow group with a shadow group for the sub-group
        """
        sub_group = Group(Item('x'))
        group = Group(sub_group)
        ui = unittest.mock.Mock()

        result = group.get_shadow(ui)

        self.assertIsInstance(result, ShadowGroup)
        self.assertIs(result.shadow, group)
        self.assertEqual(len(result.content), 1)
        shadow_subgroup = result.content[0]
        self.assertIsInstance(shadow_subgroup, ShadowGroup)
        self.assertIs(shadow_subgroup.shadow, sub_group)
        self.assertEqual(result.groups, 1)
        ui.find.assert_not_called()

    def test_get_shadow_sub_group_defined_when_true(self):
        """
        Given a group with a sub-group that has defined_when evaluate to True
        When get_shadow is called
        Then it returns a shadow group with a shadow group for the sub-group
        """
        sub_group = Group(Item('x'), defined_when="True")
        group = Group(sub_group)
        ui = unittest.mock.Mock(**{'eval_when.return_value': True})

        result = group.get_shadow(ui)

        self.assertIsInstance(result, ShadowGroup)
        self.assertIs(result.shadow, group)
        self.assertEqual(len(result.content), 1)
        shadow_subgroup = result.content[0]
        self.assertIsInstance(shadow_subgroup, ShadowGroup)
        self.assertIs(shadow_subgroup.shadow, sub_group)
        self.assertEqual(result.groups, 1)
        ui.find.assert_not_called()
        ui.eval_when.assert_called_once()

    def test_get_shadow_sub_group_defined_when_false(self):
        """
        Given a group with a sub-group that has defined_when evaluate to False
        When get_shadow is called
        Then it returns a shadow group with a shadow group for the sub-group
        """
        sub_group = Group(Item('x'), defined_when="False")
        group = Group(sub_group)
        ui = unittest.mock.Mock(**{'eval_when.return_value': False})

        result = group.get_shadow(ui)

        self.assertIsInstance(result, ShadowGroup)
        self.assertIs(result.shadow, group)
        self.assertEqual(len(result.content), 0)
        self.assertEqual(result.groups, 0)
        ui.find.assert_not_called()
        ui.eval_when.assert_called_once()

    def test_get_shadow_include_none(self):
        """
        Given a group with an include and the include resolves to None
        When get_shadow is called
        Then it returns a shadow group with no content
        """
        group = Group(Include('test_include'))
        ui = unittest.mock.Mock(**{'find.return_value': None})

        result = group.get_shadow(ui)

        self.assertIsInstance(result, ShadowGroup)
        self.assertIs(result.shadow, group)
        self.assertEqual(len(result.content), 0)
        self.assertEqual(result.groups, 0)
        ui.find.assert_called_once()

    def test_get_shadow_include_item(self):
        """
        Given a group with an include and the include resolves to an item
        When get_shadow is called
        Then it returns a shadow group with the same item
        """
        include_group = Group(Include('test_include'))
        item = Item('x')
        ui = unittest.mock.Mock(**{'find.return_value': item})

        result = include_group.get_shadow(ui)

        self.assertIsInstance(result, ShadowGroup)
        self.assertIs(result.shadow, include_group)
        self.assertEqual(len(result.content), 1)
        self.assertIs(result.content[0], item)
        self.assertEqual(result.groups, 0)
        ui.find.assert_called_once()

    def test_get_shadow_include_sub_group(self):
        """
        Given a group with an include and the include resolves to a group
        When get_shadow is called
        Then it returns a shadow group with a shadow group for the sub-group
        """
        sub_group = Group(Item('x'))
        group = Group(Include('test_include'))
        ui = unittest.mock.Mock(**{'find.return_value': sub_group})

        result = group.get_shadow(ui)

        self.assertIsInstance(result, ShadowGroup)
        self.assertIs(result.shadow, group)
        self.assertEqual(len(result.content), 1)
        shadow_subgroup = result.content[0]
        self.assertIsInstance(shadow_subgroup, ShadowGroup)
        self.assertIs(shadow_subgroup.shadow, sub_group)
        self.assertEqual(result.groups, 1)
        ui.find.assert_called_once()

    def test_get_shadow_sub_group_defined_when_true(self):
        """
        Given a group with an include and the include resolves to a group
            that has defined_when evaluate to True
        When get_shadow is called
        Then it returns a shadow group with a shadow group for the sub-group
        """
        sub_group = Group(Item('x'), defined_when="True")
        group = Group(Include('test_include'))
        ui = unittest.mock.Mock(**{
            'find.return_value': sub_group,
            'eval_when.return_value': True,
        })

        result = group.get_shadow(ui)

        self.assertIsInstance(result, ShadowGroup)
        self.assertIs(result.shadow, group)
        self.assertEqual(len(result.content), 1)
        shadow_subgroup = result.content[0]
        self.assertIsInstance(shadow_subgroup, ShadowGroup)
        self.assertIs(shadow_subgroup.shadow, sub_group)
        self.assertEqual(result.groups, 1)
        ui.find.assert_called_once()
        ui.eval_when.assert_called_once()

    def test_get_shadow_sub_group_defined_when_false(self):
        """
        Given a group with an include and the include resolves to a group
            that has defined_when evaluate to True
        When get_shadow is called
        Then it returns a shadow group with a shadow group for the sub-group
        """
        sub_group = Group(Item('x'), defined_when="False")
        group = Group(Include('test_include'))
        ui = unittest.mock.Mock(**{
            'find.return_value': sub_group,
            'eval_when.return_value': False,
        })

        result = group.get_shadow(ui)

        self.assertIsInstance(result, ShadowGroup)
        self.assertIs(result.shadow, group)
        self.assertEqual(len(result.content), 0)
        self.assertEqual(result.groups, 0)
        ui.find.assert_called_once()
        ui.eval_when.assert_called_once()
