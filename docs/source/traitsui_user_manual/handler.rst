.. _controlling-the-interface-the-handler:

======================================
Controlling the Interface: the Handler
======================================

Most of the material in the preceding chapters is concerned with the
relationship between the model and view aspects of the :term:`MVC` design
pattern as supported by TraitsUI. This chapter examines the third aspect: the
:term:`controller`, implemented in TraitsUI as an :term:`instance` of the
:term:`Handler` class. [11]_

A controller for an MVC-based application is essentially an event handler for
GUI events, i.e., for events that are generated through or by the program
interface. Such events can require changes to one or more model objects (e.g.,
because a data value has been updated) or manipulation of the interface itself
(e.g., window closure, dynamic interface behavior). In TraitsUI, such actions
are performed by a Handler object.

In the preceding examples in this guide, the Handler object has been implicit:
TraitsUI provides a default Handler that takes care of a common set of GUI
events including window initialization and closure, data value updates, and
button press events for the standard TraitsUI window buttons (see
:ref:`command-buttons-the-buttons-attribute`).

This chapter explains the features of the TraitsUI Handler, and shows how to
implement custom GUI behaviors by building and instantiating custom subclasses
of the Handler class. The final section of the chapter describes several
techniques for linking a custom Handler to the window or windows it is designed
to control.

.. _backstage-introducing-the-uiinfo-object:

Backstage: Introducing the UIInfo Object
----------------------------------------

TraitsUI supports the MVC design pattern by maintaining the model, view, and
controller as separate entities. A single View object can be used to construct
windows for multiple model objects; likewise a single Handler can handle GUI
events for windows created using different Views. Thus there is no static link
between a Handler and any particular window or model object. However, in order
to be useful, a Handler must be able to observe and manipulate both its
corresponding window and model objects. In TraitsUI, this is accomplished by
means of the UIInfo object.

Whenever TraitsUI creates a window or panel from a View, a UIInfo object is
created to act as the Handler's reference to that window and to the objects
whose :term:`trait attribute`\ s are displayed in it.  This object holds a
reference to the UI instance in its **ui** trait, and whether or not
the UI has been initialized in the **initialized** trait.  Additionally,
this object is dynamically assigned trait attributes which correspond to:

- each entry in the View's context (see :ref:`the-view-context`).

- each item's and group's editor in the view, by id (or name, if no id is
  available for an item).

Where there is conflict between ids, the editors take precedence over context
values, and if two editors have the same name then the last editor with that
name will be referenced.

For example, the UIInfo object created in :ref:`Example 7 <example-7-using-a-multi-object-view-with-a-context>`
has attributes **h1** and **h2** whose values are the objects **house1** and
**house2** respectively.  Additionally it has attributes **address**,
**bedroom**, **pool**, and **price** that reference the editors in the second
group.

In :ref:`Example 1 <example-1-using-configure-traits>`
through :ref:`Example 6 <example-6-defining-multiple-view-objects-in-a-hastraits-class>`,
the created UIInfo object has an attribute **object** whose value is the object
**sam**, together with attributes that corrspond to the items in the views,
such as **first_name**, **last_name** and **department**.


Whenever a window event causes a Handler method to be called, TraitsUI passes
the corresponding UIInfo object as one of the method arguments. This gives the
Handler the information necessary to perform its tasks.

Additionally, traits on objects in the context can be synchronized with traits
on editors via the **sync_to_view**, **sync_from_view** and **sync_with_view**
trait metadata.  Note that not every trait on every editor can react to changes:
some values are only used at editor creation time; however all editors support
dynamically changing the **enabled**, **visible** and **invalid** traits.  This
feature can sometimes allow developers to avoid having to create a custom Handler
subclass.

See the :github-demo:`Invalid state handling <Advanced/Invalid_state_handling.py>`
example which demonstrates how to use this mechanism to control the invalid state
of a dialog based on the value of multiple editors.

.. _backstage-the-ui-object:

Backstage: The UI Object
------------------------

As opposed to the very dynamic UIInfo object, the UI class provides an object
which ties together the various objects that are involved in a TraitsUI GUI:
the View, the context, the Handler, the underlying toolkit controls and the
shared state of the GUI.  It also has some life-cycle and useful utility methods
that can be useful when working from a handler.

