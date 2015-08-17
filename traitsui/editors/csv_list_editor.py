"""This modules defines CSVListEditor.

A CSVListEditor provides an editor for lists of simple data types.
It allows the user to edit the list in a text field, using commas
(or optionally some other character) to separate the elements.
"""

#------------------------------------------------------------------------------
#
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Author: Warren Weckesser
#  Date:   July 2011
#
#------------------------------------------------------------------------------

from traits.api import Str, Int, Float, Enum, Range, Bool, Trait, TraitError
from traits.trait_handlers import RangeTypes

from .text_editor import TextEditor
from ..helper import enum_values_changed


def _eval_list_str(s, sep=',', item_eval=None,
                                ignore_trailing_sep=True):
    """Convert a string into a list.

    Parameters
    ----------
    s : str
        The string to be converted.
    sep : str or None
        `sep` is the text separator of list items.  If `sep` is None,
        each contiguous stretch of whitespace is a separator.
    item_eval : callable or None
        `item_eval` is used to evaluate the list elements.  If `item_eval`
        is None, the list will be a list substrings of `s`.
    ignore_trailing_sep : bool
        If `ignore_trailing_sep` is False, it is an error to have a separator
        at the end of the list (i.e. 'foo, bar,' is invalid).
        If `ignore_trailing_sep` is True, a separator at the end of the
        string `s` is ignored.

    Returns
    -------
    values : list
        List of converted values from the string.
    """
    if item_eval is None:
        item_eval = lambda x: x
    s = s.strip()
    if sep is not None and ignore_trailing_sep and s.endswith(sep):
        s = s[:-len(sep)]
        s = s.rstrip()
    if s == '':
        values = []
    else:
        values = [item_eval(x.strip()) for x in s.split(sep)]
    return values


def _format_list_str(values, sep=',', item_format=str):
    """Convert a list to a string.

    Each item in the list `values` is converted to a string with the
    function `item_format`, and these are joined with `sep` plus a space.
    If `sep` is None, a single space is used to join the items.

    Parameters
    ----------
    values : list
        The list of values to be represented as a string.
    sep : str
        String used to join the items.  A space is also added after
        `sep`.
    item_format : callable
        Converts its single argument to a string.

    Returns
    -------
    s : str
        The result of converting the list to a string.
    """
    if sep is None:
        joiner = ' '
    else:
        joiner = sep + ' '
    s = joiner.join(item_format(x) for x in values)
    return s


def _validate_range_value(range_object, object, name, value):
    """Validate a Range value.

    This function is used by the CSVListEditor to validate a value
    when editing a list of ranges where the Range is dynamic (that
    is, one or both of the 'low' and 'high' values are strings that
    refer to other traits in `object`.

    The function implements the same validation logic as in the method
    traits.trait_types.BaseRange._set(), but does not call the
    set_value() method; instead it simply returns the valid value.
    If the value is not valid, range_object.error(...) is called.

    Parameters
    ----------
    range_object : instance of traits.trait_types.Range

    object : instance of HasTraits
        This is the HasTraits object that holds the traits
        to which the one or both of range_object.low and
        range_object.high refer.

    name : str
        The name of the List trait in `object`.

    value : object (e.g. int, float, str)
        The value to be validated.

    Returns
    -------
    value : object
        The validated value.  It might not be the same
        type as the input argument (e.g. if the range type
        is float and the input value is an int, the return
        value will be a float).
    """
    low = eval(range_object._low)
    high = eval(range_object._high)
    if low is None and high is None:
        if isinstance(value, RangeTypes):
            return value
    else:
        new_value = range_object._typed_value(value, low, high)

        satisfies_low = (low is None or low < new_value or
            ((not range_object._exclude_low) and (low == new_value)))

        satisfies_high = (high is None or high > new_value or
            ((not range_object._exclude_high) and (high == new_value)))

        if satisfies_low and satisfies_high:
            return value

    # Note: this is the only explicit use of 'object' and 'name'.
    range_object.error(object, name, value)


def _prepare_method(cls, parent):
        """ Unbound implementation of the prepare editor method to add a
        change notification hook in the items of the list before calling
        the parent prepare method of the parent class.

        """
        name = cls.extended_name
        if name != 'None':
            cls.context_object.on_trait_change(cls._update_editor,
                                                name + '[]',
                                                dispatch='ui')
        super(cls.__class__, cls).prepare(parent)

def _dispose_method(cls):
        """ Unbound implementation of the dispose editor method to remove
        the change notification hook in the items of the list before calling
        the parent dispose method of the parent class.

        """
        if cls.ui is None:
            return

        name = cls.extended_name
        if name != 'None':
            cls.context_object.on_trait_change(cls._update_editor,
                                                name + '[]',
                                                remove=True)
        super(cls.__class__, cls).dispose()

