
.. _advanced-editor-adapters:

========================
Advanced Editor Adapters
========================

A number of trait editors provide a way for code to adapt objects to the
expected API for the editor, and this can be used by Traits UI code to provide
strongly customized views of the data.  The editors which provide this facility
are the ListStrEditor, the TabularEditor and the TreeEditor.  In this section
we will look more closely at each of these and discuss how they can be
customized as needed.

The TreeEditor and TreeNodes
============================

The TreeEditor internally associates with each node in the tree a pair
consisting of the object that is associated with the node and something that
to adheres to the TreeNode interface.  The TreeNode interface is not explicitly laid out,
but it corresponds to the "overridable" public methods of the TreeNode class,
such as `get_label` and `get_children`.

This means that the tree editor expects one of the following three things
to be offered as values associated with a node, such as the value of the root
node trait or values that might be returned by the `get_children` method:

- an explicit pair of the object and a TreeNode instance for that object
- an object that has `is_node_for` return True for at least one of the
  factory's `node` items.
- an object that provides or can be adapted to the ITreeNode interface using
  Traits adaptation.

There is a crucial distinction between the way that TreeNodes and ITreeNodes
work. TreeNodes are generic---they are designed to work with certain types of
objects, but don't hold references to those objects---instead they rely on the
tree editor to keep track of the association between the objects and the
TreeNode to use with that object.  ITreeNodes, on the other hand, are adapters
so they are associated with individual objects rather than types of objects.
This means that ITreeNodes are generally more heavyweight: you end up with at
least one additional class instance for each displayed node (and most likely
two additional instances) vs. a tuple.  On the other hand, because ITreeNodes
use Traits adaptation, you can extend the set of classes that are supported
by adding more ITreeNode adapters, for example via Envisage extension points.

Specializing TreeNode Behaviour
-------------------------------

In general using TreeNodes works well when you have a hierarchy of HasTraits
objects, which is probably the most common situation.  And while the TreeNode
is fairly generic, there are times when you want to override the default
behaviour of one or more aspects of the object.  In this case it may be that
the best way to do this is to simply subclass TreeNode and adjust it to behave
the way that you want.

For example, the default behaviour of the TreeNode is to show one of 3
different icons depending on whether the node has children or not and whether
it has been expanded.  But you might want to display a different icon based
on some attribute of the object being viewed, and that would require a new
TreeNode subclass to override that behaviour.

For example, if we had different document types, identified by file extension::

    class DocumentTreeNode(TreeNode):

        icons = Dict({
            '.npy': ImageResource('document-table'),
            '.txt': ImageResource('document-text'),
            '.rst': ImageResource('document-text'),
            '.png': ImageResource('document-image'),
            '.jpg': ImageResource('document-image'),
        })

        def get_icon(self, object, is_expanded):
            icon = self.icons.get(object.extension, self.icon_item)
            return icon

This TreeNode subclass can now be used with any compatible class to give a
richer set of icons.

Common use cases for this approach would include:

- more customized icon display, as above.
- having the label built from multiple traits, which requires overriding
  `get_label`, `when_label_changed` and possibly `set_label`.
- having the children come from multiple traits, which requires overriding
  `allows_children`, `get_children`, `when_children_replaced`,
  `when_children_changed` and possibly `append_child`, `insert_child` and
  `delete_child` (although there may be better ways to handle this situation
  using multiple TreeNodes for the class).
- being more selective about what objects to use for the node.  For example,
  requiring not only that an object be of a certain class, but that it also
  have an attribute with a cetain value.  This requires overriding
  `is_node_for`.
- customization of menus on a per-object basis, or other UI behaviour like drag
  and drop, selection and clicking.

This has the advantage that most of the time the behaviour that you want is
built into the TreeNode class, and you only need to change the things which
are not to your requirements.

Where TreeNode classes are generally weak is when the object you are trying to
view is not a HasTraits instance, or where you don't know the full set of
classes that you need to display in the tree when writing the UI.  You can
overcome these obstacles by careful subclassing, taking particular care to
avoid things like trying to set traits listeners on non-HasTraits objects or
adapting the object to a desired interface before using it.  But in these cases
it may be better to use a different approach.

ITreeNodes and ITreeNodeAdapters
--------------------------------

These are most useful for situations where you don't know the full set of
classes that may be displayed in a tree.  This is a common situation when
writing complex applications using libraries like Envisage that allow new
functionality to be added to the application via plug-ins (potentially during
run-time!).  It is also useful in situations where the model object that is
being viewed isn't a HasTraits object, or where you may need some
UI state in the node that doesn't belong on the underlying model object (for
example, caching quantities which are expensive to compute).

To make writing code which satisfies the ITreeNode interface easier, there is
an ITreeNodeAdapter class which provides basic functionality and which can be
subclassed to provide an adapter class for your own nodes.  This adapter is
minimalistic and not complete.  You will at a minimum need to override the
`get_label` method, and probably many others to get the desired behaviour.
Since the ITreeNodeAdapter is an Adapter subclass, the object being adapted is
available as the `adaptee` attribute.  This means that the methods might look
similar to the ones for TreeNode, but they don't expect to be passed the object
as a parameter.

Once you have written the ITreeNodeAdapter subclass, you have to register the
adapter with trai
