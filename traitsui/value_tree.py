# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Defines tree node classes and editors for various types of values.
"""

import inspect
from operator import itemgetter

from types import FunctionType, MethodType

from traits.api import (
    Any,
    Bool,
    HasPrivateTraits,
    HasTraits,
    Instance,
    List,
    Str,
)

from .tree_node import ObjectTreeNode, TreeNode, TreeNodeObject

from .editors.tree_editor import TreeEditor


class SingleValueTreeNodeObject(TreeNodeObject):
    """A tree node for objects of types that have a single value."""

    # -------------------------------------------------------------------------
    #  Trait definitions:
    # -------------------------------------------------------------------------

    #: The parent of this node
    parent = Instance(TreeNodeObject)

    #: Name of the value
    name = Str()

    #: User-specified override of the default label
    label = Str()

    #: The value itself
    value = Any()

    #: Is the value readonly?
    readonly = Bool(False)

    def tno_allows_children(self, node):
        """Returns whether this object can have children (False for this
        class).
        """
        return False

    def tno_has_children(self, node):
        """Returns whether the object has children (False for this class)."""
        return False

    def tno_can_rename(self, node):
        """Returns whether the object's children can be renamed (False for
        this class).
        """
        return False

    def tno_can_copy(self, node):
        """Returns whether the object's children can be copied (True for this
        class).
        """
        return True

    def tno_can_delete(self, node):
        """Returns whether the object's children can be deleted (False for
        this class).
        """
        return False

    def tno_can_insert(self, node):
        """Returns whether the object's children can be inserted (False,
        meaning children are appended, for this class).
        """
        return False

    def tno_get_icon(self, node, is_expanded):
        """Returns the icon for a specified object."""
        return "@icons:%s_node" % self.__class__.__name__[:-4].lower()

    def tno_set_label(self, node, label):
        """Sets the label for a specified object."""
        if label == "?":
            label = ""
        self.label = label

    def tno_get_label(self, node):
        """Gets the label to display for a specified object."""
        if self.label != "":
            return self.label

        if self.name == "":
            return self.format_value(self.value)

        return "%s: %s" % (self.name, self.format_value(self.value))

    def format_value(self, value):
        """Returns the formatted version of the value."""
        return repr(value)

    def node_for(self, name, value):
        """Returns the correct node type for a specified value."""
        for type, node in basic_types():
            if isinstance(value, type):
                break
        else:
            node = OtherNode
            if inspect.isclass(value):
                node = ClassNode

            elif hasattr(value, "__class__"):
                node = ObjectNode

        return node(
            parent=self, name=name, value=value, readonly=self.readonly
        )


class MultiValueTreeNodeObject(SingleValueTreeNodeObject):
    """A tree node for objects of types that have multiple values."""

    def tno_allows_children(self, node):
        """Returns whether this object can have children (True for this class)."""
        return True

    def tno_has_children(self, node):
        """Returns whether the object has children (True for this class)."""
        return True


class StringNode(SingleValueTreeNodeObject):
    """A tree node for strings."""

    def format_value(self, value):
        """Returns the formatted version of the value."""
        n = len(value)
        if len(value) > 80:
            value = "%s...%s" % (value[:42], value[-35:])

        return "%s [%d]" % (repr(value), n)


class NoneNode(SingleValueTreeNodeObject):
    """A tree node for None values."""

    pass


class BoolNode(SingleValueTreeNodeObject):
    """A tree node for Boolean values."""

    pass


class IntNode(SingleValueTreeNodeObject):
    """A tree node for integer values."""

    pass


class FloatNode(SingleValueTreeNodeObject):
    """A tree node for floating point values."""

    pass


class ComplexNode(SingleValueTreeNodeObject):
    """A tree node for complex number values."""

    pass


class OtherNode(SingleValueTreeNodeObject):
    """A tree node for single-value types for which there is not another
    node type.
    """

    pass


class TupleNode(MultiValueTreeNodeObject):
    """A tree node for tuples."""

    def format_value(self, value):
        """Returns the formatted version of the value."""
        return "Tuple(%d)" % len(value)

    def tno_has_children(self, node):
        """Returns whether the object has children, based on the length of
        the tuple.
        """
        return len(self.value) > 0

    def tno_get_children(self, node):
        """Gets the object's children."""
        node_for = self.node_for
        value = self.value
        if len(value) > 500:
            return (
                [node_for("[%d]" % i, x) for i, x in enumerate(value[:250])]
                + [StringNode(value="...", readonly=True)]
                + [node_for("[%d]" % i, x) for i, x in enumerate(value[-250:])]
            )

        return [node_for("[%d]" % i, x) for i, x in enumerate(value)]


