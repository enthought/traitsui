import contextlib
import io
import os
import sys
import traceback
import unittest
from unittest import mock
import time

import pkg_resources

from traitsui.testing.tester import command, locator, query
from traitsui.testing.tester.ui_tester import UITester


DEMO = pkg_resources.resource_filename("traitsui", "examples/demo")


def load_demo(file_path, variable_name="demo"):
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
        input_amount.delay=200
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