The UI object is returned as the result of a call to edit_traits(), and as noted
in the previous section, is available as the **ui** attribute of the UIInfo object
that is passed to most handler methods.

.. rubric:: Attributes of UI, by category

TraitsUI core
   view:
      View template used to construct the user interface.
   handler:
      Handler object used for event handling.
   context:
      Dictionary of objects that the UI is editing.
   info:
      UIInfo object containing context or editor objects
   parent:
      The parent UI (if any) of this UI.

Toolkit
   control:
      Panel or dialog associated with the user interface.
   owner:
      Toolkit-specific object that "owns" **control**

GUI state
   id:
      The unique ID for this UI for persistence.
   title:
      Title of the dialog, if any.
   icon:
      The ImageResource of the dialog icon, if any.
   key_bindings:
      The KeyBindings object (if any) for this UI.
   result:
      Result from a modal or wizard dialog.
   modified:
      Have any modifications been made to UI contents?
   updated:
      Event when the user interface has changed.
   history:
      Undo and Redo history.
   errors:
      The number of currently pending editor error conditions.
      Note that changing this must be done very carefully to avoid
      permanent error states.
   destroyed:
      Set to True when the UI has finished being destroyed.


.. rubric:: Useful UI methods

+---------------------------+--------------------------------------------------+
|Method                     |Purpose                                           |
+===========================+==================================================+
|dispose(result, abort)     |Disposes of the UI.  This can be called to close a|
|                           |TraitsUI dialog programatically from a handler.   |
+---------------------------+--------------------------------------------------+
|get_editors(name)          |Returns a list of all editors matching the name.  |
+---------------------------+--------------------------------------------------+


.. _assigning-handlers-to-views:

Assigning Handlers to Views
---------------------------

In accordance with the MVC design pattern, Handlers and Views are separate
entities belonging to distinct classes. In order for a custom Handler to provide
the control logic for a window, it must be explicitly associated with the View
for that window. The TraitsUI package provides three ways to accomplish this:

- Make the Handler an attribute of the View.
- Provide the Handler as an argument to a display method such as edit_traits().
- Define the View as part of the Handler.

.. _binding-a-singleton-handler-to-a-view:

Binding a Singleton Handler to a View
`````````````````````````````````````

To associate a given custom Handler with all windows produced from a given View,
assign an instance of the custom Handler class to the View's **handler**
attribute. The result of this technique, as shown in
:ref:`Example 9 <example-9-using-a-handler-that-reacts-to-trait-changes>`, is
that the window created by the View object is automatically controlled by the
specified handler instance.

.. _linking-handler-and-view-at-edit-time:

Linking Handler and View at Edit Time
`````````````````````````````````````

It is also possible to associate a custom Handler with a specific window without
assigning it permanently to the View. Each of the three TraitsUI
window-building methods (the configure_traits() and edit_traits() methods of the
HasTraits class and the ui() method of the View class) has a *handler* keyword
argument. Assigning an instance of Handler to this argument gives that handler
instance control *only of the specific window being created by the method call*.
This assignment overrides the View's **handler** attribute.

.. _creating-a-default-view-within-a-handler:

Creating a Default View Within a Handler
````````````````````````````````````````

You seldom need to associate a single custom Handler with several different
Views or vice versa, although you can in theory and there are cases where it is
useful to be able to do so. In most real-life scenarios, a custom Handler is
tailored to a particular View with which it is always used. One way to reflect
this usage in the program design is to define the View as part of the Handler.
The same rules apply as for defining Views within HasTraits objects; for
example, a view named 'trait_view' is used as the default view.

The Handler class, which is a subclass of HasTraits, overrides the standard
configure_traits() and edit_traits() methods; the subclass versions are
identical to the originals except that the Handler object on which they are
called becomes the default Handler for the resulting windows. Note that for
these versions of the display methods, the *context* keyword parameter is not
optional.

.. _handler-subclasses:

Handler Subclasses
------------------

TraitsUI provides two Handler subclasses: ModelView and Controller.  Both of
these classes are designed to simplify the process of creating an MVC-based
application.

Both ModelView and Controller extend the Handler class by adding the following
trait attributes:

