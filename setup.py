#!/usr/bin/env python
#
# Copyright (c) 2008 by Enthought, Inc.
# All rights reserved.
#

"""
WxPython backend for Traits and TraitsGUI (Pyface).

The TraitsBackendWX project contains an implementation of TraitsGUI using
wxPython. It provides wx-based support for visualization and editing of
Traits-based objects.

Prerequisite
------------
You must have the following libraries installed before building or installing
TraitsBackendWX:
    
* `wxPython <http://www.wxpython.org/>`_ version 2.8 or later
* `setuptools <http://pypi.python.org/pypi/setuptools/0.6c8>`_.

"""


from setuptools import setup, find_packages


# Pull the description values for the setup keywords from our file docstring.
DOCLINES = __doc__.split("\n")


# Function to convert simple ETS project names and versions to a requirements
# spec that works for both development builds and stable builds.  Allows
# a caller to specify a max version, which is intended to work along with
# Enthought's standard versioning scheme -- see the following write up:
#    https://svn.enthought.com/enthought/wiki/EnthoughtVersionNumbers
def etsdep(p, min, max=None, literal=False):
    require = '%s >=%s.dev' % (p, min)
    if max is not None:
        if literal is False:
            require = '%s, <%s.a' % (require, max)
        else:
            require = '%s, <%s' % (require, max)
    return require


# Declare our ETS project dependencies.
APPTOOLS = etsdep('AppTools', '3.0.1')
ENTHOUGHTBASE_UI = etsdep('EnthoughtBase[ui]', '3.0.1')
ETSDEVTOOLS_DEVELOPER = etsdep('ETSDevTools[developer]', '3.0.1')
TRAITS = etsdep('Traits', '3.0.3')
TRAITSGUI_DOCK = etsdep('TraitsGUI[dock]', '3.0.3')

# The following soft dependencies are handled with appropriate try...except
# wrappers.
# AppTools -- used in traits.ui.wx.dnd_editor.py
# ETSDevTools -- used in traits.ui.wx.helper.py and view_application.py


setup(
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
        Programming Language :: Python
        Topic :: Scientific/Engineering
        Topic :: Software Development
        Topic :: Software Development :: Libraries
        """.splitlines() if len(c.split()) > 0],
    dependency_links = [
        'http://code.enthought.com/enstaller/eggs/source',
        ],
    description = DOCLINES[1],
    extras_require = {

        # Extra denoting that complete drag and drop support for files and
        # named bindings should be installed:
        'dnd': [
            APPTOOLS,
            ],

        # Extra denoting that complete developer debug support for the ETS FBI
        # debugger should be installed:
        'debug': [
            ETSDEVTOOLS_DEVELOPER,
            ],

        # All non-ets dependencies should be in this extra to ensure users can
        # decide whether to require them or not.
        'nonets': [
            #'wx',  # fixme: not available as an egg on all platforms.
            ],
        },
    include_package_data = True,
    install_requires = [
        ENTHOUGHTBASE_UI,
        TRAITSGUI_DOCK,
        TRAITS,
        ],
    license = 'BSD',
    long_description = '\n'.join(DOCLINES[3:]),
    maintainer = 'ETS Developers',
    maintainer_email = 'enthought-dev@enthought.com',
    name = 'TraitsBackendWX',
    namespace_packages = [
        'enthought',
        'enthought.pyface',
        'enthought.pyface.ui',
        'enthought.traits',
        'enthought.traits.ui',
        ],
    packages = find_packages(),
    platforms = ["Windows", "Linux", "Mac OS-X", "Unix", "Solaris"],
    tests_require = [
        'nose >= 0.10.3',
        ],
    # test_suite = 'nose.collector',
    url = 'http://code.enthought.com/projects/traits_gui',
    version = '3.0.3',
    zip_safe = False,
    )
