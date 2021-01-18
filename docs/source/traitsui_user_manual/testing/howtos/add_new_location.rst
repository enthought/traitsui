
.. _testing-add-new-location:

Add support for locating a nested GUI element
=============================================

Support for |UIWrapper.locate| can be extended by registering additional
location type and resolution logic via |TargetRegistry.register_location| on
a |TargetRegistry|.

Suppose we have a custom UI editor that contains some buttons. The objective of
a test is to click a specific button with a given label. We will therefore need
to locate the button with the given label before a mouse click can be
performed.

The test code we wanted to achieve looks like this::

    container = UITester().find_by_id(ui, "some_container")
    button_wrapper = container.locate(LabelledButton("OK"))

Define the location type
------------------------

We can define the new ``LabelledButton`` location type::

    class LabelledButton:
        ''' Locator for locating a push button by label.'''
        def __init__(self, label):
            self.label = label

Identify the target
-------------------

Next, we need to know which object implements the GUI component. This is where
implementation details start to come in (see
:ref:`testing-target-is-protected`). We can inspect the object being wrapped::

    >>> container._target
    <package.ui.qt.shiny_panel.ShinyPanel object at 0x7f940a3f10b8>
    >>> button_wrapper._target
    <package.ui.qt.shiny_button.ShinyButton object at 0x7fbcc3a63438>

Implement a solver
-------------------

Say ``ShinyPanel`` keeps track of the buttons with a dictionary called
``_buttons`` where the names of the buttons are the keys of the dictionary.
Then the logic to retrieving a button from a
label can be written like this::

    def get_button(wrapper, location):
        """ Returns a ShinyButton from a UIWrapper wrapping ShinyPanel."""
        # wrapper is an instance of UIWrapper
        # location is an instance of LabelledButton
        return wrapper.target._buttons[location.label]

The solvers can then be registered for the container UI target::

    registry = TargetRegistry()
    registry.register_location(
        target_class=ShinyPanel,
        locator_class=LabelledButton,
        solver=get_button,
    )

Similar to |TargetRegistry.register_interaction|, the signature of
``get_button`` is required by the |TargetRegistry.register_location|
method. By setting the ``target_class`` and ``locator_class``, we restrict the
types of ``wrapper._target`` and ``location`` received by ``get_button``
respectively.

Apply it
--------

Finally, we can use this registry with |UITester|::

    tester = UITester(registries=[custom_registry])

If we have also added a custom ``ManyMouseClick`` interaction (see section
:ref:`testing-add-new-interaction`), we can write test code like this::

    container = UITester().find_by_id(ui, "some_container")
    button_wrapper = container.locate(LabelledButton("OK"))
    button_wrapper.perform(ManyMouseClick(n_times=10))

where both ``LabelledButton`` and ``ManyMouseClick`` are custom objects.

.. include:: ../substitutions.rst
