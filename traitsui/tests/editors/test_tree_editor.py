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

from pyface.api import GUI
from traits.api import Bool, Button, HasTraits, Instance, List, Str
from traitsui.api import (
    Handler,
    Item,
    ObjectTreeNode,
    TreeEditor,
    TreeNode,
    TreeNodeObject,
    View,
)
from traitsui.testing.api import MouseClick, UITester

from traitsui.tests._tools import (
    BaseTestMixin,
    create_ui,
    requires_toolkit,
    reraise_exceptions,
    ToolkitName,
)


class BogusWrap(HasTraits):
    """A bogus class representing a bogus tree."""

    name = Str("Totally bogus")


class Bogus(HasTraits):
    """A bogus class representing a bogus tree."""

    name = Str("Bogus")

    bogus_list = List()

    wrapped_bogus = Instance(BogusWrap)

    def _wrapped_bogus_default(self):
        return BogusWrap(bogus_list=[Bogus()])


class BogusHandler(Handler):
    def object_expand_all_changed(self, info):
        editor = info.ui.get_editors('bogus')[0]
        editor.expand_all()


class BogusTreeView(HasTraits):
    """A traitsui view visualizing Bogus objects as trees."""

    bogus = Instance(Bogus)

    hide_root = Bool()

    word_wrap = Bool()

    nodes = List(TreeNode)

    expand_all = Button()

    def _nodes_default(self):
        return [
            TreeNode(node_for=[Bogus], children="bogus_list", label="=Bogus"),
            TreeNode(node_for=[BogusWrap], label='name'),
        ]

    def default_traits_view(self):
        tree_editor = TreeEditor(
            nodes=self.nodes,
            hide_root=self.hide_root,
            editable=False,
            word_wrap=self.word_wrap,
        )

        traits_view = View(
            Item(name="bogus", id="engine", editor=tree_editor),
            Item('expand_all'),
            buttons=["OK"],
            handler=BogusHandler(),
        )

        return traits_view


class BogusTreeNodeObject(TreeNodeObject):
    """A bogus tree node."""

    name = Str("Bogus")

    bogus_list = List()


class BogusTreeNodeObjectView(HasTraits):
    """A traitsui view visualizing Bogus objects as trees."""

    bogus = Instance(BogusTreeNodeObject)

    hide_root = Bool()

    nodes = List(TreeNode)

    def _nodes_default(self):
        return [
            TreeNode(
                node_for=[BogusTreeNodeObject],
                children="bogus_list",
                label="=Bogus",
            )
        ]

    def default_traits_view(self):
        tree_editor = TreeEditor(
            nodes=self.nodes, hide_root=self.hide_root, editable=False
        )

        traits_view = View(
            Item(name="bogus", id="engine", editor=tree_editor), buttons=["OK"]
        )

        return traits_view


