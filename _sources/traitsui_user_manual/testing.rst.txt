.. _testing-traitsui-applications:

=============================
Testing TraitsUI Applications
=============================

TraitsUI provides an |testing.api| module which provides test
functionality that helps developers check the behavior of their applications.

Most of the test functionality can be accessed via the |UITester| object.

.. note::
   The testing library is relatively new compared to other features in
   TraitsUI. Built-in support for testing TraitsUI editors are continuously
   being added.

Basic Testing
=============

Creating a GUI
--------------

In order to test a TraitsUI application with |UITester|, we need an
instance of |UI|. Test code can create and dispose of a |UI| in any way, but
since this is a common use case, |UITester| provides a convenient method
|UITester.create_ui| for that::

    from traitsui.testing.api import UITester

    class App(HasTraits):
        text = Str()

    obj = App()
    tester = UITester()
    with tester.create_ui(obj) as ui:
        pass

The returned value is an instance of |UI|. This is the entry
point for locating GUI elements for further testing. The context manager
ensures the GUI widgets held by the UI are destroyed after the context exits.

Locating a UI editor
--------------------
After creating a |UI| object, the first step is to navigate
into the UI editor.

Find by Name
^^^^^^^^^^^^^
When defining a TraitsUI view, we will often define an instance of
|Item| with a trait name. The name can be used with
|UITester.find_by_name|::

    from traitsui.testing.api import UITester

    class SimpleObject(HasTraits):
        text = Str()

    view = View(Item(name="text"))
    obj = SimpleObject()
    tester = UITester()
    with tester.create_ui(obj, dict(view=view)) as ui:
        wrapper = tester.find_by_name(ui, "text")

Find by ID
^^^^^^^^^^^
Various TraitsUI view related objects (e.g. |Item| and |Group|) allow setting
a ID on it. If the view declaration can be modified, it may be convenient to
add an unique identifier to the relevant view element::

    from traitsui.testing.api import UITester

    class Person(HasTraits):
        name = Str()

    class App(HasTraits):
        person = Instance(Person, ())

    view = View(
        Item(
            name="person",
            editor=InstanceEditor(),
            style="custom",
            id="person_item",    # <--- add this
        )
    )

    obj = App()
    tester = UITester()
    with tester.create_ui(obj, dict(view=view)) as ui:
        wrapper = tester.find_by_id(ui, "person_item")

The returned value ``wrapper`` will be used in the following steps.

Perform a User Interaction or Continue Navigation
-------------------------------------------------
The returned value of |UITester.find_by_name| and |UITester.find_by_id|
is an instance of |UIWrapper| on which you may navigate into more
nested GUI elements, perform a user interaction, or inspect states on the
GUI element.

The supported actions can be found via the |UIWrapper.help| method::

    from traitsui.testing.api import UITester

    class Person(HasTraits):
        name = Str()

    class App(HasTraits):
        title = Str()
        person = Instance(Person, ())

    view = View(
        Item(name="title"),
        Item(name="person", editor=InstanceEditor(), style="custom"))

    obj = App()
    tester = UITester()
    with tester.create_ui(obj, dict(view=view)) as ui:
        title_field = tester.find_by_name(ui, "title")

        # Print information about the interactions and navigation possible on this object.
        title_field.help()

The last line ``title_field.help()`` prints something like this (abbreviated
for the purpose of this section)::

    Interactions
    ------------
    <class 'traitsui.testing.tester.command.KeyClick'>
        An object representing the user clicking a key on the keyboard.
        ...

    <class 'traitsui.testing.tester.command.KeySequence'>
        An object representing the user typing a sequence of keys.
        ...

    <class 'traitsui.testing.tester.command.MouseClick'>
        An object representing the user clicking a mouse button.
        ...

    <class 'traitsui.testing.tester.query.DisplayedText'>
        An object representing an interaction to obtain the displayed
        (echoed) plain text.
        ...

    Locations
    ---------
    No locations are supported.

The "Interactions" section shows the types of objects that can be used with
|UIWrapper.perform| and |UIWrapper.inspect|. They are objects that
represent user actions such as clicking a mouse, or checking a text being
displayed.

The "Locations" section shows the types of objects that can be used with
|UIWrapper.locate|. They are objects that allow developers to navigate
further into the the current GUI element.

In this example, ``title_field`` is wrapping a textbox, no further
nested GUI elements can be located and therefore there are no locations
supported.

Most of the time these objects can be imported from |testing.api|.

