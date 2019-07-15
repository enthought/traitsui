#------------------------------------------------------------------------------
#
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Author: Pietro Berkes
#  Date:   Dec 2012
#
#------------------------------------------------------------------------------

from __future__ import absolute_import
import unittest

from traits.api import Bool, HasTraits, Instance, List, Str
from traitsui.api import (
    Item, ObjectTreeNode, TreeEditor, TreeNode, TreeNodeObject, View
)

from traitsui.tests._tools import (
    press_ok_button, skip_if_null, skip_if_not_qt4,
    store_exceptions_on_all_threads
)


class BogusWrap(HasTraits):
    """ A bogus class representing a bogus tree. """

    name = Str("Totally bogus")


class Bogus(HasTraits):
    """ A bogus class representing a bogus tree. """

    name = Str("Bogus")

    bogus_list = List

    wrapped_bogus = Instance(BogusWrap)

    def _wrapped_bogus_default(self):
        return BogusWrap(bogus_list=[Bogus()])


class BogusTreeView(HasTraits):
    """ A traitsui view visualizing Bogus objects as trees. """

    bogus = Instance(Bogus)

    hide_root = Bool

    word_wrap = Bool

    nodes = List(TreeNode)

    def _nodes_default(self):
        return [
            TreeNode(
                node_for=[Bogus],
                children='bogus_list',
                label='=Bogus'
            )
        ]

    def default_traits_view(self):
        tree_editor = TreeEditor(
            nodes=self.nodes,
            hide_root=self.hide_root,
            editable=False,
            word_wrap=self.word_wrap,
        )

        traits_view = View(
            Item(name='bogus', id='engine', editor=tree_editor),
            buttons=['OK'],
        )

        return traits_view


class BogusTreeNodeObject(TreeNodeObject):
    """ A bogus tree node. """

    name = Str("Bogus")

    bogus_list = List


class BogusTreeNodeObjectView(HasTraits):
    """ A traitsui view visualizing Bogus objects as trees. """

    bogus = Instance(BogusTreeNodeObject)

    hide_root = Bool

    nodes = List(TreeNode)

    def _nodes_default(self):
        return [
            TreeNode(
                node_for=[BogusTreeNodeObject],
                children='bogus_list',
                label='=Bogus'
            )
        ]

    def default_traits_view(self):
        tree_editor = TreeEditor(
            nodes=self.nodes,
            hide_root=self.hide_root,
            editable=False,
        )

        traits_view = View(
            Item(name='bogus', id='engine', editor=tree_editor),
            buttons=['OK'],
        )

        return traits_view


class TestTreeView(unittest.TestCase):

    def _test_tree_editor_releases_listeners(self, hide_root, nodes=None,
                                             trait='bogus_list',
                                             expected_listeners=1):
        """ The TreeEditor should release the listener to the root node's children
        when it's disposed of.
        """

        with store_exceptions_on_all_threads():
            bogus = Bogus(bogus_list=[Bogus()])
            tree_editor_view = BogusTreeView(
                bogus=bogus,
                hide_root=hide_root,
                nodes=nodes,
            )
            ui = tree_editor_view.edit_traits()

            # The TreeEditor sets a listener on the bogus object's
            # children list
            notifiers_list = bogus.trait(trait)._notifiers(False)
            self.assertEqual(expected_listeners, len(notifiers_list))

            # Manually close the UI
            press_ok_button(ui)

            # The listener should be removed after the UI has been closed
            notifiers_list = bogus.trait(trait)._notifiers(False)
            self.assertEqual(0, len(notifiers_list))

    def _test_tree_node_object_releases_listeners(self, hide_root, nodes=None,
                                                  trait='bogus_list',
                                                  expected_listeners=1):
        """ The TreeEditor should release the listener to the root node's children
        when it's disposed of.
        """

        with store_exceptions_on_all_threads():
            bogus = BogusTreeNodeObject(bogus_list=[BogusTreeNodeObject()])
            tree_editor_view = BogusTreeNodeObjectView(
                bogus=bogus,
                hide_root=hide_root,
                nodes=nodes,
            )
            ui = tree_editor_view.edit_traits()

            # The TreeEditor sets a listener on the bogus object's
            # children list
            notifiers_list = bogus.trait(trait)._notifiers(False)
            self.assertEqual(expected_listeners, len(notifiers_list))

            if trait == 'name':
                # fire a label change
                bogus.name = "Something else"
            else:
                # change the children
                bogus.bogus_list.append(BogusTreeNodeObject())

            # Manually close the UI
            press_ok_button(ui)

            # The listener should be removed after the UI has been closed
            notifiers_list = bogus.trait(trait)._notifiers(False)
            self.assertEqual(0, len(notifiers_list))

    @skip_if_null
    def test_tree_editor_listeners_with_shown_root(self):
        nodes = [
            TreeNode(
                node_for=[Bogus],
                children='bogus_list',
                label='=Bogus'
            )
        ]
        self._test_tree_editor_releases_listeners(hide_root=False, nodes=nodes)

    @skip_if_null
    def test_tree_editor_listeners_with_hidden_root(self):
        nodes = [
            TreeNode(
                node_for=[Bogus],
                children='bogus_list',
                label='=Bogus'
            )
        ]
        self._test_tree_editor_releases_listeners(hide_root=True, nodes=nodes)

    @skip_if_null
    def test_tree_editor_label_listener(self):
        nodes = [
            TreeNode(
                node_for=[Bogus],
                children='bogus_list',
                label='name'
            )
        ]
        self._test_tree_editor_releases_listeners(hide_root=False, nodes=nodes,
                                                  trait='name')

    @skip_if_null
    def test_tree_editor_xgetattr_label_listener(self):
        nodes = [
            TreeNode(
                node_for=[Bogus],
                children='bogus_list',
                label='wrapped_bogus.name'
            )
        ]
        self._test_tree_editor_releases_listeners(
            hide_root=False,
            nodes=nodes,
            trait='wrapped_bogus',
            expected_listeners=2,
        )

    @skip_if_null
    def test_tree_node_object_listeners_with_shown_root(self):
        nodes = [
            ObjectTreeNode(
                node_for=[BogusTreeNodeObject],
                children='bogus_list',
                label='=Bogus'
            )
        ]
        self._test_tree_node_object_releases_listeners(
            nodes=nodes, hide_root=False)

    @skip_if_null
    def test_tree_node_object_listeners_with_hidden_root(self):
        nodes = [
            ObjectTreeNode(
                node_for=[BogusTreeNodeObject],
                children='bogus_list',
                label='=Bogus'
            )
        ]
        self._test_tree_node_object_releases_listeners(
            nodes=nodes, hide_root=True)

    @skip_if_null
    def test_tree_node_object_label_listener(self):
        nodes = [
            ObjectTreeNode(
                node_for=[BogusTreeNodeObject],
                children='bogus_list',
                label='name'
            )
        ]
        self._test_tree_node_object_releases_listeners(
            nodes=nodes, hide_root=False, trait='name')

    @skip_if_null
    def test_smoke_save_restore_prefs(self):
        bogus = Bogus(bogus_list=[Bogus()])
        tree_editor_view = BogusTreeView(bogus=bogus)
        ui = tree_editor_view.edit_traits()
        prefs = ui.get_prefs()
        ui.set_prefs(prefs)

    @skip_if_not_qt4
    def test_smoke_word_wrap(self):
        bogus = Bogus(bogus_list=[Bogus()])
        tree_editor_view = BogusTreeView(bogus=bogus, word_wrap=True)
        ui = tree_editor_view.edit_traits()
        ui.dispose()
