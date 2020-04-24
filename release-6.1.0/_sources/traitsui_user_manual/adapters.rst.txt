
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

.. _tree-nodes:

.. module:: traitsui.tree_node

The :py:class:`~traitsui.editors.tree_editor.TreeEditor` internally associates
with each node in the tree a pair consisting of the object that is associated
with the node and something that to adheres to the :py:class:`TreeNode`
interface.  The :py:class:`TreeNode` interface is not explicitly laid out, but
it corresponds to the "overridable" public methods of the :py:class:`TreeNode`
class, such as :py:meth:`~TreeNode.get_label` and
:py:meth:`~TreeNode.get_children`.

This means that the tree editor expects one of the following three things
to be offered as values associated with a node, such as the value of the root
node trait or values that might be returned by the
:py:meth:`~TreeNode.get_children` method:

- an explicit pair of the object and a :py:class:`TreeNode` instance for that
  object
- an object that has :py:meth:`~TreeNode.is_node_for` return ``True`` for at
  least one of the factory's
  :py:attr:`~traitsui.editors.tree_editor.TreeEditor.nodes` items.
- an object that provides or can be adapted to the :py:class:`ITreeNode`
  interface using Traits adaptation.

There is a crucial distinction between the way that :py:class:`TreeNode` and
:py:class:`ITreeNode` work. :py:class:`TreeNode` is generic---it is designed
to work with certain types of objects, but doesn't hold references to those
objects---instead they rely on the :py:class:`TreeEditor` to keep track
of the association between the objects and the :py:class:`TreeNode` to use with
that object.  :py:class:`ITreeNode`, on the other hand, is an interface and
uses adapters associated with individual objects rather than types of objects.
This means that :py:class:`ITreeNode`-based approaches are generally more
heavyweight: you end up with at least one additional class instance for each
displayed node (and most likely two additional instances) vs. a tuple.  On the
other hand, because :py:class:`ITreeNode` uses Traits adaptation, you can
extend the set of classes that are supported by adding more
:py:class:`ITreeNode` adapters, for example via Envisage extension points.

Specializing TreeNode Behaviour
-------------------------------

In general using :py:class:`TreeNode` s works well when you have a hierarchy of
:py:class:`~traits.api.HasTraits` objects, which is probably the most common
situation.  And while the :py:class:`TreeNode` is fairly generic, there are
times when you want to override the default behaviour of one or more aspects of
the object.  In this case it may be that the best way to do this is to simply
subclass :py:class:`TreeNode` and adjust it to behave the way that you want.

For example, the default behaviour of the :py:class:`TreeNode` is to show one
of 3 different icons depending on whether the node has children or not and
whether it has been expanded.  But you might want to display a different icon
based on some attribute of the object being viewed, and that would require a
new :py:class:`TreeNode` subclass to override that behaviour.

Concretely, if we had different document types, identified by file extension::

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

This :py:class:`TreeNode` subclass can now be used with any compatible class to
give a richer set of icons.

Common use cases for this approach would include:

- more customized icon display, as above.
- having the label built from multiple traits, which requires overriding
  :py:meth:`~TreeNode.get_label`, :py:meth:`~TreeNode.when_label_changed` and
  possibly :py:meth:`~TreeNode.set_label`.
- having the children come from multiple traits, which requires overriding
  :py:meth:`~TreeNode.allows_children`, :py:meth:`~TreeNode.get_children`,
  :py:meth:`~TreeNode.when_children_replaced`,
  :py:meth:`~TreeNode.when_children_changed` and possibly
  :py:meth:`~TreeNode.append_child`, :py:meth:`~TreeNode.insert_child` and
  :py:meth:`~TreeNode.delete_child` (although there may be better ways to
  handle this situation by using multiple :py:class:`TreeNodes` for the class).
- being more selective about what objects to use for the node.  For example,
  requiring not only that an object be of a certain class, but that it also
  have an attribute with a cetain value.  This requires overriding
  :py:meth:`~TreeNode.is_node_for`.
- customization of menus on a per-object basis, or other UI behaviour like drag
  and drop, selection and clicking.

This has the advantage that most of the time the behaviour that you want is
built into the :py:class:`TreeNode` class, and you only need to change the
things which are not to your requirements.