class ListNode(TupleNode):
    """A tree node for lists."""

    def format_value(self, value):
        """Returns the formatted version of the value."""
        return "List(%d)" % len(value)

    def tno_can_delete(self, node):
        """Returns whether the object's children can be deleted."""
        return not self.readonly

    def tno_can_insert(self, node):
        """Returns whether the object's children can be inserted (vs.
        appended).
        """
        return not self.readonly


class SetNode(ListNode):
    """A tree node for sets."""

    def format_value(self, value):
        """Returns the formatted version of the value."""
        return "Set(%d)" % len(value)


class ArrayNode(TupleNode):
    """A tree node for arrays."""

    def format_value(self, value):
        """Returns the formatted version of the value."""
        return "Array(%s)" % ",".join([str(n) for n in value.shape])


class DictNode(TupleNode):
    """A tree node for dictionaries."""

    def format_value(self, value):
        """Returns the formatted version of the value."""
        return "Dict(%d)" % len(value)

    def tno_get_children(self, node):
        """Gets the object's children."""
        node_for = self.node_for
        items = [(repr(k), v) for k, v in self.value.items()]
        items.sort(key=itemgetter(0))
        if len(items) > 500:
            return (
                [node_for("[%s]" % k, v) for k, v in items[:250]]
                + [StringNode(value="...", readonly=True)]
                + [node_for("[%s]" % k, v) for k, v in items[-250:]]
            )

        return [node_for("[%s]" % k, v) for k, v in items]

    def tno_can_delete(self, node):
        """Returns whether the object's children can be deleted."""
        return not self.readonly


class FunctionNode(SingleValueTreeNodeObject):
    """A tree node for functions"""

    def format_value(self, value):
        """Returns the formatted version of the value."""
        return "Function %s()" % (value.__name__)


# ---------------------------------------------------------------------------
#  'MethodNode' class:
# ---------------------------------------------------------------------------


class MethodNode(MultiValueTreeNodeObject):
    def format_value(self, value):
        """Returns the formatted version of the value."""
        type = "B"
        if value.__self__ is None:
            type = "Unb"

        return "%sound method %s.%s()" % (
            type,
            value.__self__.__class__.__name__,
            value.__func__.__name__,
        )

    def tno_has_children(self, node):
        """Returns whether the object has children."""
        return self.value.__func__ is not None

    def tno_get_children(self, node):
        """Gets the object's children."""
        return [self.node_for("Object", self.value.__self__)]


class ObjectNode(MultiValueTreeNodeObject):
    """A tree node for objects."""

    def format_value(self, value):
        """Returns the formatted version of the value."""
        try:
            klass = value.__class__.__name__
        except:
            klass = "???"
        return "%s(0x%08X)" % (klass, id(value))

    def tno_has_children(self, node):
        """Returns whether the object has children."""
        try:
            return len(self.value.__dict__) > 0
        except:
            return False

    def tno_get_children(self, node):
        """Gets the object's children."""
        items = [(k, v) for k, v in self.value.__dict__.items()]
        items.sort(key=itemgetter(0))
        return [self.node_for("." + k, v) for k, v in items]


class ClassNode(ObjectNode):
    """A tree node for classes."""

    def format_value(self, value):
        """Returns the formatted version of the value."""
        return value.__name__


