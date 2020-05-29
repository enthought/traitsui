#  Copyright (c) 2020, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!

""" Tests for demo and tutorial examples.
"""

import contextlib
from itertools import chain
import os
import unittest
from unittest import mock

from traits.api import HasTraits

from traitsui.tests._tools import (
    is_current_backend_wx,
    is_current_backend_qt4,
    skip_if_null,
)


# This test file is not distributed nor is it in a package.
HERE = os.path.dirname(__file__)

EXAMPLES = os.path.join(HERE, "..", "examples")
DEMO = os.path.join(EXAMPLES, "demo")
TUTORIALS = os.path.join(EXAMPLES, "tutorials", "doc_examples", "examples")

#: Explicitly include folders from which example files should be found
#: recursively.
SOURCE_DIRS = [
    DEMO,
    TUTORIALS,
]


#: Mapping from filepath to a callable() -> (skipped: bool, reason: str)
FILES_MAY_BE_SKIPPED = {}


def skip_file_if(condition, reason, filepath):
    """ Mark a file to be skipped for a given condition.

    Parameters
    ----------
    condition: callable() -> bool
        The condition for skipping a file.
    reason : str
        Reason for skipping the file.
    filepath : str
        Path of the file which may be skipped from tests.
    """
    def wrapped():
        return condition(), reason

    filepath = os.path.abspath(filepath)
    FILES_MAY_BE_SKIPPED[filepath] = wrapped


skip_file_if(
    lambda: True, "Not a target file to be tested",
    os.path.join(DEMO, "demo.py"),
)
skip_file_if(
    is_current_backend_wx, "ProgressRenderer is not implemented in wx.",
    os.path.join(DEMO, "Advanced", "Table_editor_with_progress_column.py"),
)
skip_file_if(
    lambda: not is_current_backend_wx(), "Require wx",
    os.path.join(DEMO, "Extras", "animated_GIF.py"),
)
skip_file_if(
    lambda: not is_current_backend_qt4(), "Only support Qt",
    os.path.join(DEMO, "Extras", "Tree_editor_with_TreeNodeRenderer.py"),
)
skip_file_if(
    lambda: not is_current_backend_wx(), "Require wx",
    os.path.join(DEMO, "Extras", "windows", "flash.py"),
)
skip_file_if(
    lambda: not is_current_backend_wx(), "Require wx",
    os.path.join(DEMO, "Extras", "windows", "internet_explorer.py"),
)
skip_file_if(
    is_current_backend_wx,
    "enable tries to import a missing constant. See enthought/enable#307",
    os.path.join(DEMO, "Useful", "demo_group_size.py"),
)
skip_file_if(
    lambda: True, "Require wx and is blocking.",
    os.path.join(TUTORIALS, "view_multi_object.py"),
)
skip_file_if(
    lambda: True, "Require wx and is blocking.",
    os.path.join(TUTORIALS, "view_standalone.py"),
)
skip_file_if(
    is_current_backend_qt4, "Failing on Qt, see enthought/traitsui#773",
    os.path.join(TUTORIALS, "wizard.py"),
)


def check_special_files():
    """ Check all files that may be skipped still exist."""
    for filepath in FILES_MAY_BE_SKIPPED:
        if not os.path.exists(filepath):
            raise RuntimeError("{} does not exist.".format(filepath))


def is_python_file(path):
    """ Return true if the given path is (public) Python file."""
    _, basename = os.path.split(path)
    _, ext = os.path.splitext(basename)
    return (
        ext == ".py"
        and not basename.startswith("_")
    )


def is_skipped(path):
    """ Return if the Python file should be skipped in test.

    Parameters
    ----------
    path : str
        Path to a file.

    Returns
    -------
    skipped : bool
    reason : str
    """
    if path not in FILES_MAY_BE_SKIPPED:
        return False, ""
    skipped, reason = FILES_MAY_BE_SKIPPED[path]()
    return skipped, reason


def get_python_files(directory):
    """ Recursively walk a directory and report Python files to be tested.

    Parameters
    ----------
    directory : str
        Path of the directory to be walked.

    Returns
    -------
    paths : list of str
        List of Python file paths.
    """
    paths = []
    for root, _, files in os.walk(directory):
        for filename in files:
            path = os.path.abspath(os.path.join(root, filename))
            if is_python_file(path):
                paths.append(path)
    return sorted(paths)


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
        **args
):
    """ Mocked configure_traits to launch then close the GUI.
    """
    ui = instance.edit_traits(
        view=view,
        parent=None,
        kind="live",  # other options may block the test
        context=context,
        handler=handler,
        id=id,
        scrollable=scrollable,
        **args,
    )
    ui.dispose()


@contextlib.contextmanager
def replace_configure_traits():
    """ Context manager to temporarily replace HasTraits.configure_traits
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
    """ Execute a given Python file.

    Parameters
    ----------
    file_path : str
        File path to be tested.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    globals = {
        "__package__": __package__,
        "__name__": "traitsui",   # as long as it is not __main__
        "__file__": file_path,
    }
    with replace_configure_traits(), \
            mock.patch("sys.argv", [file_path]):
        # Some example reads sys.argv to allow more arguments
        # But all examples should support being run without additional
        # arguments.
        exec(content, globals)


@skip_if_null
class TestExample(unittest.TestCase):

    def test_run(self):
        check_special_files()
        file_paths = chain.from_iterable(
            get_python_files(source_dir) for source_dir in SOURCE_DIRS
        )
        for file_path in file_paths:
            with self.subTest(file_path=file_path):
                skipped, reason = is_skipped(file_path)
                if skipped:
                    raise unittest.SkipTest(reason)

                try:
                    run_file(file_path)
                except Exception as exc:
                    self.fail(
                        "Executing {} failed with exception {}".format(
                            file_path, exc
                        )
                    )