Perform a User Interaction to Modify GUI States
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
To modify the GUI state, we use |UIWrapper.perform| with an object whose
type is supported (as shown in the "Interactions" section from the help
message).

Say we want to modify the value in the text box as if the user has typed
in it, we can use the |KeySequence| object together with
|UIWrapper.perform|::

    from traitsui.testing.api import UITester, KeySequence

    obj = App()
    tester = UITester()
    with tester.create_ui(obj, dict(view=view)) as ui:
        title_field = tester.find_by_name(ui, "title")
        title_field.perform(KeySequence("New Title"))
        assert obj.title == "New Title"

We can then check the trait being edited is updated.

(In the test above, the trait is in fact updated many times because the default
the text editor is set such that the trait is changed at every key press.)

Modify a Trait and Inspect GUI States
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
To check the GUI state is what we expect, we use |UIWrapper.inspect|.

In the above example, ``title_field`` wrapping a text box also supports a
interaction type called |DisplayedText|. We can use that to check that when the
trait is updated, the text box is updated too::

    from traitsui.testing.api import UITester, DisplayedText

    obj = App()
    tester = UITester()
    with tester.create_ui(obj, dict(view=view)) as ui:
        obj.title = "Shiny new title"
        title_field = tester.find_by_id(ui, "title")
        displayed = title_field.inspect(DisplayedText())
        assert displayed == "Shiny new title"

Locate Specific Elements in the GUI
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Sometimes, a GUI application is complex and the GUI element we want to test is
deeply nested in the application. Sometimes, given a GUI element, we still need
to specify further where an interaction should occur (e.g. mouse clicking a
particular item in a combo box). For that, |UIWrapper.locate| can be used
to provide more information on the location for navigation.

Using the same example as above, we can navigate into the ``person`` view::

    obj = App()
    tester = UITester()
    with tester.create_ui(obj, dict(view=view)) as ui:
        person_pane = tester.find_by_name(ui, "person")

If we call ``person_pane.help()`` to see what actions are available, we
see the following::

    >>> person_pane.help()
    Interactions
    ------------
    No interactions are supported.

    Locations
    ---------
    <class 'traitsui.testing.tester.locator.TargetById'>
        A locator for locating the next UI target using an id.

        Attributes
        ----------
        id : str

    <class 'traitsui.testing.tester.locator.TargetByName'>
        A locator for locating the next UI target using a name.

        Attributes
        ----------
        name : str

We can see that |TargetById| and |TargetByName| are available for
locating the next GUI element. We can locate the text box for
``person.name`` using |TargetByName|::

    from traitsui.testing.api import UITester, TargetByName

    obj = App()
    tester = UITester()
    with tester.create_ui(obj, dict(view=view)) as ui:
        person_pane = tester.find_by_name(ui, "person")
        person_name_field = person_pane.locate(TargetByName("name"))

In fact, |UIWrapper.find_by_id| and |UIWrapper.find_by_name| are simply
aliases for |TargetById| and |TargetByName| respectively, so you
can also write::

    person_name_field = person_pane.find_by_name("name")

The returned value is again an instance of |UIWrapper|.

In this example, ``person_name_field`` wraps a textbox, we can modify the
value in the text box using |UIWrapper.perform| again::

    from traitsui.testing.api import KeySequence
    person_name_field.perform(KeySequence("Charlie"))

In some situations, the GUI can be very nested and we may need to chain many
calls to |UIWrapper.locate| before we can finally call |UIWrapper.perform| or
|UIWrapper.inspect|::

    person_pane.locate(...).locate(...).locate(...).perform(...)

Examples
========

Several test examples can be found for testing
:ref:`TraitsUI\'s own demos<traitsui-demo>`.

Editors
-------
- :github-demo:`BooleanEditor <Standard_Editors/tests/test_BooleanEditor_simple_demo.py>`
- :github-demo:`ButtonEditor <Standard_Editors/tests/test_ButtonEditor_simple_demo.py>`
- :github-demo:`CheckListEditor <Standard_Editors/tests/test_CheckListEditor_simple_demo.py>`
- :github-demo:`EnumEditor <Standard_Editors/tests/test_EnumEditor_demo.py>`
- :github-demo:`InstanceEditor <Standard_Editors/tests/test_InstanceEditor_demo.py>`
- :github-demo:`ListEditor <Advanced/tests/test_List_editor_notebook_selection_demo.py>`
- :github-demo:`RangeEditor <Standard_Editors/tests/test_RangeEditor_demo.py>`
- :github-demo:`TextEditor <Standard_Editors/tests/test_TextEditor_demo.py>`

