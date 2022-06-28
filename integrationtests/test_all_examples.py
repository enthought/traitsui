# (C) Copyright 2004-2022 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Tests for demo and tutorial examples.
"""

import contextlib
import io
import os
import sys
import traceback
import unittest
from unittest import mock

import pkg_resources
from traits.api import HasTraits

from traitsui.tests._tools import (
    BaseTestMixin,
    is_qt,
    is_qt5,
    is_qt6,
    is_wx,
    process_cascade_events,
    requires_toolkit,
    ToolkitName,
)
from traitsui.testing.api import UITester

# This test file is not distributed nor is it in a package.
HERE = os.path.dirname(__file__)


class ExampleSearcher:
    """This object collects and reports example files to be tested."""

    def __init__(self, source_dirs):
        """
        Parameters
        ----------
        source_dirs : list of str
            List of directory paths from which Python files will be collected.
        """
        self.source_dirs = source_dirs
        self.files_may_be_skipped = {}

    def skip_file_if(self, filepath, condition, reason):
        """Mark a file to be skipped for a given condition.

        Parameters
        ----------
        filepath : str
            Path of the file which may be skipped from tests.
        condition: callable() -> bool
            The condition for skipping a file.
        reason : str
            Reason for skipping the file.
        """
        filepath = os.path.abspath(filepath)
        self.files_may_be_skipped[filepath] = (condition, reason)

    def is_skipped(self, filepath):
        """Return if the Python file should be skipped in test.

        Parameters
        ----------
        path : str
            Path to a file.

        Returns
        -------
        skipped : bool
            True if the file should be skipped.
        reason : str
            Reason why it should be skipped.
        """
        path = os.path.abspath(filepath)
        if path not in self.files_may_be_skipped:
            return False, ""
        condition, reason = self.files_may_be_skipped[path]
        return condition(), reason

    def validate(self):
        """Validate configuration. Currently this checks all files that may
        be skipped still exist.
        """
        for filepath in self.files_may_be_skipped:
            if not os.path.exists(filepath):
                raise RuntimeError("{} does not exist.".format(filepath))

    @staticmethod
    def _is_python_file(path):
        """Return true if the given path is (public) non-test Python file."""
        _, basename = os.path.split(path)
        _, ext = os.path.splitext(basename)
        return (
            ext == ".py"
            and not basename.startswith("_")
            and not basename.startswith("test_")
        )

    def get_python_files(self):
        """Report Python files to be tested or to be skipped.

        Returns
        -------
        accepted_files : list of str
            Python file paths to be tested.
        skipped_files : (filepath: str, reason: str)
            Skipped files. First item is the file path, second
            item is the reason why it is skipped.
        """
        accepted_files = []
        skipped_files = []
        for source_dir in self.source_dirs:
            for root, _, files in os.walk(source_dir):
                for filename in files:
                    path = os.path.abspath(os.path.join(root, filename))
                    if not self._is_python_file(path):
                        continue

                    skipped, reason = self.is_skipped(path)
                    if skipped:
                        skipped_files.append((path, reason))
                    else:
                        accepted_files.append(path)

        # Avoid arbitrary ordering from the OS
        return sorted(accepted_files), sorted(skipped_files)


# =============================================================================
# Configuration
# =============================================================================

# Tutorial files are not part of the package data
TUTORIALS = os.path.join(
    HERE,
    "..",
    "examples",
    "tutorials",
    "doc_examples",
    "examples",
)

# Demo files are part of the package data.
DEMO = pkg_resources.resource_filename("traitsui", "examples/demo")

#: Explicitly include folders from which example files should be found
#: recursively.
SOURCE_DIRS = [
    DEMO,
    TUTORIALS,
]

SEARCHER = ExampleSearcher(source_dirs=SOURCE_DIRS)
SEARCHER.skip_file_if(
    os.path.join(DEMO, "Advanced", "HDF5_tree_demo.py"),
    lambda: sys.platform == "darwin",
    "This example depends on PyTables which may be built to require CPUs with "
    "a specific AVX version that is not supported on a paricular OSX host.",
)
SEARCHER.skip_file_if(
    os.path.join(DEMO, "Advanced", "Table_editor_with_progress_column.py"),
    is_wx,
    "ProgressRenderer is not implemented in wx.",
)
SEARCHER.skip_file_if(
    os.path.join(DEMO, "Advanced", "Scrubber_editor_demo.py"),
    is_qt,
    "ScrubberEditor is not implemented in qt.",
)
SEARCHER.skip_file_if(
    os.path.join(DEMO, "Extras", "animated_GIF.py"),
    lambda: not is_wx(),
    "Only support wx",
)
SEARCHER.skip_file_if(
    os.path.join(DEMO, "Extras", "Tree_editor_with_TreeNodeRenderer.py"),
    lambda: not is_qt(),
    "Only support Qt",
)
SEARCHER.skip_file_if(
    os.path.join(DEMO, "Extras", "windows", "flash.py"),
    lambda: not is_wx(),
    "Only support wx",
)
SEARCHER.skip_file_if(
    os.path.join(DEMO, "Extras", "windows", "internet_explorer.py"),
    lambda: not is_wx(),
    "Only support wx",
)
SEARCHER.skip_file_if(
    os.path.join(TUTORIALS, "view_multi_object.py"),
    lambda: True,
    "Require wx and is blocking.",
)
SEARCHER.skip_file_if(
    os.path.join(TUTORIALS, "view_standalone.py"),
    lambda: True,
    "Require wx and is blocking.",
)

# Validate configuration.
SEARCHER.validate()


# =============================================================================
# Test run utility functions
# =============================================================================


def replaced_configure_traits(
    instance,
    filename=None,
    view=None,
    kind=None,
    edit=True,
    context=None,
    handler=None,
    id="",
    scrollable=None,
    **args,
):
    """Mocked configure_traits to launch then close the GUI."""
    ui_kwargs = dict(
        view=view,
        parent=None,
        kind="live",  # other options may block the test
        context=context,
        handler=handler,
        id=id,
        scrollable=scrollable,
        **args,
    )
    with UITester().create_ui(instance, ui_kwargs):
        pass


@contextlib.contextmanager
def replace_configure_traits():
    """Context manager to temporarily replace HasTraits.configure_traits
    with a mocked version such that GUI launched are closed soon after they
    are open.
    """
    original_func = HasTraits.configure_traits
    HasTraits.configure_traits = replaced_configure_traits
    try:
        yield
    finally:
        HasTraits.configure_traits = original_func


def run_file(file_path):
    """Execute a given Python file.

    Parameters
    ----------
    file_path : str
        File path to be tested.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    globals = {
        "__name__": "__main__",
        "__file__": file_path,
    }
    with replace_configure_traits(), mock.patch(
        "sys.stdout", new_callable=io.StringIO
    ), mock.patch("sys.argv", [file_path]):
        # Mock stdout: Examples typically print educational information.
        # They are expected but they should not pollute test output.
        # Mock argv: Some example reads sys.argv to allow more arguments
        # But all examples should support being run without additional
        # arguments.
        exec(content, globals)