class CSVListEditor(TextEditor):
    """A text editor for a List.

    This editor provides a single line of input text of comma separated
    values.  (Actually, the default separator is a comma, but this can
    changed.)  The editor can only be used with List traits whose inner
    trait is one of Int, Float, Str, Enum, or Range.

    The 'simple', 'text', 'custom' and readonly styles are based on
    TextEditor. The 'readonly' style provides the same formatting in the
    text field as the other editors, but the user cannot change the value.

    Like other Traits editors, the background of the text field will turn
    red if the user enters an incorrectly formatted list or if the values
    do not match the type of the inner trait.  This validation only occurs
    while editing the text field.  If, for example, the inner trait is
    Range(low='lower', high='upper'), a change in 'upper' will not trigger
    the validation code of the editor.

    The editor removes whitespace of entered items with strip(), so for
    Str types, the editor should not be used if whitespace at the beginning
    or end of the string must be preserved.

    Constructor Keyword Arguments
    -----------------------------
    sep : str or None, optional
        The separator of the values in the list.  If None, each contiguous
        sequence of whitespace is a separator.
        Default is ','.

    ignore_trailing_sep : bool, optional
        If this is False, a line containing a trailing separator is invalid.
        Default is True.

    auto_set : bool
        If True, then every keystroke sets the value of the trait.

    enter_set : bool
        If True, the user input sets the value when the Enter key is pressed.

    Example
    -------
    The following will display a window containing a single input field.
    Entering, say, '0, .5, 1' in this field will result in the list
    x = [0.0, 0.5, 1.0].
    """

    # The separator of the element in the list.
    sep = Trait(',', None, Str)

     # If False, it is an error to have a trailing separator.
    ignore_trailing_sep = Bool(True)

    # Include some of the TextEditor API:

    # Is user input set on every keystroke?
    auto_set = Bool(True)

    # Is user input set when the Enter key is pressed?
    enter_set = Bool(False)

    def _funcs(self, object, name):
        """Create the evalution and formatting functions for the editor.

        Parameters
        ----------
        object : instance of HasTraits
            This is the object that has the List trait for which we are
            creating an editor.

        name : str
            Name of the List trait on `object`.

        Returns
        -------
        evaluate, fmt_func : callable, callable
            The functions for converting a string to a list (`evaluate`)
            and a list to a string (`fmt_func`).  These are the functions
            that are ultimately given as the keyword arguments 'evaluate'
            and 'format_func' of the TextEditor that will be generated by
            the CSVListEditor editor factory functions.
        """
        t = getattr(object, name)
        # Get the list of inner traits.  Only a single inner trait is allowed.
        it_list = t.trait.inner_traits()
        if len(it_list) > 1:
            raise TraitError("Only one inner trait may be specified when "
                             "using a CSVListEditor.")

        # `it` is the single inner trait.  This will be an instance of
        # traits.traits.CTrait.
        it = it_list[0]
        # The following 'if' statement figures out the appropriate evaluation
        # function (evaluate) and formatting function (fmt_func) for the
        # given inner trait.
        if it.is_trait_type(Int) or it.is_trait_type(Float) or \
                                                it.is_trait_type(Str):
            evaluate = \
                lambda s: _eval_list_str(s, sep=self.sep,
                                item_eval=it.trait_type.evaluate,
                                ignore_trailing_sep=self.ignore_trailing_sep)
            fmt_func = lambda vals: _format_list_str(vals,
                                                    sep=self.sep)
        elif it.is_trait_type(Enum):
            values, mapping, inverse_mapping = enum_values_changed(it)
            evaluate = \
                lambda s: _eval_list_str(s, sep=self.sep,
                                item_eval=mapping.__getitem__,
                                ignore_trailing_sep=self.ignore_trailing_sep)
            fmt_func = \
                lambda vals: \
                    _format_list_str(vals, sep=self.sep,
                                     item_format=inverse_mapping.__getitem__)
        elif it.is_trait_type(Range):
            # Get the type of the values from the default value.
            # range_object will be an instance of traits.trait_types.Range.
            range_object = it.handler
            if range_object.default_value_type == 8:
                # range_object.default_value is callable.
                defval = range_object.default_value(object)
            else:
                # range_object.default_value *is* the default value.
                defval = range_object.default_value
            typ = type(defval)

            if range_object.validate is None:
                # This will be the case for dynamic ranges.
                item_eval = lambda s: _validate_range_value(
                                        range_object, object, name, typ(s))
            else:
                # Static ranges have a validate method.
                item_eval = lambda s: range_object.validate(
                                                    object, name, typ(s))

            evaluate = \
                lambda s: _eval_list_str(s, sep=self.sep,
                                item_eval=item_eval,
                                ignore_trailing_sep=self.ignore_trailing_sep)
            fmt_func = lambda vals: _format_list_str(vals,
                                                     sep=self.sep)
        else:
            raise TraitError("To use a CSVListEditor, the inner trait of the "
                             "List must be Int, Float, Range, Str or Enum.")

        return evaluate, fmt_func


    #---------------------------------------------------------------------------
    #  Methods that generate backend toolkit-specific editors.
    #---------------------------------------------------------------------------

    def simple_editor ( self, ui, object, name, description, parent ):
        """ Generates an editor using the "simple" style.
        """
        self.evaluate, self.format_func = self._funcs(object, name)
        return self.simple_editor_class( parent,
                                         factory     = self,
                                         ui          = ui,
                                         object      = object,
                                         name        = name,
                                         description = description )

    def custom_editor ( self, ui, object, name, description, parent ):
        """ Generates an editor using the "custom" style.
        """
        self.evaluate, self.format_func = self._funcs(object, name)
        return self.custom_editor_class( parent,
                                         factory     = self,
                                         ui          = ui,
                                         object      = object,
                                         name        = name,
                                         description = description )

    def text_editor ( self, ui, object, name, description, parent ):
        """ Generates an editor using the "text" style.
        """
        self.evaluate, self.format_func = self._funcs(object, name)
        return self.text_editor_class( parent,
                                       factory     = self,
                                       ui          = ui,
                                       object      = object,
                                       name        = name,
                                       description = description )

    def readonly_editor ( self, ui, object, name, description, parent ):
        """ Generates an "editor" that is read-only.
        """
        self.evaluate, self.format_func = self._funcs(object, name)
        return self.readonly_editor_class( parent,
                                           factory     = self,
                                           ui          = ui,
                                           object      = object,
                                           name        = name,
                                           description = description )
