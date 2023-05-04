# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Defines the tree node descriptor used by the tree editor and tree editor
    factory classes.
"""

from itertools import zip_longest


from traits.api import (
    Adapter,
    Any,
    Bool,
    Callable,
    Dict,
    HasPrivateTraits,
    Instance,
    Interface,
    isinterface,
    List,
    Property,
    Str,
    Supports,
    Union,
    cached_property,
)

from traits.trait_base import (
    SequenceTypes,
    get_resource_path,
    xgetattr,
    xsetattr,
)

from .ui_traits import AView

# -------------------------------------------------------------------------
#  'TreeNode' class:
# -------------------------------------------------------------------------


class TreeNode(HasPrivateTraits):
    """Represents a tree node. Used by the tree editor and tree editor factory
    classes.
    """

    # -------------------------------------------------------------------------
    #  Trait definitions:
    # -------------------------------------------------------------------------

    #: Name of trait containing children (if '', the node is a leaf). Nested
    #: attributes are allowed, e.g., 'library.books'
    children = Str()

    #: Either the name of a trait containing a label, or a constant label, if
    #: the string starts with '='.
    label = Str()

    #: The name of a trait containing a list of labels for any columns.
    column_labels = Str()

    #: Either the name of a trait containing a tooltip, or constant tooltip, if
    #: the string starts with '='.
    tooltip = Str()

    #: Name to use for a new instance
    name = Str()

    #: Can the object's children be renamed?
    rename = Bool(True)

    #: Can the object be renamed?
    rename_me = Bool(True)

    #: Can the object's children be copied?
    copy = Bool(True)

    #: Can the object's children be deleted?
    delete = Bool(True)

    #: Can the object be deleted (if its parent allows it)?
    delete_me = Bool(True)

    #: Can children be inserted (vs. appended)?
    insert = Bool(True)

    #: Should tree nodes be automatically opened (expanded)?
    auto_open = Bool(False)

    #: Automatically close sibling tree nodes?
    auto_close = Bool(False)

    #: List of object classes than can be added or copied. Elements of the list
    #: can be either:
    #:
    #: - the klass itself that can be added or copied
    #: - 2-tuples of the form (klass, prompt) in which case klass is as above
    #:   and prompt is a boolean indicating whether or not to prompt the user
    #:   to specify trait values after instantiation when adding the object.
    #: - 3-tuples of the form (klass, prompt, factory) in which case klass and
    #:   prompt are as above.  factory is a callable that is expected to return
    #:   an instance of klass.  Useful if klass has required traits. Otherwise
    #:   added object is created by simply instantiating klass()
    #:   ref: enthought/traits#1502
    add = List(Any)

    #: List of object classes that can be moved
    move = List(Any)

    #: List of object classes and/or interfaces that the node applies to
    node_for = List(Any)

    #: Tuple of object classes that the node applies to
    node_for_class = Property(observe="node_for")

    #: List of object interfaces that the node applies to
    node_for_interface = Property(observe="node_for")

    #: Function for formatting the label
    formatter = Callable()

    #: Functions for formatting the other columns.
    column_formatters = List(Union(None, Callable))

    #: Function for formatting the tooltip
    tooltip_formatter = Callable()

    #: Function for handling selecting an object
    on_select = Callable()

    #: Function for handling clicking an object
    on_click = Callable()

    #: Function for handling double-clicking an object
    on_dclick = Callable()

    #: Function for handling activation of an object
    #: (double-click or Enter key press when node is in focus)
    on_activated = Callable()

    #: View to use for editing the object
    view = AView

    #: Right-click context menu. The value can be one of:
    #:
    #: - Instance( Menu ): Use this menu as the context menu
    #: - None: Use the default context menu
    #: - False: Do not display a context menu
    menu = Any()

    #: Name of leaf item icon
    icon_item = Str("<item>")

    #: Name of group item icon
    icon_group = Str("<group>")

    #: Name of opened group item icon
    icon_open = Str("<open>")

    #: Resource path used to locate the node icon
    icon_path = Str()

    #: Selector or name for background color
    background = Any()

    #: Selector or name for foreground color
    foreground = Any()

    # fixme: The 'menu' trait should really be defined as:
    #        Instance( 'traitsui.menu.MenuBar' ), but it doesn't work
    #        right currently.

    #: A toolkit-appropriate cell renderer (currently Qt only)
    renderer = Any()

    #: A cache for listeners that need to keep state.
    _listener_cache = Dict()

    def __init__(self, **traits):
        super().__init__(**traits)
        if self.icon_path == "":
            self.icon_path = get_resource_path()

    # -- Property Implementations ---------------------------------------------

    @cached_property
    def _get_node_for_class(self):
        return tuple(
            [klass for klass in self.node_for if not isinterface(klass)]
        )

    @cached_property
    def _get_node_for_interface(self):
        return [klass for klass in self.node_for if isinterface(klass)]

    # -- Overridable Methods: -------------------------------------------------

    def allows_children(self, object):
        """Returns whether this object can have children."""
        return self.children != ""

    def has_children(self, object):
        """Returns whether the object has children."""
        return len(self.get_children(object)) > 0

    def get_children(self, object):
        """Gets the object's children."""
        return getattr(object, self.children, None)

    def get_children_id(self, object):
        """Gets the object's children identifier."""
        return self.children

    def append_child(self, object, child):
        """Appends a child to the object's children."""
        children = self.get_children(object)
        children.append(child)

    def insert_child(self, object, index, child):
        """Inserts a child into the object's children."""
        children = self.get_children(object)
        children[index:index] = [child]

    def confirm_delete(self, object):
        """Checks whether a specified object can be deleted.

        The following return values are possible:

        - **True** if the object should be deleted with no further prompting.
        - **False** if the object should not be deleted.
        - Anything else: Caller should take its default action (which might
          include prompting the user to confirm deletion).
        """
        return None

    def delete_child(self, object, index):
        """Deletes a child at a specified index from the object's children."""
        del self.get_children(object)[index]

    def when_children_replaced(self, object, listener, remove):
        """Sets up or removes a listener for children being replaced on a
        specified object.
        """
        object.on_trait_change(
            listener, self.children, remove=remove, dispatch="ui"
        )

    def when_children_changed(self, object, listener, remove):
        """Sets up or removes a listener for children being changed on a
        specified object.
        """
        object.on_trait_change(
            listener,
            self.children + "_items",
            remove=remove,
            dispatch="ui",
        )

    def get_label(self, object):
        """Gets the label to display for a specified object."""
        label = self.label
        if label[:1] == "=":
            return label[1:]

        label = xgetattr(object, label, "")

        if self.formatter is None:
            return label

        return self.formatter(object, label)

    def set_label(self, object, label):
        """Sets the label for a specified object."""
        label_name = self.label
        if label_name[:1] != "=":
            xsetattr(object, label_name, label)

    def when_label_changed(self, object, listener, remove):
        """Sets up or removes a listener for the label being changed on a
        specified object.
        """
        label = self.label
        if label[:1] != "=":
            memo = ("label", label, object, listener)
            if not remove:

                def wrapped_listener(target, name, new):
                    """Ensure listener gets called with correct object."""
                    return listener(object, name, new)

                self._listener_cache[memo] = wrapped_listener
            else:
                wrapped_listener = self._listener_cache.pop(memo, None)
                if wrapped_listener is None:
                    return

            object.on_trait_change(
                wrapped_listener, label, remove=remove, dispatch="ui"
            )

    def get_column_labels(self, object):
        """Get the labels for any columns that have been defined."""
        trait = self.column_labels
        labels = xgetattr(object, trait, [])
        formatted = []
        for formatter, label in zip_longest(self.column_formatters, labels):
            # If the list of column formatters is shorter than the list of
            # labels, then zip_longest() will extend it with Nones. Just pass
            # the label as preformatted. Similarly, explicitly using None in
            # the list will pass through the item.
            if formatter is None:
                formatted.append(label)
            else:
                formatted.append(formatter(label))
        return formatted

    def when_column_labels_change(self, object, listener, remove):
        """Sets up or removes a listener for the column labels being changed on
        a specified object.

        This will fire when either the list is reassigned or when it is
        modified. I.e., it listens both to the trait change event and the
        trait_items change event. Implement the listener appropriately to
        handle either case.
        """
        trait = self.column_labels
        if trait != "":
            memo = ("column_label", trait, object, listener)
            if not remove:

                def wrapped_listener(target, name, new):
                    """Ensure listener gets called with correct object."""
                    return listener(object, name, new)

                self._listener_cache[memo] = wrapped_listener
            else:
                wrapped_listener = self._listener_cache.pop(memo, None)
                if wrapped_listener is None:
                    return

            object.on_trait_change(
                wrapped_listener, trait, remove=remove, dispatch="ui"
            )
            object.on_trait_change(
                wrapped_listener,
                trait + "_items",
                remove=remove,
                dispatch="ui",
            )

    def get_tooltip(self, object):
        """Gets the tooltip to display for a specified object."""
        tooltip = self.tooltip
        if tooltip == "":
            return tooltip

        if tooltip[:1] == "=":
            return tooltip[1:]

        tooltip = xgetattr(object, tooltip, "")

        if self.tooltip_formatter is None:
            return tooltip

        return self.tooltip_formatter(object, tooltip)

    def get_icon(self, object, is_expanded):
        """Returns the icon for a specified object."""
        if not self.allows_children(object):
            return self.icon_item

        if is_expanded:
            return self.icon_open

        return self.icon_group

    def get_icon_path(self, object):
        """Returns the path used to locate an object's icon."""
        return self.icon_path

    def get_name(self, object):
        """Returns the name to use when adding a new object instance
        (displayed in the "New" submenu).
        """
        return self.name

    def get_view(self, object):
        """Gets the view to use when editing an object."""
        return self.view

    def get_menu(self, object):
        """Returns the right-click context menu for an object."""
        return self.menu

    def get_background(self, object):
        background = self.background
        if isinstance(background, str):
            background = xgetattr(object, background, default=background)
        return background

    def get_foreground(self, object):
        foreground = self.foreground
        if isinstance(foreground, str):
            foreground = xgetattr(object, foreground, default=foreground)
        return foreground

    def get_renderer(self, object, column=0):
        """Return the renderer for the object and column."""
        return self.renderer

    def can_rename(self, object):
        """Returns whether the object's children can be renamed."""
        return self.rename

    def can_rename_me(self, object):
        """Returns whether the object can be renamed."""
        return self.rename_me

    def can_copy(self, object):
        """Returns whether the object's children can be copied."""
        return self.copy

    def can_delete(self, object):
        """Returns whether the object's children can be deleted."""
        return self.delete

    def can_delete_me(self, object):
        """Returns whether the object can be deleted."""
        return self.delete_me

    def can_insert(self, object):
        """Returns whether the object's children can be inserted (vs.
        appended).
        """
        return self.insert

    def can_auto_open(self, object):
        """Returns whether the object's children should be automatically
        opened.
        """
        return self.auto_open

    def can_auto_close(self, object):
        """Returns whether the object's children should be automatically
        closed.
        """
        return self.auto_close

    def is_node_for(self, object):
        """Returns whether this is the node that handles a specified object."""
        return isinstance(
            object, self.node_for_class
        ) or object.has_traits_interface(*self.node_for_interface)

    def can_add(self, object, add_object):
        """Returns whether a given object is droppable on the node."""
        klass = self._class_for(add_object)
        if self.is_addable(klass):
            return True

        for item in self.move:
            if type(item) in SequenceTypes:
                item = item[0]
            if issubclass(klass, item):
                return True

        return False

    def get_add(self, object):
        """Returns the list of classes that can be added to the object."""
        return self.add

    def get_drag_object(self, object):
        """Returns a draggable version of a specified object."""
        return object

    def drop_object(self, object, dropped_object):
        """Returns a droppable version of a specified object."""
        klass = self._class_for(dropped_object)
        if self.is_addable(klass):
            return dropped_object

        for item in self.move:
            if type(item) in SequenceTypes:
                if issubclass(klass, item[0]):
                    return item[1](object, dropped_object)
            elif issubclass(klass, item):
                return dropped_object

        return dropped_object

    def select(self, object):
        """Handles an object being selected."""
        if self.on_select is not None:
            self.on_select(object)
            return None

        return True

    def click(self, object):
        """Handles an object being clicked."""
        if self.on_click is not None:
            self.on_click(object)
            return None

        return True

    def dclick(self, object):
        """Handles an object being double-clicked."""
        if self.on_dclick is not None:
            self.on_dclick(object)
            return None

        return True

    def activated(self, object):
        """Handles an object being activated."""
        if self.on_activated is not None:
            self.on_activated(object)
            return None

        return True

    def is_addable(self, klass):
        """Returns whether a specified object class can be added to the node."""
        for item in self.add:
            if type(item) in SequenceTypes:
                item = item[0]

            if issubclass(klass, item):
                return True

        return False

    def _class_for(self, object):
        """Returns the class of an object."""
        if isinstance(object, type):
            return object

        return object.__class__


