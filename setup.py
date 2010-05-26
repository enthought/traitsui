#!/usr/bin/env python
#
# Copyright (c) 2008-2010 by Enthought, Inc.
# All rights reserved.

"""
PyQt backend for Traits and TraitsGUI (Pyface).

The TraitsBackendQt project contains an implementation of TraitsGUI using PyQt.
It provides Qt-based support for visualization and editing of Traits-based
objects.

Prerequisites
-------------
You must have the following libraries installed before building or installing
TraitsBackendQt:
    
* `PyQt <http://pypi.python.org/pypi/PyQt/3.15>`_
* `setuptools <http://pypi.python.org/pypi/setuptools/0.6c8>`_.

"""


from setuptools import setup, find_packages

# FIXME: This works around a setuptools bug which gets setup_data.py metadata
# from incorrect packages. Ticket #1592
#from setup_data import INFO
setup_data = dict(__name__='', __file__='setup_data.py')
execfile('setup_data.py', setup_data)
INFO = setup_data['INFO']

# Pull the description values for the setup keywords from our file docstring.
DOCLINES = __doc__.split("\n")


setup(
    author = 'Phil Thompson',
    author_email = 'phil@riverbankcomputing.co.uk',
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
        Programming Language :: Python
        Topic :: Scientific/Engineering
        Topic :: Software Development
        Topic :: Software Development :: Libraries
        """.splitlines() if len(c.split()) > 0],
    description = DOCLINES[1],
    extras_require = INFO['extras_require'],
    include_package_data = True,
    install_requires = INFO['install_requires'],
    license = 'BSD',
    long_description = '\n'.join(DOCLINES[3:]),
    maintainer = 'ETS Developers',
    maintainer_email = 'enthought-dev@enthought.com',
    name = INFO['name'],
    namespace_packages   = [
        "enthought",
        "enthought.pyface",
        "enthought.pyface.ui",
        "enthought.traits",
        "enthought.traits.ui",
        ],
    package_data = {
        '': ['images/*'],
        },
    packages = find_packages(),
    platforms = ["Windows", "Linux", "Mac OS-X", "Unix", "Solaris"],
    tests_require = [
        'nose >= 0.10.3',
        ],
    # test_suite = 'nose.collector',
    url = 'http://code.enthought.com/projects/traits_gui',
    version = INFO['version'],
    zip_safe = False,
    )
