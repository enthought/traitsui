#------------------------------------------------------------------------------
#
#  Copyright (c) 2005, Enthought, Inc.
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
#  Date:   10/07/2004
#
#------------------------------------------------------------------------------

""" Defines the abstract EditorFactory class, which represents a factory for
    creating the Editor objects used in a Traits-based user interface.
"""

#-------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------

from __future__ import absolute_import, print_function

import logging

import six

from traits.api import (
    HasPrivateTraits, Callable, Str, Bool, Event, Any, Property
)

from .helper import enum_values_changed
from .toolkit import toolkit_object


logger = logging.getLogger(__name__)

#-------------------------------------------------------------------------
#  'EditorFactory' abstract base class:
#-------------------------------------------------------------------------


class EditorFactory(HasPrivateTraits):
    """ Represents a factory for creating the Editor objects in a Traits-based
        user interface.
    """

    #-------------------------------------------------------------------------
    #  Trait definitions:
    #-------------------------------------------------------------------------

    # Function to use for string formatting
    format_func = Callable

    # Format string to use for formatting (used if **format_func** is not set).
    format_str = Str

    # Is the editor being used to create table grid cells?
    is_grid_cell = Bool(False)

    # Are created editors initially enabled?
    enabled = Bool(True)

    # The extended trait name of the trait containing editor invalid state
    # status:
    invalid = Str

    # Text aligment to use in most readonly editors
    # Possible values: left, right, top, bottom, just, vcenter, hcenter, center
    # Example: left,vcenter
    text_alignment = Str

    # The editor class to use for 'simple' style views.
    simple_editor_class = Property

    # The editor class to use for 'custom' style views.
    custom_editor_class = Property

    # The editor class to use for 'text' style views.
    text_editor_class = Property

    # The editor class to use for 'readonly' style views.
    readonly_editor_class = Property

    #-------------------------------------------------------------------------
    #  Initializes the object:
    #-------------------------------------------------------------------------

    def __init__(self, *args, **traits):
        """ Initializes the factory object.
        """
        HasPrivateTraits.__init__(self, **traits)
        self.init(*args)

    #-------------------------------------------------------------------------
    #  Performs any initialization needed after all constructor traits have
    #  been set:
    #-------------------------------------------------------------------------

    def init(self):
        """ Performs any initialization needed after all constructor traits
            have been set.
        """
        pass

    #-------------------------------------------------------------------------
    #  Returns the value of a specified extended name of the form: name or
    #  context_object_name.name[.name...]:
    #-------------------------------------------------------------------------

    def named_value(self, name, ui):
        """ Returns the value of a specified extended name of the form: name or
            context_object_name.name[.name...]:
        """
        names = name.split('.')

        if len(names) == 1:
            # fixme: This will produce incorrect values if the actual Item the
            # factory is being used with does not use the default object='name'
            # value, and the specified 'name' does not contain a '.'. The
            # solution will probably involve providing the Item as an argument,
            # but it is currently not available at the time this method needs to
            # be called...
            names.insert(0, 'object')

        value = ui.context[names[0]]
        for name in names[1:]:
            value = getattr(value, name)

        return value
    #-------------------------------------------------------------------------
    #  Methods that generate backend toolkit-specific editors.
    #-------------------------------------------------------------------------

    def simple_editor(self, ui, object, name, description, parent):
        """ Generates an editor using the "simple" style.
        """
        return self.simple_editor_class(parent,
                                        factory=self,
                                        ui=ui,
                                        object=object,
                                        name=name,
                                        description=description)

    def custom_editor(self, ui, object, name, description, parent):
        """ Generates an editor using the "custom" style.
        """
        return self.custom_editor_class(parent,
                                        factory=self,
                                        ui=ui,
                                        object=object,
                                        name=name,
                                        description=description)

    def text_editor(self, ui, object, name, description, parent):
        """ Generates an editor using the "text" style.
        """
        return self.text_editor_class(parent,
                                      factory=self,
                                      ui=ui,
                                      object=object,
                                      name=name,
                                      description=description)

    def readonly_editor(self, ui, object, name, description, parent):
        """ Generates an "editor" that is read-only.
        """
        return self.readonly_editor_class(parent,
                                          factory=self,
                                          ui=ui,
                                          object=object,
                                          name=name,
                                          description=description)

    #-------------------------------------------------------------------------
    #  Private methods
    #-------------------------------------------------------------------------

    @classmethod
    def _get_toolkit_editor(cls, class_name):
        """
        Returns the editor by name class_name in the backend package.
        """
        editor_factory_modules = [factory_class.__module__
                                  for factory_class in cls.mro()
                                  if issubclass(factory_class, EditorFactory)]
        for index, editor_module in enumerate(editor_factory_modules):
            try:
                editor_module_name = editor_module.split('.')[-1]
                object_ref = ':'.join([editor_module_name, class_name])
                return toolkit_object(object_ref, True)
            except RuntimeError as e:
                msg = "Can't import toolkit_object '{}': {}"
                logger.debug(msg.format(object_ref, e))
                if index == len(editor_factory_modules) - 1:
                    raise e
        return None

    def string_value(self, value, format_func=None):
        """ Returns the text representation of a specified object trait value.

        If the **format_func** attribute is set on the editor factory, then
        this method calls that function to do the formatting.  If the
        **format_str** attribute is set on the editor factory, then this
        method uses that string for formatting. If neither attribute is
        set, then this method just calls the appropriate text type to format.
        """
        if self.format_func is not None:
            return self.format_func(value)

        if self.format_str != '':
            return self.format_str % value

        if format_func is not None:
            return format_func(value)

        return six.text_type(value)

    #-------------------------------------------------------------------------
    #  Property getters
    #-------------------------------------------------------------------------

    def _get_simple_editor_class(self):
        """ Returns the editor class to use for "simple" style views.
        The default implementation tries to import the SimpleEditor class in the
        editor file in the backend package, and if such a class is not to found
        it returns the SimpleEditor class defined in editor_factory module in
        the backend package.

        """
        try:
            SimpleEditor = self._get_toolkit_editor('SimpleEditor')
        except Exception as e:
            msg = "Can't import SimpleEditor for {}: {}"
            logger.debug(msg.format(self.__class__, e))
            SimpleEditor = toolkit_object('editor_factory:SimpleEditor')
        return SimpleEditor

    def _get_custom_editor_class(self):
        """ Returns the editor class to use for "custom" style views.
        The default implementation tries to import the CustomEditor class in the
        editor file in the backend package, and if such a class is not to found
        it returns simple_editor_class.

        """
        try:
            CustomEditor = self._get_toolkit_editor('CustomEditor')
        except Exception as e:
            msg = "Can't import CustomEditor for {}: {}"
            logger.debug(msg.format(self.__class__, e))
            CustomEditor = self.simple_editor_class
        return CustomEditor

    def _get_text_editor_class(self):
        """ Returns the editor class to use for "text" style views.
        The default implementation tries to import the TextEditor class in the
        editor file in the backend package, and if such a class is not found
        it returns the TextEditor class declared in the editor_factory module in
        the backend package.

        """
        try:
            TextEditor = self._get_toolkit_editor('TextEditor')
        except Exception as e:
            msg = "Can't import TextEditor for {}: {}"
            logger.debug(msg.format(self.__class__, e))
            TextEditor = toolkit_object('editor_factory:TextEditor')
        return TextEditor

    def _get_readonly_editor_class(self):
        """ Returns the editor class to use for "readonly" style views.
        The default implementation tries to import the ReadonlyEditor class in
        the editor file in the backend package, and if such a class is not found
        it returns the ReadonlyEditor class declared in the editor_factory
        module in the backend package.

        """
        try:
            ReadonlyEditor = self._get_toolkit_editor('ReadonlyEditor')
        except Exception as e:
            msg = "Can't import ReadonlyEditor for {}: {}"
            logger.debug(msg.format(self.__class__, e))
            ReadonlyEditor = toolkit_object('editor_factory:ReadonlyEditor')
        return ReadonlyEditor


#-------------------------------------------------------------------------
#  'EditorWithListFactory' abstract base class:
#-------------------------------------------------------------------------

class EditorWithListFactory(EditorFactory):
    """ Base class for factories of editors for objects that contain lists.
    """

    #-------------------------------------------------------------------------
    #  Trait definitions:
    #-------------------------------------------------------------------------

    # Values to enumerate (can be a list, tuple, dict, or a CTrait or
    # TraitHandler that is "mapped"):
    values = Any

    # Extended name of the trait on **object** containing the enumeration data:
    object = Str('object')

    # Name of the trait on 'object' containing the enumeration data
    name = Str

    # Fired when the **values** trait has been updated:
    values_modified = Event

    #-------------------------------------------------------------------------
    #  Recomputes the mappings whenever the 'values' trait is changed:
    #-------------------------------------------------------------------------

    def _values_changed(self):
        """ Recomputes the mappings whenever the **values** trait is changed.
        """
        self._names, self._mapping, self._inverse_mapping = \
            enum_values_changed(self.values, strfunc=self.string_value)

        self.values_modified = True