Applications
------------
- :github-demo:`Converter <Applications/tests/test_converter.py>`

Debugging
=========
When you want to sanity check the test is doing what you intended, or when
you want to debug an issue, the ``delay`` parameter may be useful for
slowing down the test so that you can see the GUI being updated.

Example::

    from traitsui.testing.api import UITester, KeySequence

    obj = App()
    tester = UITester(delay=50)    # delay in milliseconds
    with tester.create_ui(obj, dict(view=view)) as ui:
        title_field = tester.find_by_name(ui, "title")
        title_field.perform(KeySequence("New Title"))

Note that there are limitations as to how truthful the GUI looks visually
compared to manual testing.

FAQ
===

.. rubric:: Is UITester GUI toolkit specific?

It depends. The API of UITester is toolkit independent. As long as the behavior
being tested is also toolkit independent, |UITester| should support test code
with no toolkit specific logic. However if the underlying GUI behavior
varies from toolkit to toolkit, the test code using |UITester| will need to
adjust for that.

.. rubric:: Which testing framework should I use with UITester?

|UITester| does not depend on any testing framework. You should be able to use
it with any testing framework (e.g. unittest, pytest).

.. rubric:: Is UITester compatible with PyFace ModalDialogTester?

Yes, with some care.

For example, you can use |UITester| to launch a modal dialog, and use
ModelDialogTester to close it.

But if you are attempting to modify or inspect GUI states using |UITester|
while the dialog is opened, you should set the ``auto_process_events``
attribute to false for those operations. Otherwise the ModalDialogTester and
UITester will enter a deadlock that blocks forever.

Example::

    def when_opened(modal_dialog_tester):
        ui_tester = UITester(auto_process_events=False)
        ui_tester.find_by_id(ui, "button").perform(MouseClick())

    modal_dialog_tester = ModalDialogTester(callable_to_open_dialog)
    modal_dialog_tester.open_and_run(when_opened)

In the above example, ``ui`` is an instance of |UI| that has been obtained
elsewhere in the test. Note that you can instantiate as many |UITester| objects
as you need.

.. rubric:: Is UITester compatible with PyFace GuiTestAssistant?

Yes.

|UIWrapper.perform| and |UIWrapper.inspect| automatically request GUI
events to be processed. Where they are used entirely for modifying GUI states,
you may find uses of some of GuiTestAssistant features no longer necessary.

.. rubric::
   I use the delay parameter to play back my test but it does not look
   identical to when I test the GUI manually, why?

If the GUI / trait states being asserted in tests are not consistent compared
to manually testing, then that is likely a bug. Please report it.

If the GUI / trait states being asserted in tests are consistent with manual
testing, then such visual discrepancies may have to be tolerated given there
are toolkit-dependent and platform-dependent limitations as to what can be
achieved for programmatically imitating user interactions.

.. _advanced-testing:

Advanced Testing
================

|UITester| supports testing TraitsUI editors with various user interaction
logic. However it is possible that projects' test code may require
additional logic that is not supported by |UITester| by default. Furthermore,
some projects may implement and maintain their own custom UI editors. Those
custom UI editors are also by default not supported by |UITester|.

The API allows extension such that

* projects can test TraitsUI editors with user interactions that do not
  come supported by default.
* projects can reuse the testing API for testing custom editors.

.. note::
   Extending support for testing a UI editor often requires knowledge of the
   implementation details of the editor. If UI editor and the testing support
   code are not maintained together, tests may be subject to breakages caused
   by internal changes of the UI editors. Certain attributes described in this
   document are classified as protected, to be used for extending the testing
   API. Developers should evaluate based on context whether they should be
   used.


Terminology
-----------

Before we start, we need to define some terminology:

* Target
    is an object on which we can perform an action (e.g. a mouse click) to
    modify an application state, or retrieve a GUI application state, or
    search for other contained targets (e.g. a table widget that contains
    buttons and text).

    An instance of |UIWrapper| wraps a target under the protected attribute
    ``_target``.

* Interaction
    is an object that wraps the information for performing an action
    or retrieving GUI state(s), but it does not necessarily contain information
    to a Target. For example, both |MouseClick| and |DisplayedText| are
    interactions that can be used against different targets. An interaction can
    also be specialized for a specific target if needed.

    |UIWrapper.perform| and |UIWrapper.inspect| handle an interaction.

* Location
    is an object that wraps the information for searching a target from a
    container target, but it does not necessarily contain information specific
    to a Target. For example, both |TargetById| and |TargetByName| are
    locations for identifying a contained target via an id or a name, which can
    be used against different targets. A location can also be specialized for a
    specific target if needed.

    |UIWrapper.locate| resolves a location.

