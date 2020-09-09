

from traitsui.testing.tester import command, locator, query
from traitsui.testing.tester.ui_tester import UITester



def load_demo(file_path, variable_name="demo"):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    globals_ = globals().copy()
    exec(content, globals_)
    return globals_[variable_name]