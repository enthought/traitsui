# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import setuptools


INCLUDES = [
    "etsdemo", "etsdemo.*",
]
PACKAGES = setuptools.find_packages(include=INCLUDES)


def get_long_description():
    """ Read long description from README.rst. """
    with open("README.rst", "r", encoding="utf-8") as readme:
        return readme.read()


if __name__ == "__main__":
    install_requires = [
        "configobj",
        "docutils",
        "traits",
        "traitsui",
        "pyface",
    ]
    extras_require = {
        "wx": ["wxpython>=4", "numpy"],
        "pyqt5": ["pyqt>=5", "pygments"],
        "pyside2": ["pyside2", "shiboken2", "pygments"],
    }
    setuptools.setup(
        name="etsdemo",
        version="0.0.1",
        url="https://github.com/enthought/traitsui",
        author="Enthought",
        author_email="info@enthought.com",
        classifiers=[c.strip() for c in """\
            Development Status :: 1 - Planning
            Intended Audience :: Developers
            Intended Audience :: Science/Research
            License :: OSI Approved :: BSD License
            Operating System :: MacOS
            Operating System :: Microsoft :: Windows
            Operating System :: OS Independent
            Operating System :: POSIX
            Operating System :: Unix
            Programming Language :: Python
            Programming Language :: Python :: 3.5
            Programming Language :: Python :: 3.6
            Programming Language :: Python :: 3.7
            Programming Language :: Python :: 3.8
            Topic :: Scientific/Engineering
            Topic :: Software Development
            """.splitlines() if len(c.strip()) > 0],
        description="Enthought Tool Suite Demo Application",
        long_description=get_long_description(),
        long_description_content_type="text/x-rst",
        packages=PACKAGES,
        install_requires=install_requires,
        extras_require=extras_require,
        license="BSD",
        python_requires=">=3.5",
    )
