#
#  Copyright (c) 2005-19, Enthought, Inc.
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

""" Defines the abstract Editor class, which represents an editing control for
    an object trait in a Traits-based user interface.
"""

from __future__ import absolute_import

from contextlib import contextmanager
from functools import partial

import six

from traits.api import (
    Any, Bool, HasPrivateTraits, HasTraits, Instance, List, Property, ReadOnly,
    Set, Str, TraitError, TraitListEvent, Tuple, Undefined, cached_property
)
from traits.trait_base import not_none, xgetattr, xsetattr

from .editor_factory import EditorFactory
from .context_value import ContextValue
from .undo import UndoItem
from .item import Item


#: Reference to an EditorFactory object
factory_trait = Instance(EditorFactory)


class Editor(HasPrivateTraits):
    """ Represents an editing control for an object trait in a Traits-based
        user interface.
    """

    #: The UI (user interface) this editor is part of:
    ui = Instance('traitsui.ui.UI', clean_up=True)

    #: Full name of the object the editor is editing (e.g.
    #: 'object.link1.link2'):
    object_name = Str('object')

    #: The object this editor is editing (e.g. object.link1.link2):
    object = Instance(HasTraits, clean_up=True)

    #: The name of the trait this editor is editing (e.g. 'value'):
    name = ReadOnly

    #: The context object the editor is editing (e.g. object):
    context_object = Property

    #: The extended name of the object trait being edited. That is,
    #: 'object_name.name' minus the context object name at the beginning. For
    #: example: 'link1.link2.value':
    extended_name = Property

    #: Original value of object.name (e.g. object.link1.link2.value):
    old_value = Any(clean_up=True)

    #: Text description of the object trait being edited:
    description = ReadOnly

    #: The Item object used to create this editor:
    item = Instance(Item, (), clean_up=True)

    #: The GUI widget defined by this editor:
    control = Any(clean_up=True)

    #: The GUI label (if any) defined by this editor:
    label_control = Any(clean_up=True)

    #: Is the underlying GUI widget enabled?
    enabled = Bool(True)

    #: Is the underlying GUI widget visible?
    visible = Bool(True)

    #: Is the underlying GUI widget scrollable?
    scrollable = Bool(False)

    #: The EditorFactory used to create this editor:
    factory = Instance(EditorFactory, clean_up=True)

    #: Is the editor updating the object.name value?
    updating = Bool(False)

    #: The current value of the trait being edited.
    value = Property

    #: The current value of object trait as a string.
    str_value = Property

    #: The trait the editor is editing (not its value, but the trait itself).
    value_trait = Property

    #: The current editor invalid state status:
    invalid = Bool(False)

    # Private traits --------------------------------------------------------

    #: The errors in the editor, if any.
    _error = Any

    #: A set to track values being updated to prevent infinite recursion.
    _no_trait_update = Set()

    #: A list of all values synchronized to.
    _user_to = List(Tuple)

    #: A list of all values synchronized from.
    _user_from = List(Tuple)

    # Abstract methods ------------------------------------------------------

    def init(self, parent):
        """ Creating the underlying toolkit for the widget.

        This method must be overriden by subclasses.  Implementations must
        ensure that the :attr:`control` trait is set to an appropriate
        toolkit object.

        Parameters
        ----------
        parent : toolkit control
            The parent toolkit object of the editor's toolkit objects.
        """
        raise NotImplementedError

    def update_editor(self):
        """ Updates the editor when the value changes externally to the editor.

        This should normally be overridden in a subclass.
        """
        pass

    def set_focus(self):
        """ Assigns focus to the editor's underlying toolkit widget.

        This method must be overriden by subclasses.
        """
        raise NotImplementedError

    def error(self, excp):
        """ Handles an error that occurs while setting the object's trait value.

        This should normally be overridden in a subclass.
        """
        pass

    def string_value(self, value, format_func=None):
        """ Returns the text representation of a specified object trait value.

        This simply delegates to the factorys `string_value` method.
        Sub-classes may choose to override the default implementation.
        """
        return self.factory.string_value(value, format_func)

    # Editor life-cycle methods ---------------------------------------------

    def prepare(self, parent):
        """ Finish setting up the editor.
        """
        name = self.extended_name
        if name != 'None':
            self.context_object.on_trait_change(
                self._update_editor, name, dispatch='ui')
        self.init(parent)
        self._sync_values()
        self.update_editor()

    def dispose(self):
        """ Disposes of the contents of an editor.

        This disconnects any synchronised values and resets references
        to other objects.

        Subclasses may chose to override this method to perform additional
        clean-up.
        """
        if self.ui is None:
            return

        name = self.extended_name
        if name != 'None':
            self.context_object.on_trait_change(self._update_editor, name,
                                                remove=True)

        if self._user_from is not None:
            for name, handler in self._user_from:
                self.on_trait_change(handler, name, remove=True)

        if self._user_to is not None:
            for object, name, handler in self._user_to:
                object.on_trait_change(handler, name, remove=True)

        # Break linkages to references we no longer need:
        for name in self.trait_names(clean_up=True):
            setattr(self, name, None)

    # Undo/redo methods -----------------------------------------------------

    def log_change(self, undo_factory, *undo_args):
        """ Logs a change made in the editor with undo/redo history.

        Parameters
        ----------
        undo_factory : callable
            Callable that creates an undo item.  Often self.get_undo_item.
        *undo_args
            Any arguments to pass to the undo factory.
        """
        # Indicate that the contents of the user interface have been changed:
        ui = self.ui
        ui.modified = True

        # Create an undo history entry if we are maintaining a history:
        undoable = ui._undoable
        if undoable >= 0:
            history = ui.history
            if history is not None:
                item = undo_factory(*undo_args)
                if item is not None:
                    if undoable == history.now:
                        # Create a new undo transaction:
                        history.add(item)
                    else:
                        # Extend the most recent undo transaction:
                        history.extend(item)

    def get_undo_item(self, object, name, old_value, new_value):
        """ Creates an undo history entry.

        Can be overridden in a subclass for special value types.
        """
        return UndoItem(
            object=object,
            name=name,
            old_value=old_value,
            new_value=new_value
        )

    # Trait synchronization routines ----------------------------------------

    def sync_value(self, user_name, editor_name, mode='both',
                   is_list=False, is_event=False):
        """ Synchronize an editor trait and a user object trait.

        Also sets the initial value of the editor trait from the
        user object trait (for modes 'from' and 'both'), and the initial
        value of the user object trait from the editor trait (for mode
        'to'), as long as the relevant traits are not events.

        Parameters
        ----------
        user_name : string
            The name of the trait to be used on the user object. If empty, no
            synchronization will be set up.
        editor_name : string
            The name of the relevant editor trait.
        mode : string, optional; one of 'to', 'from' or 'both'
            The direction of synchronization. 'from' means that trait changes
            in the user object should be propagated to the editor. 'to' means
            that trait changes in the editor should be propagated to the user
            object. 'both' means changes should be propagated in both
            directions. The default is 'both'.
        is_list : bool, optional
            If true, synchronization for item events will be set up in
            addition to the synchronization for the object itself.
            The default is False.
        is_event : bool, optional
            If true, this method won't attempt to initialize the user
            object or editor trait values. The default is False.
        """
        if user_name == '':
            return

        key = '%s:%s' % (user_name, editor_name)

        parts = user_name.split('.')
        if len(parts) == 1:
            user_object = self.context_object
            xuser_name = user_name
        else:
            user_object = self.ui.context[parts[0]]
            xuser_name = '.'.join(parts[1:])
            user_name = parts[-1]

        if mode in {'from', 'both'}:
            self.bind_from(key, user_object, xuser_name, editor_name, is_list)

            if not is_event:
                # initialize editor value from user value
                with self.raise_to_debug():
                    user_value = xgetattr(user_object, xuser_name)
                    setattr(self, editor_name, user_value)

        if mode in {'to', 'both'}:
            self.bind_to(key, user_object, xuser_name, editor_name, is_list)

            if mode == 'to' and not is_event:
                # initialize user value from editor value
                with self.raise_to_debug():
                    editor_value = xgetattr(self, editor_name)
                    xsetattr(user_object, xuser_name, editor_value)

    def bind_from(self, key, user_object, xuser_name, editor_name, is_list):
        """ Bind trait change handlers from a user object to the editor.

        Parameters
        ----------
        key : str
            The key to use to guard against recursive updates.
        user_object : object
            The extended name of the trait to be used on the user object.
        editor_name : string
            The name of the relevant editor trait.
        is_list : bool, optional
            If true, synchronization for item events will be set up in
            addition to the synchronization for the object itself.
            The default is False.
        """

        def user_trait_modified(new):
            if key not in self._no_trait_update:
                with self.no_trait_update(key), self.raise_to_debug():
                    xsetattr(self, editor_name, new)

        user_object.on_trait_change(user_trait_modified, xuser_name)
        self._user_to.append((user_object, xuser_name, user_trait_modified))

        if is_list:

            def user_list_modified(event):
                if (isinstance(event, TraitListEvent)
                        and key not in self._no_trait_update):
                    with self.no_trait_update(key), self.raise_to_debug():
                        n = event.index
                        getattr(self, editor_name)[
                            n: n + len(event.removed)] = event.added

            items = xuser_name + '_items'
            user_object.on_trait_change(user_list_modified, items)
            self._user_to.append((user_object, items, user_list_modified))

    def bind_to(self, key, user_object, xuser_name, editor_name, is_list):
        """ Bind trait change handlers from a user object to the editor.

        Parameters
        ----------
        key : str
            The key to use to guard against recursive updates.
        user_object : object
            The extended name of the trait to be used on the user object.
        editor_name : string
            The name of the relevant editor trait.
        is_list : bool, optional
            If true, synchronization for item events will be set up in
            addition to the synchronization for the object itself.
            The default is False.
        """

        def editor_trait_modified(new):
            if key not in self._no_trait_update:
                with self.no_trait_update(key), self.raise_to_debug():
                    xsetattr(user_object, xuser_name, new)

        self.on_trait_change(editor_trait_modified, editor_name)

        if self._user_from is None:
            self._user_from = []
        self._user_from.append((editor_name, editor_trait_modified))

        if is_list:

            def editor_list_modified(event):
                if key not in self._no_trait_update:
                    with self.no_trait_update(key), self.raise_to_debug():
                        n = event.index
                        value = xgetattr(user_object, xuser_name)
                        value[n:n + len(event.removed)] = event.added

            self.on_trait_change(
                editor_list_modified, editor_name + '_items')
            self._user_from.append(
                (editor_name + '_items', editor_list_modified))

    def parse_extended_name(self, name):
        """ Extract the object, name and a getter from an extended name

        Parameters
        ----------
        name : str
            The extended name to parse.

        Returns
        -------
        object, name, getter : any, str, callable
            The object from the context, the (extended) name of the
            attributes holding the value, and a callable which gets the
            current value from the context.
        """
        parts = name.split('.', 1)
        if len(parts) == 1:
            object = self.context_object
        else:
            object_name, name = parts
            object = self.ui.context[object_name]

        return (object, name, partial(xgetattr, object, name))

    # UI preference save/restore interface ----------------------------------

    def restore_prefs(self, prefs):
        """ Restores any saved user preference information associated with the
            editor.
        """
        pass

    def save_prefs(self):
        """ Returns any user preference information associated with the editor.
        """
        return None

    # Utility context managers ----------------------------------------------

    @contextmanager
    def no_trait_update(self, name):
        """ Context manager that blocks updates from the named trait. """
        if self._no_trait_update is None:
            self._no_trait_update = set()

        self._no_trait_update.add(name)
        try:
            yield
        finally:
            self._no_trait_update.remove(name)

    @contextmanager
    def raise_to_debug(self):
        """ Context manager that uses raise to debug to raise exceptions. """
        try:
            yield
        except Exception:
            from traitsui.api import raise_to_debug
            raise_to_debug()

    @contextmanager
    def no_value_update(self):
        """ Context manager to handle updating value. """
        self.updating = True
        try:
            yield
        finally:
            self.updating = False

    # ------------------------------------------------------------------------
    # object interface
    # ------------------------------------------------------------------------

    def __init__(self, parent, **traits):
        """ Initializes the editor object.
        """
        super(HasPrivateTraits, self).__init__(**traits)
        try:
            self.old_value = getattr(self.object, self.name)
        except AttributeError:
            ctrait = self.object.base_trait(self.name)
            if ctrait.type == 'event' or self.name == 'spring':
                # Getting the attribute will fail for 'Event' traits:
                self.old_value = Undefined
            else:
                raise

        # Synchronize the application invalid state status with the editor's:
        self.sync_value(self.factory.invalid, 'invalid', 'from')

    # ------------------------------------------------------------------------
    # private interface
    # ------------------------------------------------------------------------

    def _update_editor(self, object, name, old_value, new_value):
        """ Performs updates when the object trait changes.
        """
        # If background threads have modified the trait the editor is bound to,
        # their trait notifications are queued to the UI thread. It is possible
        # that by the time the UI thread dispatches these events, the UI the
        # editor is part of has already been closed. So we need to check if we
        # are still bound to a live UI, and if not, exit immediately:
        if self.ui is None:
            return

        # If the notification is for an object different than the one actually
        # being edited, it is due to editing an item of the form:
        # object.link1.link2.name, where one of the 'link' objects may have
        # been modified. In this case, we need to rebind the current object
        # being edited:
        if object is not self.object:
            self.object = self.ui.get_extended_value(self.object_name)

        # If the editor has gone away for some reason, disconnect and exit:
        if self.control is None:
            self.context_object.on_trait_change(
                self._update_editor, self.extended_name, remove=True)
            return

        # Log the change that was made (as long as the Item is not readonly
        # or it is not for an event):
        if (self.item.style != 'readonly'
                and object.base_trait(name).type != 'event'):
            self.log_change(self.get_undo_item, object, name,
                            old_value, new_value)

        # If the change was not caused by the editor itself:
        if not self._no_update:
            # Update the editor control to reflect the current object state:
            self.update_editor()

    def _sync_values(self):
        """ Initialize and synchronize editor and factory traits

        Initializes and synchronizes (as needed) editor traits with the
        value of corresponding factory traits.  The name of the factory
        trait and the editor trait must match and the factory trait needs
        to have ``sync_value`` metadata set.  The strategy followed is:

        - for each factory trait with ``sync_value`` metadata:

          1.  if the value is a :class:`ContextValue` instance then
              call :meth:`sync_value` with the ``name`` from the
              context value.
          2.  if the trait has ``sync_name`` metadata, look at the
              referenced trait value and if it is a non-empty string
              then use this value as the name of the value in the
              context.
          3.  otherwise initialize the current value of the factory
              trait to the corresponding value of the editor.

        - synchronization mode in cases 1 and 2 is taken from the
          ``sync_value`` metadata of the editor trait first and then
          the ``sync_value`` metadata of the factory trait if that is
          empty.

        - if the value is a container type, then the `is_list` metadata
          is set to
        """
        factory = self.factory
        for name, trait in factory.traits(sync_value=not_none).items():
            value = getattr(factory, name)
            self_trait = self.trait(name)
            if self_trait.sync_value:
                mode = self_trait.sync_value
            else:
                mode = trait.sync_value
            if isinstance(value, ContextValue):
                self.sync_value(
                    value.name, name, mode, bool(self_trait.is_list),
                    self_trait.type == 'event'
                )
            elif (trait.sync_name is not None
                    and getattr(factory, trait.sync_name, '') != ''):
                # Note: this is implemented as a stepping stone from things
                # like ``low_name`` and ``high_name`` to using context values.
                sync_name = getattr(factory, trait.sync_name)
                self.sync_value(
                    sync_name, name, mode, bool(self_trait.is_list),
                    self_trait.type == 'event'
                )
            elif value is not Undefined:
                setattr(self, name, value)

    def _str(self, value):
        """ Returns the text representation of a specified value.

        This is a convenience method to cover the differences between Python
        2 and Python 3 strings.

        Parameters
        ----------
        value : any
            The value to be represented as a string.

        Returns
        -------
        string :
        """
        # In Unicode!
        return six.text_type(value)

    # Traits property handlers ----------------------------------------------

    @cached_property
    def _get_context_object(self):
        """ Returns the context object the editor is using

        In some cases a proxy object is edited rather than an object directly
        in the context, in which case we return ``self.object``.
        """
        object_name = self.object_name
        context_key = object_name.split('.', 1)[0]
        if (object_name != '') and (context_key in self.ui.context):
            return self.ui.context[context_key]

        # This handles the case of a 'ListItemProxy', which is not in the
        # ui.context, but is the editor 'object':
        return self.object

    @cached_property
    def _get_extended_name(self):
        """ Returns the extended trait name being edited.
        """
        return ('%s.%s' % (self.object_name, self.name)).split('.', 1)[1]

    def _get_value_trait(self):
        """ Returns the trait the editor is editing.
        """
        return self.object.trait(self.name)

    def _get_value(self):
        return getattr(self.object, self.name, Undefined)

    def _set_value(self, value):
        if self.ui and self.name != 'None':
            self.ui.do_undoable(self.__set_value, value)

    def __set_value(self, value):
        self._no_update = True
        try:
            try:
                handler = self.ui.handler
                obj_name = self.object_name
                name = self.name
                method = (getattr(handler, '%s_%s_setattr' % (obj_name,
                                                              name), None) or
                          getattr(handler, '%s_setattr' % name, None) or
                          getattr(handler, 'setattr'))
                method(self.ui.info, self.object, name, value)
            except TraitError as excp:
                self.error(excp)
                raise
        finally:
            self._no_update = False

    def _get_str_value(self):
        """ Returns the text representation of the object trait.
        """
        return self.string_value(getattr(self.object, self.name, Undefined))
