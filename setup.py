# Copyright (c) 2008-2015 by Enthought, Inc.
# All rights reserved.

import os
import re
import subprocess

from setuptools import setup, find_packages
from io import open

MAJOR = 6
MINOR = 1
MICRO = 0

IS_RELEASED = True

VERSION = '%d.%d.%d' % (MAJOR, MINOR, MICRO)


def read_module(module, package='traitsui'):
    """ Read a simple .py file from traitsui in a safe way.

    It would be simpler to import the file, but that can be problematic in an
    unknown system, so we exec the file instead and extract the variables.

    This will fail if things get too complex in the file being read, but is
    sufficient to get version and requirements information.
    """
    base_dir = os.path.dirname(__file__)
    module_name = package + '.' + module
    path = os.path.join(base_dir, package, module+'.py')
    with open(path, 'r', encoding='utf-8') as fp:
        code = compile(fp.read(), module_name, 'exec')
    context = {}
    exec(code, context)
    return context


# Return the git revision as a string
def git_version():
    def _minimal_ext_cmd(cmd):
        # construct minimal environment
        env = {}
        for k in ['SYSTEMROOT', 'PATH']:
            v = os.environ.get(k)
            if v is not None:
                env[k] = v
        # LANGUAGE is used on win32
        env['LANGUAGE'] = 'C'
        env['LANG'] = 'C'
        env['LC_ALL'] = 'C'
        out = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, env=env,
        ).communicate()[0]
        return out

    try:
        out = _minimal_ext_cmd(['git', 'describe', '--tags'])
    except OSError:
        out = ''

    git_description = out.strip().decode('ascii')
    expr = r'.*?\-(?P<count>\d+)-g(?P<hash>[a-fA-F0-9]+)'
    match = re.match(expr, git_description)
    if match is None:
        git_revision, git_count = 'Unknown', '0'
    else:
        git_revision, git_count = match.group('hash'), match.group('count')

    return git_revision, git_count


def write_version_py(filename=None):
    template = u"""\
# THIS FILE IS GENERATED FROM TRAITS SETUP.PY
version = '{version}'
full_version = '{full_version}'
git_revision = '{git_revision}'
is_released = {is_released}

if not is_released:
    version = full_version
"""
    if filename is None:
        # correctly generate relative path
        base_dir = os.path.dirname(__file__)
        filename = os.path.join(base_dir, 'traitsui', '_version.py')

    # Adding the git rev number needs to be done inside
    # write_version_py(), otherwise the import of traits._version messes
    # up the build under Python 3.
    fullversion = VERSION
    if os.path.exists('.git'):
        git_rev, dev_num = git_version()
    elif os.path.exists(filename):
        # must be a source distribution, use existing version file
        try:
            data = read_module('_version')
            git_rev = data['git_revision']
            fullversion_source = data['full_version']
        except Exception:
            print("Unable to read git_revision. Try removing "
                  "traitsui/_version.py and the build directory "
                  "before building.")
            raise

        match = re.match(r'.*?\.dev(?P<dev_num>\d+)', fullversion_source)
        if match is None:
            dev_num = '0'
        else:
            dev_num = match.group('dev_num')
    else:
        git_rev = 'Unknown'
        dev_num = '0'

    if not IS_RELEASED:
        fullversion += '.dev{0}'.format(dev_num)

    with open(filename, "w", encoding='ascii') as fp:
        fp.write(template.format(version=VERSION,
                                 full_version=fullversion,
                                 git_revision=git_rev,
                                 is_released=IS_RELEASED))

    return fullversion


if __name__ == "__main__":
    __version__ = write_version_py()
    data = read_module('__init__')
    __requires__ = data['__requires__']
    __extras_require__ = data['__extras_require__']

    def additional_commands():
        try:
            from sphinx.setup_command import BuildDoc
        except ImportError:
            return {}
        else:
            return {'documentation': BuildDoc}

    setup(
        name='traitsui',
        version=__version__,
        author='David C. Morrill, et. al.',
        author_email='dmorrill@enthought.com',
        classifiers=[c.strip() for c in """\
            Development Status :: 5 - Production/Stable
            Intended Audience :: Developers
            Intended Audience :: Science/Research
            License :: OSI Approved :: BSD License
            Operating System :: MacOS
            Operating System :: Microsoft :: Windows
            Operating System :: OS Independent
            Operating System :: POSIX
            Operating System :: Unix
            Programming Language :: Python
            Programming Language :: Python :: 2.6
            Programming Language :: Python :: 2.7
            Programming Language :: Python :: 3.4
            Programming Language :: Python :: 3.5
            Topic :: Scientific/Engineering
            Topic :: Software Development
            Topic :: Software Development :: Libraries
            """.splitlines() if len(c.strip()) > 0],
        description='traitsui: traits-capable user interfaces',
        long_description=open('README.rst').read(),
        url='http://docs.enthought.com/traitsui',
        download_url='https://github.com/enthought/traitsui',
        install_requires=__requires__,
        extras_require=__extras_require__,
        license='BSD',
        maintainer='ETS Developers',
        maintainer_email='enthought-dev@enthought.com',
        package_data=dict(traitsui=['image/library/*.zip', 'images/*',
                                    'wx/images/*', 'qt4/images/*']),
        packages=find_packages(),
        entry_points={
            'traitsui.toolkits': [
                'qt4 = traitsui.qt4:toolkit',
                'wx = traitsui.wx:toolkit',
                'qt = traitsui.qt4:toolkit',
                'null = traitsui.null:toolkit',
            ],
        },
        platforms=["Windows", "Linux", "Mac OS-X", "Unix", "Solaris"],
        zip_safe=False,
    )
