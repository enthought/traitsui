# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Defines KeyBinding and KeyBindings classes, which manage the mapping of
    keystroke events into method calls on controller objects that are supplied
    by the application.
"""

from traits.api import (
    Any,
    Event,
    HasPrivateTraits,
    HasStrictTraits,
    Instance,
    List,
    Property,
    Str,
    cached_property,
    observe,
)
from traits.trait_base import SequenceTypes

from .editors.key_binding_editor import KeyBindingEditor
from .editors.list_editor import ListEditor
from .group import HGroup
from .handler import ModelView
from .item import Item
from .toolkit import toolkit
from .view import View


#: Trait definition for key bindings
Binding = Str(editor=KeyBindingEditor())


class KeyBinding(HasStrictTraits):
    """Binds one or two keystrokes to a method."""

    # -------------------------------------------------------------------------
    #  Trait definitions:
    # -------------------------------------------------------------------------

    #: First key binding
    binding1 = Binding

    #: Second key binding
    binding2 = Binding

    #: Description of what application function the method performs
    description = Str()

    #: Name of controller method the key is bound to
    method_name = Str()

    #: KeyBindings object that "owns" the KeyBinding
    owner = Instance("KeyBindings")

    def match(self, binding):
        return any(binding == x for x in {self.binding1, self.binding2})

    def clear_binding(self, binding):
        if binding == self.binding1:
            self.binding1 = self.binding2
            self.binding2 = ""
        if binding == self.binding2:
            self.binding2 = ""

    # -------------------------------------------------------------------------
    #  Traits view definitions:
    # -------------------------------------------------------------------------

    traits_view = View(
        HGroup(
            Item("binding1"),
            Item("binding2"),
            Item("description", style="readonly"),
            show_labels=False,
        )
    )


class KeyBindings(HasPrivateTraits):
    """A set of key bindings."""

    # -------------------------------------------------------------------------
    #  Trait definitions:
    # -------------------------------------------------------------------------

    #: Set of defined key bindings (redefined dynamically)
    bindings = List(Instance(KeyBinding))

    #: Optional prefix to add to each method name
    prefix = Str()

    #: Optional suffix to add to each method name
    suffix = Str()

    # -- Private Traits -------------------------------------------------------

    #: The (optional) list of controllers associated with this KeyBindings
    #: object. The controllers may also be provided with the 'do' method:
    controllers = List(transient=True)

    #: The 'parent' KeyBindings object of this one (if any):
    parent = Instance("KeyBindings", transient=True)

    #: The root of the KeyBindings tree this object is part of:
    root = Property(observe="parent")

    #: The child KeyBindings of this object (if any):
    children = List(transient=True)

    # -------------------------------------------------------------------------
    #  Traits view definitions:
    # -------------------------------------------------------------------------

    def __init__(self, *bindings, **traits):
        # initialize bindings
        if len(bindings) == 1 and isinstance(bindings[0], SequenceTypes):
            bindings = bindings[0]
        traits.setdefault("bindings", list(bindings))
        for binding in traits["bindings"]:
            binding.owner = self

        super().__init__(**traits)

    def do(self, event, controllers=[], *args, **kw):
        """Processes a keyboard event."""
        if isinstance(controllers, dict):
            controllers = list(controllers.values())
        elif not isinstance(controllers, SequenceTypes):
            controllers = [controllers]
        else:
            controllers = list(controllers)

        return self._do(
            toolkit().key_event_to_name(event),
            controllers,
            args,
            kw.get("recursive", False),
        )

    def merge(self, key_bindings):
        """Merges another set of key bindings into this set."""
        binding_dic = {}
        for binding in self.bindings:
            binding_dic[binding.method_name] = binding

        for binding in key_bindings.bindings:
            binding2 = binding_dic.get(binding.method_name)
            if binding2 is not None:
                binding2.binding1 = binding.binding1
                binding2.binding2 = binding.binding2

    def clone(self, **traits):
        """Returns a clone of the KeyBindings object."""
        return self.__class__(*self.bindings, **traits).trait_set(
            **self.trait_get("prefix", "suffix")
        )

    def dispose(self):
        """Dispose of the object."""
        if self.parent is not None:
            self.parent.children.remove(self)

        del self.controllers
        del self.children
        del self.bindings

        self.parent = self._root = None

    def edit(self):
        """Edits a possibly hierarchical set of KeyBindings."""
        model_view = KeyBindingsHandler(model=self)
        ui = model_view.edit_traits()

    # -- Property Implementations ---------------------------------------------

    @cached_property
    def _get_root(self):
        root = self
        while root.parent is not None:
            root = root.parent

        return root

    # -- Event Handlers -------------------------------------------------------

    @observe('bindings:items:[binding1,binding2]')
    def _binding_updated(self, event):
        if event.new != "":
            for a_binding in self._match_binding(event.new, skip={event.object}):
                a_binding.clear_binding(event.new)

    @observe("children.items")
    def _children_modified(self, event):
        """Handles child KeyBindings being added to the object."""
        # the full children list is changed
        if isinstance(event.object, KeyBindings):
            for item in event.new:
                item.parent = self
        # the contents of the children list are changed
        else:
            for item in event.added:
                item.parent = self

    # -- Private Methods ------------------------------------------------------

    def _get_bindings(self, bindings):
        """Returns all of the bindings of this object and all of its children."""
        bindings.extend(self.bindings)
        for child in self.children:
            child._get_bindings(bindings)

        return bindings

    def _do(self, key_name, controllers, args, recursive):
        """Process the specified key for the specified set of controllers for
        this KeyBindings object and all of its children.
        """
        # Search through our own bindings for a match:
        for binding in self._match_binding(key_name):
            method_name = "%s%s%s" % (
                self.prefix,
                binding.method_name,
                self.suffix,
            )
            for controller in controllers + self.controllers:
                method = getattr(controller, method_name, None)
                if method is not None:
                    result = method(*args)
                    if result is not False:
                        return True

            if binding.method_name == "edit_bindings":
                self.edit()
                return True

        # If recursive, continue searching through a children's bindings:
        if recursive:
            for child in self.children:
                if child._do(key_name, controllers, args, recursive):
                    return True

        # Indicate no one processed the key:
        return False

    def _match_binding(self, binding, skip=frozenset()):
        """Return all KeyBinding instances that match the given binding.
        """
        return (
            a_binding
            for a_binding in self.bindings
            if a_binding not in skip and a_binding.match(binding)
        )


class KeyBindingsHandler(ModelView):

    bindings = List(Instance(KeyBinding))

    def key_binding_for(self, binding, key_name):
        """Returns the current binding for a specified key (if any)."""
        if key_name != "":
            for a_binding in self._match_binding(key_name, skip={binding}):
                return a_binding

        return None

    def _match_binding(self, binding, skip=frozenset()):
        """Return all KeyBinding instances that match the given binding.
        """
        return (
            a_binding
            for a_binding in self.bindings
            if a_binding not in skip and a_binding.match(binding)
        )

    def _bindings_default(self):
        bindings = list(set(self.model.root._get_bindings([])))
        bindings.sort(key=lambda x: (x.binding1[-1:], x.binding1))
        return bindings

    traits_view = View(
        [
            Item(
                "bindings",
                style="readonly",
                show_label=False,
                editor=ListEditor(style="custom"),
            ),
            "|{Click on an entry field, then press the key to "
            "assign. Double-click a field to clear it.}<>",
        ],
        title="Update Key Bindings",
        kind="livemodal",
        resizable=True,
        width=0.4,
        height=0.4,
    )
