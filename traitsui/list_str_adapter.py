# (C) Copyright 2004-2022 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

"""  Defines adapter interfaces for use with the ListStrEditor.
"""

from traits.api import (
    Any,
    Bool,
    Dict,
    Enum,
    Event,
    HasPrivateTraits,
    Int,
    Interface,
    List,
    Str,
    observe,
    provides,
)
from .toolkit_traits import Color


# -------------------------------------------------------------------------
#  'IListStrAdapter' interface:
# -------------------------------------------------------------------------


class IListStrAdapter(Interface):

    #: The index of the current item being adapted.
    index = Int()

    #: Current item being adapted.
    item = Any()

    #: The current value (if any).
    value = Any()

    #: Does the adapter know how to handle the current *item* or not?
    accepts = Bool()

    #: Does the value of *accepts* depend only upon the type of *item*?
    is_cacheable = Bool()


# -------------------------------------------------------------------------
#  'AnIListStrAdapter' class:
# -------------------------------------------------------------------------


@provides(IListStrAdapter)
class AnIListStrAdapter(HasPrivateTraits):

    # Implementation of the IListStrAdapter Interface ------------------------

    #: The index of the current item being adapted.
    index = Int()

    #: Current item being adapted.
    item = Any()

    #: The current value (if any).
    value = Any()

    #: Does the adapter know how to handle the current *item* or not?
    accepts = Bool(True)

    #: Does the value of *accepts* depend only upon the type of *item*?
    is_cacheable = Bool(True)


# -------------------------------------------------------------------------
#  'ListStrAdapter' class:
# -------------------------------------------------------------------------