# -------------------------------------------------------------------------
#  'ITreeNode' class
# -------------------------------------------------------------------------


class ITreeNode(Interface):
    def allows_children(self):
        """Returns whether this object can have children."""

    def has_children(self):
        """Returns whether the object has children."""

    def get_children(self):
        """Gets the object's children."""

    def get_children_id(self):
        """Gets the object's children identifier."""

    def append_child(self, child):
        """Appends a child to the object's children."""

    def insert_child(self, index, child):
        """Inserts a child into the object's children."""

    def confirm_delete(self):
        """Checks whether a specified object can be deleted.

        The following return values are possible:

        - **True** if the object should be deleted with no further prompting.
        - **False** if the object should not be deleted.
        - Anything else: Caller should take its default action (which might
          include prompting the user to confirm deletion).
        """

    def delete_child(self, index):
        """Deletes a child at a specified index from the object's children."""

    def when_children_replaced(self, listener, remove):
        """Sets up or removes a listener for children being replaced on a
        specified object.
        """

    def when_children_changed(self, listener, remove):
        """Sets up or removes a listener for children being changed on a
        specified object.
        """

    def get_label(self):
        """Gets the label to display for a specified object."""

    def set_label(self, label):
        """Sets the label for a specified object."""

    def when_label_changed(self, listener, remove):
        """Sets up or removes a listener for the label being changed on a
        specified object.
        """

    def get_column_labels(self, object):
        """Get the labels for any columns that have been defined."""

    def when_column_labels_change(self, object, listener, remove):
        """Sets up or removes a listener for the column labels being changed
        on a specified object.

        This will fire when either the list is reassigned or when it is
        modified. I.e., it listens both to the trait change event and the
        trait_items change event. Implement the listener appropriately to
        handle either case.
        """

    def get_tooltip(self):
        """Gets the tooltip to display for a specified object."""

    def get_icon(self, is_expanded):
        """Returns the icon for a specified object."""

    def get_icon_path(self):
        """Returns the path used to locate an object's icon."""

    def get_name(self):
        """Returns the name to use when adding a new object instance
        (displayed in the "New" submenu).
        """

    def get_view(self):
        """Gets the view to use when editing an object."""

    def get_menu(self):
        """Returns the right-click context menu for an object."""

    def can_rename(self):
        """Returns whether the object's children can be renamed."""

    def can_rename_me(self):
        """Returns whether the object can be renamed."""

    def can_copy(self):
        """Returns whether the object's children can be copied."""

    def can_delete(self):
        """Returns whether the object's children can be deleted."""

    def can_delete_me(self):
        """Returns whether the object can be deleted."""

    def can_insert(self):
        """Returns whether the object's children can be inserted (vs.
        appended).
        """

    def can_auto_open(self):
        """Returns whether the object's children should be automatically
        opened.
        """

    def can_auto_close(self):
        """Returns whether the object's children should be automatically
        closed.
        """

    def can_add(self, add_object):
        """Returns whether a given object is droppable on the node."""

    def get_add(self):
        """Returns the list of classes that can be added to the object."""

    def get_drag_object(self):
        """Returns a draggable version of a specified object."""

    def drop_object(self, dropped_object):
        """Returns a droppable version of a specified object."""

    def select(self):
        """Handles an object being selected."""

    def click(self):
        """Handles an object being clicked."""

    def dclick(self):
        """Handles an object being double-clicked."""

    def activated(self):
        """Handles an object being activated."""