Where :py:class:`TreeNode` classes are generally weak is when the object you
are trying to view is not a :py:class:`~traits.api.HasTraits` instance, or
where you don't know the full set of classes that you need to display in the
tree when writing the UI.  You can overcome these obstacles by careful
subclassing, taking particular care to avoid things like trying to set traits
listeners on non-:py:class:`~traits.api.HasTraits` objects or adapting the
object to a desired interface before using it.  But in these cases it may be
better to use a different approach.

ITreeNodes and ITreeNodeAdapters
--------------------------------

These are most useful for situations where you don't know the full set of
classes that may be displayed in a tree.  This is a common situation when
writing complex applications using libraries like Envisage that allow new
functionality to be added to the application via plug-ins (potentially during
run-time!).  It is also useful in situations where the model object that is
being viewed isn't a :py:class:`~traits.api.HasTraits` object, or where you may
need some UI state in the node that doesn't belong on the underlying model
object (for example, caching quantities which are expensive to compute).

Before using this approach, you should make sure that you understand the way
that traits adaptation works.

To make writing code which satisfies the :py:class:`ITreeNode` interface
easier, there is an :py:class:`ITreeNodeAdapter` class which provides basic
functionality and which can be subclassed to provide an adapter class for your
own nodes.  This adapter is minimalistic and not complete.  You will at a
minimum need to override the :py:meth:`~ITreeNodeAdapter.get_label` method, and
probably many others to get the desired behaviour. Since the
:py:class:`ITreeNodeAdapter` is an :py:class:`Adapter` subclass, the object
being adapted is available as the :py:attr:`adaptee` attribute.  This means
that the methods might look similar to the ones for :py:class:`TreeNode`, but
they don't expect to be passed the object as a parameter.

Once you have written the :py:class:`ITreeNodeAdapter` subclass, you have to
register the adapter with traits using the Traits :py:func:`regsiter_factory`
function. You are not required to use :py:class:`ITreeNodeAdapter` if you don't
wish to.  You can instead write a class which ``@provides`` the
:py:class:`ITreeNode` interface directly, or create an alternative adapter
class.

Note that currently the tree editor infrastructure uses the deprecated Traits
:py:func:`adapts` class advisor and the default traits adapter registry which
means that you can't have mulitple different :py:class:`ITreeNode` adapters for
a given object to use in different editors within a given application.  This is
likely to be fixed in a future release of TraitsUI.  In the mean-time you can
work around this somewhat by having the trait being edited and/or the
:py:meth:`~ITreeNodeAdapter.get_children` method return pre-adapted objects,
rather than relying on traits adaptation machinery to find and adapt the
object.

ObjectTreeNodes and TreeNodeObjects
-----------------------------------

Another approach to adapting objects, particularly non-:py:class:`HasTraits`
objects is used by the :py:class:`ValueEditor`, but is available for general
tree editors to use as well.  In this approach you write one or more
:py:class:`TreeNodeObject` classes that wrap the model objects that you want to
display, and then use instances of the :py:class:`TreeNodeObject` classes
within the tree editor, both as the root node being edited, and the objects
returned by the :py:meth:`tno_get_children` methods.  To fit these with the
expected :py:class:`TreeNode` classes used by the :py:class:`TreeEditor`, there
is the :py:class:`ObjectTreeNode` class which knows how to call the appropriate
:py:class:`TreeNodeObjects` and which can be given a list of
:py:class:`TreeNodeObject` classes that it understands.

For example, it is possible to represent a tree structure in Python using
nested dictionaries with strings as keys.  A :py:class:`TreeNodeObject` for
such a structure might look like this::

    class DictNode(TreeNodeObject):

        #: The parent of the node
        parent = Instance('DictNode')

        #: The label for the node
        label = Str

        #: The value for this node
        value = Any

        def tno_get_label(self, node):
            return self.label

        def tno_allows_children(self, node):
            return isinstance(self.value, dict)

        def tno_has_children(self, node):
            return bool(self.value)

        def tno_get_children(self, node):
            return [DictNode(parent=self, label=key, value=value)
                    for key, value in sorted(self.value.items())]

and so forth.  There is additional work if you want to be able to modify
the structure of the tree, for example.  In addition to defining the
:py:class:`TreeNodeObject` subclass, you also need provide the nodes for the
editor something like this::

    dict_tree_editor = TreeEditor(
        editable=False,
        nodes=[
            ObjectTreeNode(
                node_for=[DictNode],
                rename=False,
                rename_me=False,
                copy=False,
                delete=False,
                delete_me=False,
            )
        ]
    )

