"""
Simple example for utilizing UI Tester on a button editor.
Currently, the clicks happen instantaneously, so visually in the example,
the button will not change color as it normally would while being clicked
manually.
In this example, the Tester simply clicks the button 5 times (which can be
observed by the displayed click counter incrementing).
"""
import os
import pkg_resources
import unittest

from traitsui.testing.tester import command, query
from traitsui.testing.tester.examples.load_demo import load_demo
from traitsui.testing.tester.ui_tester import UITester

from traitsui.tests._tools import (
    requires_toolkit,
    ToolkitName,
)

DEMO = pkg_resources.resource_filename("traitsui", "examples/demo")


@requires_toolkit([ToolkitName.qt, ToolkitName.wx])
class TestButtonExamples(unittest.TestCase):

    def test_button_editor_simple_demo(self):
        # Showcase using UI Tester on ButtonEditor_simple_demo.py in
        # examples/demo/Standard_Edtiors
        filepath = os.path.join(
            DEMO, "Standard_Editors", "ButtonEditor_simple_demo.py"
        )
        demo = load_demo(filepath, "demo")

        tester = UITester(delay=500)
        with tester.create_ui(demo) as ui:
            button = tester.find_by_name(ui, "my_button_trait")
            for _ in range(5):
                button.perform(command.MouseClick())
            click_counter = tester.find_by_name(ui, "click_counter")
            displayed_count = click_counter.inspect(query.DisplayedText())
            self.assertEqual(displayed_count, '5')
