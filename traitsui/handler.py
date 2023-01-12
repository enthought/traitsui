# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Defines the Handler class used to manage and control the editing process in
    a Traits-based user interface.
"""

# avoid deprecation warning
from inspect import getfullargspec

from traits.api import HasPrivateTraits, HasTraits, Instance

from .toolkit import toolkit
from .help import on_help_call
from .view_element import ViewElement
from .helper import user_name_for
from .ui_info import UIInfo

# -------------------------------------------------------------------------
#  Closes a DockControl (if allowed by the associated traits UI Handler):
# -------------------------------------------------------------------------


def close_dock_control(dock_control):
    """Closes a DockControl (if allowed by the associated Traits UI Handler)."""
    # Retrieve the traits UI object set when we created the DockControl:
    ui = dock_control.data

    # Ask the traits UI handler if it is OK to close the window:
    if not ui.handler.close(ui.info, True):
        # If not, tell the DockWindow not to close it:
        return False

    # Otherwise, clean up and close the traits UI:
    ui.dispose()

    # And tell the DockWindow to remove the DockControl:
    return True


class Handler(HasPrivateTraits):
    """Provides access to and control over the run-time workings of a
    Traits-based user interface.
    """

    def init_info(self, info):
        """Informs the handler what the UIInfo object for a View will be.

        This method is called before the UI for the View has been
        constructed. It is provided so that the handler can save the
        reference to the UIInfo object in case it exposes viewable traits
        whose values are properties that depend upon items in the context
        being edited.
        """
        pass

    def init(self, info):
        """Initializes the controls of a user interface.

        This method is called after all user interface elements have been
        created, but before the user interface is displayed. Override this
        method to customize the user interface before it is displayed.

        Parameters
        ----------
        info : UIInfo object
            The UIInfo object associated with the view

        Returns
        -------
        initialized : bool
            A Boolean, indicating whether the user interface was successfully
            initialized. A True value indicates that the UI can be displayed;
            a False value indicates that the display operation should be
            cancelled. The default implementation returns True without taking
            any other action.
        """
        return True

    def position(self, info):
        """Positions a dialog-based user interface on the display.

        This method is called after the user interface is initialized (by
        calling init()), but before the user interface is displayed. Override
        this method to position the window on the display device. The default
        implementation calls the position() method of the current toolkit.

        Usually, you do not need to override this method, because you can
        control the window's placement using the **x** and **y** attributes
        of the View object.

        Parameters
        ----------
        info : UIInfo object
            The UIInfo object associated with the window
        """
        toolkit().position(info.ui)

    def close(self, info, is_ok):
        """Handles the user attempting to close a dialog-based user interface.

        This method is called when the user attempts to close a window, by
        clicking an **OK** or **Cancel** button, or clicking a Close control
        on the window). It is called before the window is actually destroyed.
        Override this method to perform any checks before closing a window.

        While Traits UI handles "OK" and "Cancel" events automatically, you
        can use the value of the *is_ok* parameter to implement additional
        behavior.

        Parameters
        ----------
        info : UIInfo object
            The UIInfo object associated with the view
        is_ok : Boolean
            Indicates whether the user confirmed the changes (such as by
            clicking **OK**.)

        Returns
        -------
        allow_close : bool
            A Boolean, indicating whether the window should be allowed to
            close.
        """
        return True

    def closed(self, info, is_ok):
        """Handles a dialog-based user interface being closed by the user.

        This method is called *after* the window is destroyed. Override this
        method to perform any clean-up tasks needed by the application.

        Parameters
        ----------
        info : UIInfo object
            The UIInfo object associated with the view
        is_ok : Boolean
            Indicates whether the user confirmed the changes (such as by
            clicking **OK**.)
        """
        return

    def revert(self, info):
        """Handles the **Revert** button being clicked."""
        return

    def apply(self, info):
        """Handles the **Apply** button being clicked."""
        return

    def show_help(self, info, control=None):
        """Shows the help associated with the view.

        This method is called when the user clicks a **Help** button in a
        Traits user interface. The method calls the global help handler, which
        might be the default help handler, or might be a custom help handler.
        See **traitsui.help** for details about the setting the
        global help handler.

        Parameters
        ----------
        info : UIInfo object
            The UIInfo object associated with the view
        control : UI control
            The control that invokes the help dialog box
        """
        if control is None:
            control = info.ui.control
        on_help_call()(info, control)

    def perform(self, info, action, event):
        """Perform computation for an action.

        The default method looks for a method matching ``action.action`` and
        calls it (sniffing the signature to determine how to call it for
        historical reasons).  If this is not found, then it calls the
        :py:meth:`~traitsui.menu.Action.perform` method of the action.

        Parameters
        ----------
        info : UIInfo instance
            The UIInfo assicated with the view, if available.
        action : Action instance
            The Action that the user invoked.
        event : ActionEvent instance
            The ActionEvent associated with the user action.

        Notes
        -----
        If overriding in a subclass, the method needs to ensure that any
        standard menu action items that are needed (eg. "Close", "Undo",
        "Redo", "Help", etc.) get dispatched correctly.
        """
        if action.action != "":
            method_name = action.action
        else:
            method_name = "_{}_clicked".format(action.name.lower())

        for object in self.get_perform_handlers(info):
            method = getattr(object, method_name, None)
            if method is not None:
                # call the action method
                specification = getfullargspec(method)
                if len(specification.args) == 1:
                    method()
                else:
                    method(info)
                # and we are done
                return

        # otherwise, call the perform method of the action
        specification = getfullargspec(action.perform)
        if len(specification.args) == 1:
            action.perform()
        else:
            action.perform(event)

    def get_perform_handlers(self, info):
        """Return a list of objects which can handle actions.

        This method may be overridden by sub-classes to return a more relevant
        set of objects.

        Parameters
        ----------
        info : UIInfo instance or None
            The UIInfo associated with the view, or None.

        Returns
        -------
        handlers : list
            A list of objects that may potentially have action methods on them.
        """
        handlers = [self]
        if info is not None:
            additional_objects = ["object", "model"]
            handlers += [
                info.ui.context[name]
                for name in additional_objects
                if name in info.ui.context
            ]
        return handlers

    def setattr(self, info, object, name, value):
        """Handles the user setting a specified object trait's value.

        This method is called when an editor attempts to set a new value for
        a specified object trait attribute. Use this method to control what
        happens when a trait editor tries to set an attribute value. For
        example, you can use this method to record a history of changes, in
        order to implement an "undo" mechanism. No result is returned. The
        default implementation simply calls the built-in setattr() function.
        If you override this method, make sure that it actually sets the
        attribute, either by calling the parent method or by setting the
        attribute directly

        Parameters
        ----------
        info : UIInfo instance
            The UIInfo for the current UI
        object : object
            The object whose attribute is being set
        name : string
            The name of the attribute being set
        value
            The value to which the attribute is being set

        """
        setattr(object, name, value)

    def trait_view_for(self, info, view, object, object_name, trait_name):
        """Gets a specified View object."""
        # If a view element was passed instead of a name or None, return it:
        if isinstance(view, ViewElement):
            return view

        # Generate a series of possible view or method names of the form:
        # - 'view'
        #   trait_view_for_'view'( object )
        # - 'class_view'
        #   trait_view_for_'class_view'( object )
        # - 'object_name_view'
        #   trait_view_for_'object_name_view'( object )
        # - 'object_name_class_view'
        #   trait_view_for_'object_name_class_view'( object )
        # where 'class' is the class name of 'object', 'object' is the object
        #       name, and 'name' is the trait name. It returns the first view
        #       or method result which is defined on the handler:
        klass = object.__class__.__name__
        cname = "%s_%s" % (object_name, trait_name)
        aview = ""
        if view:
            aview = "_" + view
        names = [
            "%s_%s%s" % (cname, klass, aview),
            "%s%s" % (cname, aview),
            "%s%s" % (klass, aview),
        ]
        if view:
            names.append(view)
        for name in names:
            result = self.trait_view(name)
            if result is not None:
                return result
            method = getattr(self, "trait_view_for_%s" % name, None)
            if callable(method):
                result = method(info, object)
                if result is not None:
                    return result

        # If nothing is defined on the handler, return either the requested
        # view on the object itself, or the object's default view:
        return object.trait_view(view) or object.trait_view()

    # -- 'DockWindowHandler' interface implementation -------------------------

    def can_drop(self, info, object):
        """Can the specified object be inserted into the view?"""
        from pyface.dock.api import DockControl

        if isinstance(object, DockControl):
            return self.can_import(info, object.export)

        drop_class = info.ui.view.drop_class
        return (drop_class is not None) and isinstance(object, drop_class)

    def can_import(self, info, category):
        return category in info.ui.view.imports

    def dock_control_for(self, info, parent, object):
        """Returns the DockControl object for a specified object."""
        from pyface.dock.api import IDockable, DockControl
        from .dockable_view_element import DockableViewElement

        try:
            name = object.name
        except:
            try:
                name = object.label
            except:
                name = ""
        if len(name) == 0:
            name = user_name_for(object.__class__.__name__)

        image = None
        export = ""
        if isinstance(object, DockControl):
            dock_control = object
            image = dock_control.image
            export = dock_control.export
            dockable = dock_control.dockable
            close = dockable.dockable_should_close()
            if close:
                dock_control.close(force=True)

            control = dockable.dockable_get_control(parent)

            # If DockControl was closed, then reset it to point to the new
            # control:
            if close:
                dock_control.trait_set(
                    control=control, style=parent.owner.style
                )
                dockable.dockable_init_dockcontrol(dock_control)
                return dock_control

        elif isinstance(object, IDockable):
            dockable = object
            control = dockable.dockable_get_control(parent)
        else:
            ui = object.get_dockable_ui(parent)
            dockable = DockableViewElement(ui=ui)
            export = ui.view.export
            control = ui.control

        dc = DockControl(
            control=control,
            name=name,
            export=export,
            style=parent.owner.style,
            image=image,
            closeable=True,
        )

        dockable.dockable_init_dockcontrol(dc)

        return dc

    def open_view_for(self, control, use_mouse=True):
        """Creates a new view of a specified control."""
        from pyface.dock.api import DockWindowShell

        DockWindowShell(control, use_mouse=use_mouse)

    def dock_window_empty(self, dock_window):
        """Handles a DockWindow becoming empty."""
        if dock_window.auto_close:
            dock_window.control.GetParent.Destroy()

    # -- HasTraits overrides: -------------------------------------------------

    def edit_traits(
        self,
        view=None,
        parent=None,
        kind=None,
        context=None,
        handler=None,
        id="",
        scrollable=None,
        **args,
    ):
        """Edits the object's traits."""
        if context is None:
            context = self

        if handler is None:
            handler = self

        return self.trait_view(view).ui(
            context,
            parent,
            kind,
            self.trait_view_elements(),
            handler,
            id,
            scrollable,
            args,
        )

    def configure_traits(
        self,
        filename=None,
        view=None,
        kind=None,
        edit=True,
        context=None,
        handler=None,
        id="",
        scrollable=None,
        **args,
    ):
        """Configures the object's traits."""
        return super().configure_traits(
            filename,
            view,
            kind,
            edit,
            context,
            handler or self,
            id,
            scrollable,
            **args,
        )

    # -- Private Methods: -----------------------------------------------------

    def _on_undo(self, info):
        """Handles an "Undo" change request."""
        if info.ui.history is not None:
            info.ui.history.undo()

    def _on_redo(self, info):
        """Handles a "Redo" change request."""
        if info.ui.history is not None:
            info.ui.history.redo()

    def _on_revert(self, info):
        """Handles a "Revert all changes" request."""
        if info.ui.history is not None:
            info.ui.history.revert()
            self.revert(info)

    def _on_close(self, info):
        """Handles a "Close" request."""
        if (info.ui.owner is not None) and self.close(info, True):
            info.ui.owner.close()