The :py:class:`ObjectTreeNode` is a :py:class:`TreeNode` subclass that
delegates operations to the :py:class:`TreeNodeObject`, but the default
:py:class:`TreeNodeObject` methods try to behave in the same way as the base
:py:class:`TreeNode`, so you can specify global behaviour on the
:py:class:`ObjectTreeNode` in the same way that you can for a
:py:class:`TreeNode`.

The last piece to make this approach work is that the root node when editing
has to be a :py:class:`DictNode` instance, so you may need to provide a
property that wraps the raw tree structure in a :py:class:`DictNode` to get
started: unlike the :py:class:`ITreeNodeAdapter` approaches this wrapping not
automatically provided for you.

Custom Renderers
----------------

The Qt backend allows users to completely override the rendering of cells in
a TreeEditor.  To do this, the TreeNode should override the
:py:meth:`TreeNode.get_renderer` method to return an instance of a
subclass of :py:class:`~traitsui.tree_node_renderer.AbstractTreeNodeRenderer`.
A :py:class:`~traitsui.qt4.tree_node_renderers.WordWrapRenderer` is available
to provide basic word-wrapped layout in a cell, but user-defined subclasses
can do any rendering that they want by implementing their own
:py:class:`~traitsui.tree_node_renderer.AbstractTreeNodeRenderer` subclass.

:py:class:`~traitsui.tree_node_renderer.AbstractTreeNodeRenderer` is an
abstract base class, and subclasses must implement two methods:

:py:meth:`~traitsui.tree_node_renderer.AbstractTreeNodeRenderer.size`
    A method which should return a (height, width) tuple giving the preferred
    size for the cell.  Depending on other constraints and user interactions,
    this may not be the actual size that the cell will have available.

    The toolkit will provide a ``size_context`` object that provides useful
    parameters to help with sizing operations.  In the Qt backend, this is a
    tuple containing the arguments passed to the Qt :py:meth:`sizeHint` method
    of a :py:class:`QStyledItemDelegate`.

:py:meth:`~traitsui.tree_node_renderer.AbstractTreeNodeRenderer.paint`
    Toolkit-dependent code that renders the cell

    The toolkit will provide a ```paint_context``` object that provides useful
    parameters to help with painting operations.  In the Qt backend, this is a
    tuple containing the arguments passed to the Qt :py:meth:`paint` method
    of a :py:class:`QStyledItemDelegate`.  In particular, the first argument
    is always a :py:class:`QPainter` instance and the second a
    :py:class:`QStyleOptionViewItem` from which you can get the rectangle of
    the cell being rendered as well as style and font information.

The renderer can choose to not handle all of the rendering, and instead let
the tree editor handle rendering the icon or the text of the cell, by setting
the :py:meth:`~traitsui.tree_node_renderer.AbstractTreeNodeRenderer.handles_icon`,
:py:meth:`~traitsui.tree_node_renderer.AbstractTreeNodeRenderer.handles_text`,
and :py:meth:`~traitsui.tree_node_renderer.AbstractTreeNodeRenderer.handles_all`
traits appropriately.

Lastly there is a convenience method
:py:meth:`~traitsui.tree_node_renderer.AbstractTreeNodeRenderer.get_label` that
gets the label text given the tree node, the underlying object, and the column,
smoothing over the TreeNode columns label API.


Examples
--------

There are a number of examples of use of the
:py:class:`~traitsui.editors.tree_editor.TreeEditor` in the TraitsUI demos:

- :github-demo:`TreeEditor <Standard_Editors/TreeEditor_demo.py>`
- :github-demo:`Adapted TreeEditor <Advanced/Adapted_tree_editor_demo.py>`
- :github-demo:`HDF5 Tree <Advanced/HDF5_tree_demo.py>`
- :github-demo:`Tree Editor with Renderer <Extras/Tree_editor_with_TreeNodeRenderer.py>`


The TabularAdapter Class
========================

.. module:: traitsui.tabular_adapter

The power and flexibility of the tabular editor is mostly a result of the
:py:class:`TabularAdapter` class, which is the base class from which all
tabular editor adapters must be derived.

