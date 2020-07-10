# ------------------------------------------------------------------------------
#
#  Copyright (c) 2005-2013, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
#  Author: David C. Morrill
#  Date:   10/07/2004
#
# ------------------------------------------------------------------------------


try:
    from traitsui._version import full_version as __version__
except ImportError:
    __version__ = "not-built"

__requires__ = ["traits", "pyface>=6.0.0"]
__extras_require__ = {
    "wx": ["wxpython>=4", "numpy"],
    "pyqt": ["pyqt>=4.10", "pygments"],
    "pyqt5": ["pyqt>=5", "pygments"],
    "pyside": ["pyside>=1.2", "pygments"],
    "demo": ["configobj", "docutils"],
    "test": ["packaging"],
}


# ============================= Test Loader ==================================
def load_tests(loader, standard_tests, pattern):
    """ Custom test loading function that enables test filtering using regex
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
    from os import environ
    from os.path import dirname
    from traitsui.tests._tools import filter_tests
    from unittest import TestSuite

    # Make sure the right toolkit is up and running before importing tests
    from traitsui.toolkit import toolkit
    toolkit()

    this_dir = dirname(__file__)
    package_tests = loader.discover(start_dir=this_dir, pattern=pattern)

    exclusion_pattern = environ.get("EXCLUDE_TESTS", None)
    if exclusion_pattern is None:
        return package_tests

    filtered_package_tests = TestSuite()
    for test_suite in package_tests:
        filtered_test_suite = filter_tests(test_suite, exclusion_pattern)
        filtered_package_tests.addTest(filtered_test_suite)

    return filtered_package_tests
