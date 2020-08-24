#
#  Copyright (c) 2017, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
"""
Tasks for Test Runs
===================

This file is intended to be used with a python environment with the
click library to automate the process of setting up test environments
and running the test within them.  This improves repeatability and
reliability of tests be removing many of the variables around the
developer's particular Python environment.  Test environment setup and
package management is performed using `EDM
<http://docs.enthought.com/edm/>`_

To use this to run you tests, you will need to install EDM and click
into your working environment.  You will also need to have git
installed to access required source code from github repositories.
You can then do::

    python etstool.py install --runtime=... --toolkit=...

to create a test environment from the current codebase and::

    python etstool.py test --runtime=... --toolkit=...

to run tests in that environment.  You can remove the environment with::

    python etstool.py cleanup --runtime=... --toolkit=...

If you need to make frequent changes to the source, it is often convenient
to install the source in editable mode::

    python etstool.py install --editable --runtime=... --toolkit=...

You can run all three tasks at once with::

    python etstool.py test_clean --runtime=... --toolkit=...

which will create, install, run tests, and then clean-up the environment.  And
you can run tests in all supported runtimes and toolkits (with cleanup)
using::

    python etstool.py test_all

Currently supported runtime values are ``3.5`` and ``3.6``, and currently
supported toolkits are ``null``, ``pyqt``, ``pyqt5``, ``pyside`` and ``wx``.
Not all combinations of toolkits and runtimes will work, but the tasks will
fail with a clear error if that is the case.

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
    '3.5': {'pyside2', 'pyqt', 'pyqt5', 'null'},
    '3.6': {'pyside2', 'pyqt', 'pyqt5', 'wx', 'null'},
}

# Default Python version to use in the comamnds below if none is specified.
DEFAULT_RUNTIME = '3.6'

# Default toolkit to use if none specified.
DEFAULT_TOOLKIT = 'null'

# Traits version requirement (empty string to mean no specific requirement).
# The requirement is to be interpreted by EDM
TRAITS_VERSION_REQUIRES = os.environ.get("TRAITS_REQUIRES", "")

dependencies = {
    "numpy",
    "traits" + TRAITS_VERSION_REQUIRES,
    "pandas",
    "pygments",
    "pip",
    "nose",
    "coverage",
    "configobj",
    "docutils",
}

# NOTE : pyface is always installed from source
source_dependencies = {
    "traits": "git+http://github.com/enthought/traits.git#egg=traits",
}

# Additional toolkit-independent dependencies for demo testing
# This should correspond to the "examples" dependencies in extras_requires but
# the following names are used by EDM.
test_dependencies = {
    "apptools",
    "chaco",
    "h5py",
    "numpy",
    "pandas",
    "pytables",
}

extra_dependencies = {
    # XXX once pyside2 is available in EDM, we will want it here
    'pyside2': set(),
    'pyqt': {'pyqt<4.12'},  # FIXME: build 1 of 4.12.1 appears to be bad
    'pyqt5': {'pyqt5'},
    # XXX once wxPython 4 is available in EDM, we will want it here
    'wx': set(),
    'null': set()
}

runtime_dependencies = {}

doc_dependencies = {
    "sphinx",
    "enthought_sphinx_theme",
}

environment_vars = {
    'pyside2': {'ETS_TOOLKIT': 'qt4', 'QT_API': 'pyside2'},
    'pyqt': {"ETS_TOOLKIT": "qt4", "QT_API": "pyqt"},
    'pyqt5': {"ETS_TOOLKIT": "qt4", "QT_API": "pyqt5"},
    'wx': {'ETS_TOOLKIT': 'wx'},
    'null': {'ETS_TOOLKIT': 'null'},
}


def normalize(name):
    return name.replace("_", "-")


@click.group(context_settings={"token_normalize_func": normalize})
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
@click.option('--source/--no-source', default=False)
def install(runtime, toolkit, environment, editable, source):
    """ Install project and dependencies into a clean EDM environment.

    """
    parameters = get_parameters(runtime, toolkit, environment)
    packages = ' '.join(
        dependencies
        | extra_dependencies.get(toolkit, set())
        | runtime_dependencies.get(runtime, set())
        | test_dependencies
    )

    install_traitsui = "edm run -e {environment} -- pip install "
    if editable:
        install_traitsui += "--editable "
    install_traitsui += "."

    # edm commands to setup the development environment
    if sys.platform == 'linux':
        commands = ["edm environments create {environment} --platform=rh6-x86_64 --force --version={runtime}"]
    else:
        commands = ["edm environments create {environment} --force --version={runtime}"]

    commands.extend([
        "edm install -y -e {environment} " + packages,
        "edm run -e {environment} -- pip install --force-reinstall -r ci-src-requirements.txt --no-dependencies",
        "edm run -e {environment} -- python setup.py clean --all",
        install_traitsui,
    ])

    # pip install pyqt5 and pyside2, because we don't have them in EDM yet
    if toolkit == 'pyside2':
        commands.append(
            "edm run -e {environment} -- pip install pyside2"
        )
    elif toolkit == 'wx':
        if sys.platform != 'linux':
            commands.append(
                "edm run -e {environment} -- pip install wxPython"
            )
        else:
            # XXX this is mainly for TravisCI workers; need a generic solution
            commands.append(
                "edm run -e {environment} -- pip install -f https://extras.wxpython.org/wxPython4/extras/linux/gtk3/ubuntu-14.04 wxPython"
            )

    click.echo("Creating environment '{environment}'".format(**parameters))
    execute(commands, parameters)

    if source:
        cmd_fmt = "edm plumbing remove-package --environment {environment} --force "
        commands = [cmd_fmt+dependency for dependency in source_dependencies.keys()]
        execute(commands, parameters)
        source_pkgs = source_dependencies.values()
        commands = [
            "python -m pip install {pkg} --no-deps".format(pkg=pkg)
            for pkg in source_pkgs
        ]
        commands = ["edm run -e {environment} -- " + command for command in commands]
        execute(commands, parameters)

    click.echo('Done install')


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

    if toolkit == "wx":
        environ["EXCLUDE_TESTS"] = "qt"
    elif toolkit in {"pyqt", "pyqt5", "pyside", "pyside2"}:
        environ["EXCLUDE_TESTS"] = "wx"
    else:
        environ["EXCLUDE_TESTS"] = "(wx|qt)"

    parameters["integrationtests"] = os.path.abspath("integrationtests")
    commands = [
        "edm run -e {environment} -- python -W default -m coverage run -p -m unittest discover -v traitsui",
        # coverage run prevents local images to be loaded for demo examples
        # which are not defined in Python packages. Run with python directly
        # instead.
        "edm run -e {environment} -- python -W default -m unittest discover -v {integrationtests}",
    ]

    # We run in a tempdir to avoid accidentally picking up wrong traitsui
    # code from a local dir.  We need to ensure a good .coveragerc is in
    # that directory, plus coverage has a bug that means a non-local coverage
    # file doesn't get populated correctly.
    click.echo("Running tests in '{environment}'".format(**parameters))
    with do_in_tempdir(files=['.coveragerc'], capture_files=['./.coverage*']):
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
@click.option('--runtime', default=DEFAULT_RUNTIME)
@click.option('--toolkit', default=DEFAULT_TOOLKIT)
@click.option('--environment', default=None)
def update(runtime, toolkit, environment):
    """ Update/Reinstall package into environment.

    """
    parameters = get_parameters(runtime, toolkit, environment)
    commands = [
        "edm run -e {environment} -- python setup.py install"]
    click.echo("Re-installing in  '{environment}'".format(**parameters))
    execute(commands, parameters)
    click.echo('Done update')


@cli.command()
@click.option('--runtime', default=DEFAULT_RUNTIME)
@click.option('--toolkit', default=DEFAULT_TOOLKIT)
@click.option('--environment', default=None)
def docs(runtime, toolkit, environment):
    """ Autogenerate documentation

    """
    parameters = get_parameters(runtime, toolkit, environment)
    packages = ' '.join(doc_dependencies)
    commands = [
        "edm install -y -e {environment} " + packages,
    ]
    click.echo("Installing documentation tools in  '{environment}'".format(
        **parameters))
    execute(commands, parameters)
    click.echo('Done installing documentation tools')

    os.chdir('docs')
    commands = [
        "edm run -e {environment} -- make html",
    ]
    click.echo("Building documentation in  '{environment}'".format(**parameters))
    try:
        execute(commands, parameters)
    finally:
        os.chdir('..')
    click.echo('Done building documentation')


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


# ----------------------------------------------------------------------------
# Utility routines
# ----------------------------------------------------------------------------

def get_parameters(runtime, toolkit, environment):
    """ Set up parameters dictionary for format() substitution """
    parameters = {'runtime': runtime, 'toolkit': toolkit, 'environment': environment}
    if toolkit not in supported_combinations[runtime]:
        msg = ("Python {runtime} and toolkit {toolkit} not supported by " +
               "test environments")
        raise RuntimeError(msg.format(**parameters))
    if environment is None:
        parameters['environment'] = 'traitsui-test-{runtime}-{toolkit}'.format(**parameters)
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
