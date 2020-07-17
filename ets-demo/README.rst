=====================================
Enthought Tool Suite Demo Application
=====================================

This package provides a GUI application for browsing and executing Python
scripts, with the intention to demonstrate how Enthought Tool Suite
packages can be used.

The actual demonstration materials are not provided by this package.

How to run
----------

After installing ``etsdemo``, the application can be launched from the
command line prompt::

    $ etsdemo

It can also be launched programmatically. For example, from Python prompt::

    >>> from etsdemo.main import main
    >>> main()

How to contribute data via entry points
---------------------------------------

Any Python package can contribute data to be viewed from the application.
To do so, define a function in the package that returns information about the
data files. For example::

    def info(request):
        # request is currently a placeholder, not used.
        return {
            "version": 1,
            # Name to be displayed in the node wrapping the data files.
            "name": "Project X Examples",
            # Path to a directory where data files can be found.
            "root": pkg_resources.resource_filename("my_project", "data"),
        }

Then add an entry point in ``setup.py`` that points to the newly created
function. For example::

    from setuptools import setup

    setup(
        name="my_project",
        ...
        entry_points={
            "etsdemo_data": ["demo = my_project.info:info"],
        ...
    )

Launch with specific data sources
---------------------------------

Instead of launching the application with data collected from packages
installed in the Python environment, the demo application can be launched with
specific data sources::

    from etsdemo.main import main
    main(
        [
            {
                "version": 1,
                "name": "Project X Examples",
                "root": pkg_resources.resource_filename("my_project", "data"),
            },
            {
                "version": 1,
                "name": "Project X Demo",
                "root": pkg_resources.resource_filename("my_project", "demo"),
            },
        ]
    )

Notice that the nested dictionaries follow the same schema specification
described above.

Dependencies
------------

- Traits_
- TraitsUI_
- Pyface_

.. _Traits: https://pypi.org/project/traits/
.. _TraitsUI: https://pypi.org/project/traitsui/
.. _Pyface: https://pypi.org/project/pyface/
