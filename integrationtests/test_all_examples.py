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
import io
import os
import sys
import traceback
import unittest
from unittest import mock

import pkg_resources
from traits.api import HasTraits

from traitsui.tests._tools import (
    is_qt,
    is_wx,
    process_cascade_events,
    requires_toolkit,
    reraise_exceptions,
    ToolkitName,
)
from traitsui.testing.tester import command, locator, query
from traitsui.testing.tester.ui_tester import UITester

# This test file is not distributed nor is it in a package.
HERE = os.path.dirname(__file__)


class ExampleSearcher:
    """ This object collects and reports example files to be tested."""

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
        """ Mark a file to be skipped for a given condition.

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
        """ Return if the Python file should be skipped in test.

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
        """ Validate configuration. Currently this checks all files that may
        be skipped still exist.
        """
        for filepath in self.files_may_be_skipped:
            if not os.path.exists(filepath):
                raise RuntimeError("{} does not exist.".format(filepath))

    @staticmethod
    def _is_python_file(path):
        """ Return true if the given path is (public) Python file."""
        _, basename = os.path.split(path)
        _, ext = os.path.splitext(basename)
        return (
            ext == ".py"
            and not basename.startswith("_")
        )

    def get_python_files(self):
        """ Report Python files to be tested or to be skipped.

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
    HERE, "..", "examples", "tutorials", "doc_examples", "examples",
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
    os.path.join(DEMO, "Advanced", "Table_editor_with_progress_column.py"),
    is_wx, "ProgressRenderer is not implemented in wx.",
)
SEARCHER.skip_file_if(
    os.path.join(DEMO, "Advanced", "Scrubber_editor_demo.py"),
    is_qt, "ScrubberEditor is not implemented in qt.",
)
SEARCHER.skip_file_if(
    os.path.join(DEMO, "Extras", "animated_GIF.py"),
    lambda: not is_wx(), "Only support wx",
)
SEARCHER.skip_file_if(
    os.path.join(DEMO, "Extras", "Tree_editor_with_TreeNodeRenderer.py"),
    lambda: not is_qt(), "Only support Qt",
)
SEARCHER.skip_file_if(
    os.path.join(DEMO, "Extras", "windows", "flash.py"),
    lambda: not is_wx(), "Only support wx",
)
SEARCHER.skip_file_if(
    os.path.join(DEMO, "Extras", "windows", "internet_explorer.py"),
    lambda: not is_wx(), "Only support wx",
)
SEARCHER.skip_file_if(
    os.path.join(DEMO, "Useful", "demo_group_size.py"),
    is_wx,
    "enable tries to import a missing constant. See enthought/enable#307",
)
SEARCHER.skip_file_if(
    os.path.join(TUTORIALS, "view_multi_object.py"),
    lambda: True, "Require wx and is blocking.",
)
SEARCHER.skip_file_if(
    os.path.join(TUTORIALS, "view_standalone.py"),
    lambda: True, "Require wx and is blocking.",
)
SEARCHER.skip_file_if(
    os.path.join(TUTORIALS, "wizard.py"),
    is_qt, "Failing on Qt, see enthought/traitsui#773",
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
    with reraise_exceptions():
        process_cascade_events()

        # Temporary fix for enthought/traitsui#907
        if is_qt():
            ui.control.hide()
        if is_wx():
            ui.control.Hide()

        ui.dispose()
        process_cascade_events()


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
        "__name__": "__main__",
        "__file__": file_path,
    }
    with replace_configure_traits(), \
            mock.patch("sys.stdout", new_callable=io.StringIO), \
            mock.patch("sys.argv", [file_path]):
        # Mock stdout: Examples typically print educational information.
        # They are expected but they should not pollute test output.
        # Mock argv: Some example reads sys.argv to allow more arguments
        # But all examples should support being run without additional
        # arguments.
        exec(content, globals)


def load_demo(file_path, variable_name="demo"):
    """ Loads a demo example from given file_path. Extracts the relevant
    object via variable_name.

    Parameters
    ----------
    file_path : str
        The file_path of the file to be loaded
    variable_name : str
        The key in the global symbol state corresponding to the object of
        interest for the demo.

    Returns
    -------
    Instance of HasTraits
        It is expected that this object will have edit_traits called on it,
        so that the demo can be tested.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    globals_ = globals().copy()
    exec(content, globals_)
    return globals_[variable_name]


# =============================================================================
# Test cases
# =============================================================================

@requires_toolkit([ToolkitName.qt, ToolkitName.wx])
class TestExample(unittest.TestCase):

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