The :py:class:`~traitsui.editors.tabular_editor.TabularEditor` object
interfaces between the underlying toolkit widget and your program, while the
:py:class:`TabularAdapter` object associated with the editor interfaces between
the editor and your data.

The design of the :py:class:`TabularAdapter` base class is such that it tries
to make simple cases simple and complex cases possible. How it accomplishes
this is what we'll be discussing in the following sections.

The TabularAdapter *columns* Trait
----------------------------------

First up is the :py:class:`TabularAdapter` :py:attr:`columns` trait, which is a
list of values which define, in presentation order, the set of columns to be
displayed by the associated
:py:class:`~traitsui.editors.tabular_editor.TabularEditor`.

Each entry in the :py:attr:`~TabularAdapter.columns` list can have one of two
forms:

- ``string``
- ``(string, id)``

where ``string`` is the user interface name of the column (which will appear in
the table column header) and ``id`` is any value that you want to use to
identify that column to your adapter. Normally this value is either a trait
name or an integer index value, but it can be any value you want. If only
``string`` is specified, then ``id`` is the index of the ``string`` within
``columns``.

For example, say you want to display a table containing a list of tuples, each
of which has three values: a name, an age, and a weight. You could then use
the following value for the :py:attr:`~TabularAdapter.columns` trait::

    columns = ['Name', 'Age', 'Weight']

By default, the ``id`` values (also referred to in later sections as the
*column ids*) for the columns will be the corresponding tuple index values.

Say instead that you have a list of :py:class:`Person` objects, with
:py:attr:`name`, :py:attr:`age` and :py:attr:`weight` traits that you want to
display in the table. Then you could use the following
:py:attr:`~TabularAdapter.columns` value instead::

    columns = [('Name', 'name'),
               ('Age', 'age'),
               ('Weight', 'weight')]

In this case, the *column ids* are the names of the traits you want to display
in each column.

Note that it is possible to dynamically modify the contents of the
:py:attr:`~TabularAdapter.columns` trait while the
:py:class:`~traitsui.editors.tabular_editor.TabularEditor` is active. The
:py:class:`~traitsui.editors.tabular_editor.TabularEditor` will automatically
modify the table to show the new set of defined columns.

The Core TabularAdapter Interface
---------------------------------

In this section, we'll describe the core interface to the
:py:class:`TabularAdapter` class. This is the actual interface used by the
:py:class:`~traitsui.editors.tabular_editor.TabularEditor` to access your data
and display attributes. In the most complex data representation cases, these
are the methods that you must override in order to have the greatest control
over what the editor sees and does.

However, the base :py:class:`TabularAdapter` class provides default
implementations for all of these methods. In subsequent sections, we'll look at
how these default implementations provide simple means  of customizing the
adapter to your needs.  But for now, let's start by covering the details of the
core interface itself.

To reduce the amount of repetition, we'll use the following definitions in all
of the method argument lists that follow in this section:

object
    The object whose trait is being edited by the
    :py:class:`~traitsui.editors.tabular_editor.TabularEditor`.

trait
    The name of the trait the
    :py:class:`~traitsui.editors.tabular_editor.TabularEditor` is editing.

row
    The row index (starting with 0) of a table item.

column
    The column index (starting with 0) of a table column.

The adapter interface consists of a number of methods which can be divided into
two main categories: those which are sensitive to the type of a particular table
item, and those which are not. We'll begin with the methods that are
sensitive to an item's type:

:py:meth:`~TabularAdapter.get_alignment`
    Returns the alignment style to use for a specified column.

    The possible values that can be returned are: ``'left'``, ``'center'``
    or ``'right'``. All table items share the same alignment for a
    specified column.

:py:meth:`~TabularAdapter.get_width`
    Returns the width to use for a specified column.

    If the value is <= 0, the column will have a *default* width, which is
    the same as specifying a width of 0.1.

    If the value is > 1.0, it is converted to an integer and the result is
    the width of the column in pixels. This is referred to as a
    *fixed width* column.

    If the value is a float such that 0.0 < value <= 1.0, it is treated as
    the *unnormalized fraction of the available space* that is to be
    assigned to the column. What this means requires a little explanation.

    To arrive at the size in pixels of the column at any given time, the
    editor adds together all of the *unnormalized fraction* values
    returned for all columns in the table to arrive at a total value. Each
    *unnormalized fraction* is then divided by the total to create a
    *normalized fraction*. Each column is then assigned an amount of space
    in pixels equal to the maximum of 30 or its *normalized fraction*
    multiplied by the *available space*. The *available space* is defined
    as the actual width of the table minus the width of all *fixed width*
    columns. Note that this calculation is performed each time the table is
    resized in the user interface, thus allowing columns of this type to
    increase or decrease their width dynamically, while leaving *fixed
    width* columns unchanged.

