"""
Invoke Tasks for Test Runs
==========================

This file is intended to be used with `Invoke http://www.pyinvoke.org/`_ to
automate the process of setting up test environments and running the test
within them.  This improves repeatability and reliability of tests be removing
many of the variables around the developer's particular Python environment.
Test environment setup and package management is performed using
`EDM http://docs.enthought.com/edm/`_

To use this to run you tests, you will need to install EDM and Invoke into
your working environment.  You will also need to have git installed to access
required source code from github repositories.  You can then do::

    invoke install --runtime=... --toolkit=...

to create a test environment from the current codebase and::

    invoke test --runtime=... --toolkit=...

to run tests in that environment.  You can remove the environment with::

    invoke cleanup --runtime=... --toolkit=...

If you make changes you will either need to remove and re-install the
environment or manually update the environment using ``edm``, as
the install performs a ``python setup.py install`` rather than a ``develop``,
so changes in your code will not be automatically mirrored in the test
environment.  You can update with a command like::

    edm run --environment ... -- python setup.py install

You can run all three tasks at once with::

    invoke test_clean --runtime=... --toolkit=...

which will create, install, run tests, and then clean-up the environment.  And
you can run tests in all supported runtimes and toolkits (with cleanup)
using::

    invoke test_all

Currently supported runtime values are ``2.7`` and ``3.5``, and currently
supported toolkits are ``null``, ``pyqt``, ``pyside`` and ``wx``.  Not all
combinations of toolkits and runtimes will work, but the tasks will fail with
a clear error if that is the case.

Tests can still be run via the usual means in other environments if that suits
a developer's purpose.

Changing This File
------------------

To change the packages installed during a test run, change the dependencies
variable below.  To install a package from github, or one which is not yet
available via EDM, add it to the `ci-src-requirements.txt` file (these will be
installed by `pip`).

Other changes to commands should be a straightforward change to the listed
commands for each task. See the EDM documentation for more information about
how to run commands within an EDM enviornment.

"""

from contextlib import contextmanager
import os
from shutil import rmtree, copy as copyfile
from tempfile import mkdtemp

from invoke import task


supported_combinations = {
    '2.7': {'pyside', 'pyqt', 'wx', 'null'},
    '3.5': {'pyqt', 'null'},
}

dependencies = {
    "numpy",
    "pandas",
    "pygments",
    "traits",
    "pip",
    "nose",
    "coverage",
}

extra_dependencies = {
    'pyside': {'pyside'},
    'pyqt': {'pyqt'},
    'wx': {'wxpython'},
    'null': set()
}

environment_vars = {
    'pyside': {'ETS_TOOLKIT': 'qt4', 'QT_API': 'pyside'},
    'pyqt': {'ETS_TOOLKIT': 'qt4', 'QT_API': 'pyqt'},
    'wx': {'ETS_TOOLKIT': 'wx'},
    'null': {'ETS_TOOLKIT': 'null'},
}



@task
def install(ctx, runtime='3.5', toolkit='null', environment=None):
    """ Install project and dependencies into a clean EDM environment. """
    parameters = _get_parameters(runtime, toolkit, environment)

    parameters['packages'] = ' '.join(dependencies |
                                      extra_dependencies.get(toolkit, set()))

    commands = [
        # create environment with dependencies
        "edm install -y -e '{environment}' --version '{runtime}' {packages}",
        # install any source dependencies from github using pip
        "edm run -e '{environment}' -- pip install -r ci-src-requirements.txt --no-dependencies",
        # install the project
        "edm run -e '{environment}' -- python setup.py install",
    ]

    print("Creating environment '{environment}'".format(**parameters))
    for command in commands:
        ctx.run(command.format(**parameters))

    print('Done install')


@task
def test(ctx, runtime='3.5', toolkit='null', environment=None):
    """ Run the test suite in a given environment with the specified toolkit """
    parameters = _get_parameters(runtime, toolkit, environment)

    environ = environment_vars.get(toolkit, {}).copy()
    environ['PYTHONUNBUFFERED'] = "1"

    commands = [
        # run the main test suite
        "edm run -e '{environment}' -- coverage run -m nose.core -v traitsui.tests",
    ]
    if toolkit in {'pyqt', 'pyside'}:
        commands += [
            # run the qt4 toolkit test suite
            "edm run -e '{environment}' -- coverage run -m nose.core -v traitsui.qt4.tests"
        ]

    # run tests & coverage
    print("Running tests in '{environment}'".format(**parameters))

    # We run in a tempdir to avoid accidentally picking up wrong traitsui
    # code from a local dir.  We need to ensure a good .coveragerc is in
    # that directory, plus coverage has a bug that means a non-local coverage
    # file doesn't get populated correctly.
    with do_in_tempdir(files=['.coveragerc'], capture_files=['.coverage']):
        for command in commands:
            ctx.run(command.format(**parameters), env=environ)

    print('Done test')


@task
def cleanup(ctx, runtime='3.5', toolkit='null', environment=None):
    parameters = _get_parameters(runtime, toolkit, environment)

    commands = [
        "edm run -e '{environment}' -- python setup.py clean",
        "edm environments remove '{environment}' --purge -y",
    ]

    print("Cleaning up environment '{environment}'".format(**parameters))
    for command in commands:
        ctx.run(command.format(**parameters))

    print('Done cleanup')


@task
def test_clean(ctx, runtime='3.5', toolkit='null'):
    """ Run tests in a clean environment, cleaning up afterwards """
    try:
        install(ctx, runtime, toolkit)
        test(ctx, runtime, toolkit)
    finally:
        cleanup(ctx, runtime, toolkit)


@task
def test_all(ctx):
    """ Run test_clean across all supported environments """
    for runtime, toolkits in supported_combinations.items():
        for toolkit in toolkits:
            try:
                test_clean(ctx, runtime, toolkit)
            except Exception as exc:
                # continue to next runtime
                print(exc)

# ----------------------------------------------------------------------------
# Utility routines
# ----------------------------------------------------------------------------

def _get_parameters(runtime, toolkit, environment):
    """ Set up parameters dictionary for format() substitution """
    parameters = {'runtime': runtime, 'toolkit': toolkit}

    if toolkit not in supported_combinations.get(runtime, set()):
        msg = ("Python {runtime} and toolkit {toolkit} not supported by " +
               "test environments")
        raise RuntimeError(msg.format(**parameters))

    if environment is None:
        environment = 'traitsui-test-{runtime}-{toolkit}'.format(**parameters)
    parameters['environment'] = environment

    return parameters


@contextmanager
def do_in_tempdir(files=(), capture_files=()):
    """ Create a temporary directory, cleaning up after done.

    Creates the temporary directory, and changes into it.  On exit returns to
    original directory and removes temporary dir.

    Parameters
    ----------
    files : sequence of filenames
        Files to be copied across to temporary directory.
    capture_files : sequence of filenames
        Files to be copied back from temporary directory.
    """
    path = mkdtemp()
    old_path = os.getcwd()

    # send across any files we need
    for filepath in files:
        copyfile(filepath, path)

    os.chdir(path)
    try:
        yield path

        # retrieve any result files we want
        for filepath in capture_files:
            copyfile(filepath, old_path)
    finally:
        os.chdir(old_path)
        rmtree(path)
