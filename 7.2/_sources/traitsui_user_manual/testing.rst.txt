.. _testing-traitsui-applications:

=============================
Testing TraitsUI Applications
=============================

TraitsUI provides a toolkit independent API to help developers check the
behavior of their applications in automated tests.

Most of the testing functionality can be accessed via the |testing.api| module.

.. note::
   The testing library is relatively new compared to other features in
   TraitsUI. Built-in support for testing TraitsUI editors are continuously
   being added.


Get started
===========

.. toctree::
   :maxdepth: 1

   testing/tutorials/first_test
   testing/tutorials/test_with_nested_object

How-to guides
=============

.. toctree::
   :maxdepth: 1

   testing/howtos/add_new_interaction
   testing/howtos/add_new_location


Discussions
===========

.. toctree::
   :maxdepth: 1

   testing/discussions/automated_vs_manual_test
   testing/discussions/debugging-gui-tests-at-runtime
   testing/discussions/compatibility_pyface_testing
   testing/discussions/event_loop_and_exceptions
   testing/discussions/target_interaction_location
   testing/discussions/working_of_extensions

Technical Reference
===================

.. toctree::
   :maxdepth: 1

   testing/references/examples
   API Reference <../api/traitsui.testing>

.. include:: testing/substitutions.rst
