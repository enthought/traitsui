# (C) Copyright 2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import os
import tempfile
import textwrap
import unittest
from xml.etree import ElementTree as ET

from traitsui.api import Handler, UI, UIInfo

from etsdemo.app import (
    Demo,
    DemoPath,
    DemoVirtualDirectory,
    extract_docstring_from_source,
    parse_source,
    next_tool,
    previous_tool,
    parent_tool,
)

HTML_NS_PREFIX = "{http://www.w3.org/1999/xhtml}"


def get_html_tag(tag):
    return HTML_NS_PREFIX + tag


def get_action_enabled(action, model_view):
    """ Helper funciton to return if a tool is enabled.

    Parameters
    ----------
    action : Action
    model_view : ModelView
    """
    context = model_view.trait_get()
    context.update(model_view.trait_context())
    return eval(
        compile(action.enabled_when, "<string>", "eval"),
        {},
        context,
    )


class TestDemo(unittest.TestCase):
    """ Test actions on the Demo class. """

    def test_demo_previous_button_default(self):
        # Make sure the previous button behaves in the default state.
        # This ensures the enable flag can be computed (instead of crashing),
        # and the action allowed by it does not crash.
        demo = Demo(model=DemoPath())
        if get_action_enabled(previous_tool, demo):
            demo.perform(None, next_tool, None)

    def test_demo_next_button_default(self):
        # Make sure the next button behaves in the default state.
        # This ensures the enable flag can be computed (instead of crashing),
        # and the action allowed by it does not crash.
        demo = Demo(model=DemoPath())
        if get_action_enabled(next_tool, demo):
            demo.perform(None, next_tool, None)

    def test_demo_parent_button_default(self):
        # Make sure the parent button behaves in the default state.
        # This ensures the enable flag can be computed (instead of crashing),
        # and the action allowed by it does not crash.
        demo = Demo(model=DemoPath())
        if get_action_enabled(parent_tool, demo):
            demo.perform(None, parent_tool, None)

    def test_demo_init_set_children(self):
        # Test if there are children, the first one will be selected.
        resources = [DemoPath(), DemoPath()]
        model = DemoVirtualDirectory(resources=resources)
        demo = Demo(model=model)
        demo.selected_node = None

        # when
        info = UIInfo(ui=UI(handler=Handler()))
        demo.init(info)

        # then
        self.assertIs(demo.selected_node, resources[0])

    def test_demo_init_no_children_to_be_set(self):
        # Test if there are no children, nothing is selected.
        model = DemoVirtualDirectory(resources=[])
        demo = Demo(model=model)
        demo.selected_node = None

        # when
        info = UIInfo(ui=UI(handler=Handler()))
        demo.init(info)

        # then
        self.assertIsNone(demo.selected_node)


class TestDemoPathDescription(unittest.TestCase):
    """ Test ``DemoPath.description`` """

    def test_description_with_empty_directory(self):
        # If the directory is empty, the content of the description should
        # be empty.
        with tempfile.TemporaryDirectory() as directory:
            model = DemoPath(
                name=directory,
            )

            tree = ET.fromstring(model.description)
        body_node = next(tree.iter(get_html_tag("body")))
        div_node, = list(body_node)
        self.assertEqual(list(div_node), [])

    def test_use_index_rst(self):
        with tempfile.TemporaryDirectory() as directory:
            index_rst = os.path.join(directory, "index.rst")
            with open(index_rst, "w", encoding="utf-8") as f:
                f.write(".. image:: any_image.jpg\n")

            model = DemoPath(
                name=directory,
            )

            tree = ET.fromstring(model.description)
        img_node = next(tree.iter(get_html_tag("img")))
        self.assertEqual(img_node.attrib["src"], "any_image.jpg")

    def test_description_use_css(self):
        with tempfile.TemporaryDirectory() as directory:
            model = DemoPath(
                name=directory,
                css_filename="default.css",
            )

            tree = ET.fromstring(model.description)

        link_node = next(tree.iter(get_html_tag("link")))
        self.assertEqual(link_node.attrib["href"], "default.css")


class TestDemoPathInitLocals(unittest.TestCase):
    """ Test ``DemoPath.init_dic`` """

    def test_init_dict_with_empty_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            model = DemoPath(
                name=directory,
            )
            # traits api is still imported.
            init_dic = model.init_dic
            self.assertIsInstance(init_dic, dict)
            self.assertIn("HasTraits", init_dic)

    def test_init_dict_with_init_py(self):
        with tempfile.TemporaryDirectory() as directory:
            init_py = os.path.join(directory, "__init__.py")
            with open(init_py, "w", encoding="utf-8") as f:
                f.write("a = 1\n")
            model = DemoPath(
                name=directory,
            )
            self.assertIn("a", model.init_dic)
            self.assertEqual(model.init_dic["a"], 1)
            # traits api is still imported.
            self.assertIn("HasTraits", model.init_dic)


