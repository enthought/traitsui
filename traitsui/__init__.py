# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

def __getattr__(name):
    """Handle deprecated attributes."""
    if name == "__version__":
        try:
            from importlib.metadata import version
        except ImportError:
            from importlib_metadata import version
        from warnings import warn

        warn(
            f"traitsui.{name} is deprecated, "
            f"use impportlib.metadata.version('traitsui') ",
            DeprecationWarning,
        )
        return version('traitsui')
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


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