:py:meth:`~TabularAdapter.get_can_edit`
    Returns whether the user can edit a specified row.

    A ``True`` result indicates that the value can be edited, while a
    ``False`` result indicates that it cannot.

:py:meth:`~TabularAdapter.get_drag`
    Returns the value to be *dragged* for a specified row.

    A result of ``None`` means that the item cannot be dragged. Note that
    the value returned does not have to be the actual row item. It can be
    any value that you want to drag in its place. In particular, if you
    want the drag target to receive a copy of the row item, you should
    return a copy or clone of the item in its place.

    Also note that if multiple items are being dragged, and this method
    returns ``None`` for any item in the set, no drag operation is
    performed.

:py:meth:`~TabularAdapter.get_can_drop`
    Returns whether the specified ``value`` can be dropped on the specified row.

    A value of ``True`` means the ``value`` can be dropped; and a value of
    ``False`` indicates that it cannot be dropped.

    The result is used to provide the user positive or negative drag
    feedback while dragging items over the table. ``value`` will always be
    a single value, even if multiple items are being dragged. The editor
    handles multiple drag items by making a separate call to
    :py:meth:`get_can_drop` for each item being dragged.

:py:meth:`~TabularAdapter.get_dropped`
    Returns how to handle a specified ``value`` being dropped on a specified row.

    The possible return values are:

    - ``'before'``: Insert the specified ``value`` before the dropped on item.
    - ``'after'``: Insert the specified ``value`` after the dropped on item.

    Note there is no result indicating *do not drop* since you will have
    already indicated that the ``object`` can be dropped by the result
    returned from a previous call to :py:meth:`get_can_drop`.

:py:meth:`~TabularAdapter.get_font`
    Returns the font to use for displaying a specified row or cell.

    A result of ``None`` means use the default font; otherwise a toolkit
    font object should be returned. Note that all columns for the specified
    table row will use the font value returned.

:py:meth:`~TabularAdapter.get_text_color`
    Returns the text color to use for a specified row or cell.

    A result of ``None`` means use the default text color; otherwise a
    toolkit-compatible color should be returned. Note that all columns for
    the specified table row will use the text color value returned.

:py:meth:`~TabularAdapter.get_bg_color`
    Returns the background color to use for a specified row or cell.

    A result of ``None`` means use the default background color; otherwise
    a toolkit-compatible color should be returned. Note that all columns
    for the specified table row will use the background color value
    returned.

:py:meth:`~TabularAdapter.get_image`
    Returns the image to display for a specified cell.

    A result of ``None`` means no image will be displayed in the specified
    table cell. Otherwise the result should either be the name of the
    image, or an :py:class:`~pyface.image_resource.ImageResource` object
    specifying the image to display.

    A name is allowed in the case where the image is specified in the
    :py:class:`~traitsui.editors.tabular_editor.TabularEditor`
    :py:attr:`~traitsui.editors.tabular_editor.TabularEditor.images` trait.
    In that case, the name should be the same as the string specified in
    the :py:class:`~pyface.image_resource.ImageResource` constructor.

:py:meth:`~TabularAdapter.get_format`
    Returns the Python formatting string to apply to the specified cell.

    The resulting of formatting with this string will be used as the text
    to display it in the table.

    The return can be any Python string containing exactly one old-style
    Python formatting sequence, such as ``'%.4f'`` or ``'(%5.2f)'``.

:py:meth:`~TabularAdapter.get_text`
    Returns a string containing the text to display for a specified cell.

    If the underlying data representation for a specified item is not a
    string, then it is your responsibility to convert it to one before
    returning it as the result.

:py:meth:`~TabularAdapter.set_text`
    Sets the value for the specified cell.

    This method is called when the user completes an editing operation on a
    table cell.

    The string specified by ``text`` is the value that the user has
    entered in the table cell.  If the underlying data does not store the
    value as text, it is your responsibility to convert ``text`` to the
    correct representation used.

