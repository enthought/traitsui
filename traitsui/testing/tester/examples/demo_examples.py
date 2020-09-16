""" The examples in this file showcase UI Tester being used on some of the
already existing demos for TraitsUI itself.
"""
import os
import time

import pkg_resources

from traitsui.testing.tester import command, locator, query
from traitsui.testing.tester.ui_tester import UITester

DEMO = pkg_resources.resource_filename("traitsui", "examples/demo")


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


if __name__ == '__main__':
    # Test converter.py in examples/demo/Applications
    filepath = os.path.join(
        DEMO, "Applications", "converter.py"
    )
    demo = load_demo(filepath, "popup")
    tester = UITester(delay=1500)
    with tester.create_ui(demo) as ui:
        input_amount = tester.find_by_name(ui, "input_amount")
        input_amount.delay = 200
        output_amount = tester.find_by_name(ui, "output_amount")
        input_units = tester.find_by_name(ui, "input_units")
        output_units = tester.find_by_name(ui, "output_units")

        for _ in range(4):
            input_amount.perform(command.KeyClick("Backspace"))
        input_amount.perform(command.KeySequence("14.0"))
        assert output_amount.inspect(query.DisplayedText())[:4] == "1.16"

        tester.find_by_id(ui, "Undo").perform(command.MouseClick())

        assert output_amount.inspect(query.DisplayedText()) == "1.0"

        for _ in range(3):
            input_amount.perform(command.KeyClick("Backspace"))
        input_units.locate(locator.Index(5)).perform(command.MouseClick())
        output_units.locate(locator.Index(3)).perform(command.MouseClick())

        assert output_amount.inspect(query.DisplayedText())[:3] == "1.6"

        time.sleep(2)