class TraitsNode(ObjectNode):
    """A tree node for traits."""

    def tno_has_children(self, node):
        """Returns whether the object has children."""
        return len(self._get_names()) > 0

    def tno_get_children(self, node):
        """Gets the object's children."""
        names = sorted(self._get_names())
        value = self.value
        node_for = self.node_for
        nodes = []
        for name in names:
            try:
                item_value = getattr(value, name, "<unknown>")
            except Exception as excp:
                item_value = "<%s>" % excp
            nodes.append(node_for("." + name, item_value))

        return nodes

    def _get_names(self):
        """Gets the names of all defined traits or attributes."""
        value = self.value
        names = {}
        for name in value.trait_names(type=lambda x: x != "event"):
            names[name] = None
        for name in value.__dict__.keys():
            names[name] = None
        return list(names.keys())

    def tno_when_children_replaced(self, node, listener, remove):
        """Sets up or removes a listener for children being replaced on a
        specified object.
        """
        self._listener = listener
        self.value.on_trait_change(
            self._children_replaced, remove=remove, dispatch="ui"
        )

    def _children_replaced(self):
        self._listener(self)

    def tno_when_children_changed(self, node, listener, remove):
        """Sets up or removes a listener for children being changed on a
        specified object.
        """
        pass


class RootNode(MultiValueTreeNodeObject):
    """A root node."""

    def format_value(self, value):
        """Returns the formatted version of the value."""
        return ""

    def tno_get_children(self, node):
        """Gets the object's children."""
        return [self.node_for("", self.value)]


# -------------------------------------------------------------------------
#  Define the mapping of object types to nodes:
# -------------------------------------------------------------------------

_basic_types = None


def basic_types():
    global _basic_types

    if _basic_types is None:
        # Create the mapping of object types to nodes:
        _basic_types = [
            (type(None), NoneNode),
            (str, StringNode),
            (str, StringNode),
            (bool, BoolNode),
            (int, IntNode),
            (float, FloatNode),
            (complex, ComplexNode),
            (tuple, TupleNode),
            (list, ListNode),
            (set, SetNode),
            (dict, DictNode),
            (FunctionType, FunctionNode),
            (MethodType, MethodNode),
            (HasTraits, TraitsNode),
        ]

        try:
            from numpy import array

            _basic_types.append((type(array([1])), ArrayNode))
        except ImportError:
            pass

    return _basic_types


class _ValueTree(HasPrivateTraits):

    # -------------------------------------------------------------------------
    #  Trait definitions:
    # -------------------------------------------------------------------------

    #: List of arbitrary Python values contained in the tree:
    values = List(SingleValueTreeNodeObject)


# -------------------------------------------------------------------------
#  Defines the value tree editor(s):
# -------------------------------------------------------------------------

# Nodes in a value tree:
value_tree_nodes = [
    ObjectTreeNode(
        node_for=[
            NoneNode,
            StringNode,
            BoolNode,
            IntNode,
            FloatNode,
            ComplexNode,
            OtherNode,
            TupleNode,
            ListNode,
            ArrayNode,
            DictNode,
            SetNode,
            FunctionNode,
            MethodNode,
            ObjectNode,
            TraitsNode,
            RootNode,
            ClassNode,
        ]
    )
]

# Editor for a value tree:
value_tree_editor = TreeEditor(
    auto_open=3, hide_root=True, editable=False, nodes=value_tree_nodes
)

# Editor for a value tree with a root:
value_tree_editor_with_root = TreeEditor(
    auto_open=3,
    editable=False,
    nodes=[
        ObjectTreeNode(
            node_for=[
                NoneNode,
                StringNode,
                BoolNode,
                IntNode,
                FloatNode,
                ComplexNode,
                OtherNode,
                TupleNode,
                ListNode,
                ArrayNode,
                DictNode,
                SetNode,
                FunctionNode,
                MethodNode,
                ObjectNode,
                TraitsNode,
                RootNode,
                ClassNode,
            ]
        ),
        TreeNode(
            node_for=[_ValueTree],
            auto_open=True,
            children="values",
            move=[SingleValueTreeNodeObject],
            copy=False,
            label="=Values",
            icon_group="traits_node",
            icon_open="traits_node",
        ),
    ],
)

# -------------------------------------------------------------------------
#  Defines a 'ValueTree' trait:
# -------------------------------------------------------------------------

# Trait for a value tree:
ValueTree = Instance(_ValueTree, (), editor=value_tree_editor_with_root)