:py:meth:`~TabularAdapter.get_tooltip`
    Returns a string containing the tooltip to display for a specified cell.

    You should return the empty string if you do not wish to display a
    tooltip.

The following are the remaining adapter methods, which are not sensitive to the
type of item or column data:

:py:meth:`~TabularAdapter.get_item`
    Returns the specified row item.

    The value returned should be the value that exists (or *logically*
    exists) at the specified ``row`` in your data. If your data is not
    really a list or array, then you can just use ``row`` as an integer
    *key* or *token* that can be used to retrieve a corresponding item. The
    value of ``row`` will always be in the range: 0 <= row <
    ``len(object, trait)`` (i.e. the result returned by the adapter
    :py:meth:`len` method).

:py:meth:`~TabularAdapter.len`
    Returns the number of row items in the specified ``object.trait``.

    The result should be an integer greater than or equal to 0.

:py:meth:`~TabularAdapter.delete`
    Deletes the specified row item.

    This method is only called if the *delete* operation is specified in
    the :py:class:`~traitsui.editors.tabular_editor.TabularEditor`
    :py:attr:`~traitsui.editors.tabular_editor.TabularEditor.operation`
    trait, and the user requests that the item be deleted from the table.

    The adapter can still choose not to delete the specified item if
    desired, although that may prove confusing to the user.

:py:meth:`~TabularAdapter.insert`
    Inserts ``value`` at the specified ``object.trait[row]`` index.

    The specified ``value`` can be:

    - An item being moved from one location in the data to another.
    - A new item created by a previous call to
        :py:meth:`~TabularAdapter.get_default_value`.
    - An item the adapter previously approved via a call to
        :py:meth:`~TabularAdapter.get_can_drop`.

    The adapter can still choose not to insert the item into the data,
    although that may prove confusing to the user.

:py:meth:`~TabularAdapter.get_default_value`
    Returns a new default value for the specified ``object.trait`` list.

    This method is called when *insert* or *append* operations are allowed
    and the user requests that a new item be added to the table. The result
    should be a new instance of whatever underlying representation is being
    used for table items.

Creating a Custom TabularAdapter
--------------------------------

Having just taken a look at the core :py:class:`TabularAdapter` interface, you
might now be thinking that there are an awful lot of methods that need to be
specified to get an adapter up and running. But as we mentioned earlier
:py:class:`TabularAdapter` is not an abstract base class. It is a concrete base
class with implementations for each of the methods in its interface. And the
implementations are written in such a way that you will hopefully hardly ever
need to override them.

In this section, we'll explain the general implementation style used by these
methods, and how you can take advantage of them in creating your own adapters.

One of the things you probably noticed as you read through the core adapter
interface section is that most of the methods have names of the form:
``get_xxx`` or ``set_xxx``, which is similar to the familiar *getter/setter*
pattern used when defining trait properties. The adapter interface is purposely
defined this way so that it can expose and leverage a simple set of design rules.

The design rules are followed consistently in the implementations of all of the
adapter methods described in the first section of the core adapter interface, so
that once you understand how they work, you can easily apply the design pattern
to all items in that section. Then, only in the case where the design rules will
not work for your application will you ever have to override any of those
:py:class:`TabularAdapter` base class method implementations.

So the first thing to understand is that if an adapter method name has the form:
``get_xxx`` or ``set_xxx`` it really is dealing with some kind of trait called
``xxx``, or which contains ``xxx`` in its name. For example, the
:py:meth`~TabularAdapter.get_alignment` method retrieves the value of some
:py:attr:`~TabularAdapter.alignment` trait defined on the adapter.  In the
following discussion we'll simply refer to an attribute name generically as
*attribute*, but you will need to replace it by an actual attribute name (e.g.
:py:attr:`~TabularAdapter.alignment`) in your adapter.

The next thing to keep in mind is that the adapter interface is designed to
easily deal with items that are not all of the same type. As we just said, the
design rules apply to all adapter methods in the first group, which were
defined as methods which are sensitive to an item's type. Item type sensitivity
plays an important part in the design rules, as we will see shortly.

With this in mind, we now describe the simple design rules used by the first
group of methods in the :py:class:`TabularAdapter` class:

- When getting or setting an adapter attribute, the method first retrieves the
  underlying item for the specified data row. The item, and type (i.e. class) of
  the item, are then used in the next rule.

- The method gets or sets the first trait it finds on the adapter that matches
  one of the following names:

  - *classname_columnid_attribute*
  - *classsname_attribute*
  - *columnid_attribute*
  - *attribute*

  where:

  - *classname* is the name of the class of the item found in the first step, or
    one of its base class names, searched in the order defined by the *mro*
    (**method resolution order**) for the item's class.
  - *columnid* is the column id specified by the developer in the adapter's
    *column* trait for the specified table column.
  - *attribute* is the attribute name as described previously (e.g.
    *alignment*).

Note that this last rule always finds a matching trait, since the
:py:class:`TabularAdapter` base class provides traits that match the simple
*attribute* form for all attributes these rules apply to. Some of these are
simple traits, while others are properties. We'll describe the behavior of all
these *default* traits shortly.

The basic idea is that rather than override the first group of core adapter
methods, you simply define one or more simple traits or trait properties on
your :py:class:`TabularAdapter` subclass that provide or accept the specified
information.

All of the adapter methods in the first group provide a number of arguments,
such as ``object``, ``trait``, ``row`` and ``column``. In order to define a
trait property, which cannot be passed this information directly, the adapter
always stores the arguments and values it computes in the following adapter
traits, where they can be easily accessed by a trait getter or setter method:

- ``row``: The table row being accessed.
- ``column``: The column id of the table column being accessed (not its index).
- ``item``: The data item for the specified table row (i.e. the item determined
  in the first step described above).