# -------------------------------------------------------------------------
#  'ITreeNodeAdapter' class
# -------------------------------------------------------------------------


class ITreeNodeAdapter(Adapter):
    """Abstract base class for an adapter that implements the ITreeNode
    interface.

    Usage:

    1. Create a subclass of ITreeNodeAdapter.
    2. Register the adapter to define what class (or classes) this is an
       ITreeNode adapter for (ie.
       ``register_factory(<from class>, ITreeNode, ITreeNodeAdapter)``).
    3. Override any of the following methods as necessary, using the
       ``self.adaptee`` trait to access the adapted object if needed.

    Note
    ----
    This base class implements all of the ITreeNode interface methods,
    but does not necessarily provide useful implementations for all of the
    methods. It allows you to get a new adapter class up and running quickly,
    but you should carefully review your final adapter implementation class
    to make sure it behaves correctly in your application.
    """

    def allows_children(self):
        """Returns whether this object can have children."""
        return False

    def has_children(self):
        """Returns whether the object has children."""
        return False

    def get_children(self):
        """Gets the object's children."""
        return []

    def get_children_id(self):
        """Gets the object's children identifier."""
        return ""

    def append_child(self, child):
        """Appends a child to the object's children."""
        pass

    def insert_child(self, index, child):
        """Inserts a child into the object's children."""
        pass

    def confirm_delete(self):
        """Checks whether a specified object can be deleted.

        The following return values are possible:

        - **True** if the object should be deleted with no further prompting.
        - **False** if the object should not be deleted.
        - Anything else: Caller should take its default action (which might
          include prompting the user to confirm deletion).
        """
        return False

    def delete_child(self, index):
        """Deletes a child at a specified index from the object's children."""
        pass

    def when_children_replaced(self, listener, remove):
        """Sets up or removes a listener for children being replaced on a
        specified object.
        """
        pass

    def when_children_changed(self, listener, remove):
        """Sets up or removes a listener for children being changed on a
        specified object.
        """
        pass

    def get_label(self):
        """Gets the label to display for a specified object."""
        return "No label specified"

    def set_label(self, label):
        """Sets the label for a specified object."""
        pass

    def when_label_changed(self, listener, remove):
        """Sets up or removes a listener for the label being changed on a
        specified object.
        """
        pass

    def get_column_labels(self):
        """Get the labels for any columns that have been defined."""
        return []

    def when_column_labels_change(self, listener, remove):
        """Sets up or removes a listener for the column labels being changed
        on a specified object.

        This will fire when either the list is reassigned or when it is
        modified. I.e., it listens both to the trait change event and the
        trait_items change event. Implement the listener appropriately to
        handle either case.
        """
        pass

    def get_tooltip(self):
        """Gets the tooltip to display for a specified object."""
        return ""

    def get_icon(self, is_expanded):
        """Returns the icon for a specified object.

        Valid values are '<item>' (file looking icon), '<group>' (closed folder
        looking icon) and '<open>' (open folder looking icon).
        """
        return "<item>"

    def get_icon_path(self):
        """Returns the path used to locate an object's icon."""
        return ""

    def get_name(self):
        """Returns the name to use when adding a new object instance
        (displayed in the "New" submenu).
        """
        return ""

    def get_view(self):
        """Gets the view to use when editing an object."""
        return None

    def get_menu(self):
        """Returns the right-click context menu for an object."""
        return None

    def get_background(self):
        """Returns the background for object"""
        return None

    def get_foreground(self):
        """Returns the foreground for object"""
        return None

    def get_renderer(self, column=0):
        """Returns the renderer for object"""
        return None

    def can_rename(self):
        """Returns whether the object's children can be renamed."""
        return False

    def can_rename_me(self):
        """Returns whether the object can be renamed."""
        return False

    def can_copy(self):
        """Returns whether the object's children can be copied."""
        return False

    def can_delete(self):
        """Returns whether the object's children can be deleted."""
        return False

    def can_delete_me(self):
        """Returns whether the object can be deleted."""
        return False

    def can_insert(self):
        """Returns whether the object's children can be inserted (vs.
        appended).
        """
        return False

    def can_auto_open(self):
        """Returns whether the object's children should be automatically
        opened.
        """
        return False

    def can_auto_close(self):
        """Returns whether the object's children should be automatically
        closed.
        """
        return False

    def can_add(self, add_object):
        """Returns whether a given object is droppable on the node."""
        return False

    def get_add(self):
        """Returns the list of classes that can be added to the object."""
        return []

    def get_drag_object(self):
        """Returns a draggable version of a specified object."""
        return self.adaptee

    def drop_object(self, dropped_object):
        """Returns a droppable version of a specified object."""
        return dropped_object

    def select(self):
        """Handles an object being selected."""
        pass

    def click(self):
        """Handles an object being clicked."""
        pass

    def dclick(self):
        """Handles an object being double-clicked."""
        pass

    def activated(self):
        """Handles an object being activated."""
        pass


