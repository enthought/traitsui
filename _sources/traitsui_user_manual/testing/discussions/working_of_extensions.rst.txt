.. _testing-how-extension-works:

How extension works
===================

|UITester| supports testing TraitsUI editors with various user interaction
logic. However it is possible that projects' test code may require
additional logic that is not supported by |UITester| by default. Furthermore,
some projects may implement and maintain their own custom UI editors. Those
custom UI editors are also by default not supported by |UITester|.

The API allows extension such that

* projects can test TraitsUI editors with user interactions that do not
  come supported by default.
* projects can reuse the testing API for testing custom editors.

As described in :ref:`testing-add-new-interaction` and
:ref:`testing-add-new-location`, the testing API can be extended by providing
one or many registry objects. Internally, |UITester| maintains a list of
registries ordered in decreasing priority. For example, if you provide multiple
registries::

    tester = UITester(registries=[custom_registry, another_registry])

Interaction and location support registered in the first registry will
supersede that of the second (if such implementation exists).

This list of registries is passed on to all |UIWrapper| created from the
|UITester|. When |UIWrapper.perform| or |UIWrapper.inspect| is called, the
first registry that can support the given target and interaction will be used.
Likewise, |UIWrapper.locate| follows the same rule for the given target and
location. See :ref:`testing-target-interaction-location` for an explanation on
these three types of objects.

This is how |UITester| supports testing on TraitsUI editor: It extends
the given list of registries with more built-in registries that know how to
interact with TraitsUI editors, and let |UIWrapper| do most of the work.

.. include:: ../substitutions.rst
