#------------------------------------------------------------------------------
#
#  Copyright (c) 2014, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Author: Matt Reay
#  Date:   Jun 2019
#
#------------------------------------------------------------------------------
"""
Test cases for the TreeNode object.
"""

from __future__ import absolute_import
import unittest

from traits.api import HasStrictTraits, List, Str, This
from traits.testing.api import UnittestTools

from traitsui.api import TreeNode


class DummyModel(HasStrictTraits):
    """ Dummy model with children.
    """

    name = Str

    children = List(This)


class TestTreeNode(UnittestTools, unittest.TestCase):

    def test_insert_child(self):
        # Regression test for #559
        model = DummyModel(
            name="Parent",
            children=[
                DummyModel(name="Child0"),
                DummyModel(name="Child2")
            ]
        )
        node = TreeNode(
            children="children",
            node_for=[DummyModel]
        )
        node.insert_child(model, 1, DummyModel(name="Child1"))

        # Assert
        self.assertEqual(len(model.children), 3)
        for i in range(3):
            self.assertEqual(model.children[i].name, "Child{}".format(i))


if __name__ == '__main__':
    unittest.run()