# -------------------------------------------------------------------------
#  'ITreeNodeAdapterBridge' class
# -------------------------------------------------------------------------


class ITreeNodeAdapterBridge(HasPrivateTraits):
    """Private class for use by a toolkit-specific implementation of the
    TreeEditor to allow bridging the TreeNode interface used by the editor
    to the ITreeNode interface used by object adapters.
    """

    #: The ITreeNode adapter being bridged:
    adapter = Supports(ITreeNode)

    # -- TreeNode implementation ----------------------------------------------

    def allows_children(self, object):
        """Returns whether this object can have children."""
        return self.adapter.allows_children()

    def has_children(self, object):
        """Returns whether the object has children."""
        return self.adapter.has_children()

    def get_children(self, object):
        """Gets the object's children."""
        return self.adapter.get_children()

    def get_children_id(self, object):
        """Gets the object's children identifier."""
        return self.adapter.get_children_id()

    def append_child(self, object, child):
        """Appends a child to the object's children."""
        return self.adapter.append_child(child)

    def insert_child(self, object, index, child):
        """Inserts a child into the object's children."""
        return self.adapter.insert_child(index, child)

    def confirm_delete(self, object):
        """Checks whether a specified object can be deleted.

        The following return values are possible:

        - **True** if the object should be deleted with no further prompting.
        - **False** if the object should not be deleted.
        - Anything else: Caller should take its default action (which might
          include prompting the user to confirm deletion).
        """
        return self.adapter.confirm_delete()

    def delete_child(self, object, index):
        """Deletes a child at a specified index from the object's children."""
        return self.adapter.delete_child(index)

    def when_children_replaced(self, object, listener, remove):
        """Sets up or removes a listener for children being replaced on a
        specified object.
        """
        return self.adapter.when_children_replaced(listener, remove)

    def when_children_changed(self, object, listener, remove):
        """Sets up or removes a listener for children being changed on a
        specified object.
        """
        return self.adapter.when_children_changed(listener, remove)

    def get_label(self, object):
        """Gets the label to display for a specified object."""
        return self.adapter.get_label()

    def set_label(self, object, label):
        """Sets the label for a specified object."""
        return self.adapter.set_label(label)

    def when_label_changed(self, object, listener, remove):
        """Sets up or removes a listener for the label being changed on a
        specified object.
        """
        return self.adapter.when_label_changed(listener, remove)

    def get_column_labels(self, object):
        """Get the labels for any columns that have been defined."""
        return self.adapter.get_column_labels()

    def when_column_labels_change(self, object, listener, remove):
        """Sets up or removes a listener for the column labels being changed
        on a specified object.

        This will fire when either the list is reassigned or when it is
        modified. I.e., it listens both to the trait change event and the
        trait_items change event. Implement the listener appropriately to
        handle either case.
        """
        return self.adapter.when_column_labels_change(listener, remove)

    def get_tooltip(self, object):
        """Gets the tooltip to display for a specified object."""
        return self.adapter.get_tooltip()

    def get_icon(self, object, is_expanded):
        """Returns the icon for a specified object."""
        return self.adapter.get_icon(is_expanded)

    def get_icon_path(self, object):
        """Returns the path used to locate an object's icon."""
        return self.adapter.get_icon_path()

    def get_name(self, object):
        """Returns the name to use when adding a new object instance
        (displayed in the "New" submenu).
        """
        return self.adapter.get_name()

    def get_view(self, object):
        """Gets the view to use when editing an object."""
        return self.adapter.get_view()

    def get_menu(self, object):
        """Returns the right-click context menu for an object."""
        return self.adapter.get_menu()

    def get_background(self, object):
        """Returns the background for object"""
        return self.adapter.get_background()

    def get_foreground(self, object):
        """Returns the foreground for object"""
        return self.adapter.get_foreground()

    def get_renderer(self, object, column=0):
        """Returns the renderer for object"""
        return self.adapter.get_renderer(column)

    def can_rename(self, object):
        """Returns whether the object's children can be renamed."""
        return self.adapter.can_rename()

    def can_rename_me(self, object):
        """Returns whether the object can be renamed."""
        return self.adapter.can_rename_me()

    def can_copy(self, object):
        """Returns whether the object's children can be copied."""
        return self.adapter.can_copy()

    def can_delete(self, object):
        """Returns whether the object's children can be deleted."""
        return self.adapter.can_delete()

    def can_delete_me(self, object):
        """Returns whether the object can be deleted."""
        return self.adapter.can_delete_me()

    def can_insert(self, object):
        """Returns whether the object's children can be inserted (vs.
        appended).
        """
        return self.adapter.can_insert()

    def can_auto_open(self, object):
        """Returns whether the object's children should be automatically
        opened.
        """
        return self.adapter.can_auto_open()

    def can_auto_close(self, object):
        """Returns whether the object's children should be automatically
        closed.
        """
        return self.adapter.can_auto_close()

    def can_add(self, object, add_object):
        """Returns whether a given object is droppable on the node."""
        return self.adapter.can_add(add_object)

    def get_add(self, object):
        """Returns the list of classes that can be added to the object."""
        return self.adapter.get_add()

    def get_drag_object(self, object):
        """Returns a draggable version of a specified object."""
        return self.adapter.get_drag_object()

    def drop_object(self, object, dropped_object):
        """Returns a droppable version of a specified object."""
        return self.adapter.drop_object(dropped_object)

    def select(self, object):
        """Handles an object being selected."""
        return self.adapter.select()

    def click(self, object):
        """Handles an object being clicked."""
        return self.adapter.click()

    def dclick(self, object):
        """Handles an object being double-clicked."""
        return self.adapter.dclick()

    def activated(self, object):
        """Handles an object being activated."""
        return self.adapter.activated()


