GUI event processing and exception handling
===========================================

The testing API is designed such that GUI event processing is requested
automatically wherever there may be pending GUI events. While events are being
processed, the global exception handling is overridden temporarily in order to
capture any unhandled exceptions. If any exceptions are caught, a test error
is raised after all pending events are processed.

For example, |UIWrapper.locate|, |UIWrapper.perform| and |UIWrapper.inspect|
all request pending events to be processed before and/or after interacting
with GUI states. This automatic behavior is enabled by default, but it can be
disabled via the |UITester.auto_process_events| flag (see
:ref:`testing-with-modal-dialogs` for example).

Motivation
----------

In production environments, the GUI event loop typically blocks as it waits
and processes new GUI events continuously, until the last window is closed.
In tests, the GUI event loop needs to be run programmatically for a limited
scope of commands and yield to test instructions every now and then while the
GUI is still open.

In production environments, some unhandled exceptions are tolerated and
suppressed by the GUI event loop, but some exceptions could cause the entire
runtime to abort abnormally. Neither of these conditions are desirable in
tests. Unhandled exceptions typically indicate bugs and should cause a test to
error. Abortion of the Python runtime prevents running and collecting
results from multiple tests in a test suite.

.. include:: ../substitutions.rst