- **model**: The model object for which this handler defines a view and
  controller.
- **info**: The UIInfo object associated with the actual user interface window
  or panel for the model object.

The **model** attribute provides convenient access to the model object
associated with either subclass. Normally, the **model** attribute is set in the
constructor when an instance of ModelView or Controller is created.

The **info** attribute provides convenient access to the UIInfo object
associated with the active user interface view for the handler object. The
**info** attribute is automatically set when the handler object's view is
created.

Both classes' constructors accept an optional *model* parameter, which is the
model object. They also can accept metadata as keyword parameters.

.. class:: ModelView( [model = None, **metadata] )

.. class:: Controller( [model = None, **metadata] )

The difference between the ModelView and Controller classes lies in the context
dictionary that each one passes to its associated user interface, as described
in the following sections.

.. _controller-class:

Controller Class
````````````````

The Controller class is normally used when implementing a standard MVC-based
design, and plays the "controller" role in the MVC design pattern. The "model"
role is played by the object referenced by the Controller's **model** attribute;
and the "view" role is played by the View object associated with the model
object.

The context dictionary that a Controller object passes to the View's ui() method
contains the following entries:

- ``object``: The Controller's model object.
- ``controller``: The Controller object itself.

Using a Controller as the handler class assumes that the model object contains
most, if not all, of the data to be viewed. Therefore, the model object is used
for the object key in the context dictionary, so that its attributes can be
easily referenced with unqualified names (such as Item('name')).

.. _modelview-class:

ModelView Class
```````````````

The ModelView class is useful when creating a variant of the standard MVC
design pattern. In this variant, the ModelView subclass reformulates a number
of trait attributes on its model object as properties on the ModelView, usually
to convert the model's data into a format that is more suited to a user
interface.

The context dictionary that a ModelView object passes to the View's ui() method
contains the following entries:

- ``object``: The ModelView object itself.
- ``model``: The ModelView's model object.

In effect, the ModelView object substitutes itself for the model object in
relation to the View object, serving both the "controller" role and the "model"
role (as a set of properties wrapped around the original model). Because the
ModelView object is passed as the context's object, its attributes can be
referenced by unqualified names in the View definition.

.. _writing-handler-methods:

Writing Handler Methods
-----------------------

If you create a custom Handler subclass, depending on the behavior you want to
implement, you might override the standard methods of Handler, or you might
create methods that respond to changes to specific trait attributes.

.. _overriding-standard-methods:

Overriding Standard Methods
```````````````````````````

The Handler class provides methods that are automatically executed at certain
points in the lifespan of the window controlled by a given Handler. By
overriding these methods, you can implement a variety of custom window
behaviors. The following sequence shows the points at which the Handler methods
are called.

1. A UIInfo object is created
2. The Handler's init_info() method is called. Override this method if the
   handler needs access to viewable traits on the UIInfo object whose values
   are properties that depend on items in the context being edited.
3. The UI object is created, and generates the actual window.
4. The init() method is called. Override this method if you need to initialize
   or customize the window.

.. TODO: Add a non-trivial example here.

5. The position() method is called. Override this method to modify the position
   of the window (if setting the x and y attributes of the View is insufficient).
6. The window is displayed.

.. _when-handler-methods-are-called-and-when-to-override-them-table:

.. rubric:: When Handler methods are called, and when to override them