# FIXME RTK: add the column_labels API to the following TreeNodes, too.


# -------------------------------------------------------------------------
#  'ObjectTreeNode' class
# -------------------------------------------------------------------------


class ObjectTreeNode(TreeNode):
    def allows_children(self, object):
        """Returns whether this object can have children."""
        return object.tno_allows_children(self)

    def has_children(self, object):
        """Returns whether the object has children."""
        return object.tno_has_children(self)

    def get_children(self, object):
        """Gets the object's children."""
        return object.tno_get_children(self)

    def get_children_id(self, object):
        """Gets the object's children identifier."""
        return object.tno_get_children_id(self)

    def append_child(self, object, child):
        """Appends a child to the object's children."""
        return object.tno_append_child(self, child)

    def insert_child(self, object, index, child):
        """Inserts a child into the object's children."""
        return object.tno_insert_child(self, index, child)

    def confirm_delete(self, object):
        """Checks whether a specified object can be deleted.

        The following return values are possible:

        - **True** if the object should be deleted with no further prompting.
        - **False** if the object should not be deleted.
        - Anything else: Caller should take its default action (which might
          include prompting the user to confirm deletion).
        """
        return object.tno_confirm_delete(self)

    def delete_child(self, object, index):
        """Deletes a child at a specified index from the object's children."""
        return object.tno_delete_child(self, index)

    def when_children_replaced(self, object, listener, remove):
        """Sets up or removes a listener for children being replaced on a
        specified object.
        """
        return object.tno_when_children_replaced(self, listener, remove)

    def when_children_changed(self, object, listener, remove):
        """Sets up or removes a listener for children being changed on a
        specified object.
        """
        return object.tno_when_children_changed(self, listener, remove)

    def get_label(self, object):
        """Gets the label to display for a specified object."""
        return object.tno_get_label(self)

    def set_label(self, object, label):
        """Sets the label for a specified object."""
        return object.tno_set_label(self, label)

    def when_label_changed(self, object, listener, remove):
        """Sets up or removes a listener for the label being changed on a
        specified object.
        """
        return object.tno_when_label_changed(self, listener, remove)

    def get_tooltip(self, object):
        """Gets the tooltip to display for a specified object."""
        return object.tno_get_tooltip(self)

    def get_icon(self, object, is_expanded):
        """Returns the icon for a specified object."""
        return object.tno_get_icon(self, is_expanded)

    def get_icon_path(self, object):
        """Returns the path used to locate an object's icon."""
        return object.tno_get_icon_path(self)

    def get_name(self, object):
        """Returns the name to use when adding a new object instance
        (displayed in the "New" submenu).
        """
        return object.tno_get_name(self)

    def get_view(self, object):
        """Gets the view to use when editing an object."""
        return object.tno_get_view(self)

    def get_menu(self, object):
        """Returns the right-click context menu for an object."""
        return object.tno_get_menu(self)

    def can_rename(self, object):
        """Returns whether the object's children can be renamed."""
        return object.tno_can_rename(self)

    def can_rename_me(self, object):
        """Returns whether the object can be renamed."""
        return object.tno_can_rename_me(self)

    def can_copy(self, object):
        """Returns whether the object's children can be copied."""
        return object.tno_can_copy(self)

    def can_delete(self, object):
        """Returns whether the object's children can be deleted."""
        return object.tno_can_delete(self)

    def can_delete_me(self, object):
        """Returns whether the object can be deleted."""
        return object.tno_can_delete_me(self)

    def can_insert(self, object):
        """Returns whether the object's children can be inserted (vs.
        appended).
        """
        return object.tno_can_insert(self)

    def can_auto_open(self, object):
        """Returns whether the object's children should be automatically
        opened.
        """
        return object.tno_can_auto_open(self)

    def can_auto_close(self, object):
        """Returns whether the object's children should be automatically
        closed.
        """
        return object.tno_can_auto_close(self)

    def is_node_for(self, object):
        """Returns whether this is the node that should handle a
        specified object.
        """
        if isinstance(object, TreeNodeObject):
            return object.tno_is_node_for(self)

        return False

    def can_add(self, object, add_object):
        """Returns whether a given object is droppable on the node."""
        return object.tno_can_add(self, add_object)

    def get_add(self, object):
        """Returns the list of classes that can be added to the object."""
        return object.tno_get_add(self)

    def get_drag_object(self, object):
        """Returns a draggable version of a specified object."""
        return object.tno_get_drag_object(self)

    def drop_object(self, object, dropped_object):
        """Returns a droppable version of a specified object."""
        return object.tno_drop_object(self, dropped_object)

    def select(self, object):
        """Handles an object being selected."""
        return object.tno_select(self)

    def click(self, object):
        """Handles an object being clicked."""
        return object.tno_click(self)

    def dclick(self, object):
        """Handles an object being double-clicked."""
        return object.tno_dclick(self)

    def activated(self, object):
        """Handles an object being activated."""
        return object.tno_activated(self)


