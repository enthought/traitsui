# Copyright (c) 2008-2013 by Enthought, Inc.
# All rights reserved.
from os.path import join

from setuptools import setup, find_packages


info = {}
execfile(join('traitsui', '__init__.py'), info)


setup(
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
    package_data = dict(traitsui=['image/library/*.zip',
                                  'wx/images/*', 'qt4/images/*']),
    packages = find_packages(),
    platforms = ["Windows", "Linux", "Mac OS-X", "Unix", "Solaris"],
    zip_safe = False,
)