+---------------------------+--------------------------+-----------------------+
|Method                     |Called When               |Override When?         |
+===========================+==========================+=======================+
|apply(info)                |The user clicks the       |To perform additional  |
|                           |:guilabel:`Apply` button, |processing at this     |
|                           |and after the changes have|point.                 |
|                           |been applied to the       |                       |
|                           |context objects.          |                       |
+---------------------------+--------------------------+-----------------------+
|close(info, is_ok)         |The user requests to close|To perform additional  |
|                           |the window, clicking      |checks before          |
|                           |:guilabel:`OK`,           |destroying the window. |
|                           |:guilabel:`Cancel`, or the|                       |
|                           |window close button, menu,|                       |
|                           |or icon.                  |                       |
+---------------------------+--------------------------+-----------------------+
|closed(info, is_ok)        |The window has been       |To perform additional  |
|                           |destroyed.                |clean-up tasks.        |
+---------------------------+--------------------------+-----------------------+
|revert(info)               |The user clicks the       |To perform additional  |
|                           |:guilabel:`Revert` button,|processing.            |
|                           |or clicks                 |                       |
|                           |:guilabel:`Cancel` in a   |                       |
|                           |live window.              |                       |
+---------------------------+--------------------------+-----------------------+
|setattr(info, object, name,|The user changes a trait  |To perform additional  |
|value)                     |attribute value through   |processing, such as    |
|                           |the user interface.       |keeping a change       |
|                           |                          |history. Make sure that|
|                           |                          |the overriding method  |
|                           |                          |actually sets the      |
|                           |                          |attribute.             |
+---------------------------+--------------------------+-----------------------+
|show_help(info,            |The user clicks the       |To call a custom help  |
|control=None)              |:guilabel:`Help` button.  |handler in addition to |
|                           |                          |or instead of the      |
|                           |                          |global help handler,   |
|                           |                          |for this window.       |
+---------------------------+--------------------------+-----------------------+
|perform(info, action,      |The user clicks a button  |To change the way that |
|event)                     |or toolbar item, or       |actions are handled,   |
|                           |selects a menu item.      |eg. to pass more info  |
|                           |                          |to a method.           |
+---------------------------+--------------------------+-----------------------+

.. _reacting-to-trait-changes:

Reacting to Trait Changes
`````````````````````````

The setattr() method described above is called whenever any trait value is
changed in the UI. However, TraitsUI also provides a mechanism for calling
methods that are automatically executed whenever the user edits a *particular*
trait. While you can use static notification handler methods on the HasTraits
object, you might want to implement behavior that concerns only the user
interface. In that case, following the MVC pattern dictates that such behavior
should not be implemented in the "model" part of the code. In keeping with this
pattern, TraitsUI supports "user interface notification" methods, which must
have a signature with the following format:

.. method:: extended_traitname_changed(info)

This method is called whenever a change is made to the attribute specified by
*extended_traitname* in the **context** of the View used to create the window
(see :ref:`multi-object-views`), where the dots in the extended trait reference
have been replaced by underscores. For example, for a method to handle changes
on the **salary** attribute of the object whose context key is 'object' (the
default object), the method name should be object_salary_changed().

By contrast, a subclass of Handler for
:ref:`Example 7 <example-7-using-a-multi-object-view-with-a-context>` might
include a method called h2_price_changed() to be called whenever the price of
the second house is edited.

.. note:: These methods are called on window creation.

   User interface notification methods are called when the window is first
   created.

To differentiate between code that should be executed when the window is first
initialized and code that should be executed when the trait actually changes,
use the **initialized** attribute of the UIInfo object (i.e., of the *info*
argument)::

    def object_foo_changed(self, info):

        if not info.initialized:
            #code to be executed only when the window is
            #created
        else:
            #code to be executed only when 'foo' changes after
            #window initialization

        #code to be executed in either case

The following script, which annotates its window's title with an asterisk ('*')
the first time a data element is updated, demonstrates a simple use of both an
overridden setattr() method and user interface notification method.

.. _example-9-using-a-handler-that-reacts-to-trait-changes:

.. rubric:: Example 9: Using a Handler that reacts to trait changes

.. literalinclude:: examples/handler_override.py
   :start-at: handler_override.py

.. image:: images/alter_title_before.png
   :alt: Dialog box with empty checkboxes and a title of "Alter Title"

.. figure:: images/alter_title_after.png
   :alt: Dialog box with one filled checkbox and a title of "Alter Title*"

   Figure 7: Before and after views of Example 9

.. _implementing-custom-window-commands:

Implementing Custom Window Commands
```````````````````````````````````

Another use of a Handler is to define custom window
actions, which can be presented as buttons, menu items, or toolbar buttons.

.. _actions:

Actions
:::::::

In TraitsUI, window commands are implemented as instances of the Action class.
Actions can be used in :term:`command button`\ s, menus, and toolbars.

Suppose you want to build a window with a custom **Recalculate** action. Suppose
further that you have defined a subclass of Handler called MyHandler to provide
the logic for the window. To create the action:

