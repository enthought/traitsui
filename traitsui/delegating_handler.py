# (C) Copyright 2004-2022 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

"""
A handler that delegates the handling of events to a set of sub-handlers.

This is typically used as the handler for dynamic views.  See the
**traits.has_dynamic_view** module.
"""

# Enthought library imports
from traits.api import HasTraits, List
from .ui import Dispatcher

# Local imports.
from .handler import Handler

# Set up a logger:
import logging

logger = logging.getLogger(__name__)


class DelegatingHandler(Handler):
    """A handler that delegates the handling of events to a set of
    sub-handlers.
    """

    # -- Public 'DelegatingHandler' Interface ---------------------------------

    #: The list of sub-handlers this object delegates to:
    sub_handlers = List(HasTraits)

    # -- Protected 'DelegatingHandler' Interface ------------------------------

    #: A list of dispatchable handler methods:
    _dispatchers = List()

    # -------------------------------------------------------------------------
    #  'Handler' interface:
    # -------------------------------------------------------------------------

    # -- Public Methods -------------------------------------------------------

    def closed(self, info, is_ok):
        """Handles the user interface being closed by the user.

        This method is overridden here to unregister any dispatchers that
        were set up in the *init()* method.
        """
        for d in self._dispatchers:
            d.remove()

    def init(self, info):
        """Initializes the controls of a user interface.

        This method is called after all user interface elements have been
        created, but before the user interface is displayed. Use this method to
        further customize the user interface before it is displayed.

        This method is overridden here to delegate to sub-handlers.

        Parameters
        ----------
        info : *UIInfo* object
            The UIInfo object associated with the view

        Returns
        -------
        initialized : bool
            A boolean, indicating whether the user interface was successfully
            initialized. A True value indicates that the UI can be displayed;
            a False value indicates that the display operation should be
            cancelled.
        """

        # Iterate through our sub-handlers, and for each method whose name is
        # of the form 'object_name_changed', where 'object' is the name of an
        # object in the UI's context, create a trait notification handler that
        # will call the method whenever object's 'name' trait changes.
        logger.debug("Initializing delegation in DelegatingHandler [%s]", self)
        context = info.ui.context
        for h in self.sub_handlers:
            # fixme: I don't know why this wasn't here before... I'm not
            # sure this is right!
            h.init(info)

            for name in self._each_trait_method(h):
                if name[-8:] == "_changed":
                    prefix = name[:-8]
                    col = prefix.find("_", 1)
                    if col >= 0:
                        object = context.get(prefix[:col])
                        if object is not None:
                            logger.debug(
                                "\tto method [%s] on handler[%s]", name, h
                            )
                            method = getattr(h, name)
                            trait_name = prefix[col + 1 :]
                            self._dispatchers.append(
                                Dispatcher(method, info, object, trait_name)
                            )

                            # Also invoke the method immediately so initial
                            # user interface state can be correctly set.
                            if object.base_trait(trait_name).type != "event":
                                method(info)

                # fixme: These are explicit workarounds for problems with:-
                #
                # 'GeometryHierarchyViewHandler'
                #
                # which is used in the :-
                #
                # 'GeometryHierarchyTreeEditor'
                #
                # which are in the 'encode.cad.ui.geometry' package.
                #
                # The tree editor has dynamic views, and hence the handler gets
                # wrapped by a 'DelegatingHandler'. Unfortunately the handler
                # has a couple of methods that aren't picked up by the usual
                # wrapping strategy:-
                #
                # 1) 'tree_item_selected'
                #
                # - which is obviously called when a tree item is selected.
                #
                # 2) 'inspect_object'
                #
                # - which is called directly as as action from the context menu
                #   defined in the tree editor.
                #
                elif name in ["tree_item_selected", "inspect_object"]:
                    self.__dict__[name] = self._create_delegate(h, name)

        return True

    def _create_delegate(self, h, name):
        """Quick fix for handler methods that are currently left out!"""

        def delegate(*args, **kw):
            method = getattr(h, name)
            return method(*args, **kw)

        return delegate