- `value``: In the case of a *set_xxx* method, the value to be set; otherwise it
  is ``None``.

As mentioned previously, the :py:class:`TabularAdapter` class provides trait
definitions for all of the attributes these rules apply to. You can either use
the default values as they are, override the default, set a new value, or
completely replace the trait definition in a subclass. A description of the
default trait implementation for each attribute is as follows:

:py:attr:`~TabularAdapter.default_value` = ``Any('')``
    The default value for a new row.

    The default value is the empty string, but you will normally need to assign
    a different (default) value.

:py:attr:`~TabularAdapter.format` = ``Str('%s')``
    The default Python formatting string for a column item.

    The default value is ``'%s'`` which will simply convert the column item to
    a displayable string value.

:py:attr:`~TabularAdapter.text` = ``Property``
    The text to display for the column item.

    The implementation of the property checks the type of the column's
    *column id*:

    - If it is an integer, it returns ``format % item[column_id]``.
    - Otherwise, it returns ``format % item.column_id``.

    Note that ``format`` refers to the value returned by a call to
    :py:meth:`~TabularAdapter.get_format` for the current column item.

:py:attr:`~TabularAdapter.text_color` = ``Property``
    The text color for a row item.

    The property implementation checks to see if the current table row is even
    or odd, and based on the result returns the value of the
    :py:attr:`~TabularAdapter.even_text_color` or
    :py:attr:`~TabularAdapter.odd_text_color` trait if the value is not
    ``None``, and the value of the
    :py:attr:`~TabularAdapter.default_text_color` trait if it is. The
    definition of these additional traits are as follows:

    - :py:attr:`~TabularAdapter.odd_text_color` = ``Color(None)``
    - :py:attr:`~TabularAdapter.even_text_color` = ``Color(None)``
    - :py:attr:`~TabularAdapter.default_text_color` = ``Color(None)``

    Remember that a ``None`` value means use the default text color.

:py:attr:`~TabularAdapter.bg_color` = ``Property``
    The background color for a row item.

    The property implementation checks to see if the current table row is even
    or odd, and based on the result returns the value of the
    :py:attr:`~TabularAdapter.even_bg_color` or
    :py:attr:`~TabularAdapter.odd_bg_color` trait if the value is not ``None``,
    and the value of the :py:attr:`~TabularAdapter.default_bg_color` trait if
    it is. The definition of these additional traits are as follows:

    - :py:attr:`~TabularAdapter.odd_bg_color` = ``Color(None)``
    - :py:attr:`~TabularAdapter.even_bg_color` = ``Color(None)``
    - :py:attr:`~TabularAdapter.default_bg_color` = ``Color(None)``

    Remember that a ``None`` value means use the default background color.

:py:attr:`~TabularAdapter.alignment` = ``Enum('left', 'center', 'right')``
    The alignment to use for a specified column.

    The default value is ``'left'``.

:py:attr:`~TabularAdapter.width` = ``Float(-1)``
    The width of a specified column.

    The default value is -1, which means a dynamically sized column with an
    *unnormalized fractional* value of 0.1.

:py:attr:`~TabularAdapter.can_edit` = ``Bool(True)``
    Specifies whether the text value of the current item can be edited.

    The default value is ``True``, which means that the user can edit the
    value.

:py:attr:`~TabularAdapter.drag` = ``Property``
    A property which returns the value to be dragged for a specified row item.

    The property implementation simply returns the current row item.

:py:attr:`~TabularAdapter.can_drop` = ``Bool(False)``
    Specifies whether the specified value be dropped on the current item.

    The default value is ``False``, meaning that the value cannot be dropped.

:py:attr:`~TabularAdapter.dropped` = ``Enum('after', 'before')``
    Specifies where a dropped item should be placed in the table relative to
    the item it is dropped on.

    The default value is ``'after'``.

:py:attr:`~TabularAdapter.font` = ``Font``
    The font to use for the current item.

    The default value is the standard default Traits font value.

:py:attr:`~TabularAdapter.image` = ``Str(None)``
    The name of the default image to use for a column.

    The default value is ``None``, which means that no image will be displayed
    for the column.

:py:attr:`~TabularAdapter.tooltip` = ``Str``
    The tooltip information for a column item.

    The default value is the empty string, which means no tooltip information
    will be displayed for the column.

The preceding discussion applies to all of the methods defined in the first
group of :py:attr:`TabularAdapter` interface methods. However, the design rules
do not apply to the remaining five adapter methods, although they all provide a
useful default implementation:

:py:meth:`~TabularAdapter.get_item`
    The default implementation assumes the trait defined by ``object.trait`` is
    a *sequence* and attempts to return the value at index ``row``. If an error
    occurs, it returns ``None`` instead. This definition should work correctly
    for lists, tuples and arrays, or any other object that is indexable, but
    will have to be overridden for all other cases.

    Note that this method is the one called in the first design rule described
    previously to retrieve the item at the current table row.

:py:meth:`~TabularAdapter.len`
    Again, the default implementation assumes the trait defined by
    ``object.trait`` is a *sequence* and attempts to return the result of
    calling ``len(object.trait)``. It will need to be overridden for any type
    of data which for which :py:func:`len` will not work.

:py:meth:`~TabularAdapter.delete`
    The default implementation assumes the trait defined by ``object.trait`` is
    a mutable sequence and attempts to perform a ``del object.trait[row]``
    operation.

:py:meth:`~TabularAdapter.insert`
    The default implementation assumes the trait defined by ``object.trait`` is
    a mutable sequence and attempts to perform an
    ``object.trait[row:row] = [value]`` operation.

:py:meth:`~TabularAdapter.get_default_value`
    The default implementation simply returns the value of the adapter's
    :py:attr:`~TabularAdapter.default_value` trait.

Examples
--------

There are a number of examples of use of the :py:class:`TabularAdapter` in the
TraitsUI demos:

- :github-demo:`TabularEditor <Advanced/Tabular_editor_demo.py>`
- :github-demo:`TabularEditor (auto-update) <Advanced/Auto_update_TabularEditor_demo.py>`
- :github-demo:`NumPy array TabularEditor <Advanced/NumPy_array_tabular_editor_demo.py>`


The ListStrAdapter Class
========================

.. module:: traitsui.list_str_adapter

Although the :py:class:`~traitsui.editors.list_str_editor.ListStrEditor` editor
is frequently used, as might be expected, with lists of strings, it also
provides facilities to edit lists of other object types that can be adapted
to produce strings for display and editing via :py:class:`ListStrAdapter`
subclasses

The design of the :py:class:`ListStrAdapter` base class follows the same
design as the :py:class:`~traitsui.tabular_adapter.TabularAdapter`, simplified
by the fact that there are only rows, no columns.  However, the names and
intents of the various methods and traits are the same as the
:py:class:`~traitsui.tabular_adapter.TabularAdapter`, and so the approaches
discussed in the previous section work for the :py:class:`ListStrAdapter` as
well.
