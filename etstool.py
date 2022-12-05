# (C) Copyright 2004-2022 Enthought, Inc., Austin, TX
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

Currently supported runtime values are ``3.6``, and currently
supported toolkits are ``null``, ``pyqt5``, ``pyside2`` and ``wx``.
Not all combinations of toolkits and runtimes will work, but the tasks will
fail with a clear error if that is the case.

Tests can still be run via the usual means in other environments if that suits
a developer's purpose.

Tasks for generating documentation
==================================

First, install or update the development environment::

    python etstool.py install --runtime=... --toolkit=...

Then, run the command to build documentation::

    python etstool.py docs --runtime=... --toolkit=...

Changing This File
------------------

To change the packages installed during a test run, change the dependencies
variable below.  To install a package from github, or one which is not yet
available via EDM, add it to the `ci-src-requirements.txt` file (these will be
installed by `pip`).

Other changes to commands should be a straightforward change to the listed
commands for each task. See the EDM documentation for more information about
how to run commands within an EDM enviornment.

Build changelog
---------------
To create a first-cut changelog from the news fragments, use this command::

    python etstool.py changelog build

This will update the changelog file. You should review and edit it.
"""

import glob
import os
import subprocess
import sys
from contextlib import contextmanager
from shutil import copy as copyfile
from shutil import rmtree
from tempfile import mkdtemp

import click


EDM_CONFIG_LOCATION = os.path.join(os.path.dirname(__file__), 'edm.yaml')

supported_combinations = {
    '3.6': {'pyside2', 'pyside6', 'pyqt5', 'pyqt6', 'wx', 'null'},
    '3.8': {'pyside2', 'pyside6', 'pyqt5', 'pyqt6', 'wx', 'null'},
}

# Default Python version to use in the comamnds below if none is specified.
DEFAULT_RUNTIME = '3.6'

# Default toolkit to use if none specified.
DEFAULT_TOOLKIT = 'null'

# Required runtime dependencies. Should match install_requires in setup.py
dependencies = {
    # temporarily get pyface from pip until EDM release
    # "pyface>=7.4.1",
    "traits",
}

# Dependencies we install from source for cron tests
# Order from packages with the most dependencies to one with the least
# dependencies. Packages are forced re-installed in this order.
source_dependencies = {
    "pyface": "git+http://github.com/enthought/pyface.git#egg=pyface",
    "traits": "git+http://github.com/enthought/traits.git#egg=traits",
}

# The following should match extras_require in setup.py but with package
# names compatible with EDM
extra_dependencies = {
    'pyside2': {
        'pygments',
    },
    'pyside6': {
        'pygments',
    },
    'pyqt5': {
        'pygments',
    },
    'pyqt6': {
        'pygments',
    },
    # XXX once wxPython 4 is available in EDM, we will want it here
    'wx': {
        'numpy',
    },
    'null': set(),
    # Toolkit-independent dependencies for demo testing.
    'examples': {
        'apptools',
        'chaco',
        'h5py',
        'numpy',
        'pandas',
    },
    # Optional dependencies for some editors
    'editors': {
        'numpy',
        'pandas',
    },
    # Test dependencies also applied to installation from PYPI
    'test': {
        'packaging',
    },
}

# Extra runtime dependencies
runtime_dependencies = {
    "3.6": {"pillow", "pytables"},
    "3.8": {"pillow_simd", "tables"},
}

# Dependencies for CI jobs using this file.
ci_dependencies = {
    "coverage",
    "flake8",
    "flake8_ets",
}

doc_dependencies = {
    "sphinx",
    "enthought_sphinx_theme",
    "pyface",
}

#: Paths to ignore in Sphinx-apidoc
doc_ignore = {
    "traitsui/qt4/*",
    "traitsui/wx/*",
    "*/tests",
}

environment_vars = {
    'pyside2': {'ETS_TOOLKIT': 'qt', 'QT_API': 'pyside2'},
    'pyside6': {'ETS_TOOLKIT': 'qt', 'QT_API': 'pyside6'},
    'pyqt5': {"ETS_TOOLKIT": "qt", "QT_API": "pyqt5"},
    'pyqt6': {"ETS_TOOLKIT": "qt", "QT_API": "pyqt6"},
    'wx': {'ETS_TOOLKIT': 'wx'},
    'null': {'ETS_TOOLKIT': 'null'},
}

# toolkit versions in EDM
edm_versions = {
    ('3.6', 'pyside2'),
    ('3.6', 'pyqt5'),
    ('3.8', 'pyside6'),
    ('3.8', 'pyqt6'),
}

# Location of documentation files
HERE = os.path.dirname(__file__)
DOCS_DIR = os.path.join(HERE, "docs")

# Location of news fragment for creating changelog.
NEWS_FRAGMENT_DIR = os.path.join(DOCS_DIR, "releases", "upcoming")

# Location of the Changelog file.
CHANGELOG_PATH = os.path.join(HERE, "CHANGES.txt")


def normalize(name):
    return name.replace("_", "-")


# Ensure that "-h" is supported for getting help.
CONTEXT_SETTINGS = dict(
    help_option_names=["-h", "--help"],
    token_normalize_func=normalize,
)


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
@click.option('--source/--no-source', default=False)
def install(runtime, toolkit, environment, editable, source):
    """Install project and dependencies into a clean EDM environment."""
    parameters = get_parameters(runtime, toolkit, environment)
    packages = (
        dependencies
        | extra_dependencies.get(toolkit, set())
        | extra_dependencies["test"]
        | extra_dependencies["examples"]
        | extra_dependencies["editors"]
        | runtime_dependencies[runtime]
        | ci_dependencies
    )

    # edm commands to setup the development environment
    commands = [
        "edm -c {config} environments create {environment} --force --version={runtime}",
        "edm -c {config} install -y -e {environment} " + " ".join(packages),
    ]

    if (runtime, toolkit) in edm_versions:
        commands.append(
            "edm -c {config} install -y -e {environment} {toolkit}"
        )
    elif toolkit == 'wx':
        if sys.platform != 'linux':
            commands.append("edm -c {config} run -e {environment} -- pip install wxPython")
        else:
            # XXX this is mainly for TravisCI workers; need a generic solution
            commands.append(
                "edm -c {config} run -e {environment} -- pip install -f https://extras.wxpython.org/wxPython4/extras/linux/gtk3/ubuntu-16.04/ wxPython"
            )
    elif toolkit == 'pyside6':
        # On Linux and macOS, some versions of PySide6 between 6.2.2 and 6.3.0
        # are unimportable on Python 3.6 and Python 3.7. See
        # https://bugreports.qt.io/browse/PYSIDE-1797. It may be possible to
        # remove this workaround once PySide6 6.3.1 or later is released.
        # Also there are currently issues with PySide 6.4
        if sys.platform in {'darwin', 'linux'}:
            commands.append(
                "edm -c {config} run -e {environment} -- pip install pyside6<6.2.2")
        else:
            commands.append('edm run -e {environment} -- pip install "pyside6<6.4.0"')
    elif toolkit != "null":
        commands.append("edm -c {config} run -e {environment} -- pip install {toolkit}")

    commands.extend(
        [
            "edm -c {config} run -e {environment} -- pip install --force-reinstall -r ci-src-requirements.txt --no-dependencies",
            "edm -c {config} run -e {environment} -- python setup.py clean --all",
        ]
    )

    click.echo("Creating environment '{environment}'".format(**parameters))
    execute(commands, parameters)

    if source:
        cmd_fmt = (
            "edm -c {config} plumbing remove-package --environment {environment} --force -c {config} "
        )
        commands = [
            cmd_fmt + dependency for dependency in source_dependencies.keys()
        ]
        execute(commands, parameters)
        source_pkgs = source_dependencies.values()
        # Without the --no-dependencies flag such that new dependencies on
        # main branch are brought in.
        commands = [
            "python -m pip install --force-reinstall {pkg}".format(pkg=pkg)
            for pkg in source_pkgs
        ]
        commands = [
            "edm -c {config} run -e {environment} -- " + command for command in commands
        ]
        execute(commands, parameters)

    # Always install local source again with no dependencies
    # to mitigate risk of testing against a distributed release.
    install_traitsui = (
        "edm -c {config} run -e {environment} -- "
        "pip install --force-reinstall  --no-dependencies "
    )
    if editable:
        install_traitsui += "--editable "
    install_traitsui += "."
    execute([install_traitsui], parameters)

    click.echo('Done install')


@cli.command()
@click.option('--runtime', default=DEFAULT_RUNTIME)
@click.option('--toolkit', default=DEFAULT_TOOLKIT)
@click.option('--environment', default=None)
def shell(runtime, toolkit, environment):
    """Create a shell into the EDM development environment
    (aka 'activate' it).

    """
    parameters = get_parameters(runtime, toolkit, environment)
    commands = [
        "edm -c {config} shell -e {environment}",
    ]
    execute(commands, parameters)


@cli.command()
@click.option('--runtime', default=DEFAULT_RUNTIME)
@click.option('--toolkit', default=DEFAULT_TOOLKIT)
@click.option('--environment', default=None)
def test(runtime, toolkit, environment):
    """Run the test suite in a given environment with the specified toolkit."""
    parameters = get_parameters(runtime, toolkit, environment)
    environ = environment_vars.get(toolkit, {}).copy()
    environ['PYTHONUNBUFFERED'] = "1"

    parameters["integrationtests"] = os.path.abspath("integrationtests")
    commands = [
        "edm -c {config} run -e {environment} -- python -X faulthandler -W default -m coverage run -p -m unittest discover -v traitsui",
        # coverage run prevents local images to be loaded for demo examples
        # which are not defined in Python packages. Run with python directly
        # instead.
        "edm -c {config} run -e {environment} -- python -X faulthandler -W default -m unittest discover -v {integrationtests}",
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
    """Remove a development environment."""
    parameters = get_parameters(runtime, toolkit, environment)
    commands = [
        "edm -c {config} run -e {environment} -- python setup.py clean",
        "edm -c {config} environments remove {environment} --purge -y",
    ]
    click.echo("Cleaning up environment '{environment}'".format(**parameters))
    execute(commands, parameters)
    click.echo('Done cleanup')


@cli.command()
@click.option('--runtime', default=DEFAULT_RUNTIME)
@click.option('--toolkit', default=DEFAULT_TOOLKIT)
def test_clean(runtime, toolkit):
    """Run tests in a clean environment, cleaning up afterwards"""
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
    """Update/Reinstall package into environment."""
    parameters = get_parameters(runtime, toolkit, environment)
    commands = ["edm -c {config} run -e {environment} -- python setup.py install"]
    click.echo("Re-installing in  '{environment}'".format(**parameters))
    execute(commands, parameters)
    click.echo('Done update')


@cli.command()
@click.option('--runtime', default=DEFAULT_RUNTIME)
@click.option('--toolkit', default=DEFAULT_TOOLKIT)
@click.option('--environment', default=None)
def docs(runtime, toolkit, environment):
    """Autogenerate documentation"""
    parameters = get_parameters(runtime, toolkit, environment)
    packages = ' '.join(doc_dependencies)
    ignore = " ".join(doc_ignore)
    commands = [
        "edm -c {config} install -y -e {environment} " + packages,
    ]
    click.echo(
        "Installing documentation tools in  '{environment}'".format(
            **parameters
        )
    )
    execute(commands, parameters)
    click.echo('Done installing documentation tools')

    click.echo(
        "Regenerating API docs in  '{environment}'".format(**parameters)
    )
    output_path = os.path.join("docs", "source", "api")
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    commands = [
        "edm -c {config} run -e {environment} -- sphinx-apidoc "
        "-e "
        "-M "
        "--no-toc "
        "-o " + output_path + " traitsui " + ignore
    ]
    execute(commands, parameters)
    click.echo("Done regenerating API docs")

    os.chdir('docs')
    command = (
        "edm -c {config} run -e {environment} -- sphinx-build -b html "
        "-d build/doctrees "
        "source "
        "build/html"
    )
    click.echo(
        "Building documentation in  '{environment}'".format(**parameters)
    )
    try:
        execute([command], parameters)
    finally:
        os.chdir('..')
    click.echo('Done building documentation')


@cli.command()
def test_all():
    """Run test_clean across all supported environment combinations."""
    failed_command = False
    for runtime, toolkits in supported_combinations.items():
        for toolkit in toolkits:
            args = [
                '--toolkit={}'.format(toolkit),
                '--runtime={}'.format(runtime),
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
@click.option(
    '--strict/--not-strict',
    default=False,
    help="Use strict configuration for flake8 [default: --not-strict]",
)
def flake8(runtime, toolkit, environment, strict):
    """Run a flake8 check in a given environment."""
    parameters = get_parameters(runtime, toolkit, environment)
    config = ""
    if strict:
        config = "--config=flake8_strict.cfg "
    commands = [
        "edm -c {config} run -e {environment} -- python -m flake8 " + config,
    ]
    execute(commands, parameters)


@cli.group("changelog")
@click.pass_context
def changelog(ctx):
    """Group of commands related to creating changelog."""

    ctx.obj = {
        # Mapping from news fragment type to their description in
        # the changelog.
        "type_to_description": {
            "feature": "Features",
            "bugfix": "Fixes",
            "deprecation": "Deprecations",
            "removal": "Removals",
            "doc": "Documentation changes",
            "test": "Test suite",
            "build": "Build System",
        }
    }


@changelog.command("create")
@click.pass_context
def create_news_fragment(ctx):
    """Create a news fragment for your PR."""

    pr_number = click.prompt('Please enter the PR number', type=int)
    type_ = click.prompt(
        "Choose a fragment type:",
        type=click.Choice(ctx.obj["type_to_description"]),
    )

    filepath = os.path.join(NEWS_FRAGMENT_DIR, f"{pr_number}.{type_}.rst")

    if os.path.exists(filepath):
        click.echo("FAILED: File {} already exists.".format(filepath))
        ctx.exit(1)

    content = click.prompt(
        "Describe the changes to the END USERS.\n"
        "Example: 'Remove subpackage xyz.'\n",
        type=str,
    )
    if not os.path.exists(NEWS_FRAGMENT_DIR):
        os.makedirs(NEWS_FRAGMENT_DIR)
    with open(filepath, "w", encoding="utf-8") as fp:
        fp.write(content + f" (#{pr_number})")

    click.echo("Please commit the file created at: {}".format(filepath))


@changelog.command("build")
@click.pass_context
def build_changelog(ctx):
    """Build Changelog created from all the news fragments."""
    # This is a rather simple first-cut generation of the changelog.
    # It removes the laborious concatenation, but the end results might
    # still require some tweaking.
    contents = []

    # Collect news fragment files as we go, and then optionally remove them.
    handled_file_paths = []

    for type_, description in ctx.obj["type_to_description"].items():
        pattern = os.path.join(NEWS_FRAGMENT_DIR, f"*.{type_}.rst")
        file_paths = sorted(glob.glob(pattern))

        if file_paths:
            contents.append("")
            contents.append(description)
            contents.append("-" * len(description))

        for filename in file_paths:
            with open(filename, "r", encoding="utf-8") as fp:
                contents.append("* " + fp.read())
            handled_file_paths.append(filename)

    # Prepend content to the changelog file.

    with open(CHANGELOG_PATH, "r", encoding="utf-8") as fp:
        original_changelog = fp.read()

    with open(CHANGELOG_PATH, "w", encoding="utf-8") as fp:
        if contents:
            print(*contents, sep="\n", file=fp)
        fp.write(original_changelog)

    click.echo(f"Changelog is updated. Please review it at {CHANGELOG_PATH}")

    # Optionally clean up collected news fragments.
    should_clean = click.confirm("Do you want to remove the news fragments?")
    if should_clean:
        for file_path in handled_file_paths:
            os.remove(file_path)

        # Report any leftover for developers to inspect.
        leftovers = sorted(glob.glob(os.path.join(NEWS_FRAGMENT_DIR, "*")))
        if leftovers:
            click.echo("These files are not collected:")
            click.echo("\n  ".join([""] + leftovers))

    click.echo("Done")


# ----------------------------------------------------------------------------
# Utility routines
# ----------------------------------------------------------------------------


def get_parameters(runtime, toolkit, environment, config=EDM_CONFIG_LOCATION):
    """Set up parameters dictionary for format() substitution"""
    parameters = {
        'runtime': runtime,
        'toolkit': toolkit,
        'environment': environment,
        'config': config,
    }
    if toolkit not in supported_combinations[runtime]:
        msg = (
            "Python {runtime} and toolkit {toolkit} not supported by "
            + "test environments"
        )
        raise RuntimeError(msg.format(**parameters))
    if environment is None:
        parameters['environment'] = 'traitsui-test-{runtime}-{toolkit}'.format(
            **parameters
        )
    return parameters


@contextmanager
def do_in_tempdir(files=(), capture_files=()):
    """Create a temporary directory, cleaning up after done.

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
            subprocess.check_call(
                [arg.format(**parameters) for arg in command.split()]
            )
        except subprocess.CalledProcessError as exc:
            click.echo(str(exc))
            sys.exit(1)


if __name__ == '__main__':
    cli(prog_name="python etstool.py")
