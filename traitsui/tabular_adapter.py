#-------------------------------------------------------------------------
#
#  Copyright (c) 2008, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
#  Author: David C. Morrill
#  Date:   02/29/2008
#
#-------------------------------------------------------------------------

""" Defines the adapter classes associated with the Traits UI TabularEditor.
"""

#-------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------

from __future__ import absolute_import

from traits.api import (
    Any,
    Bool,
    Color,
    Either,
    Enum,
    Event,
    Float,
    Font,
    HasPrivateTraits,
    HasTraits,
    Instance,
    Int,
    Interface,
    List,
    Property,
    Str,
    cached_property,
    on_trait_change,
    provides)
import six

#-------------------------------------------------------------------------
#  'ITabularAdapter' interface:
#-------------------------------------------------------------------------


class ITabularAdapter(Interface):

    #: The row index of the current item being adapted:
    row = Int

    #: The current column id being adapted (if any):
    column = Any

    #: Current item being adapted:
    item = Any

    #: The current value (if any):
    value = Any

    #: The list of columns the adapter supports. The items in the list have the
    #: same format as the :py:attr:`columns` trait in the
    #: :py:class:`TabularAdapter` class, with the additional requirement that
    #: the ``string`` values must correspond to a ``string`` value in the
    #: associated :py:class:`TabularAdapter` class.
    columns = List(Str)

    #: Does the adapter know how to handle the current *item* or not:
    accepts = Bool

    #: Does the value of *accepts* depend only upon the type of *item*?
    is_cacheable = Bool

#-------------------------------------------------------------------------
#  'AnITabularAdapter' class:
#-------------------------------------------------------------------------


@provides(ITabularAdapter)
class AnITabularAdapter(HasPrivateTraits):

    # Implementation of the ITabularAdapter Interface ------------------------

    #: The row index of the current item being adapted:
    row = Int

    #: The current column id being adapted (if any):
    column = Any

    #: Current item being adapted:
    item = Any

    #: The current value (if any):
    value = Any

    #: The list of columns the adapter supports. The items in the list have the
    #: same format as the :py:attr:`columns` trait in the
    #: :py:class:`TabularAdapter` class, with the additional requirement that
    #: the ``string`` values must correspond to a ``string`` value in the
    #: associated :py:class:`TabularAdapter` class.
    columns = List(Str)

    #: Does the adapter know how to handle the current *item* or not:
    accepts = Bool(True)

    #: Does the value of *accepts* depend only upon the type of *item*?
    is_cacheable = Bool(True)


#-------------------------------------------------------------------------
#  'TabularAdapter' class:
#-------------------------------------------------------------------------

