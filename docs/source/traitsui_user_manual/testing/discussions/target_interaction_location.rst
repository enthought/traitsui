.. _testing-target-interaction-location:

Understanding Target, Interaction and Location
==============================================

When one writes a test using |UITester|, three categories of objects are
involved.

* Target
    is an object on which we can perform an action (e.g. a mouse click) to
    modify an application state, or retrieve a GUI application state, or
    search for other contained targets (e.g. a table widget that contains
    buttons and text).

    An instance of |UIWrapper| wraps a target under the protected attribute
    |UIWrapper._target|.

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


.. _testing-target-is-protected:

Why is Target protected?
------------------------

The |UIWrapper._target| attribute is protected because it often exposes
implementation details of the GUI component being tested (e.g. it may refer to
the Qt specific implementation of a ButtonEditor). Since it is best for tests
to avoid dependencies on implementation details, its usage in test code is
discouraged.

However, this attribute is expected to be used while extending the testing API,
which inevitably requires knowledge of the implementation details on the tested
components. If the implementation details and the testing support code are not
maintained together, tests may be subject to breakages caused by changes to
implementation details that do not affect the overall behavior. Developers
should evaluate based on context whether they should proceed.


.. include:: ../substitutions.rst
