from unittest import TestCase

from traitsui.extras.demo import extract_docstring_from_source


class TestDemo(TestCase):

    def test_extract_docstring_from_source(self):
        source_code = b""
        with self.assertRaises(TypeError):
            docstring, source = extract_docstring_from_source(source_code)

        source_code = u""
        docstring, source = extract_docstring_from_source(source_code)
        self.assertEqual((u"", u""), (docstring, source))

        source_code = u'''""" Module description """'''
        docstring, source = extract_docstring_from_source(source_code)
        expected = (u' Module description ', '')
        self.assertEqual(expected, (docstring, source))