# =============================================================================
# load_tests protocol for unittest discover
# =============================================================================


def load_tests(loader, tests, pattern):
    """Implement load_tests protocol so that when unittest discover is run
    with this test module, the tests in the demo folder (not a package) are
    also loaded.

    See unittest documentation on load_tests
    """
    # Keep all the other loaded tests.
    suite = unittest.TestSuite()
    suite.addTests(tests)

    # Expand the test suite with tests from the examples, assuming
    # the test for ``group/script.py`` is placed in ``group/tests/`` directory.
    accepted_files, _ = SEARCHER.get_python_files()
    test_dirs = set(
        os.path.join(os.path.dirname(path), "tests") for path in accepted_files
    )
    test_dirs = set(path for path in test_dirs if os.path.exists(path))
    for dirpath in sorted(test_dirs):

        # Test files are scripts too and they demonstrate running the
        # tests. Mock the run side-effect when we load the test cases.
        with mock.patch.object(unittest.TextTestRunner, "run"):
            test_suite = unittest.TestLoader().discover(
                dirpath, pattern=pattern
            )
        if is_qt() or is_wx():
            suite.addTests(test_suite)

    return suite


# =============================================================================
# Test cases
# =============================================================================


@requires_toolkit([ToolkitName.qt, ToolkitName.wx])
class TestExample(BaseTestMixin, unittest.TestCase):
    def setUp(self):
        BaseTestMixin.setUp(self)

    def tearDown(self):
        BaseTestMixin.tearDown(self)

    def test_run(self):
        accepted_files, skipped_files = SEARCHER.get_python_files()

        for file_path in accepted_files:
            with self.subTest(file_path=file_path):
                try:
                    run_file(file_path)
                except Exception as exc:
                    message = "".join(
                        traceback.format_exception(*sys.exc_info())
                    )
                    self.fail(
                        "Executing {} failed with exception {}\n {}".format(
                            file_path, exc, message
                        )
                    )
                finally:
                    # Whatever failure, always flush the GUI event queue
                    # before running the next one.
                    process_cascade_events()

        # Report skipped files
        for file_path, reason in skipped_files:
            with self.subTest(file_path=file_path):
                # make up for unittest not reporting the parameter in skip
                # message.
                raise unittest.SkipTest(
                    "{reason} (File: {file_path})".format(
                        reason=reason, file_path=file_path
                    )
                )