class TestTreeView(BaseTestMixin, unittest.TestCase):
    def setUp(self):
        BaseTestMixin.setUp(self)

    def tearDown(self):
        BaseTestMixin.tearDown(self)

    # test for wx is failing for other reasons.
    # It might pass once we receive fix for enthought/pyface#558
    @requires_toolkit([ToolkitName.qt])
    def test_tree_editor_with_nested_ui(self):
        tree_editor = TreeEditor(
            nodes=[
                TreeNode(
                    node_for=[Bogus],
                    auto_open=True,
                    children="bogus_list",
                    label="bogus",
                    view=View(Item("name")),
                ),
            ],
            hide_root=True,
        )
        bogus_list = [Bogus()]
        object_view = BogusTreeView(bogus=Bogus(bogus_list=bogus_list))
        view = View(Item("bogus", id="tree", editor=tree_editor))
        with reraise_exceptions(), create_ui(
            object_view, dict(view=view)
        ) as ui:
            editor = ui.info.tree
            editor.selected = bogus_list[0]
            GUI.process_events()

    def _test_tree_editor_releases_listeners(
        self, hide_root, nodes=None, trait="bogus_list", expected_listeners=1
    ):
        """The TreeEditor should release the listener to the root node's children
        when it's disposed of.
        """

        bogus = Bogus(bogus_list=[Bogus()])
        tree_editor_view = BogusTreeView(
            bogus=bogus, hide_root=hide_root, nodes=nodes
        )
        with reraise_exceptions(), create_ui(tree_editor_view):

            # The TreeEditor sets a listener on the bogus object's
            # children list
            notifiers_list = bogus.trait(trait)._notifiers(False)
            self.assertEqual(expected_listeners, len(notifiers_list))

        # The listener should be removed after the UI has been closed
        notifiers_list = bogus.trait(trait)._notifiers(False)
        self.assertEqual(0, len(notifiers_list))

    def _test_tree_node_object_releases_listeners(
        self, hide_root, nodes=None, trait="bogus_list", expected_listeners=1
    ):
        """The TreeEditor should release the listener to the root node's children
        when it's disposed of.
        """

        bogus = BogusTreeNodeObject(bogus_list=[BogusTreeNodeObject()])
        tree_editor_view = BogusTreeNodeObjectView(
            bogus=bogus, hide_root=hide_root, nodes=nodes
        )
        with reraise_exceptions(), create_ui(tree_editor_view):

            # The TreeEditor sets a listener on the bogus object's
            # children list
            notifiers_list = bogus.trait(trait)._notifiers(False)
            self.assertEqual(expected_listeners, len(notifiers_list))

            if trait == "name":
                # fire a label change
                bogus.name = "Something else"
            else:
                # change the children
                bogus.bogus_list.append(BogusTreeNodeObject())

        # The listener should be removed after the UI has been closed
        notifiers_list = bogus.trait(trait)._notifiers(False)
        self.assertEqual(0, len(notifiers_list))

    @requires_toolkit([ToolkitName.qt])
    def test_tree_editor_listeners_with_shown_root(self):
        nodes = [
            TreeNode(node_for=[Bogus], children="bogus_list", label="=Bogus")
        ]
        self._test_tree_editor_releases_listeners(hide_root=False, nodes=nodes)

    @requires_toolkit([ToolkitName.qt])
    def test_tree_editor_listeners_with_hidden_root(self):
        nodes = [
            TreeNode(node_for=[Bogus], children="bogus_list", label="=Bogus")
        ]
        self._test_tree_editor_releases_listeners(hide_root=True, nodes=nodes)

    @requires_toolkit([ToolkitName.qt])
    def test_tree_editor_label_listener(self):
        nodes = [
            TreeNode(node_for=[Bogus], children="bogus_list", label="name")
        ]
        self._test_tree_editor_releases_listeners(
            hide_root=False, nodes=nodes, trait="name"
        )

    @requires_toolkit([ToolkitName.qt])
    def test_tree_editor_xgetattr_label_listener(self):
        nodes = [
            TreeNode(
                node_for=[Bogus],
                children="bogus_list",
                label="wrapped_bogus.name",
            )
        ]
        self._test_tree_editor_releases_listeners(
            hide_root=False,
            nodes=nodes,
            trait="wrapped_bogus",
            expected_listeners=2,
        )

    @requires_toolkit([ToolkitName.qt])
    def test_tree_node_object_listeners_with_shown_root(self):
        nodes = [
            ObjectTreeNode(
                node_for=[BogusTreeNodeObject],
                children="bogus_list",
                label="=Bogus",
            )
        ]
        self._test_tree_node_object_releases_listeners(
            nodes=nodes, hide_root=False
        )

    @requires_toolkit([ToolkitName.qt])
    def test_tree_node_object_listeners_with_hidden_root(self):
        nodes = [
            ObjectTreeNode(
                node_for=[BogusTreeNodeObject],
                children="bogus_list",
                label="=Bogus",
            )
        ]
        self._test_tree_node_object_releases_listeners(
            nodes=nodes, hide_root=True
        )

    @requires_toolkit([ToolkitName.qt])
    def test_tree_node_object_label_listener(self):
        nodes = [
            ObjectTreeNode(
                node_for=[BogusTreeNodeObject],
                children="bogus_list",
                label="name",
            )
        ]
        self._test_tree_node_object_releases_listeners(
            nodes=nodes, hide_root=False, trait="name"
        )

    @requires_toolkit([ToolkitName.qt, ToolkitName.wx])
    def test_smoke_save_restore_prefs(self):
        bogus = Bogus(bogus_list=[Bogus()])
        tree_editor_view = BogusTreeView(bogus=bogus)
        with create_ui(tree_editor_view) as ui:
            prefs = ui.get_prefs()
            ui.set_prefs(prefs)

    @requires_toolkit([ToolkitName.qt])
    def test_smoke_word_wrap(self):
        bogus = Bogus(bogus_list=[Bogus()])
        tree_editor_view = BogusTreeView(bogus=bogus, word_wrap=True)
        with create_ui(tree_editor_view):
            pass

    # regression test for enthought/traitsui#1726
    @requires_toolkit([ToolkitName.qt])
    def test_expand_all(self):
        bogus = Bogus(bogus_list=[BogusWrap()])
        tree_editor_view = BogusTreeView(bogus=bogus)
        tester = UITester()
        with tester.create_ui(tree_editor_view) as ui:
            expand_all_button = tester.find_by_name(ui, "expand_all")
            expand_all_button.perform(MouseClick())