class ListStrAdapter(HasPrivateTraits):
    """The base class for adapting list items to values that can be edited
    by a ListStrEditor.
    """

    # Trait Definitions ------------------------------------------------------

    #: Specifies the default value for a new list item.
    default_value = Any("")

    #: Specifies the default text for a new list item.
    default_text = Str()

    #: The default text color for even list items.
    even_text_color = Color(None, update=True)

    #: The default text color for odd list items.
    odd_text_color = Color(None, update=True)

    #: The default text color for list items.
    text_color = Color(None, update=True)

    #: The default background color for even list items.
    even_bg_color = Color(None, update=True)

    #: The default background color for odd list items.
    odd_bg_color = Color(None, update=True)

    #: The default background color for list items.
    bg_color = Color(None, update=True)

    #: The name of the default image to use for list items.
    image = Str(None, update=True)

    #: Can the text value of each list item be edited.
    can_edit = Bool(True)

    #: Specifies where a dropped item should be placed in the list relative to
    #: the item it is dropped on.
    dropped = Enum("after", "before")

    #: The index of the current item being adapter.
    index = Int()

    #: The current item being adapted.
    item = Any()

    #: The current value (if any).
    value = Any()

    #: The tooltip information for a item.
    tooltip = Str(update=True)

    #: List of optional delegated adapters.
    adapters = List(IListStrAdapter, update=True)

    # -- Private Trait Definitions --------------------------------------------

    #: Cache of attribute handlers.
    cache = Dict()

    #: Event fired when the cache is flushed.
    cache_flushed = Event(update=True)

    # -- Adapter methods that are sensitive to item type ----------------------

    def get_can_edit(self, object, trait, index):
        """Returns whether the user can edit a specified *object.trait[index]*
        list item. A True result indicates the value can be edited, while
        a False result indicates that it cannot be edited.
        """
        return self._result_for("get_can_edit", object, trait, index)

    def get_drag(self, object, trait, index):
        """Returns the 'drag' value for a specified *object.trait[index]*
        list item. A result of *None* means that the item cannot be
        dragged.
        """
        return self._result_for("get_drag", object, trait, index)

    def get_can_drop(self, object, trait, index, value):
        """Returns whether the specified *value* can be dropped on the
        specified *object.trait[index]* list item. A value of **True**
        means the *value* can be dropped; and a value of **False**
        indicates that it cannot be dropped.
        """
        return self._result_for("get_can_drop", object, trait, index, value)

    def get_dropped(self, object, trait, index, value):
        """Returns how to handle a specified *value* being dropped on a
        specified *object.trait[index]* list item. The possible return
        values are:

        'before'
            Insert the specified *value* before the dropped on item.
        'after'
            Insert the specified *value* after the dropped on item.
        """
        return self._result_for("get_dropped", object, trait, index, value)

    def get_text_color(self, object, trait, index):
        """Returns the text color for a specified *object.trait[index]* list
        item. A result of None means use the default list item text color.
        """
        return self._result_for("get_text_color", object, trait, index)

    def get_bg_color(self, object, trait, index):
        """Returns the background color for a specified *object.trait[index]*
        list item. A result of None means use the default list item
        background color.
        """
        return self._result_for("get_bg_color", object, trait, index)

    def get_image(self, object, trait, index):
        """Returns the name of the image to use for a specified
        *object.trait[index]* list item. A result of None means no image
        should be used. Otherwise, the result should either be the name of
        the image, or an ImageResource item specifying the image to use.
        """
        return self._result_for("get_image", object, trait, index)

    def get_item(self, object, trait, index):
        """Returns the value of the *object.trait[index]* list item."""
        return self._result_for("get_item", object, trait, index)

    def get_text(self, object, trait, index):
        """Returns the text to display for a specified *object.trait[index]*
        list item.
        """
        return self._result_for("get_text", object, trait, index)

    def get_tooltip(self, object, trait, index):
        """Returns a string containing the tooltip to display for a specified
        *object.trait[index]* list item.

        Users should return *self.tooltip* to use the Adapter's default, or the
        empty string to disable the tooltip for this row (in which case the Item's
        tooltip, if present, will be shown on QT).
        """
        return self._result_for("get_tooltip", object, trait, index)

    # -- Adapter methods that are not sensitive to item type ------------------

    def len(self, object, trait):
        """Returns the number of items in the specified *object.trait* list."""
        # Sometimes, during shutdown, the object has been set to None.
        if object is None:
            return 0
        else:
            return len(getattr(object, trait))

    def get_default_value(self, object, trait):
        """Returns a new default value for the specified *object.trait* list."""
        return self.default_value

    def get_default_text(self, object, trait):
        """Returns the default text for the specified *object.trait* list."""
        return self.default_text

    def get_default_image(self, object, trait):
        """Returns the default image for the specified *object.trait* list."""
        return self.image

    def get_default_bg_color(self, object, trait):
        """Returns the default background color for the specified
        *object.trait* list.
        """
        return self._get_bg_color()

    def get_default_text_color(self, object, trait):
        """Returns the default text color for the specified *object.trait*
        list.
        """
        return self._get_text_color()

    def set_text(self, object, trait, index, text):
        """Sets the text for a specified *object.trait[index]* list item to
        *text*.
        """
        getattr(object, trait)[index] = text

    def delete(self, object, trait, index):
        """Deletes the specified *object.trait[index]* list item."""
        del getattr(object, trait)[index]

    def insert(self, object, trait, index, value):
        """Inserts a new value at the specified *object.trait[index]* list
        index.
        """
        getattr(object, trait)[index:index] = [value]

    # -- Private Adapter Implementation Methods -------------------------------

    def _get_can_edit(self):
        return self.can_edit

    def _get_drag(self):
        return str(self.item)

    def _get_can_drop(self):
        return isinstance(self.value, str)

    def _get_dropped(self):
        return self.dropped

    def _get_text_color(self):
        if (self.index % 2) == 0:
            return self.even_text_color_ or self.text_color_

        return self.odd_text_color or self.text_color_

    def _get_bg_color(self):
        if (self.index % 2) == 0:
            return self.even_bg_color_ or self.bg_color_

        return self.odd_bg_color or self.bg_color_

    def _get_image(self):
        return self.image

    def _get_item(self):
        return self.item

    def _get_text(self):
        return str(self.item)

    def _get_tooltip(self):
        return self.tooltip

    # -- Private Methods ------------------------------------------------------

    def _result_for(self, name, object, trait, index, value=None):
        """Returns/Sets the value of the specified *name* attribute for the
        specified *object.trait[index]* list item.
        """
        self.index = index
        self.value = value
        items = getattr(object, trait)
        if index >= len(items):
            self.item = item = None
        else:
            self.item = item = items[index]

        item_class = item.__class__
        key = "%s:%s" % (item_class.__name__, name)
        handler = self.cache.get(key)
        if handler is not None:
            return handler()

        trait_name = name[4:]

        for adapter in self.adapters:
            adapter.index = index
            adapter.item = item
            adapter.value = value
            if adapter.accepts and (adapter.trait(trait_name) is not None):
                handler = lambda: getattr(
                    adapter.trait_set(
                        index=self.index, item=self.item, value=self.value
                    ),
                    trait_name,
                )

                if adapter.is_cacheable:
                    break

                return handler()
        else:
            for klass in item_class.__mro__:
                cname = "%s_%s" % (klass.__name__, trait_name)
                if self.trait(cname) is not None:
                    handler = lambda: getattr(self, cname)
                    break
            else:
                handler = getattr(self, "_" + name)

        self.cache[key] = handler
        return handler()

    @observe("adapters.items.+update")
    def _flush_cache(self, event):
        """Flushes the cache when any trait on any adapter changes."""
        self.cache = {}
        self.cache_flushed = True