Add Support for Performing a User Interaction
---------------------------------------------

Support for |UIWrapper.perform| can be extended by registering additional
interaction type and handling logic via |TargetRegistry.register_interaction| on
a |TargetRegistry|.

For the purpose of this document, suppose we want to perform many mouse clicks
on a UI component, but instead of calling ``perform(MouseClick())`` many times
in a loop like this::

    my_widget = UITester().find_by_id(ui, "some_id")
    for _ in range(10):
        my_widget.perform(MouseClick())

We want to exercise the mouse click many times by invoking |UIWrapper.perform| once
only::

    my_widget = UITester().find_by_id(ui, "some_id")
    my_widget.perform(ManyMouseClick(n_times=10))

First, we need to define this ``ManyMouseClick`` object::

    class ManyMouseClick:
        def __init__(self, n_times):
            self.n_times = n_times

Next, we need to know which object implements the GUI component. This is where
implementation details start to come in. We can inspect the object being
wrapped::

    >>> my_widget
    <traitsui.testing.tester.ui_wrapper.UIWrapper object at 0x7f940a3f10b8>
    >>> my_widget._target
    <package.ui.qt.shiny_button.ShinyButton object at 0x7fc90fb3b570>

The target is an instance of a ``ShinyButton`` class (made up
for this document). In this object, there is an instance of Qt QPushButton
widget which we want click with the mouse::

    >>> my_widget._target.control
    <PyQt5.QtWidgets.QPushButton object at 0x7fbcc3ac3558>

So now all we need to do, is to tell |UITester| how to perform
``ManyMouseClick`` on an instance of ``ShinyButton``.

We define a function to perform the mouse clicks::

    def many_mouse_click(wrapper, interaction):
        # wrapper is an instance of UIWrapper
        # interaction is an instance of ManyMouseClick
        for _ in range(interaction.n_times):
            wrapper._target.control.click()

Then we need to register this function with an instance of |TargetRegistry|::

    from traitsui.testing.api import TargetRegistry
    from package.ui.qt.shiny_button import ShinyButton

    custom_registry = TargetRegistry()
    custom_registry.register_interaction(
        target_class=ShinyButton,
        interaction_class=ManyMouseClick,
        handler=many_mouse_click,
    )

The signature of ``many_mouse_click`` is required by the |TargetRegistry.register_interaction|
method on |TargetRegistry|. By setting the ``target_class`` and
``interaction_class``, we restrict the types of ``wrapper._target`` and
``interaction`` received by ``many_mouse_click`` respectively.

Finally, we can use this registry with the |UITester|::

    tester = UITester(registries=[custom_registry])

All the builtin testing support for TraitsUI editors are still present, but now
this tester can perform the additional, custom user interaction.

Add Support for Inspecting GUI States
-------------------------------------

The steps to extend |UIWrapper.inspect| are identical to those for extending
|UIWrapper.perform| (see section above). The distinction between
|UIWrapper.perform| and |UIWrapper.inspect| is merely in their returned
values.

In fact, following the steps in the above section, the new ``ManyMouseClick``
can also be called via |UIWrapper.inspect|::

    value = tester.inspect(ManyMouseClick(n_times=10))

The returned value is the returned value from ``many_mouse_click``, which is
``None``.

Add Support for Locating a Nested GUI Element
---------------------------------------------

Support for |UIWrapper.locate| can be extended by registering additional
location type and resolution logic via |TargetRegistry.register_location| on
a |TargetRegistry|.

Suppose we have a custom UI editor that contains some buttons. The objective of
a test is to click a specific button with a given label. We will therefore need
to locate the button with the given label before a mouse click can be
performed.

The test code we wanted to achieve looks like this::

    container = UITester().find_by_id(ui, "some_container")
    button_wrapper = container.locate(NamedButton("OK"))

where the targets are::

    >>> container._target
    <package.ui.qt.shiny_panel.ShinyPanel object at 0x7f940a3f10b8>
    >>> button_wrapper._target
    <package.ui.qt.shiny_button.ShinyButton object at 0x7fbcc3a63438>

We can define the new ``NamedButton`` location type::

    class NamedButton:
        ''' Locator for locating a push button by label.'''
        def __init__(self, label):
            self.label = label

