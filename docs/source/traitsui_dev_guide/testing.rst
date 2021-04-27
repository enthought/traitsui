
.. _testing-internals:

==============================
Developing The Testing Package
==============================

This document describes the context and design decisions surrounding the
development of the |traitsui.testing| package. Readers are assumed to be
familiar with the content of the :ref:`testing-traitsui-applications` Section.

Background Motivation
---------------------

There had been proposals for introducing a public API to make it easier and
safer to write self-checking tests for TraitsUI applications. At the same time,
we noticed that a lot of what TraitsUI needs for testing are common in
downstream projects as well:

- test needs to modify a trait and then checks the GUI state has changed.
- test needs to modify the GUI state and then checks a trait has changed.
- test needs to create a UI and makes sure it is disposed of properly at
  the end of the test.
- test needs to ensure uncaught exceptions that occur in the GUI event
  loop cause the test to fail.

The step that is the least trivial to get right or the most often-overlooked
is the need to process pending events on the GUI event loop.

Pyface (a dependency of TraitsUI) has provided a base class called
GuiTestAssistant which helps running the GUI event loops in tests. However,
test code manipulating a TraitsUI editor will still need to know which methods
on the editor it should call and what to call it with. These methods don't have
a common interface, and their signatures vary from toolkit to toolkit, editor
to editor. Often one needs to read the source code in order to call them
correctly.

For example, in order to update the date trait edited by a DateEditor, in Qt,
one needs to call the Qt DateEditor like this::

  editor.update_object(QDate(...))

In Wx, one will need to create an wx event with the date value following wx
API, and then call a method only wx DateEditor has::

  event = wx.adv.DateEvent(...)
  event.SetDate(...)
  editor.day_selected(event)

In addition to the lack of a common interface, this approach also has the
following drawbacks:

- The test code is toolkit specific.
- Advanced technical knowledge on the low level toolkit control is required to
  write these tests.
- The test provides less confidence as it bypasses GUI event hooking logic
  (aka signals and slots).
- There is a strong coupling between the test code and TraitsUI 's internal
  implementation details.

The last point is important for both TraitsUI and downstream projects. Strong
coupling between the application code structure and test code means any small
refactoring or internal changes could cause a lot of test code to fail. This
would make changing TraitsUI more difficult. Downstream projects realizing the
fragility of such tests may decide not to write the tests that would otherwise
be written.

In fact, TraitsUI 's test suite already makes use of a number of internal
helper functions for testing its own UI editors. Therefore we noticed that
there was an opportunity to wrap these helper functions and re-expose them
in a simpler public API for testing.

By implementing a testing API motivated and tested by TraitsUI 's own test
code, the API is likely to be more useful and has fewer bugs.

Goals
-----

- The API should be simple, intuitive to use and to understand.
- The API should be toolkit agnostic.
- Test code using the API should not need to depend on implementation details
  of a UI editor.
- Easy-to-forget logic such as processing GUI events should be provided by
  default.
- Despite the rich and varying features supported by TraitsUI editors, the API
  should still be self-explanatory and self-documenting so that it is easy to
  find what is supported.
- The testing helper can be used in collaboration with Pyface's
  ModalDialogTester and GuiTestAssistant.
- Unexpected exceptions from the GUI event loop should cause a test to fail.
- Functionalities provided should be immediately useful for TraitsUI's own
  tests.
- The API should be extensible so that projects can add their own test logic
  and TraitsUI test code can optionally defer publishing less mature test logic
  to the public API.

Non-Goals
---------

The API does NOT aim to:

- Replace Pyface's ModalDialogTester and GuiTestAssistant.
- Reproduce the full visual experience compared to manual testing, as long
  as the test objective is fulfilled.

System Context
--------------

In a software system, tests are the most isolated system component, which are
not necessary for production use. Since the testing library supports tests,
it should only be used by tests and nothing else in a software system.

The fact that tests and production use require different exception handling
further justifies disallowing the testing library to be used in a production
environment.

API
---

As mentioned in :ref:`testing-traitsui-applications`, there are broadly
speaking three types of actions when one manipulates a GUI in test:

- Locate a GUI target.
- Perform an action that mutates GUI state like a user would.
- Inspect a GUI state like a user would.

(Terminologies are defined in :ref:`testing-target-interaction-location`).
Each of these three types of actions should have a public method in the API.

Technically speaking, the behavior of "inspect" is very similar to "perform",
they only differ in their intent, and therefore whether they should have a
returned value. They are separate so that test code using these methods will
read more naturally, and communicate intent more clearly.

Likewise, "locate" is similar to "inspect"; both are making
queries about GUI states. However, "locate" is likely used in conjunction with
"perform" and "inspect", whereas "perform" and "inspect" could also occur as a
standalone command.

In summary, test code should read something like the following::

  perform(...)
  inspect(...)
  locate(...).perform(...)
  locate(...).inspect(...)
  locate(...).locate(...).locate(...).inspect(...)

Each of these functions provides the natural place for GUI event processing to
occur automatically so that users do not have to worry about that any more.

Different types of interactions and locations should be supported based on
the GUI target type. For example, if the current GUI target being handled
is a button, then "perform" should support an interaction type "MouseClick".

Public API objects
------------------

All objects exposed in the ``traitsui.testing.api`` are part of the public API.
Objects accessible via publicly named attributes through this API are also
part of the public API.

The less obvious part of the public API are the supported interactions and
locations exposed via the registry pattern.

