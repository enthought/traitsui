import contextlib
import io
import os
import sys
import traceback
import unittest
from unittest import mock
from functools import partial

import pkg_resources

from pyface.qt import QtGui

from traits.api import HasTraits
from traitsui.testing.api import UITester

# Demo files are part of the package data.
DEMO = pkg_resources.resource_filename("traitsui", "examples/demo")
screenshot_name = None

def _is_python_file(path):
    """ Return true if the given path is (public) non-test Python file."""
    _, basename = os.path.split(path)
    _, ext = os.path.splitext(basename)
    return (
        ext == ".py"
        and not basename.startswith("_")
        and not basename.startswith("test_")
    )


def get_python_files(directory):
    """ Report Python files to be tested or to be skipped.

    Returns
    -------
    accepted_files : list of str
        Python file paths to be tested.
    """
    accepted_files = []
    for root, _, files in os.walk(directory):
        for filename in files:
            path = os.path.abspath(os.path.join(root, filename))
            if not _is_python_file(path):
                continue
            accepted_files.append(path)

    # Avoid arbitrary ordering from the OS
    return sorted(accepted_files)


def get_editor_example_filees(python_files):
    Editor_demo_files = []
    for filename in python_files:
        if filename.endswith('Editor_demo.py'):
            Editor_demo_files.append(filename)
    return Editor_demo_files


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
    """ Mocked configure_traits to launch then close the GUI.
    """
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
    with UITester().create_ui(instance, ui_kwargs) as ui:
        ui_pixmap = QtGui.QPixmap.grabWidget(ui.control)
        ui_pixmap.save(
            os.path.join(
                "docs",
                "source",
                "traitsui_user_manual",
                "images",
                screenshot_name
            )
        )


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
    demo_name = os.path.basename(file_path)
    global screenshot_name
    screenshot_name = demo_name.split('.')[0] + '.png'
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    globals = {
        "__name__": "__main__",
        "__file__": file_path,
    }
    with replace_configure_traits(), mock.patch("sys.argv", [file_path]):
        # Mock argv: Some example reads sys.argv to allow more arguments
        # But all examples should support being run without additional
        # arguments.
        exec(content, globals)


def main():
    py_files = get_python_files(DEMO)
    example_files = get_editor_example_filees(py_files)

    for filename in example_files:
        run_file(filename)


if __name__ == '__main__':
    main()