Compatibility with Pyface test utilities
========================================

|UITester| is intended to be compatible with Pyface's |ModalDialogTester|,
(for testing with modal dialogs) and |GuiTestAssistant| (for general
GUI event loop handling in tests).

.. _testing-with-modal-dialogs:

Testing with modal dialogs
--------------------------

When a test involves a modal dialog, |ModalDialogTester| will be needed.
|UITester| can be used together, for example, to launch the modal dialog
which then gets closed by |ModalDialogTester|::

    from pyface.constant import OK
    from pyface.toolkit import toolkit_object

    from traitsui.testing.api import MouseClick, UITester

    ModalDialogTester = toolkit_object(
        "util.modal_dialog_tester:ModalDialogTester"
    )

    tester = UITester()
    with tester.create_ui(demo) as ui:

        simple_button = tester.find_by_id(ui, "simple")

        def click_simple_button():
            simple_button.perform(MouseClick())

        modal_tester = ModalDialogTester(click_simple_button)
        modal_tester.open_and_run(lambda x: x.click_button(OK))
        assert modal_tester.dialog_was_opened

But if you try to modify or inspect GUI states using |UITester| while the
dialog is opened, you should set the |UITester.auto_process_events|
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

Using UITester and GuiTestAssistant
-----------------------------------

|GuiTestAssistant| is a more general tool dealing with GUI processing in tests.
|UITester|, on the other hand, is a more specific tool for testing GUI
components managed by TraitsUI. The two can be used together in tests.
|GuiTestAssistant| has been around before |UITester| is introduced.

Since various methods on |UIWrapper| (such as |UIWrapper.perform| and
|UIWrapper.inspect|) automatically request GUI events to be processed, where
they are used entirely for modifying and inspecting GUI states, some previous
usage of |GuiTestAssistant| features may no longer be necessary.

.. include:: ../substitutions.rst
