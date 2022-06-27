# (C) Copyright 2004-2022 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!


try:
    from traitsui._version import full_version as __version__
except ImportError:
    __version__ = "not-built"

__requires__ = ["traits>=6.2.0", "pyface>=7.4.1"]
__extras_require__ = {
    "wx": ["wxpython>=4", "numpy"],
    "pyqt": ["pyqt>=4.10", "pygments"],
    "pyqt5": ["pyqt5", "pygments"],
    "pyside2": ["pyside2", "pygments"],
    "pyside6": [
        # Avoid https://bugreports.qt.io/browse/PYSIDE-1797, which causes
        # some versions of PySide6 to be unimportable on Python 3.6 and 3.7.
        "pyside6!=6.2.2,!=6.2.2.1,!=6.2.3,!=6.2.4,!=6.3.0; python_version<'3.8'",
        "pyside6; python_version>='3.8'",
        "pygments",
    ],
    "docs": ["enthought-sphinx-theme", "sphinx", "sphinx-copybutton"],
    "demo": [
        # to be deprecated, see enthought/traitsui#950
        "configobj",
        "docutils",
    ],
    "examples": [
        # Dependencies for examples
        "apptools",
        "h5py",
        "numpy",
        "pandas",
        "pillow",
        "tables",
    ],
    "editors": [
        # Optional dependencies for certain editors which may not be needed by
        # projects. If they are absent, ``traitsui.api``` should still be
        # importable and the relevant tests should be skipped.
        "numpy",  # For ArrayEditor and DataFrameEditor
        "pandas",  # For DataFrameEditor
    ],
    "test": [
        # Dependencies for running test suites.
        "packaging",
        "numpy",
    ],
}


# ============================= Test Loader ==================================
def load_tests(loader, standard_tests, pattern):
    """Custom test loading function that enables test filtering using regex
    exclusion pattern.

    Parameters
    ----------
    loader : unittest.TestLoader
        The instance of test loader
    standard_tests : unittest.TestSuite
        Tests that would be loaded by default from this module (no tests)
    pattern : str
        An inclusion pattern used to match test files (test*.py default)

    Returns
    -------
    filtered_package_tests : unittest.TestSuite
        TestSuite representing all package tests that did not match specified
        exclusion pattern.
    """
    from os.path import dirname
    from unittest import TestSuite
    from traits.etsconfig.api import ETSConfig
    from traitsui.tests._tools import filter_tests

    # Make sure the right toolkit is up and running before importing tests
    from traitsui.toolkit import toolkit

    toolkit()

    if ETSConfig.toolkit.startswith("qt"):
        exclusion_pattern = "wx"
    elif ETSConfig.toolkit == "wx":
        exclusion_pattern = "qt"
    else:
        exclusion_pattern = "(wx|qt)"

    this_dir = dirname(__file__)
    package_tests = loader.discover(start_dir=this_dir, pattern=pattern)

    if exclusion_pattern is None:
        return package_tests

    filtered_package_tests = TestSuite()
    for test_suite in package_tests:
        filtered_test_suite = filter_tests(test_suite, exclusion_pattern)
        filtered_package_tests.addTest(filtered_test_suite)

    return filtered_package_tests
