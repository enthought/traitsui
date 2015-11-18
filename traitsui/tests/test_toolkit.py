
from contextlib import contextmanager
import warnings

from traits.testing.unittest_tools import unittest
from traits.trait_base import ETSConfig
import traitsui.toolkit


@contextmanager
def clear_toolkit():
    """ If a toolkit has been selected, clear it, resetting on exit """
    old_ETS_toolkit = ETSConfig._toolkit
    old_traitsui_toolkit = traitsui.toolkit._toolkit
    ETSConfig._toolkit = ''
    traitsui.toolkit._toolkit = None
    try:
        yield
    finally:
        ETSConfig._toolkit = old_ETS_toolkit
        traitsui.toolkit._toolkit = old_traitsui_toolkit


class TestToolkit(unittest.TestCase):

    def test_toolkit_warning(self):
        # reset toolkit state
        with clear_toolkit():
            with warnings.catch_warnings(record=True) as ws:
                # Cause all warnings to always be triggered.
                warnings.simplefilter("always")
                # Trigger a warning.
                tk = traitsui.toolkit.toolkit()
                # Verify some things
                self.assertGreaterEqual(len(ws), 1)
                self.assertTrue(any(issubclass(w.category, DeprecationWarning)
                                    for w in ws))
                self.assertTrue(any("Default toolkit" in str(w.message)
                                    for w in ws))