class TabularAdapter(HasPrivateTraits):
    """ The base class for adapting list items to values that can be edited
        by a TabularEditor.
    """

    #-- Public Trait Definitions ---------------------------------------------

    #: A list of columns that should appear in the table. Each entry can have
    #: one of two forms: ``string`` or ``(string, id)``, where ``string`` is
    #: the UI name of the column, and ``id`` is a value that identifies that
    #: column to the adapter. Normally this value is either a trait name or an
    #: index, but it can be any value that the adapter wants. If only
    #: ``string`` is specified, then ``id`` is the index of the ``string``
    #: within :py:attr:`columns`.
    columns = List()

    #: Maps UI name of column to value identifying column to the adapter, if
    #: different.
    column_dict = Property()

    #: Specifies the default value for a new row.  This will usually need to be
    #: overridden.
    default_value = Any('')

    #: The default text color for odd table rows.
    odd_text_color = Color(None, update=True)

    #: The default text color for even table rows.
    even_text_color = Color(None, update=True)

    #: The default text color for table rows.
    default_text_color = Color(None, update=True)

    #: The default background color for odd table rows.
    odd_bg_color = Color(None, update=True)

    #: The default background color for even table rows.
    even_bg_color = Color(None, update=True)

    #: The default background color for table rows.
    default_bg_color = Color(None, update=True)

    #: Horizontal alignment to use for a specified column.
    alignment = Enum('left', 'center', 'right')

    #: The Python format string to use for a specified column.
    format = Str('%s')

    #: Width of a specified column.
    width = Float(-1)

    #: Can the text value of each item be edited?
    can_edit = Bool(True)

    #: The value to be dragged for a specified row item.
    drag = Property

    #: Can any arbitrary value be dropped onto the tabular view.
    can_drop = Bool(False)

    #: Specifies where a dropped item should be placed in the table relative to
    #: the item it is dropped on.
    dropped = Enum('after', 'before')

    #: The font for a row item.
    font = Font(None)

    #: The text color for a row item.
    text_color = Property

    #: The background color for a row item.
    bg_color = Property

    #: The name of the default image to use for column items.
    image = Str(None, update=True)

    #: The text of a row/column item.
    text = Property

    #: The content of a row/column item (may be any Python value).
    content = Property

    #: The tooltip information for a row/column item.
    tooltip = Str

    #: The context menu for a row/column item.
    menu = Any

    #: The context menu for column header.
    column_menu = Any

    #: List of optional delegated adapters.
    adapters = List(ITabularAdapter, update=True)

    #-- Traits Set by the Editor ---------------------------------------------

    #: The object whose trait is being edited.
    object = Instance(HasTraits)

    #: The name of the trait being edited.
    name = Str

    #: The row index of the current item being adapted.
    row = Int

    #: The column index of the current item being adapted.
    column = Int

    #: The current column id being adapted (if any).
    column_id = Any

    #: Current item being adapted.
    item = Any

    #: The current value (if any).
    value = Any

    #-- Private Trait Definitions --------------------------------------------

    #: Cache of attribute handlers.
    cache = Any({})

    #: Event fired when the cache is flushed.
    cache_flushed = Event(update=True)

    #: The mapping from column indices to column identifiers (defined by the
    #: :py:attr:`columns` trait).
    column_map = Property(depends_on='columns')

    #: The mapping from column indices to column labels (defined by the
    #: :py:attr:`columns` trait).
    label_map = Property(depends_on='columns')

    #: The name of the trait on a row item containing the value to use
    #: as a row label. If ``None``, the label will be the empty string.
    row_label_name = Either(None, Str)

    #: For each adapter, specifies the column indices the adapter handles.
    adapter_column_indices = Property(depends_on='adapters,columns')

    #: For each adapter, specifies the mapping from column index to column id.
    adapter_column_map = Property(depends_on='adapters,columns')

    #-------------------------------------------------------------------------
    # TabularAdapter interface
    #-------------------------------------------------------------------------

    def cleanup(self):
        """ Clean up the adapter to remove references to objects.
        """
        self.trait_setq(
            object=None,
            item=None,
            value=None,
        )

    #-- Adapter methods that are sensitive to item type ----------------------

    def get_alignment(self, object, trait, column):
        """ Returns the alignment style to use for a specified column.

        The possible values that can be returned are: ``'left'``, ``'center'``
        or ``'right'``. All table items share the same alignment for a
        specified column.
        """
        return self._result_for('get_alignment', object, trait, 0, column)

    def get_width(self, object, trait, column):
        """ Returns the width to use for a specified column.

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
        """
        return self._result_for('get_width', object, trait, 0, column)

    def get_can_edit(self, object, trait, row):
        """ Returns whether the user can edit a specified row.

        A ``True`` result indicates that the value can be edited, while a
        ``False`` result indicates that it cannot.
        """
        return self._result_for('get_can_edit', object, trait, row, 0)

    def get_drag(self, object, trait, row):
        """ Returns the value to be *dragged* for a specified row.

        A result of ``None`` means that the item cannot be dragged. Note that
        the value returned does not have to be the actual row item. It can be
        any value that you want to drag in its place. In particular, if you
        want the drag target to receive a copy of the row item, you should
        return a copy or clone of the item in its place.

        Also note that if multiple items are being dragged, and this method
        returns ``None`` for any item in the set, no drag operation is
        performed.
        """
        return self._result_for('get_drag', object, trait, row, 0)

    def get_can_drop(self, object, trait, row, value):
        """ Returns whether the specified ``value`` can be dropped on the specified row.

        A value of ``True`` means the ``value`` can be dropped; and a value of
        ``False`` indicates that it cannot be dropped.

        The result is used to provide the user positive or negative drag
        feedback while dragging items over the table. ``value`` will always be
        a single value, even if multiple items are being dragged. The editor
        handles multiple drag items by making a separate call to
        :py:meth:`get_can_drop` for each item being dragged.
        """
        return self._result_for('get_can_drop', object, trait, row, 0, value)

    def get_dropped(self, object, trait, row, value):
        """ Returns how to handle a specified ``value`` being dropped on a specified row.

        The possible return values are:

        - ``'before'``: Insert the specified ``value`` before the dropped on item.
        - ``'after'``: Insert the specified ``value`` after the dropped on item.

        Note there is no result indicating *do not drop* since you will have
        already indicated that the ``object`` can be dropped by the result
        returned from a previous call to :py:meth:`get_can_drop`.
        """
        return self._result_for('get_dropped', object, trait, row, 0, value)

    def get_font(self, object, trait, row, column=0):
        """ Returns the font to use for displaying a specified row or cell.

        A result of ``None`` means use the default font; otherwise a toolkit
        font object should be returned. Note that all columns for the specified
        table row will use the font value returned.
        """
        return self._result_for('get_font', object, trait, row, column)

    def get_text_color(self, object, trait, row, column=0):
        """ Returns the text color to use for a specified row or cell.

        A result of ``None`` means use the default text color; otherwise a
        toolkit-compatible color should be returned. Note that all columns for
        the specified table row will use the text color value returned.
        """
        return self._result_for('get_text_color', object, trait, row, column)

    def get_bg_color(self, object, trait, row, column=0):
        """ Returns the background color to use for a specified row or cell.

        A result of ``None`` means use the default background color; otherwise
        a toolkit-compatible color should be returned. Note that all columns
        for the specified table row will use the background color value
        returned.
        """
        return self._result_for('get_bg_color', object, trait, row, column)

    def get_image(self, object, trait, row, column):
        """ Returns the image to display for a specified cell.

        A result of ``None`` means no image will be displayed in the specified
        table cell. Otherwise the result should either be the name of the
        image, or an :py:class:`~pyface.image_resource.ImageResource` object
        specifying the image to display.

        A name is allowed in the case where the image is specified in the
        :py:class:`~traitsui.editors.tabular_editor.TabularEditor`
        :py:attr:`~traitsui.editors.tabular_editor.TabularEditor.images` trait.
        In that case, the name should be the same as the string specified in
        the :py:class:`~pyface.image_resource.ImageResource` constructor.
        """
        return self._result_for('get_image', object, trait, row, column)

    def get_format(self, object, trait, row, column):
        """ Returns the Python formatting string to apply to the specified cell.

        The resulting of formatting with this string will be used as the text
        to display it in the table.

        The return can be any Python string containing exactly one old-style
        Python formatting sequence, such as ``'%.4f'`` or ``'(%5.2f)'``.
        """
        return self._result_for('get_format', object, trait, row, column)

    def get_text(self, object, trait, row, column):
        """ Returns a string containing the text to display for a specified cell.

        If the underlying data representation for a specified item is not a
        string, then it is your responsibility to convert it to one before
        returning it as the result.
        """
        return self._result_for('get_text', object, trait, row, column)

    def get_content(self, object, trait, row, column):
        """ Returns the content to display for a specified cell.
        """
        return self._result_for('get_content', object, trait, row, column)

    def set_text(self, object, trait, row, column, text):
        """ Sets the value for the specified cell.

        This method is called when the user completes an editing operation on a
        table cell.

        The string specified by ``text`` is the value that the user has
        entered in the table cell.  If the underlying data does not store the
        value as text, it is your responsibility to convert ``text`` to the
        correct representation used.
        """
        self._result_for('set_text', object, trait, row, column, text)

    def get_tooltip(self, object, trait, row, column):
        """ Returns a string containing the tooltip to display for a specified cell.

        You should return the empty string if you do not wish to display a
        tooltip.
        """
        return self._result_for('get_tooltip', object, trait, row, column)

    def get_menu(self, object, trait, row, column):
        """ Returns the context menu for a specified cell.
        """
        return self._result_for('get_menu', object, trait, row, column)

    def get_column_menu(self, object, trait, row, column):
        """ Returns the context menu for a specified column.
        """
        return self._result_for('get_column_menu', object, trait, row, column)

    #-- Adapter methods that are not sensitive to item type ------------------

    def get_item(self, object, trait, row):
        """ Returns the specified row item.

        The value returned should be the value that exists (or *logically*
        exists) at the specified ``row`` in your data. If your data is not
        really a list or array, then you can just use ``row`` as an integer
        *key* or *token* that can be used to retrieve a corresponding item. The
        value of ``row`` will always be in the range: 0 <= row <
        ``len(object, trait)`` (i.e. the result returned by the adapter
        :py:meth:`len` method).

        The default implementation assumes the trait defined by
        ``object.trait`` is a *sequence* and attempts to return the value at
        index ``row``. If an error occurs, it returns ``None`` instead. This
        definition should work correctly for lists, tuples and arrays, or any
        other object that is indexable, but will have to be overridden for all
        other cases.
        """
        try:
            return getattr(object, trait)[row]
        except:
            return None

    def len(self, object, trait):
        """ Returns the number of row items in the specified ``object.trait``.

        The result should be an integer greater than or equal to 0.

        The default implementation assumes the trait defined by
        ``object.trait`` is a *sequence* and attempts to return the result of
        calling ``len(object.trait)``. It will need to be overridden for any
        type of data which for which :py:func:`len` will not work.
        """
        # Sometimes, during shutdown, the object has been set to None.
        if object is None:
            return 0
        else:
            return len(getattr(object, trait))

    def get_default_value(self, object, trait):
        """ Returns a new default value for the specified ``object.trait`` list.

        This method is called when *insert* or *append* operations are allowed
        and the user requests that a new item be added to the table. The result
        should be a new instance of whatever underlying representation is being
        used for table items.

        The default implementation simply returns the value of the adapter's
        :py:attr:`default_value` trait.
        """
        return self.default_value

    def delete(self, object, trait, row):
        """ Deletes the specified row item.

        This method is only called if the *delete* operation is specified in
        the :py:class:`~traitsui.editors.tabular_editor.TabularEditor`
        :py:attr:`~traitsui.editors.tabular_editor.TabularEditor.operation`
        trait, and the user requests that the item be deleted from the table.

        The adapter can still choose not to delete the specified item if
        desired, although that may prove confusing to the user.

        The default implementation assumes the trait defined by
        ``object.trait`` is a mutable sequence and attempts to perform a
        ``del object.trait[row]`` operation.
        """
        del getattr(object, trait)[row]

    def insert(self, object, trait, row, value):
        """ Inserts ``value`` at the specified ``object.trait[row]`` index.

        The specified ``value`` can be:

        - An item being moved from one location in the data to another.
        - A new item created by a previous call to
          :py:meth:`~TabularAdapter.get_default_value`.
        - An item the adapter previously approved via a call to
          :py:meth:`~TabularAdapter.get_can_drop`.

        The adapter can still choose not to insert the item into the data,
        although that may prove confusing to the user.

        The default implementation assumes the trait defined by
        ``object.trait`` is a mutable sequence and attempts to perform an
        ``object.trait[row:row] = [value]`` operation.
        """
        getattr(object, trait)[row: row] = [value]

    def get_column(self, object, trait, index):
        """ Returns the column id corresponding to a specified column index.
        """
        self.object, self.name = object, trait
        return self.column_map[index]

    #-- Property Implementations ---------------------------------------------

    def _get_drag(self):
        return self.item

    def _get_text_color(self):
        if (self.row % 2) == 1:
            return self.even_text_color_ or self.default_text_color

        return self.odd_text_color or self.default_text_color_

    def _get_bg_color(self):
        if (self.row % 2) == 1:
            return self.even_bg_color_ or self.default_bg_color_

        return self.odd_bg_color or self.default_bg_color_

    def _get_text(self):
        return self.get_format(
            self.object, self.name, self.row, self.column) % self.get_content(
            self.object, self.name, self.row, self.column)

    def _set_text(self, value):
        if isinstance(self.column_id, int):
            self.item[self.column_id] = self.value
        else:
            # Convert value to the correct trait type.
            try:
                trait_handler = self.item.trait(self.column_id).handler
                setattr(self.item, self.column_id,
                        trait_handler.evaluate(self.value))
            except:
                setattr(self.item, self.column_id, value)

    def _get_content(self):
        if isinstance(self.column_id, int):
            return self.item[self.column_id]

        return getattr(self.item, self.column_id)

    #-- Property Implementations ---------------------------------------------

    @cached_property
    def _get_column_dict(self):
        cols = {}
        for i, value in enumerate(self.columns):
            if isinstance(value, six.string_types):
                cols.update({value: value})
            else:
                cols.update({value[0]: value[1]})
        return cols

    @cached_property
    def _get_column_map(self):
        map = []
        for i, value in enumerate(self.columns):
            if isinstance(value, six.string_types):
                map.append(i)
            else:
                map.append(value[1])

        return map

    def get_label(self, section, obj=None):
        """Override this method if labels will vary from object to object."""
        return self.label_map[section]

    def get_row_label(self, section, obj=None):
        if self.row_label_name is None:
            return None
        rows = getattr(obj, self.name, None)
        if rows is None:
            return None
        item = rows[section]
        return getattr(item, self.row_label_name, None)

    @cached_property
    def _get_label_map(self):
        map = []
        for i, value in enumerate(self.columns):
            if isinstance(value, six.string_types):
                map.append(value)
            else:
                map.append(value[0])

        return map

    @cached_property
    def _get_adapter_column_indices(self):
        labels = self.label_map
        map = []
        for adapter in self.adapters:
            indices = []
            for label in adapter.columns:
                if not isinstance(label, six.string_types):
                    label = label[0]

                indices.append(labels.index(label))
            map.append(indices)
        return map

    @cached_property
    def _get_adapter_column_map(self):
        labels = self.label_map
        map = []
        for adapter in self.adapters:
            mapping = {}
            for label in adapter.columns:
                id = None
                if not isinstance(label, six.string_types):
                    label, id = label

                key = labels.index(label)
                if id is None:
                    id = key

                mapping[key] = id

            map.append(mapping)

        return map

    #-- Private Methods ------------------------------------------------------

    def _result_for(self, name, object, trait, row, column, value=None):
        """ Returns/Sets the value of the specified *name* attribute for the
            specified *object.trait[row].column* item.
        """
        self.object = object
        self.name = trait
        self.row = row
        self.column = column
        self.column_id = column_id = self.column_map[column]
        self.value = value
        self.item = item = self.get_item(object, trait, row)
        item_class = item.__class__
        key = '%s:%s:%d' % (item_class.__name__, name, column)
        handler = self.cache.get(key)
        if handler is not None:
            return handler()

        prefix = name[:4]
        trait_name = name[4:]

        for i, adapter in enumerate(self.adapters):
            if column in self.adapter_column_indices[i]:
                adapter.row = row
                adapter.item = item
                adapter.value = value
                adapter.column = column_id = self.adapter_column_map[i][column]
                if adapter.accepts:
                    get_name = '%s_%s' % (column_id, trait_name)
                    if adapter.trait(get_name) is not None:
                        if prefix == 'get_':
                            handler = lambda: getattr(adapter.trait_set(
                                row=self.row, column=column_id,
                                item=self.item), get_name)
                        else:
                            handler = lambda: setattr(adapter.trait_set(
                                row=self.row, column=column_id,
                                item=self.item), get_name, self.value)

                        if adapter.is_cacheable:
                            break

                        return handler()
        else:
            if item is not None and hasattr(item_class, '__mro__'):
                for klass in item_class.__mro__:
                    handler = (
                        self._get_handler_for(
                            '%s_%s_%s' %
                            (klass.__name__, column_id, trait_name), prefix) or self._get_handler_for(
                            '%s_%s' %
                            (klass.__name__, trait_name), prefix))
                    if handler is not None:
                        break

            if handler is None:
                handler = (
                    self._get_handler_for(
                        '%s_%s' %
                        (column_id, trait_name), prefix) or self._get_handler_for(
                        trait_name, prefix))

        self.cache[key] = handler
        return handler()

    def _get_handler_for(self, name, prefix):
        """ Returns the handler for a specified trait name (or None if not
            found).
        """
        if self.trait(name) is not None:
            if prefix == 'get_':
                return lambda: getattr(self, name)

            return lambda: setattr(self, name, self.value)

        return None

    @on_trait_change('columns,adapters.+update')
    def _flush_cache(self):
        """ Flushes the cache when the columns or any trait on any adapter
            changes.
        """
        self.cache = {}
        self.cache_flushed = True