#. Add a method to MyHandler that implements the command logic. This method can
   have any name (e.g., do_recalc()), but must accept exactly one argument: a
   UIInfo object.
#. Create an Action instance using the name of the new method, e.g.::

        recalc = Action(name="Recalculate", action="do_recalc")

.. _custom-command-buttons:

Custom Command Buttons
::::::::::::::::::::::

The simplest way to turn an Action into a window command is to add it to the
**buttons** attribute for the View. It appears in the button area of the window,
along with any standard buttons you specify.

#. Define the handler method and action, as described in :ref:`actions`.
#. Include the new Action in the **buttons** attribute for the View::

    View(
        # view contents,
        # ...,
        buttons=[OKButton, CancelButton, recalc],
    )

.. _menus-and-menu-bars:

Menus and Menu Bars
:::::::::::::::::::

Another way to install an Action such as **recalc** as a window command is to
make it into a menu option.

#. Define the handler method and action, as described in :ref:`actions`.
#. If the View does not already include a MenuBar, create one and assign it to
   the View's **menubar** attribute.
#. If the appropriate Menu does not yet exist, create it and add it to the
   MenuBar.
#. Add the Action to the Menu.

These steps can be executed all at once when the View is created, as in the
following code::

    View(
        # view contents,
        # ...,
        menubar=MenuBar(
            Menu(my_action, name='My Special Menu'),
        ),
    )

.. _toolbars:

Toolbars
::::::::

A third way to add an action to a Traits View is to make it a button on a
toolbar. Adding a toolbar to a Traits View is similar to adding a menu bar,
except that toolbars do not contain menus; they directly contain actions.

1. Define the handler method and the action, as in :ref:`actions`, including a
   tooltip and an image to display on the toolbar. The image must be a Pyface
   ImageResource instance; if a path to the image file is not specified, it is
   assumed to be in an images subdirectory of the directory where ImageResource
   is used::

    From pyface.api import ImageResource

    recalc = Action(
        name="Recalculate",
        action="do_recalc",
        toolip="Recalculate the results",
        image=ImageResource("recalc.png"),
    )

2. If the View does not already include a ToolBar, create one and assign it to
   the View's **toolbar** attribute.
3. Add the Action to the ToolBar.

As with a MenuBar, these steps can be executed all at once when the View is
created, as in the following code::

    View(
       # view contents,
       # ...,
       toolbar=ToolBar(my_action),
    )

Schemas
:::::::

Pyface also provides action Schemas as a way to specify MenuBars, Toolbars and
their components without instantiating them.  These are particularly used in
the Tasks framework.  TraitsUI supports their use in Views, permitting better
interoperability.  The primary advantage of Schemas is that the deferred
instantiation makes it less likely to have unintentionally shared state between
declarative Views.


.. _undo_redo:

Undo and Redo
-------------

TraitsUI provides basic undo/redo functionality via the |UI| object's history
trait.  This is created automatically for |View| objects other than subpanels
whenever the |View| has a menubar or an "Undo" or "Revert" button.  This
system is largely independent of the
`Pyface undo/redo functionality <https://docs.enthought.com/pyface/undo.html>`_,
although that may change in the future.

The primary hook into the undo/redo system is via the |do_undoable| method of
the |UI| object, which calls the supplied callable while capturing all changes
to traits that are being viewed while the callable is running.  Undo and redo
actions then simply reset the values of all of those traits to the appropriate
before or after values.  This works well for simple cases where traits are not
heavily interdependent, but may break down in situations where there are
complex dependencies.

The |do_undoable| method is called when the value property of an |Editor| is
set or when any |Action| is performed, including actions associated with
complex editors that provide context menus.


.. rubric:: Footnotes

.. [11] Except those implemented via the **enabled_when**, **visible_when**,
   and **defined_when** attributes of Items and Groups.


.. |Action| replace:: :py:class:`~traitsui.menu.Action`
.. |Editor| replace:: :py:class:`~traitsui.editor.Editor`
.. |UI| replace:: :py:class:`~traitsui.ui.UI`
.. |View| replace:: :py:class:`~traitsui.view.View`
.. |do_undoable| replace:: :py:meth:`~traitsui.ui.UI.do_undoable`