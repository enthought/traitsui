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


@contextmanager
def do_in_tempdir():
    path = mkdtemp()
    old_path = os.getcwd()
    os.chdir(path)
    try:
        yield path
    finally:
        os.chdir(old_path)
        rmtree(path)


def run_in_env(ctx, environment, command):
    ctx.run("edm run -e '{}' -- {}".format(environment, command))


def clone_into_env(ctx, environment, project, organization='enthought',
                   branch='master'):
    with do_in_tempdir():
        ctx.run("git clone 'https://github.com/{}/{}.git'".format(
            organization, project))
        if branch != "master":
            ctx.run("git checkout '{}'".format(branch))
        os.chdir(project)
        run_in_env(ctx, environment, 'python setup.py install')


@task
def test(ctx, runtime='3.5', toolkit='null', environment=None):
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
    ctx.run("edm install -y -e '{}' --version '{}' {}".format(
        environment, runtime, ' '.join(packages)))
    try:
        # use current master of pyface
        clone_into_env(ctx, environment, 'pyface')

        # install install traitsui
        run_in_env(ctx, environment, "python setup.py install")

        os.environ.update({
            "ETS_TOOLKIT": ets_toolkit,
            "COVERAGE_FILE": os.path.join(os.getcwd(), '.coverage')
        })
        # run tests
        with do_in_tempdir():
            run_in_env(ctx, environment,
                       "coverage run -m nose.core -v traitsui.tests")
            if ets_toolkit == 'qt4':
                run_in_env(ctx, environment,
                           "coverage run -m nose.core -v traitsui.qt4.tests")
    finally:
        try:
            ctx.run("edm environments remove --purge -y '{}'".format(environment))
        except Failure as exc:
            env_path = os.path.join('~', '.edm', 'envs', environment)
            print("Removing {}".format(env_path))
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
