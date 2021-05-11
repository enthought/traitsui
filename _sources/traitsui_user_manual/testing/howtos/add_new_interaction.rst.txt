
.. _testing-add-new-interaction:

Add support for performing actions or inspecting states
=======================================================

Support for |UIWrapper.perform| and |UIWrapper.inspect| can be extended by
registering additional interaction type and handling logic via
|TargetRegistry.register_interaction| on a |TargetRegistry|.

Suppose we want to perform many mouse clicks on a UI component in a test, but
instead of calling ``perform(MouseClick())`` many times in a loop like this::

    my_widget = UITester().find_by_id(ui, "some_id")
    for _ in range(10):
        my_widget.perform(MouseClick())

We want to exercise the mouse click many times by invoking |UIWrapper.perform|
once only::

    my_widget = UITester().find_by_id(ui, "some_id")
    my_widget.perform(ManyMouseClick(n_times=10))

Define the interaction
----------------------

We can define this ``ManyMouseClick`` object simply like this::

    class ManyMouseClick:
        def __init__(self, n_times):
            self.n_times = n_times

Identify the target
-------------------

Next, we need to know which object implements the GUI component. This is where
implementation details start to come in (see
:ref:`testing-target-is-protected`). We can inspect the object being wrapped::

    >>> my_widget
    <traitsui.testing.tester.ui_wrapper.UIWrapper object at 0x7f940a3f10b8>
    >>> my_widget._target
    <package.ui.qt.shiny_button.ShinyButton object at 0x7fc90fb3b570>

The target is an instance of a ``ShinyButton`` class (made up
for this document). In this object, there is an instance of Qt QPushButton
widget which we want to click with the mouse::

    >>> my_widget._target.control
    <PyQt5.QtWidgets.QPushButton object at 0x7fbcc3ac3558>

Implement a handler
-------------------

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

Apply it
--------

Finally, we can use this registry with the |UITester|::

    tester = UITester(registries=[custom_registry])
    my_widget = tester.find_by_id(ui, "some_id")
    my_widget.perform(ManyMouseClick(n_times=10))

All the builtin testing support for TraitsUI editors are still present, but now
this tester can perform the additional, custom user interaction.

Inspecting states
-----------------

The distinction between |UIWrapper.perform| and |UIWrapper.inspect| is merely
in their returned values.

We can call |UIWrapper.inspect| with the ``ManyMouseClick`` object we just
created::

    value = my_widget.inspect(ManyMouseClick(n_times=10))

The returned value is the value returned by ``many_mouse_click``, the handler
registered for ``ManyMouseClick`` and ``ShinyButton``. In this case, the
value is ``None``.


.. include:: ../substitutions.rst