Say ``ShinyPanel`` keeps track of the buttons with a dictionary called
``_buttons`` where the names of the buttons are the keys of the dictionary.
Then the logic to retrieving a button from a
label can be written like this::

    def get_button(wrapper, location):
        """ Returns a ShinyButton from a UIWrapper wrapping ShinyPanel."""
        # wrapper is an instance of UIWrapper
        # location is an instance of NamedButton
        return wrapper.target._buttons[location.label]

The solvers can then be registered for the container UI target::

    registry = TargetRegistry()
    registry.register_location(
        target_class=ShinyPanel,
        locator_class=NamedButton,
        solver=get_button,
    )

Similar to |TargetRegistry.register_interaction|, the signature of
``get_button`` is required by the |TargetRegistry.register_location|
method. By setting the ``target_class`` and ``locator_class``, we restrict the
types of ``wrapper._target`` and ``location`` received by ``get_button``
respectively.

Then we can use this registry with |UITester|::

    tester = UITester(registries=[custom_registry])

If we have also added a custom ``ManyMouseClick`` interaction (see section
above), we can write test code like this::

    container = UITester().find_by_id(ui, "some_container")
    button_wrapper = container.locate(NamedButton("OK"))
    button_wrapper.perform(ManyMouseClick(n_times=10))

where both ``NamedButton`` and ``ManyMouseClick`` are custom objects.

Overriding TraitsUI Builtin Testing Support
-------------------------------------------

|UITester| maintains a list of registries ordered in decreasing priority.
For example, if you provide multiple registries::

    tester = UITester(registries=[custom_registry, another_registry])

Interactions and locations registered in the first registry will supersede that
of the second (if such implementation exists). Builtin support for TraitsUI
editors is added last, hence with the lowest priority.

With that, one can override TraitsUI builtin testing support by redefining the
interaction handler and/or location solver via an instance of
|TargetRegistry|::

    from traitsui.qt4.button_editor import SimpleEditor
    from traitsui.testing.api import command

    custom_registry = TargetRegistry(
        target_class=SimpleEditor,
        locator_class=command.MouseClick,
        handler=my_custom_handler,
    )
    tester = UITester(registries=[custom_registry])

..
   # substitutions

.. |testing.api| replace:: :mod:`~traitsui.testing.api`

.. |Group| replace:: :class:`~traitsui.group.Group`
.. |Item| replace:: :class:`~traitsui.item.Item`
.. |UI| replace:: :class:`~traitsui.ui.UI`

.. |MouseClick| replace:: :class:`~traitsui.testing.tester.command.MouseClick`
.. |KeySequence| replace:: :class:`~traitsui.testing.tester.command.KeySequence`
.. |DisplayedText| replace:: :class:`~traitsui.testing.tester.query.DisplayedText`
.. |TargetById| replace:: :class:`~traitsui.testing.tester.locator.TargetById`
.. |TargetByName| replace:: :class:`~traitsui.testing.tester.locator.TargetByName`

.. |TargetRegistry| replace:: :class:`~traitsui.testing.tester.target_registry.TargetRegistry`
.. |TargetRegistry.register_interaction| replace:: :func:`~traitsui.testing.tester.target_registry.TargetRegistry.register_interaction`
.. |TargetRegistry.register_location| replace:: :class:`~traitsui.testing.tester.target_registry.TargetRegistry.register_location`

.. |UITester| replace:: :class:`~traitsui.testing.tester.ui_tester.UITester`
.. |UITester.create_ui| replace:: :func:`~traitsui.testing.tester.ui_tester.UITester.create_ui`
.. |UITester.find_by_id| replace:: :func:`~traitsui.testing.tester.ui_tester.UITester.find_by_id`
.. |UITester.find_by_name| replace:: :func:`~traitsui.testing.tester.ui_tester.UITester.find_by_name`
.. |UIWrapper| replace:: :class:`~traitsui.testing.tester.ui_wrapper.UIWrapper`
.. |UIWrapper.find_by_id| replace:: :func:`~traitsui.testing.tester.ui_wrapper.UIWrapper.find_by_id`
.. |UIWrapper.find_by_name| replace:: :func:`~traitsui.testing.tester.ui_wrapper.UIWrapper.find_by_name`
.. |UIWrapper.help| replace:: :func:`~traitsui.testing.tester.ui_wrapper.UIWrapper.help`
.. |UIWrapper.inspect| replace:: :func:`~traitsui.testing.tester.ui_wrapper.UIWrapper.inspect`
.. |UIWrapper.locate| replace:: :func:`~traitsui.testing.tester.ui_wrapper.UIWrapper.locate`
.. |UIWrapper.perform| replace:: :func:`~traitsui.testing.tester.ui_wrapper.UIWrapper.perform`
