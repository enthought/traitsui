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

import unittest
import unittest.mock

from traitsui.api import Group, Include, Item
from traitsui.group import ShadowGroup
from traitsui.tests._tools import BaseTestMixin


class TestGroup(BaseTestMixin, unittest.TestCase):

    def test_get_shadow_item(self):
        """
        Given a group with an item
        When get_shadow is called
        Then it returns the group
        """
        item = Item('x')
        group = Group(item)
        ui = unittest.mock.Mock()

        result = group.get_shadow(ui)

        self.assertIs(result, group)
        ui.find.assert_not_called()

    def test_get_shadow_item_defined_when_true(self):
        """
        Given a group with an item that has defined_when evaluate to True
        When get_shadow is called
        Then it returns the group
        """
        item = Item('x', defined_when="True")
        group = Group(item)
        ui = unittest.mock.Mock(**{'eval_when.return_value': True})

        result = group.get_shadow(ui)

        self.assertIs(result, group)
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
        Then it returns the group
        """
        sub_group = Group(Item('x'))
        group = Group(sub_group)
        ui = unittest.mock.Mock()

        result = group.get_shadow(ui)

        self.assertIs(result, group)
        ui.find.assert_not_called()

    def test_get_shadow_sub_group_recurses(self):
        """
        Given a group with a sub-group
            which returns a ShadowGroup from get_shadow
        When get_shadow is called
        Then it returns a shadow group with a shadow group for the subgroup
        """
        sub_group = Group(Item('x', defined_when="False"))
        group = Group(sub_group)
        ui = unittest.mock.Mock(**{'eval_when.return_value': False})

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
        Then it returns the group.
        """
        sub_group = Group(Item('x'), defined_when="True")
        group = Group(sub_group)
        ui = unittest.mock.Mock(**{'eval_when.return_value': True})

        result = group.get_shadow(ui)

        self.assertIs(result, group)
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
        Then it returns a shadow group containing the subgroup
        """
        sub_group = Group(Item('x'))
        group = Group(Include('test_include'))
        ui = unittest.mock.Mock(**{'find.return_value': sub_group})

        result = group.get_shadow(ui)

        self.assertIsInstance(result, ShadowGroup)
        self.assertIs(result.shadow, group)
        self.assertEqual(len(result.content), 1)
        self.assertIs(result.content[0], sub_group)
        self.assertEqual(result.groups, 1)
        ui.find.assert_called_once()

    def test_get_shadow_include_sub_group_defined_when_true(self):
        """
        Given a group with an include and the include resolves to a group
            that has defined_when evaluate to True
        When get_shadow is called
        Then it returns a shadow group containing the subgroup
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
        self.assertIs(result.content[0], sub_group)
        self.assertEqual(result.groups, 1)
        ui.find.assert_called_once()
        ui.eval_when.assert_called_once()

    def test_get_shadow_include_sub_group_defined_when_false(self):
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

    def test_get_content_all_items(self):
        """
        Given a Group with only Items
        When get_content is called
        Then it returns the list of Items
        """
        item_x = Item('x')
        item_y = Item('y')
        group = Group(item_x, item_y)

        result = group.get_content()

        self.assertEqual(len(result), 2)
        self.assertIs(result[0], item_x)
        self.assertIs(result[1], item_y)

    def test_get_content_all_subgroups_allow_groups(self):
        """
        Given a Group with only Groups
        When get_content is called with allow_groups
        Then it returns the list of Groups
        """
        item_x = Item('x')
        group_x = Group(item_x)
        item_y = Item('y')
        group_y = Group(item_y)
        group = Group(group_x, group_y)

        result = group.get_content()

        self.assertEqual(len(result), 2)
        self.assertIs(result[0], group_x)
        self.assertIs(result[1], group_y)

    def test_get_content_mixed_allow_groups(self):
        """
        Given a Group with a mixture of Groups and Items
        When get_content is called with allow_groups
        Then it assembles runs of items into ShadowGroups
        """
        item_x = Item('x')
        group_x = Group(item_x)
        item_y = Item('y')
        group_y = Group(item_y)
        item_z = Item('z')
        group = Group(group_x, item_z, group_y)

        result = group.get_content()

        self.assertEqual(len(result), 3)
        self.assertIs(result[0], group_x)
        self.assertIsInstance(result[1], ShadowGroup)
        shadow_group_z = result[1]
        self.assertIs(shadow_group_z.shadow, group)
        self.assertEqual(len(shadow_group_z.content), 1)
        self.assertIs(shadow_group_z.content[0], item_z)
        self.assertIs(result[2], group_y)

    def test_get_content_mixed_allow_groups_layout_not_normal(self):
        """
        Given a Group with a mixture of Groups and Items and non-normal layout
        When get_content is called with allow_groups
        Then it returns the contents as-is
        """
        item_x = Item('x')
        group_x = Group(item_x)
        item_y = Item('y')
        group_y = Group(item_y)
        item_z = Item('z')
        group = Group(group_x, item_z, group_y, layout='tabbed')

        result = group.get_content()

        self.assertEqual(len(result), 3)
        self.assertIs(result[0], group_x)
        self.assertIs(result[1], item_z)
        self.assertIs(result[2], group_y)

    def test_get_content_all_subgroups_allow_groups_false(self):
        """
        Given a Group with only Groups
        When get_content is called with allow_groups False
        Then it returns the flattened list of items.
        """
        item_x = Item('x')
        group_x = Group(item_x)
        item_y = Item('y')
        group_y = Group(item_y)
        group = Group(group_x, group_y)

        result = group.get_content(False)

        self.assertEqual(len(result), 2)
        self.assertIs(result[0], item_x)
        self.assertIs(result[1], item_y)

    def test_get_content_mixed_allow_groups_false(self):
        """
        Given a Group with a mix of Groups and items
        When get_content is called with allow_groups False
        Then it returns the flattened list of items.
        """
        item_x = Item('x')
        group_x = Group(item_x)
        item_y = Item('y')
        group_y = Group(item_y)
        item_z = Item('z')
        group = Group(group_x, item_z, group_y)

        result = group.get_content(False)

        self.assertEqual(len(result), 3)
        self.assertIs(result[0], item_x)
        self.assertIs(result[1], item_z)
        self.assertIs(result[2], item_y)

    def test_groups_property(self):
        item_x = Item('x')
        group_x = Group(item_x)
        item_y = Item('y')
        group_y = Group(item_y)
        item_z = Item('z')
        group = Group(group_x, item_z, group_y)

        self.assertEqual(group.groups, 2)


