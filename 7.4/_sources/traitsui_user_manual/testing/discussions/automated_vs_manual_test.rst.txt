Limitations on automated GUI testing
====================================

The testing library allows more manual GUI tests to be rewritten as automated
tests. However, automated tests cannot replace manual testing entirely, and
there exists toolkit-dependent and platform-dependent limitations as to what
can be achieved for programmatically imitating user interactions, e.g. the
animation of a button being depressed when clicked may not be replicated in
automated tests.

The |UITester.delay| parameter allows playing back a test for visual
confirmation, but it may not look identical to how the GUI looks when it is
tested manually.

If the GUI / trait states being asserted in tests are not consistent compared
to manually testing, then that is likely a bug. Please report it.

If the GUI / trait states being asserted in tests are consistent with manual
testing, then such visual discrepancies may have to be tolerated.

.. include:: ../substitutions.rst
