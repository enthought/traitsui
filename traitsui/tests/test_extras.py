from unittest import TestCase

from traitsui.extras.demo import extract_docstring_from_source, parse_source


class TestDemo(TestCase):
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