class TreeNodeObject(HasPrivateTraits):
    """Represents the object that corresponds to a tree node."""

    #: A cache for listeners that need to keep state.
    _listener_cache = Dict()

    def tno_allows_children(self, node):
        """Returns whether this object allows children."""
        return node.children != ""

    def tno_has_children(self, node):
        """Returns whether this object has children."""
        return len(self.tno_get_children(node)) > 0

    def tno_get_children(self, node):
        """Gets the object's children."""
        return getattr(self, node.children, None)

    def tno_get_children_id(self, node):
        """Gets the object's children identifier."""
        return node.children

    def tno_append_child(self, node, child):
        """Appends a child to the object's children."""
        self.tno_get_children(node).append(child)

    def tno_insert_child(self, node, index, child):
        """Inserts a child into the object's children."""
        children = self.tno_get_children(node)
        children[index:index] = [child]

    def tno_confirm_delete(self, node):
        """Checks whether a specified object can be deleted.

        The following return values are possible:

        - **True** if the object should be deleted with no further prompting.
        - **False** if the object should not be deleted.
        - Anything else: Caller should take its default action (which might
          include prompting the user to confirm deletion).
        """
        return None

    def tno_delete_child(self, node, index):
        """Deletes a child at a specified index from the object's children."""

        del self.tno_get_children(node)[index]

    def tno_when_children_replaced(self, node, listener, remove):
        """Sets up or removes a listener for children being replaced on a
        specified object.
        """
        self.on_trait_change(
            listener, node.children, remove=remove, dispatch="ui"
        )

    def tno_when_children_changed(self, node, listener, remove):
        """Sets up or removes a listener for children being changed on a
        specified object.
        """
        self.on_trait_change(
            listener,
            node.children + "_items",
            remove=remove,
            dispatch="ui",
        )

    def tno_get_label(self, node):
        """Gets the label to display for a specified object."""
        label = node.label
        if label[:1] == "=":
            return label[1:]

        label = xgetattr(self, label)

        if node.formatter is None:
            return label

        return node.formatter(self, label)

    def tno_set_label(self, node, label):
        """Sets the label for a specified object."""
        label_name = node.label
        if label_name[:1] != "=":
            xsetattr(self, label_name, label)

    def tno_when_label_changed(self, node, listener, remove):
        """Sets up or removes a listener for  the label being changed on a
        specified object.
        """
        label = node.label
        if label[:1] != "=":
            memo = ("label", label, node, listener)
            if not remove:

                def wrapped_listener(target, name, new):
                    """Ensure listener gets called with correct object."""
                    return listener(self, name, new)

                self._listener_cache[memo] = wrapped_listener
            else:
                wrapped_listener = self._listener_cache.pop(memo, None)
                if wrapped_listener is None:
                    return

            self.on_trait_change(
                wrapped_listener, label, remove=remove, dispatch="ui"
            )

    def tno_get_tooltip(self, node):
        """Gets the tooltip to display for a specified object."""
        tooltip = node.tooltip
        if tooltip == "":
            return tooltip

        if tooltip[:1] == "=":
            return tooltip[1:]

        tooltip = xgetattr(self, tooltip)

        if node.tooltip_formatter is None:
            return tooltip

        return node.tooltip_formatter(self, tooltip)

    def tno_get_icon(self, node, is_expanded):
        """Returns the icon for a specified object."""
        if not self.tno_allows_children(node):
            return node.icon_item

        if is_expanded:
            return node.icon_open

        return node.icon_group

    def tno_get_icon_path(self, node):
        """Returns the path used to locate an object's icon."""
        return node.icon_path

    def tno_get_name(self, node):
        """Returns the name to use when adding a new object instance
        (displayed in the "New" submenu).
        """
        return node.name

    def tno_get_view(self, node):
        """Gets the view to use when editing an object."""
        return node.view

    def tno_get_menu(self, node):
        """Returns the right-click context menu for an object."""
        return node.menu

    def tno_can_rename(self, node):
        """Returns whether the object's children can be renamed."""
        return node.rename

    def tno_can_rename_me(self, node):
        """Returns whether the object can be renamed."""
        return node.rename_me

    def tno_can_copy(self, node):
        """Returns whether the object's children can be copied."""
        return node.copy

    def tno_can_delete(self, node):
        """Returns whether the object's children can be deleted."""
        return node.delete

    def tno_can_delete_me(self, node):
        """Returns whether the object can be deleted."""
        return node.delete_me

    def tno_can_insert(self, node):
        """Returns whether the object's children can be inserted (vs.
        appended).
        """
        return node.insert

    def tno_can_auto_open(self, node):
        """Returns whether the object's children should be automatically
        opened.
        """
        return node.auto_open

    def tno_can_auto_close(self, node):
        """Returns whether the object's children should be automatically
        closed.
        """
        return node.auto_close

    def tno_is_node_for(self, node):
        """Returns whether this is the node that should handle a
        specified object.
        """
        return isinstance(
            self, node.node_for_class
        ) or self.has_traits_interface(*node.node_for_interface)

    def tno_can_add(self, node, add_object):
        """Returns whether a given object is droppable on the node."""
        klass = node._class_for(add_object)
        if node.is_addable(klass):
            return True

        for item in node.move:
            if type(item) in SequenceTypes:
                item = item[0]
            if issubclass(klass, item):
                return True

        return False

    def tno_get_add(self, node):
        """Returns the list of classes that can be added to the object."""
        return node.add

    def tno_get_drag_object(self, node):
        """Returns a draggable version of a specified object."""
        return self

    def tno_drop_object(self, node, dropped_object):
        """Returns a droppable version of a specified object."""
        if node.is_addable(dropped_object):
            return dropped_object

        for item in node.move:
            if type(item) in SequenceTypes:
                if isinstance(dropped_object, item[0]):
                    return item[1](self, dropped_object)
            else:
                if isinstance(dropped_object, item):
                    return dropped_object

    def tno_select(self, node):
        """Handles an object being selected."""
        if node.on_select is not None:
            node.on_select(self)
            return None

        return True

    def tno_click(self, node):
        """Handles an object being clicked."""
        if node.on_click is not None:
            node.on_click(self)
            return None

        return True

    def tno_dclick(self, node):
        """Handles an object being double-clicked."""
        if node.on_dclick is not None:
            node.on_dclick(self)
            return None

        return True

    def tno_activated(self, node):
        """Handles an object being activated."""
        if node.on_activated is not None:
            node.on_activated(self)
            return None

        return True


