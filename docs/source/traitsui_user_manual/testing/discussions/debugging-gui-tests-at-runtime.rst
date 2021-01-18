Debugging GUI tests at runtime
==============================

While debugging an issue with a GUI test, one can use the |UITester.delay|
parameter to slow down the test, or they may use a Python debugger to inspect
internal states while the test is being run. In both cases, developers should
be aware that the GUI can react to any additional events that may be caused by
these debugging activities, causing the test to behave differently when run in
debugging mode.

For example, if a test relies on focus staying in or moving out of a GUI
widget, a Python debugger may interfere with the test by stealing focus from
the GUI when a break point occurs.
