from contextlib import contextmanager
import os
from shutil import rmtree, copytree, copy as copyfile
from tempfile import mkdtemp

from invoke import task
from invoke.exceptions import Failure


supported_combinations = {
    '2.7': {'pyside', 'pyqt', 'wx', 'null'},
    '3.5': {'pyqt', 'null'},
}

dependencies = {
    "numpy",
    "pandas",
    "pygments",
    "traits",
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
def install(ctx, runtime='3.5', toolkit='null', environment=None, edm='edm'):
    """ Install traitsui and dependencies into a clean EDM environment. """
    if toolkit not in supported_combinations.get(runtime, set()):
        msg = "Python {} and toolkit {} not supported by test environments"
        raise RuntimeError(msg.format(runtime, toolkit))

    if environment is None:
        environment = 'traitsui-test-{}-{}'.format(runtime, toolkit)

    packages = dependencies | extra_dependencies.get(toolkit, set())

    print("Creating environment '{}'".format(environment))
    ctx.run("{} install -y -e '{}' --version '{}' {}".format(
        edm, environment, runtime, ' '.join(packages)))

    # use current master of pyface
    clone_into_env(ctx, environment, 'pyface', edm=edm)

    # install traitsui from this directory
    run_in_env(ctx, environment, "python setup.py install", edm=edm)


@task
def test(ctx, runtime='3.5', toolkit='null', environment=None, edm='edm'):
    """ Run the test suite in a given environment with the specified toolkit """
    if toolkit not in supported_combinations.get(runtime, set()):
        msg = "Python {} and toolkit {} not supported by test environments"
        raise RuntimeError(msg.format(runtime, toolkit))

    if environment is None:
        environment = 'traitsui-test-{}-{}'.format(runtime, toolkit)

    try:
        # simple test to see if designated environment exists
        ctx.run("{} prefix -e '{}'".format(edm, environment))
    except Failure:
        # environment doesn't exist, so create it and populate
        print("Environment not found, creating...")
        install(ctx, runtime, toolkit, environment, edm)

    envvars = environment_vars.get(toolkit, {}).copy()

    # run tests
    with do_in_tempdir(files=['.coveragerc'], capture_files=['.coverage']):
        run_in_env(ctx, environment,
                   "coverage run -m nose.core -v traitsui.tests",
                   envvars, edm)
        if toolkit in {'pyqt', 'pyside'}:
            run_in_env(ctx, environment,
                       "coverage run -m nose.core -v traitsui.qt4.tests",
                       envvars, edm)
    print('Done')


@task
def cleanup(ctx, runtime='3.5', toolkit='null', environment=None, edm='edm'):
    if toolkit not in supported_combinations.get(runtime, set()):
        msg = "Python {} and toolkit {} not supported by test environments"
        raise RuntimeError(msg.format(runtime, toolkit))

    if environment is None:
        environment = 'traitsui-test-{}-{}'.format(runtime, toolkit)

    env_path = ctx.run("{} prefix -e '{}'".format(edm, environment)).stdout
    try:
        ctx.run("{} environments remove --purge -y '{}'".format(
            edm, environment))
    except Failure:
        print("Force removing environment dir: {}".format(env_path))
        ctx.run("rm -rf {}".format(env_path))

    print('Done')


@task
def test_clean(ctx, runtime='3.5', toolkit='null', edm='edm'):
    """ Run tests in a clean environment, cleaning up afterwards """
    try:
        install(ctx, runtime, toolkit, edm=edm)
        test(ctx, runtime, toolkit, edm=edm)
    finally:
        cleanup(ctx, runtime, toolkit, edm=edm)


@task
def test_all(ctx):

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


def run_in_env(ctx, environment, command, envvars={}, edm='edm'):
    """ Run a shell command in an edm environment

    Parameters
    ----------
    ctx : Invoke context
        The Invoke context with the run command.
    environment : str
        The name of the edm environment to run the command in.
    command : str
        The command to run.
    envvars : dict
        Optional additional environment variables for running the command.
    """
    ctx.run("{} run -e '{}' -- {}".format(edm, environment, command),
            env=envvars)


def clone_into_env(ctx, environment, project, organization='enthought',
                   branch='master', edm='edm'):
    """ Clone a Python github repo and isntall into an edm environment.

    This is very simplistic.  It assumes that the repo is public and that the
    project has a top-level setup.py that we can invoke with the "install"
    command.

    Parameters
    ----------
    ctx : Invoke context
        The Invoke context with the run command.
    environment : str
        The name of the edm environment to run the command in.
    project : str
        The name of the project we wish to clone.
    organization : str
        The organization that owns the repo.
    branch: str
        The branch to check-out.
    """
    with do_in_tempdir():
        ctx.run("git clone 'https://github.com/{}/{}.git'".format(
            organization, project))
        if branch != "master":
            ctx.run("git checkout '{}'".format(branch))
        os.chdir(project)
        run_in_env(ctx, environment, 'python setup.py install', edm=edm)
