# (C) Copyright 2020-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

"""
Tasks for Test Runs
===================

This file is intended to be used in a Python environment equipped with the
click library, to automate the process of setting up test environments
and running the tests within them.  This improves repeatability and
reliability of tests be removing many of the variables around the
developer's particular Python environment.  Test environment setup and
package management is performed using `EDM
<http://docs.enthought.com/edm/>`_

To use this to run your tests, you will need to install EDM and click
into your working environment.  You will also need to have git
installed to access required source code from github repositories.
You can then do::

    python etstool.py install --runtime=... --toolkit=...

If you need to make local changes, it might be convenient to include the
``--editable`` flag::

    python etstool.py install --runtime=... --toolkit=... --editable

to create a test environment from the current codebase and::

    python etstool.py test --runtime=... --toolkit=...

to run tests in that environment.  You can remove the environment with::

    python etstool.py cleanup --runtime=... --toolkit=...

If you make changes and you have not used ``--editable`` flag in the
``install`` command, you will either need to remove and re-install the
environment or manually update the environment using ``edm``, as
the install performs a ``pip install .`` rather than a ``pip install -e .``,
so changes in your code will not be automatically mirrored in the test
environment.  You can update with a command like::

    edm run --environment ... -- python setup.py install

You can run all three tasks at once with::

    python etstool.py test_clean --runtime=... --toolkit=...

which will create, install, run tests, and then clean-up the environment.  And
you can run tests in all supported runtimes and toolkits (with cleanup)
using::

    python etstool.py test_all

Currently supported runtime values are ``3.6``, and currently
supported toolkits are ``null``, ``pyqt``, ``pyqt5``, ``pyside2`` and ``wx``.
Not all combinations of toolkits and runtimes will work, but the tasks will
fail with a clear error if that is the case.

Tests can still be run via the usual means in other environments if that suits
a developer's purpose.

Changing This File
------------------

To change the packages installed during a test run, change the dependencies
variable below.

Other changes to commands should be a straightforward change to the listed
commands for each task. See the EDM documentation for more information about
how to run commands within an EDM environment.

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
    '3.6': {'pyside2', 'pyqt', 'pyqt5', 'wx', 'null'},
}

# Default Python version to use in the comamnds below if none is specified.
DEFAULT_RUNTIME = '3.6'

# Default toolkit to use if none specified.
DEFAULT_TOOLKIT = 'null'

# The main package name, also used to form the Python environment name.
PACKAGE_NAME = "etsdemo"

dependencies = {
    "configobj",
    "docutils",
    "eam",
    "flake8",
    "flake8_ets",
    "traits",
    "traitsui",
    "pyface",
    "pip",
}

extra_dependencies = {
    # XXX once pyside2 is available in EDM, we will want it here
    'pyside2': {
        "pygments",
    },
    'pyqt': {
        'pyqt<4.12',  # FIXME: build 1 of 4.12.1 appears to be bad
        'pygments',
    },
    'pyqt5': {
        'pyqt5',
        'pygments',
    },
    # XXX once wxPython 4 is available in EDM, we will want it here
    'wx': set(),
    'null': set(),
}

runtime_dependencies = {}

doc_dependencies = {}

environment_vars = {
    'pyside2': {'ETS_TOOLKIT': 'qt4', 'QT_API': 'pyside2'},
    "pyqt": {'ETS_TOOLKIT': 'qt4', 'QT_API': 'pyqt'},
    'pyqt5': {"ETS_TOOLKIT": "qt4", "QT_API": "pyqt5"},
    'wx': {'ETS_TOOLKIT': 'wx'},
    'null': {'ETS_TOOLKIT': 'null'},
}

CONTEXT_SETTINGS = {
    "help_option_names": ["-h", "--help"],
}


@click.group(context_settings=CONTEXT_SETTINGS)
def cli():
    pass


@cli.command()
@click.option('--runtime', default=DEFAULT_RUNTIME)
@click.option('--toolkit', default=DEFAULT_TOOLKIT)
@click.option('--environment', default=None)
@click.option(
    "--editable/--not-editable",
    default=False,
    help="Install main package in 'editable' mode?  [default: --not-editable]",
)
def install(runtime, toolkit, environment, editable):
    """ Install project and dependencies into a clean EDM environment.

    """
    parameters = get_parameters(runtime, toolkit, environment)
    packages = ' '.join(
        dependencies
        | extra_dependencies.get(toolkit, set())
        | runtime_dependencies.get(runtime, set())
    )

    install_here = "edm run -e {environment} -- pip install "
    if editable:
        install_here += "--editable "
    install_here += "."

    # edm commands to setup the development environment
    if sys.platform == 'linux':
        commands = ["edm environments create {environment} --platform=rh6-x86_64 --force --version={runtime}"]  # noqa: E501
    else:
        commands = ["edm environments create {environment} --force --version={runtime}"]  # noqa: E501

    commands.extend([
        "edm install -y -e {environment} " + packages,
        "edm run -e {environment} -- python setup.py clean --all",
        install_here,
    ])

    # pip install pyside2, because we don't have it in EDM yet
    if toolkit == 'pyside2':
        commands.append(
            "edm run -e {environment} -- pip install pyside2==5.11"
        )
    elif toolkit == 'wx':
        if sys.platform != 'linux':
            commands.append(
                "edm run -e {environment} -- pip install wxPython"
            )
        else:
            # XXX this is mainly for TravisCI workers; need a generic solution
            commands.append(
                "edm run -e {environment} -- pip install -f https://extras.wxpython.org/wxPython4/extras/linux/gtk3/ubuntu-16.04 wxPython"   # noqa: E501
            )

    click.echo("Creating environment '{environment}'".format(**parameters))
    execute(commands, parameters)
    click.echo('Done install')


@cli.command()
@click.option('--runtime', default=DEFAULT_RUNTIME)
@click.option('--toolkit', default=DEFAULT_TOOLKIT)
@click.option('--environment', default=None)
def shell(runtime, toolkit, environment):
    """ Create a shell into the EDM development environment
    (aka 'activate' it).

    """
    parameters = get_parameters(runtime, toolkit, environment)
    commands = [
        "edm shell -e {environment}",
    ]
    execute(commands, parameters)


@cli.command()
@click.option('--runtime', default=DEFAULT_RUNTIME)
@click.option('--toolkit', default=DEFAULT_TOOLKIT)
@click.option('--environment', default=None)
def test(runtime, toolkit, environment):
    """ Run the test suite in a given environment with the specified toolkit.

    """
    parameters = get_parameters(runtime, toolkit, environment)
    environ = environment_vars.get(toolkit, {}).copy()
    environ['PYTHONUNBUFFERED'] = "1"

    commands = [
        "python -m unittest discover -v " + PACKAGE_NAME,
    ]
    commands = [
        "edm run -e {environment} -- " + command
        for command in commands
    ]

    # We run in a tempdir to avoid accidentally picking up wrong code from a
    # local dir.
    click.echo("Running tests in '{environment}'".format(**parameters))
    with do_in_tempdir():
        os.environ.update(environ)
        execute(commands, parameters)
    click.echo('Done test')


@cli.command()
@click.option('--runtime', default=DEFAULT_RUNTIME)
@click.option('--toolkit', default=DEFAULT_TOOLKIT)
@click.option('--environment', default=None)
def cleanup(runtime, toolkit, environment):
    """ Remove a development environment.

    """
    parameters = get_parameters(runtime, toolkit, environment)
    commands = [
        "edm run -e {environment} -- python setup.py clean",
        "edm environments remove {environment} --purge -y"]
    click.echo("Cleaning up environment '{environment}'".format(**parameters))
    execute(commands, parameters)
    click.echo('Done cleanup')


@cli.command()
@click.option('--runtime', default=DEFAULT_RUNTIME)
@click.option('--toolkit', default=DEFAULT_TOOLKIT)
def test_clean(runtime, toolkit):
    """ Run tests in a clean environment, cleaning up afterwards

    """
    args = ['--toolkit={}'.format(toolkit), '--runtime={}'.format(runtime)]
    try:
        install(args=args, standalone_mode=False)
        test(args=args, standalone_mode=False)
    finally:
        cleanup(args=args, standalone_mode=False)


@cli.command()
def test_all():
    """ Run test_clean across all supported environment combinations.

    """
    failed_command = False
    for runtime, toolkits in supported_combinations.items():
        for toolkit in toolkits:
            args = [
                '--toolkit={}'.format(toolkit),
                '--runtime={}'.format(runtime)
            ]
            try:
                test_clean(args, standalone_mode=True)
            except SystemExit:
                failed_command = True
    if failed_command:
        sys.exit(1)


@cli.command()
@click.option('--runtime', default=DEFAULT_RUNTIME)
@click.option('--toolkit', default=DEFAULT_TOOLKIT)
@click.option(
    "--environment", default=None, help="Name of EDM environment to check."
)
def flake8(runtime, toolkit, environment):
    """ Run a flake8 check in a given environment.

    """
    parameters = get_parameters(runtime, toolkit, environment)
    commands = ["edm run -e {environment} -- python -m flake8"]
    execute(commands, parameters)


# ----------------------------------------------------------------------------
# Utility routines
# ----------------------------------------------------------------------------

def get_parameters(runtime, toolkit, environment):
    """ Set up parameters dictionary for format() substitution """
    parameters = {
        'runtime': runtime,
        'toolkit': toolkit,
        'environment': environment,
    }
    if toolkit not in supported_combinations[runtime]:
        msg = ("Python {runtime} and toolkit {toolkit} not supported by " +
               "test environments")
        raise RuntimeError(msg.format(**parameters))
    if environment is None:
        parameters['environment'] = (
            PACKAGE_NAME + '-test-{runtime}-{toolkit}'.format(**parameters)
        )
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


def execute(commands, parameters):
    for command in commands:
        click.echo("[EXECUTING] {}".format(command.format(**parameters)))
        try:
            subprocess.check_call([arg.format(**parameters)
                                   for arg in command.split()])
        except subprocess.CalledProcessError as exc:
            click.echo(str(exc))
            sys.exit(1)


if __name__ == '__main__':
    cli()
