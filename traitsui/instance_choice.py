# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Defines the various instance descriptors used by the instance editor and
    instance editor factory classes.
"""

from abc import abstractmethod

from traits.api import (
    ABCHasStrictTraits,
    Str,
    Any,
    Dict,
    Tuple,
    Callable,
    Bool,
)

from .ui_traits import AView

from .helper import user_name_for


class InstanceChoiceItem(ABCHasStrictTraits):

    # -------------------------------------------------------------------------
    #  Trait definitions:
    # -------------------------------------------------------------------------

    #: User interface name for the item
    name = Str()

    #: View associated with this item
    view = AView

    #: Does this item create new instances?
    is_factory = Bool(False)

    def get_name(self, object=None):
        """Returns the name of the item."""
        return self.name

    def get_view(self):
        """Returns the view associated with the object."""
        return self.view

    @abstractmethod
    def get_object(self):
        """Returns the object associated with the item."""
        pass

    @abstractmethod
    def is_compatible(self, object):
        """Indicates whether a specified object is compatible with the item."""
        pass

    def is_selectable(self):
        """Indicates whether the item can be selected by the user."""
        return True

    def is_droppable(self):
        """Indicates whether the item supports drag and drop."""
        return False


class InstanceChoice(InstanceChoiceItem):

    # -------------------------------------------------------------------------
    #  Trait definitions:
    # -------------------------------------------------------------------------

    #: Object associated with the item
    object = Any()

    #: The name of the object trait containing its user interface name:
    name_trait = Str("name")

    def get_name(self, object=None):
        """Returns the name of the item."""
        if self.name != "":
            return self.name

        name = getattr(self.object, self.name_trait, None)
        if isinstance(name, str):
            return name

        return user_name_for(self.object.__class__.__name__)

    def get_object(self):
        """Returns the object associated with the item."""
        return self.object

    def is_compatible(self, object):
        """Indicates whether a specified object is compatible with the item."""
        return object is self.object


class InstanceFactoryChoice(InstanceChoiceItem):

    # -------------------------------------------------------------------------
    #  Trait definitions:
    # -------------------------------------------------------------------------

    #: Indicates whether an instance compatible with this item can be dragged
    #: and dropped rather than created
    droppable = Bool(False)

    #: Indicates whether the item can be selected by the user
    selectable = Bool(True)

    #: A class (or other callable) that can be used to create an item
    #: compatible with this item
    klass = Callable()

    #: Tuple of arguments to pass to **klass** to create an instance
    args = Tuple()

    #: Dictionary of arguments to pass to **klass** to create an instance
    kw_args = Dict(Str, Any)

    #: Does this item create new instances? This value overrides the default.
    is_factory = True

    def get_name(self, object=None):
        """Returns the name of the item."""
        if self.name != "":
            return self.name

        name = getattr(object, "name", None)
        if isinstance(name, str):
            return name

        if issubclass(type(self.klass), type):
            klass = self.klass
        else:
            klass = self.get_object().__class__

        return user_name_for(klass.__name__)

    def get_object(self):
        """Returns the object associated with the item."""
        return self.klass(*self.args, **self.kw_args)

    def is_droppable(self):
        """Indicates whether the item supports drag and drop."""
        return self.droppable

    def is_compatible(self, object):
        """Indicates whether a specified object is compatible with the item."""
        if issubclass(type(self.klass), type):
            return isinstance(object, self.klass)
        return isinstance(object, self.get_object().__class__)

    def is_selectable(self):
        """Indicates whether the item can be selected by the user."""
        return self.selectable


class InstanceDropChoice(InstanceFactoryChoice):

    # -------------------------------------------------------------------------
    #  Trait definitions:
    # -------------------------------------------------------------------------

    #: Indicates whether an instance compatible with this item can be dragged
    #: and dropped rather than created . This value overrides the default.
    droppable = True

    #: Indicates whether the item can be selected by the user. This value
    #: overrides the default.
    selectable = False

    #: Does this item create new instances? This value overrides the default.
    is_factory = False
