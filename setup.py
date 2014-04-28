#-------------------------------------------------------------------------------
# Copyright (c) 2008-2013 by Enthought, Inc.
# All rights reserved.
#-------------------------------------------------------------------------------
from os.path import join

from setuptools import setup, find_packages

# pylint: disable=C0103,W0122
info = {}
traitsui_init = join('traitsui', '__init__.py')
exec(compile(open(traitsui_init).read(), traitsui_init, 'exec'), info)


setup(
    # pylint: disable=C0326
    name = 'traitsui',
    version = info['__version__'],
    author = 'David C. Morrill, et. al.',
    author_email = 'dmorrill@enthought.com',
    classifiers = [c.strip() for c in """\
        Development Status :: 5 - Production/Stable
        Intended Audience :: Developers
        Intended Audience :: Science/Research
        License :: OSI Approved :: BSD License
        Operating System :: MacOS
        Operating System :: Microsoft :: Windows
        Operating System :: OS Independent
        Operating System :: POSIX
        Operating System :: Unix
        Programming Language :: C
        Programming Language :: Python
        Topic :: Scientific/Engineering
        Topic :: Software Development
        Topic :: Software Development :: Libraries
        """.splitlines() if len(c.strip()) > 0],
    description = 'traitsui: traits-capable user interfaces',
    long_description = open('README.rst').read(),
    url = 'https://github.com/enthought/traitsui',
    download_url = ('http://www.enthought.com/repo/ets/traitsui-%s.tar.gz' %
                    info['__version__']),
    install_requires = info['__requires__'],
    license = 'BSD',
    maintainer = 'ETS Developers',
    maintainer_email = 'enthought-dev@enthought.com',
    package_data = {
        "traitsui": ['image/library/*.zip', 'wx/images/*', 'qt4/images/*']
    },
    packages = find_packages(),
    platforms = ["Windows", "Linux", "Mac OS-X", "Unix", "Solaris"],
    zip_safe = False,
    use_2to3 = True,
    use_2to3_exclude_fixers = ['lib2to3.fixes.fix_next']   # traits_listener.ListenerItem has a trait *name* which gets wrongly renamed
)
