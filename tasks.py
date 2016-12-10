from contextlib import contextmanager
import os
from shutil import rmtree
from tempfile import mkdtemp

from invoke import task
from invoke.exceptions import Failure


DEPENDENCIES = [
    "numpy",
    "pandas",
    "pygments",
    "traits",
    "nose",
    "coverage",
]


supported_combinations = {
    '2.7': {'pyside', 'pyqt', 'wxpython', 'null'},
    '3.5': {'pyqt', 'null'},
}

@task
def test(ctx, runtime='3.5', toolkit='null', environment=None, edm='edm'):
    """ Run the test suite in a given runtime with the specified toolkit """
    if toolkit not in supported_combinations.get(runtime, set()):
        msg = "Python {} and toolkit {} not supported by test environments"
        raise RuntimeError(msg.format(runtime, toolkit))

    if environment is None:
        environment = 'traitsui-test-{}-{}'.format(runtime, toolkit)

    packages = DEPENDENCIES[:]

    if toolkit == 'pyqt':
        packages.append('pyqt')
        ets_toolkit = 'qt4'
    elif toolkit == 'pyside':
        packages.append('pyside')
        ets_toolkit = 'qt4'
    elif toolkit == 'wx':
        packages.append('wxpython')
        ets_toolkit = 'wx'
    else:
        ets_toolkit = 'null'

    print("Creating environment '{}'".format(environment))
    ctx.run("{} install -y -e '{}' --version '{}' {}".format(
        edm, environment, runtime, ' '.join(packages)))
    try:
        # use current master of pyface
        clone_into_env(ctx, environment, 'pyface', edm=edm)

        # install install traitsui
        run_in_env(ctx, environment, "python setup.py install", edm=edm)

        envvar = {
            "ETS_TOOLKIT": ets_toolkit,
            "COVERAGE_FILE": os.path.join(os.getcwd(), '.coverage')
        }
        # run tests
        with do_in_tempdir():
            run_in_env(
                ctx, environment,
                "coverage run -m nose.core -v traitsui.tests", envvar, edm)
            if ets_toolkit == 'qt4':
                run_in_env(
                    ctx, environment,
                    "coverage run -m nose.core -v traitsui.qt4.tests", envvar,
                    edm)
    finally:
        try:
            env_path = ctx.run("{} prefix -e '{}'".format(edm, environment)).stdout
            ctx.run("{} environments remove --purge -y '{}'".format(edm,environment))
        except Failure:
            print("Force removing environment dir: {}".format(env_path))
            ctx.run("rm -rf {}".format(env_path))

        print('Done')

@task
def test_all(ctx):
    for runtime, toolkits in supported_combinations.items():
        for toolkit in toolkits:
            try:
                test(ctx, runtime, toolkit)
            except Exception as exc:
                # continue to next runtime
                print(exc)

# ----------------------------------------------------------------------------
# Utility routines
# ----------------------------------------------------------------------------

@contextmanager
def do_in_tempdir():
    """ Create a temporary directory, cleaning up after done.

    Creates the temporary directory, and changes into it.  On exit returns to
    original directory and removes temporary dir.
    """
    path = mkdtemp()
    old_path = os.getcwd()
    os.chdir(path)
    try:
        yield path
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