# -------------------------------------------------------------------------
#  Default handler:
# -------------------------------------------------------------------------

_default_handler = Handler()


def default_handler(handler=None):
    """Returns the global default handler.

    If *handler* is an instance of Handler, this function sets it as the
    global default handler.
    """
    global _default_handler

    if isinstance(handler, Handler):
        _default_handler = handler
    return _default_handler


class Controller(Handler):
    """Defines a handler class which provides a view and controller for a
    specified model.

    This class is used when implementing a standard MVC-based design. The
    **model** trait contains most, if not all, of the data being viewed,
    and can be referenced in a Controller instance's View definition using
    unadorned trait names. (e.g., ``Item('name')``).
    """

    # -- Trait Definitions ----------------------------------------------------

    #: The model this handler defines a view and controller for
    model = Instance(HasTraits)

    #: The Info object associated with the controller
    info = Instance(UIInfo)

    # -- HasTraits Method Overrides -------------------------------------------

    def __init__(self, model=None, **metadata):
        """Initializes the object and sets the model (if supplied)."""
        super().__init__(**metadata)
        if model is not None:
            self.model = model

    def trait_context(self):
        """Returns the default context to use for editing or configuring
        traits.
        """
        return {"object": self.model, "controller": self, "handler": self}

    # -- Handler Method Overrides ---------------------------------------------

    def get_perform_handlers(self, info):
        """Return a list of objects which can handle actions.

        By default this returns the Controller instance and the model.

        Parameters
        ----------
        info : UIInfo instance or None
            The UIInfo associated with the view, or None.

        Returns
        -------
        handlers : list
            A list of objects that may potentially have action methods on them.
        """
        return [self, self.model]

    def init_info(self, info):
        """Informs the handler what the UIInfo object for a View will be."""
        self.info = info


class ModelView(Controller):
    """Defines a handler class which provides a view and controller for a
    specified model.

    This class is useful when creating a variant of the standard MVC-based
    design. A subclass of ModelView reformulates a number of traits on
    its **model** object as properties on the ModelView subclass itself,
    usually in order to convert them into a more user-friendly format. In
    this design, the ModelView subclass supplies not only the view and
    the controller, but also, in effect, the model (as a set of properties
    wrapped around the original model). Because of this, the ModelView
    context dictionary specifies the ModelView instance itself as the
    special *object* value, and assigns the original model object as the
    *model* value. Thus, the traits of the ModelView object can be
    referenced in its View definition using unadorned trait names.
    """

    # -- HasTraits Method Overrides -------------------------------------------

    def trait_context(self):
        """Returns the default context to use for editing or configuring
        traits.
        """
        return {"object": self, "handler": self, "model": self.model}


class ViewHandler(Handler):

    pass
