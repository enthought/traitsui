"""
Tasks for Test Runs
===================

This file is intended to be used with a python environment with the
click library to automate the process of setting up test environments
and running the test within them.  This improves repeatability and
reliability of tests be removing many of the variables around the
developer's particular Python environment.  Test environment setup and
package management is performed using `EDM
http://docs.enthought.com/edm/`_

To use this to run you tests, you will need to install EDM and click
into your working environment.  You will also need to have git
installed to access required source code from github repositories.
You can then do::

    python -m tasks install --runtime=... --toolkit=...

to create a test environment from the current codebase and::

    python -m tasks test --runtime=... --toolkit=...

to run tests in that environment.  You can remove the environment with::

    python -m tasks cleanup --runtime=... --toolkit=...

If you make changes you will either need to remove and re-install the
environment or manually update the environment using ``edm``, as
the install performs a ``python setup.py install`` rather than a ``develop``,
so changes in your code will not be automatically mirrored in the test
environment.  You can update with a command like::

    edm run --environment ... -- python setup.py install

You can run all three tasks at once with::

    python -m tasks test_clean --runtime=... --toolkit=...

which will create, install, run tests, and then clean-up the environment.  And
you can run tests in all supported runtimes and toolkits (with cleanup)
using::

    python -m tasks test_all

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

import glob
import os
import subprocess
import sys
from shutil import rmtree, copy as copyfile
from tempfile import mkdtemp
from contextlib import contextmanager

import click

supported_combinations = {
    '2.7': {'pyside', 'pyqt', 'wx', 'null'},
    '3.5': {'pyqt', 'pyqt5', 'null'},
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
    # XXX once pyqt5 is available in EDM, we will want it here
    'pyqt5': set(),
    'wx': {'wxpython'},
    'null': set()
}

environment_vars = {
    'pyside': {'ETS_TOOLKIT': 'qt4', 'QT_API': 'pyside'},
    'pyqt': {'ETS_TOOLKIT': 'qt4', 'QT_API': 'pyqt'},
    'pyqt5': {'ETS_TOOLKIT': 'qt4', 'QT_API': 'pyqt5'},
    'wx': {'ETS_TOOLKIT': 'wx'},
    'null': {'ETS_TOOLKIT': 'null'},
}


@click.group()
def cli():
    pass


@cli.command()
@click.option('--runtime', default='3.5')
@click.option('--toolkit', default='null')
@click.option('--environment', default=None)
def install(runtime, toolkit, environment):
    """ Install project and dependencies into a clean EDM environment. """
    parameters = _get_parameters(runtime, toolkit, environment)
    parameters['packages'] = ' '.join(
        dependencies | extra_dependencies.get(toolkit, set()))

    commands = [
        # create environment with dependencies
        "edm environments create {environment} --force --version={runtime}",
        "edm install -y -e {environment} {packages}",
        # install any source dependencies from github using pip
        "edm run -e {environment} -- pip install -r ci-src-requirements.txt --no-dependencies",
        # install the project
        "edm run -e {environment} -- python setup.py install",
    ]
    if toolkit == 'pyqt5':
        # pip install pyqt5, because we don't have in EDM yet
        # this assumes Qt5 is available, which implies Linux, for now
        commands += "edm run -e {environment} -- pip install pyqt5"

    click.echo("Creating environment '{environment}'".format(**parameters))
    for command in commands:
        check_call(command.format(**parameters).split())

    click.echo('Done install')


@cli.command()
@click.option('--runtime', default='3.5')
@click.option('--toolkit', default='null')
@click.option('--environment', default=None)
def test(runtime, toolkit, environment):
    """ Run the test suite in a given environment with the specified toolkit """
    parameters = _get_parameters(runtime, toolkit, environment)

    environ = environment_vars.get(toolkit, {}).copy()
    environ['PYTHONUNBUFFERED'] = "1"

    commands = [
        # run the main test suite
        "edm run -e {environment} -- coverage run -p -m nose.core -v traitsui.tests --nologcapture",
    ]
    if toolkit in {'pyqt', 'pyside', 'pyqt5'}:
        commands += [
            # run the qt4 toolkit test suite
            "edm run -e {environment} -- coverage run -p -m nose.core -v traitsui.qt4.tests --nologcapture"
        ]

    # run tests & coverage
    click.echo("Running tests in '{environment}'".format(**parameters))

    # We run in a tempdir to avoid accidentally picking up wrong traitsui
    # code from a local dir.  We need to ensure a good .coveragerc is in
    # that directory, plus coverage has a bug that means a non-local coverage
    # file doesn't get populated correctly.
    with do_in_tempdir(files=['.coveragerc'], capture_files=['./.coverage*']):
        for command in commands:
            check_call(command.format(**parameters).split())

    click.echo('Done test')

@cli.command()
@click.option('--runtime', default='3.5')
@click.option('--toolkit', default='null')
@click.option('--environment', default=None)
def cleanup(runtime, toolkit, environment):
    parameters = _get_parameters(runtime, toolkit, environment)

    commands = [
        "edm run -e {environment} -- python setup.py clean",
        "edm environments remove {environment} --purge -y",
    ]

    click.echo("Cleaning up environment '{environment}'".format(**parameters))
    for command in commands:
        subprocess.check_call(command.format(**parameters).split())

    click.echo('Done cleanup')


@cli.command()
@click.option('--runtime', default='3.5')
@click.option('--toolkit', default='null')
def test_clean(runtime, toolkit):
    """ Run tests in a clean environment, cleaning up afterwards """
    args = ['--toolkit={}'.format(toolkit), '--runtime={}'.format(runtime)]
    try:
        install(args=args, standalone_mode=False)
        test(args=args, standalone_mode=False)
    finally:
        cleanup(args=args, standalone_mode=False)

@cli.command()
@click.option('--runtime', default='3.5')
@click.option('--toolkit', default='null')
@click.option('--environment', default=None)
def update(runtime, toolkit, environment):
    parameters = _get_parameters(runtime, toolkit, environment)

    commands = [
        "edm run -e {environment} -- python setup.py install",
    ]

    click.echo("Re-installing in  '{environment}'".format(**parameters))
    for command in commands:
        subprocess.check_call(command.format(**parameters).split())

    click.echo('Done update')


@cli.command()
def test_all():
    """ Run test_clean across all supported environments """
    for runtime, toolkits in supported_combinations.items():
        for toolkit in toolkits:
            args = ['--toolkit={}'.format(toolkit), '--runtime={}'.format(runtime)]
            test_clean(args, standalone_mode=True)

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
        click.echo('copying file to tempdir: {}'.format(filepath))
        copyfile(filepath, path)

    os.chdir(path)
    try:
        yield path

        # retrieve any result files we want
        for pattern in capture_files:
            for filepath in glob.iglob(pattern):
                click.echo('copying file back: {}'.format(filepath))
                copyfile(filepath, old_path)
    finally:
        os.chdir(old_path)
        rmtree(path)


def check_call(*args, **kwargs):
    try:
        subprocess.check_call(*args, **kwargs)
    except subprocess.CalledProcessError:
        sys.exit(1)


if __name__ == '__main__':
    cli()
