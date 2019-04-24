============================================
TraitsUI: Traits-capable windowing framework
============================================

.. image:: https://travis-ci.org/enthought/traitsui.svg?branch=master
   :target: https://travis-ci.org/enthought/traitsui

.. image:: https://ci.appveyor.com/api/projects/status/n2qy8kcwh8ibi9g3/branch/master?svg=true
   :target: https://ci.appveyor.com/project/EnthoughtOSS/traitsui/branch/master

.. image:: https://codecov.io/github/enthought/traitsui/coverage.svg?branch=master
   :target: https://codecov.io/github/enthought/traitsui?branch=master

The TraitsUI project contains a toolkit-independent GUI abstraction layer,
which is used to support the "visualization" features of the
`Traits <http://github.com/enthought/traits>`__ package.
Thus, you can write model in terms of the Traits API and specify a GUI
in terms of the primitives supplied by TraitsUI (views, items, editors,
etc.), and let TraitsUI and your selected toolkit and back-end take care of
the details of displaying them.

Example
-------

Given a Traits model like the following::

    from traits.api import HasTraits, Str, Range, Enum

    class Person(HasTraits):
        name = Str('Jane Doe')
        age = Range(low=0)
        gender = Enum('female', 'male')

    person = Person(age=30)

we can use TraitsUI to specify a and display a GUI view::

    from traitsui.api import Item, RangeEditor, View

    person_view = View(
        Item('name'),
        Item('gender'),
        Item('age', editor=RangeEditor(mode='spinner', low=0, high=150)),
        buttons=['OK', 'Cancel'],
        resizable=True,
    )

    person.configure_traits(view=person_view)

which creates a GUI which looks like this:

.. image:: https://raw.github.com/enthought/traitsui/master/README_example.png

Important Links
---------------

- Website and Documentation: `<http://docs.enthought.com/traitsui>`__

  * User Manual `<http://docs.enthought.com/traitsui/traitsui_user_maunal>`__
  * Tutorial `<http://docs.enthought.com/traitsui/tutorial>`__
  * API Documentation `<http://docs.enthought.com/traitsui/api>`__

- Source code repository: `<https://github.com/enthought/traitsui>`__

  * Issue tracker: `<https://github.com/enthought/traitsui/issues>`__

- Download releases: `<https://pypi.python.org/pypi/traitsui>`__

- Mailing list: `<https://groups.google.com/forum/#!forum/ets-users>`__

Installation
------------

If you want to run traitsui, you must also install:

- Traits `<https://github.com/enthought/traits>`__
- Pyface `<https://github.com/enthought/pyface>`__

You will also need one of the following backends:

- PyQt
- wxPython
- PySide
- PyQt5

Backends have additional dependencies and there are optional dependencies on
NumPy and Pandas for some editors.

TraitsUI along with all dependencies can be installed in a straightforward way
using the `Enthought Deployment Manager <http://docs.enthought.com/edm/>`__,
``pip`` or other .

Running the Test Suite
----------------------

To run the test suite, you will need to install Git and
`EDM <http://docs.enthought.com/edm/>`__ as well as have a Python environment
which has install `Click <http://click.pocoo.org/>`__ available. You can then
follow the instructions in ``etstool.py``.  In particular::

    > python etstool.py test_all

will run tests in all supported environments automatically.