@requires_toolkit([ToolkitName.qt, ToolkitName.wx])
class TestInteractExample(unittest.TestCase):
    """ Test examples with more interactions."""

    @requires_toolkit([ToolkitName.qt])
    def test_button_editor_demo(self):
        from pyface.ui.qt4.util.modal_dialog_tester import ModalDialogTester
        from pyface.constant import OK

        # Test ButtonEditor_demo.py in examples/demo/Standard_Edtiors
        filepath = os.path.join(
            DEMO, "Standard_Editors", "ButtonEditor_demo.py"
        )
        demo = load_demo(filepath, "demo")

        tester = UITester()
        with tester.create_ui(demo) as ui:

            simple_button = tester.find_by_id(ui, "simple")
            custom_button = tester.find_by_id(ui, "custom")

            # funcion object for instantiating ModalDialogTester should be a
            # function that opens the dialog
            # we want clicking the buttons to do that
            def click_simple_button():
                simple_button.perform(command.MouseClick())

            def click_custom_button():
                custom_button.perform(command.MouseClick())

            mdtester_simple = ModalDialogTester(click_simple_button)
            mdtester_simple.open_and_run(lambda x: x.click_button(OK))
            self.assertTrue(mdtester_simple.dialog_was_opened)

            mdtester_custom = ModalDialogTester(click_custom_button)
            mdtester_custom.open_and_run(lambda x: x.click_button(OK))
            self.assertTrue(mdtester_custom.dialog_was_opened)

    def test_button_editor_simple_demo(self):
        # Test ButtonEditor_simple_demo.py in examples/demo/Standard_Edtiors
        filepath = os.path.join(
            DEMO, "Standard_Editors", "ButtonEditor_simple_demo.py"
        )
        demo = load_demo(filepath, "demo")

        tester = UITester()
        with tester.create_ui(demo) as ui:
            button = tester.find_by_name(ui, "my_button_trait")
            for index in range(5):
                button.perform(command.MouseClick())
                self.assertEqual(demo.click_counter, index + 1)

            click_counter = tester.find_by_name(ui, "click_counter")
            displayed_count = click_counter.inspect(query.DisplayedText())
            self.assertEqual(displayed_count, '5')

            demo.click_counter = 10
            displayed_count = click_counter.inspect(query.DisplayedText())
            self.assertEqual(displayed_count, '10')

    def test_converter(self):
        # Test converter.py in examples/demo/Applications
        filepath = os.path.join(
            DEMO, "Applications", "converter.py"
        )
        demo = load_demo(filepath, "popup")
        tester = UITester()
        with tester.create_ui(demo) as ui:
            input_amount = tester.find_by_name(ui, "input_amount")
            output_amount = tester.find_by_name(ui, "output_amount")
            for _ in range(4):
                input_amount.perform(command.KeyClick("Backspace"))
            input_amount.perform(command.KeySequence("14.0"))
            self.assertEqual(
                output_amount.inspect(query.DisplayedText())[:4],
                "1.16",
            )
            tester.find_by_id(ui, "Undo").perform(command.MouseClick())
            self.assertEqual(
                output_amount.inspect(query.DisplayedText()),
                "1.0",
            )

    def test_checklist_editor_simple_demo(self):
        # Test CheckListEditor_simple_demo.py in examples/demo/Standard_Edtiors
        filepath = os.path.join(
            DEMO, "Standard_Editors", "CheckListEditor_simple_demo.py"
        )
        demo = load_demo(filepath, "demo")

        tester = UITester()
        with tester.create_ui(demo) as ui:
            checklist = tester.find_by_id(ui, "custom")
            item3 = checklist.locate(locator.Index(2))
            item3.perform(command.MouseClick())
            self.assertEqual(demo.checklist, ["three"])
            item3.perform(command.MouseClick())
            self.assertEqual(demo.checklist, [])

    def test_list_editor_notebook_selection_demo(self):
        # Test List_editor_notebook_selection_demo.py in examples/demo/Advanced
        filepath = os.path.join(
            DEMO, "Advanced", "List_editor_notebook_selection_demo.py"
        )
        demo = load_demo(filepath, "demo")

        tester = UITester()
        with tester.create_ui(demo) as ui:
            people_list = tester.find_by_name(ui, "people")
            person2 = people_list.locate(locator.Index(2))
            person2.perform(command.MouseClick())
            self.assertEqual(demo.index, 2)
            age = person2.find_by_name("age")
            age.perform(command.KeyClick("Backspace"))
            age.perform(command.KeyClick("9"))
            self.assertEqual(demo.people[2].age, 39)
