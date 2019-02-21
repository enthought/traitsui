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
        expected = (u' Module description ', 'x=1\ny=2')
        self.assertEqual(expected, (docstring, source))

    def test_parse_source(self):
        docstring, source = parse_source('non-existent-file.<>|:')
        self.assertIn('Sorry, something went wrong.', docstring)