# -------------------------------------------------------------------------
#  'MultiTreeNode' object:
# -------------------------------------------------------------------------


class MultiTreeNode(TreeNode):

    # -------------------------------------------------------------------------
    #  Trait definitions:
    # -------------------------------------------------------------------------

    #: TreeNode that applies to the base object itself
    root_node = Instance(TreeNode)

    #: List of TreeNodes (one for each sub-item list)
    nodes = List(TreeNode)

    def allows_children(self, object):
        """Returns whether this object can have children (True for this
        class).
        """
        return True

    def has_children(self, object):
        """Returns whether this object has children (True for this class)."""
        return True

    def get_children(self, object):
        """Gets the object's children."""
        return [(object, node) for node in self.nodes]

    def get_children_id(self, object):
        """Gets the object's children identifier."""
        return ""

    def when_children_replaced(self, object, listener, remove):
        """Sets up or removes a listener for children being replaced on a
        specified object.
        """
        pass

    def when_children_changed(self, object, listener, remove):
        """Sets up or removes a listener for children being changed on a
        specified object.
        """
        pass

    def get_label(self, object):
        """Gets the label to display for a specified object."""
        return self.root_node.get_label(object)

    def set_label(self, object, label):
        """Sets the label for a specified object."""
        return self.root_node.set_label(object, label)

    def when_label_changed(self, object, listener, remove):
        """Sets up or removes a listener for the label being changed on a
        specified object.
        """
        return self.root_node.when_label_changed(object, listener, remove)

    def get_icon(self, object, is_expanded):
        """Returns the icon for a specified object."""
        return self.root_node.get_icon(object, is_expanded)

    def get_icon_path(self, object):
        """Returns the path used to locate an object's icon."""
        return self.root_node.get_icon_path(object)

    def get_name(self, object):
        """Returns the name to use when adding a new object instance
        (displayed in the "New" submenu).
        """
        return self.root_node.get_name(object)

    def get_view(self, object):
        """Gets the view to use when editing an object."""
        return self.root_node.get_view(object)

    def get_menu(self, object):
        """Returns the right-click context menu for an object."""
        return self.root_node.get_menu(object)

    def can_rename(self, object):
        """Returns whether the object's children can be renamed (False for
        this class).
        """
        return False

    def can_rename_me(self, object):
        """Returns whether the object can be renamed (False for this class)."""
        return False

    def can_copy(self, object):
        """Returns whether the object's children can be copied."""
        return self.root_node.can_copy(object)

    def can_delete(self, object):
        """Returns whether the object's children can be deleted (False for
        this class).
        """
        return False

    def can_delete_me(self, object):
        """Returns whether the object can be deleted (True for this class)."""
        return True

    def can_insert(self, object):
        """Returns whether the object's children can be inserted (False,
        meaning that children are appended, for this class).
        """
        return False

    def can_auto_open(self, object):
        """Returns whether the object's children should be automatically
        opened.
        """
        return self.root_node.can_auto_open(object)

    def can_auto_close(self, object):
        """Returns whether the object's children should be automatically
        closed.
        """
        return self.root_node.can_auto_close(object)

    def can_add(self, object, add_object):
        """Returns whether a given object is droppable on the node (False for
        this class).
        """
        return False

    def get_add(self, object):
        """Returns the list of classes that can be added to the object."""
        return []

    def get_drag_object(self, object):
        """Returns a draggable version of a specified object."""
        return self.root_node.get_drag_object(object)

    def drop_object(self, object, dropped_object):
        """Returns a droppable version of a specified object."""
        return self.root_node.drop_object(object, dropped_object)

    def select(self, object):
        """Handles an object being selected."""
        return self.root_node.select(object)

    def click(self, object):
        """Handles an object being clicked."""
        return self.root_node.click(object)

    def dclick(self, object):
        """Handles an object being double-clicked."""
        return self.root_node.dclick(object)

    def activated(self, object):
        """Handles an object being activated."""
        return self.root_node.activated(object)