Separating |UITester| from |UIWrapper|
--------------------------------------

|UITester| is designed to be a top-level object to provide the first point of
use for developers testing a TraitsUI application.

It puts together two other types of objects:

- |UIWrapper|
- |TargetRegistry|

|UITester| is specific to TraitsUI, whereas |UIWrapper| and |TargetRegistry|
are more generic and can be used for testing any types of objects.

|TargetRegistry| collects the information required for resolving an interaction
and/or a location for a given GUI target. |UIWrapper| depends on one
or many registries. If the |TargetRegistry| is empty, the |UIWrapper| would not
be very useful at all. The |UITester| supports testing of TraitsUI objects by
providing an instance of |TargetRegistry| that knows how to locate, inspect
and perform actions on TraitsUI objects.

This abstraction covers the existing use cases and it also allows TraitsUI
to extend the API in its internal GUI tests without necessarily exposing the
logic to the public. Likewise, external projects can extend testing support for
their custom UI editors.

Registry VS Inheritance: Registry wins
--------------------------------------

The types of locations and interactions that should be supported depends on
the type of TraitsUI editor being used. e.g. A TextEditor that only wraps
a text box does not need to support further location logic, and it should
support modifying the text via key events. However a CheckListEditor will
require support for locating an item in the list, but not support for modifying
the item by key events.

Since there are more than one axis of variables, class inheritance is not
enough to achieve polymorphism. If we had used subclasses, we will end up with
an API where there are a lot of optional methods that are not implemented by
a subclass, making it difficult for users to find what can be used.

At the end, the registry pattern wins, and that becomes |TargetRegistry|.

Rejected design: Default location
---------------------------------

Early in the development there was a proposal to support a special location
type called the "DefaultTarget". The idea was that if an interaction is not
supported by a given GUI target, the "default target" is tried. This was
motivated by the use case of testing simple UI editors such as TextEditor
where there is one obvious toolkit widget to interact with. With this design,
one would register interaction handlers with the low level toolkit specific
object as the target type, allowing those handlers to be reused in other
contexts.

The pseudo-code for this patterns looked like this::

  def perform(interaction, target):
      try:
          _perform(interaction, target):
      except InteractionNotSupported:
          try:
              default_target = locate(DefaultTarget, target)
          except LocationNotSupported:
              raise InteractionNotSupported
          else:
              _perform(interaction, default_target)

The default target for a TextEditor can be resolved using this function::

  def resolve_default_target(target: TextEditor):
      return target.control   # would be a QLineEdit for simple editor in Qt.

And one would have registered an interaction (e.g. KeySequence) on a low level
toolkit widget type::

  registry.register_interaction(
    target_type=QLineEdit,
    interaction_type=KeySequence,
    handler=...,  # some callable
  )

The design was rejected for two reasons:

#. The control flow resulting from trying to resolve an interaction
   or location on the default target adds complexity to the code.
#. The resulting code is obscure because it is hard to see which UI editors
   are using the registered interaction handlers. This makes it difficult to
   perform impact analysis when one needs to change the code.

At the end we simply register the interaction types on those simple UI editors
directly but we refactor the registration logic so that it is easy to reuse.

Where are the tests?
--------------------

When a functionality is added to support testing TraitsUI editors, the
functionality should be used in TraitsUI 's own tests for the editor.
e.g. The MouseClick support for ButtonEditor is tested in the tests for
ButtonEditor, in ``traitsui.editors.tests.test_button_editor``.

By dog-fooding the implementations back to TraitsUI 's own tests with the goal
of writing toolkit independent test code, this allows us to capture
inconsistencies among different toolkits early and to make sure the new
functionality is indeed useful.

Tests for functionality provided by the tester API can be found in the
``testing`` package (or subpackages). e.g. API of |UITester| is tested in
``traitsui.testing.tester.tests``.

Package structures
------------------

The ``traitsui.testing`` package adopts a naming convention that is in fact
not new: Preceding underscores in names are used to indicate an object is
intended to be used within the namespace it is defined in.

If a module has a name with a preceding underscore, this means it is intended
to be used by objects that live in the same package (including subpackages),
but not objects that are defined in a package outside of that package.
If a module is intended to be used by objects defined outside of the package,
the module should have a "public" name.

For example, ``traitsui.testing.tester._ui_tester.default_registry`` can be
imported by ``traitsui.testing.tester.something`` but should not be imported
by ``traitsui.testing.api`` or anything outside of ``traitsui.testing.tester``.

..
   # substitutions

.. |Editor| replace:: :class:`~traitsui.editor.Editor`
.. |UI| replace:: :class:`~traitsui.ui.UI`

.. |traitsui.testing| replace:: :mod:`~traitsui.testing`
.. |UITester| replace:: :class:`~traitsui.testing.tester.ui_tester.UITester`
.. |UIWrapper| replace:: :class:`~traitsui.testing.tester.ui_wrapper.UIWrapper`
.. |UIWrapper.inspect| replace:: :func:`~traitsui.testing.tester.ui_wrapper.UIWrapper.inspect`
.. |UIWrapper.locate| replace:: :func:`~traitsui.testing.tester.ui_wrapper.UIWrapper.locate`
.. |UIWrapper.perform| replace:: :func:`~traitsui.testing.tester.ui_wrapper.UIWrapper.perform`
.. |TargetRegistry| replace:: :class:`~traitsui.testing.tester.target_registry.TargetRegistry`