class TestShadowGroup(BaseTestMixin, unittest.TestCase):

    def test_get_content_all_items(self):
        """
        Given a ShadowGroup with only Items
        When get_content is called
        Then it returns the list of Items
        """
        item_x = Item('x')
        item_y = Item('y')
        group = Group(item_x, item_y)
        shadow_group = ShadowGroup(
            shadow=group,
            content=group.content,
        )

        result = shadow_group.get_content()

        self.assertEqual(len(result), 2)
        self.assertIs(result[0], item_x)
        self.assertIs(result[1], item_y)

    def test_get_content_all_subgroups_allow_groups(self):
        """
        Given a ShadowGroup with only Groups and ShadowGroups
        When get_content is called with allow_groups
        Then it returns the list of Groups and ShadowGroups
        """
        item_x = Item('x')
        group_x = Group(item_x)
        shadow_group_x = ShadowGroup(
            shadow=group_x,
            content=group_x.content,
        )
        item_y = Item('y')
        group_y = Group(item_y)
        group = Group(group_x, group_y)
        shadow_group = ShadowGroup(
            shadow=group,
            content=[shadow_group_x, group_y],
        )

        result = shadow_group.get_content()

        self.assertEqual(len(result), 2)
        self.assertIs(result[0], shadow_group_x)
        self.assertIs(result[1], group_y)

    def test_get_content_mixed_allow_groups(self):
        """
        Given a ShadowGroup with a mix of Groups, ShadowGroups and Items
        When get_content is called with allow_groups
        Then it assembles runs of items into ShadowGroups
        """
        item_x = Item('x')
        group_x = Group(item_x)
        shadow_group_x = ShadowGroup(
            shadow=group_x,
            content=group_x.content,
        )
        item_y = Item('y')
        group_y = Group(item_y)
        item_z = Item('z')
        group = Group(group_x, item_z, group_y)
        shadow_group = ShadowGroup(
            shadow=group,
            content=[shadow_group_x, item_z, group_y],
        )

        result = shadow_group.get_content()

        self.assertEqual(len(result), 3)
        self.assertIs(result[0], shadow_group_x)
        self.assertIsInstance(result[1], ShadowGroup)
        shadow_group_z = result[1]
        self.assertIs(shadow_group_z.shadow, group)
        self.assertEqual(len(shadow_group_z.content), 1)
        self.assertIs(shadow_group_z.content[0], item_z)
        self.assertIs(result[2], group_y)

    def test_get_content_mixed_allow_groups_layout_not_normal(self):
        """
        Given a ShadowGroup with a mixture of Groups, ShadowGroups and Items
            and non-normal layout
        When get_content is called with allow_groups
        Then it returns the contents as-is
        """
        item_x = Item('x')
        group_x = Group(item_x)
        shadow_group_x = ShadowGroup(
            shadow=group_x,
            content=group_x.content,
        )
        item_y = Item('y')
        group_y = Group(item_y)
        item_z = Item('z')
        group = Group(group_x, item_z, group_y, layout='tabbed')
        shadow_group = ShadowGroup(
            shadow=group,
            content=[shadow_group_x, item_z, group_y],
        )

        result = shadow_group.get_content()

        self.assertEqual(len(result), 3)
        self.assertIs(result[0], shadow_group_x)
        self.assertIs(result[1], item_z)
        self.assertIs(result[2], group_y)

    def test_get_content_all_subgroups_allow_groups_false(self):
        """
        Given a ShadowGroup with only Groups and ShadowGroups
        When get_content is called with allow_groups False
        Then it returns the flattened list of items.
        """
        item_x = Item('x')
        group_x = Group(item_x)
        shadow_group_x = ShadowGroup(
            shadow=group_x,
            content=group_x.content,
        )
        item_y = Item('y')
        group_y = Group(item_y)
        group = Group(group_x, group_y)
        shadow_group = ShadowGroup(
            shadow=group,
            content=[shadow_group_x, group_y],
        )

        result = shadow_group.get_content(False)

        self.assertEqual(len(result), 2)
        self.assertIs(result[0], item_x)
        self.assertIs(result[1], item_y)

    def test_get_content_mixed_allow_groups_false(self):
        """
        Given a ShadowGroup with a mix of Groups, ShadowGroups and items
        When get_content is called with allow_groups False
        Then it returns the flattened list of items.
        """
        item_x = Item('x')
        group_x = Group(item_x)
        shadow_group_x = ShadowGroup(
            shadow=group_x,
            content=group_x.content,
        )
        item_y = Item('y')
        group_y = Group(item_y)
        item_z = Item('z')
        group = Group(group_x, item_z, group_y)
        shadow_group = ShadowGroup(
            shadow=group,
            content=[shadow_group_x, item_z, group_y],
        )

        result = shadow_group.get_content(False)

        self.assertEqual(len(result), 3)
        self.assertIs(result[0], item_x)
        self.assertIs(result[1], item_z)
        self.assertIs(result[2], item_y)
