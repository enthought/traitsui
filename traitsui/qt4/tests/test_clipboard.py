#
# (C) Copyright 2013 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This file is open source software distributed according to the terms in
# LICENSE.txt
#

import unittest
from cPickle import dumps

from traitsui.qt4.clipboard import PyMimeData

class PyMimeDataTestCase(unittest.TestCase):
    
    # Basic functionality tests
    
    def test_pickle(self):
        md = PyMimeData(data=0)
        self.assertEqual(md._local_instance, 0)
        self.assertTrue(md.hasFormat(PyMimeData.MIME_TYPE))
        self.assertFalse(md.hasFormat(PyMimeData.NOPICKLE_MIME_TYPE))
        self.assertEqual(bytes(md.data(PyMimeData.MIME_TYPE)), dumps(int)+dumps(0))
    
    def test_nopickle(self):
        md = PyMimeData(data=0, pickle=False)
        self.assertEqual(md._local_instance, 0)
        self.assertTrue(md.hasFormat(PyMimeData.NOPICKLE_MIME_TYPE))
        self.assertFalse(md.hasFormat(PyMimeData.MIME_TYPE))
        self.assertEqual(bytes(md.data(PyMimeData.NOPICKLE_MIME_TYPE)), str(id(0)))

    def test_cant_pickle(self):
        md = PyMimeData(data=0)
        self.assertEqual(md._local_instance, 0)
        self.assertTrue(md.hasFormat(PyMimeData.MIME_TYPE))
        self.assertFalse(md.hasFormat(PyMimeData.NOPICKLE_MIME_TYPE))
        self.assertEqual(bytes(md.data(PyMimeData.MIME_TYPE)), dumps(int)+dumps(0))

    def test_cant_pickle(self):
        md = PyMimeData(data=0)
        self.assertEqual(md._local_instance, 0)
        self.assertTrue(md.hasFormat(PyMimeData.MIME_TYPE))
        self.assertFalse(md.hasFormat(PyMimeData.NOPICKLE_MIME_TYPE))
        self.assertEqual(bytes(md.data(PyMimeData.MIME_TYPE)), dumps(int)+dumps(0))
    

if __name__ == '__main__':
    unittest.main()
