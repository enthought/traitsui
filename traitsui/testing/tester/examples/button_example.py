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

from traitsui.testing.tester import command
from traitsui.testing.tester.examples.load_demo import load_demo
from traitsui.testing.tester.ui_tester import UITester

DEMO = pkg_resources.resource_filename("traitsui", "examples/demo")

if __name__ == '__main__':
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
