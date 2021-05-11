Debugging GUI tests at runtime
==============================

To debug an issue with a GUI test, one can use the |UITester.delay| parameter
to slow down the test, or they may use a Python debugger to inspect internal
states while the test is being run. In both cases, developers should
be aware that the GUI can react to any additional events that may be caused by
these debugging activities, and this may cause the test to behave differently
compared to running it in normal conditions.

For example, if a test relies on a GUI widget having the keyboard input focus,
a Python debugger may interfere with the test by stealing focus from the GUI
when a break point occurs.

.. include:: ../substitutions.rst