class TestDemoPathChildren(unittest.TestCase):
    """ Integration test with DemoPath and its children
    """

    def test_init_dict_used_by_children(self):
        # Test the __init__.py in a directory (if exists) is visible
        # by the example scripts in that folder.
        # Not sure if this is really needed, but this is an existing feature.
        with tempfile.TemporaryDirectory() as directory:

            init_content = "CONSTANT = 'HELLO'"
            example_content = textwrap.dedent(
                """
                from . import CONSTANT
                from . import HasTraits
                """
            )
            subdir = os.path.join(directory, "Examples")
            os.makedirs(subdir)
            init_py = os.path.join(subdir, "__init__.py")
            with open(init_py, "w", encoding="utf-8") as f:
                f.write(init_content)
            example_py = os.path.join(subdir, "example.py")
            with open(example_py, "w", encoding="utf-8") as f:
                f.write(example_content)

            model = DemoPath(
                name=directory,
                use_files=False,
            )

            # sanity check:
            # This is one subdirectory
            children = model.get_children()
            self.assertEqual(len(children), 1)

            # In that subdirectory, there is one Python file that is not
            # __init__.py
            subdir_node, = children
            file_nodes = subdir_node.get_children()
            self.assertEqual(len(file_nodes), 1)
            example, = file_nodes
            self.assertEqual(example.name, "example.py")

            # This is the test objective: The __init__.py and traits api are
            # loaded and accessible by the example script.
            # Try running the code
            example.run_code()
            self.assertIn("CONSTANT", example.locals)
            self.assertIn("HasTraits", example.locals)


class TestDemoVirtualDirectory(unittest.TestCase):

    def test_no_resources(self):
        node = DemoVirtualDirectory(resources=[])
        self.assertFalse(node.tno_has_children(None))
        self.assertEqual(node.tno_get_children(None), [])
        self.assertTrue(node.tno_allows_children(None))

    def test_some_resources(self):
        node = DemoVirtualDirectory(resources=[DemoPath()])
        self.assertTrue(node.tno_has_children(None))
        self.assertEqual(node.tno_get_children(None), node.resources)
        self.assertTrue(node.tno_allows_children(None))


class TestParseSource(unittest.TestCase):

    def test_extract_docstring_from_source(self):
        source_code = b""
        with self.assertRaises(TypeError):
            docstring, source = extract_docstring_from_source(source_code)

        source_code = u""
        docstring, source = extract_docstring_from_source(source_code)
        self.assertEqual((u"", u""), (docstring, source))

        source_code = u'''""" Module description """\nx=1\ny=2'''
        docstring, source = extract_docstring_from_source(source_code)
        expected = (u" Module description ", "x=1\ny=2")
        self.assertEqual(expected, (docstring, source))

    def test_parse_source(self):
        docstring, source = parse_source("non-existent-file.<>|:")
        self.assertIn("Sorry, something went wrong.", docstring)

    def test_simple_source(self):
        source_code = "\n".join(['"""', "Docstring", '"""', "a = 1"])
        docstring, source = extract_docstring_from_source(source_code)
        self.assertEqual(docstring, "\nDocstring\n")
        self.assertEqual(source, "a = 1")

    def test_alternate_quotes(self):
        source_code = "\n".join(["'''", "Docstring", "'''", "a = 1"])
        docstring, source = extract_docstring_from_source(source_code)
        self.assertEqual(docstring, "\nDocstring\n")
        self.assertEqual(source, "a = 1")

    def test_string_in_source(self):
        source_code = "\n".join(
            ['"""', "Docstring", '"""', '"string in source"', "a = 1"]
        )
        docstring, source = extract_docstring_from_source(source_code)
        self.assertEqual(docstring, "\nDocstring\n")
        self.assertEqual(source, "\n".join(['"string in source"', "a = 1"]))

    def test_string_in_docstring(self):
        source_code = "\n".join(
            ['"""', "Docstring", '"string in docstring"', '"""', "a = 1"]
        )
        docstring, source = extract_docstring_from_source(source_code)
        self.assertEqual(
            docstring,
            "\n".join(["", "Docstring", '"string in docstring"', ""]),
        )
        self.assertEqual(source, "\n".join(["a = 1"]))

    def test_ignore_class_docstring(self):
        source_code = "\n".join(["class Foo:", '    """Class docstring"""'])
        docstring, source = extract_docstring_from_source(source_code)
        self.assertEqual(docstring, "")
        self.assertEqual(
            source, "\n".join(["class Foo:", '    """Class docstring"""'])
        )

    def test_ignore_starting_comment(self):
        source_code = "\n".join(
            [
                "# Copyright notice.",
                "# Something about the author.",
                '"""',
                "Docstring",
                '"""',
                "a = 1",
            ]
        )
        docstring, source = extract_docstring_from_source(source_code)
        self.assertEqual(docstring, "\nDocstring\n")
        self.assertEqual(
            source,
            "\n".join(
                [
                    "# Copyright notice.",
                    "# Something about the author.",
                    "a = 1",
                ]
            ),
        )
