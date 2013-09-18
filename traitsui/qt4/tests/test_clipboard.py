#
# (C) Copyright 2013 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This file is open source software distributed according to the terms in
# LICENSE.txt
#

import unittest
from cPickle import dumps

from pyface.qt import QtCore
from traitsui.qt4.clipboard import PyMimeData

class PMDSubclass(PyMimeData):
    pass

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
        unpicklable = lambda: None
        md = PyMimeData(data=unpicklable)
        self.assertEqual(md._local_instance, unpicklable)
        self.assertTrue(md.hasFormat(PyMimeData.NOPICKLE_MIME_TYPE))
        self.assertFalse(md.hasFormat(PyMimeData.MIME_TYPE))
        self.assertEqual(bytes(md.data(PyMimeData.NOPICKLE_MIME_TYPE)), str(id(unpicklable)))

    def test_coerce_pymimedata(self):
        md = PyMimeData(data=0)
        md2 = PyMimeData.coerce(md)
        self.assertEqual(md, md2)
        
    def test_coerce_subclass(self):
        md = PMDSubclass(data=0)
        md2 = PyMimeData.coerce(md)
        self.assertEqual(md, md2)
        
    def test_coerce_QMimeData(self):
        md = QtCore.QMimeData()
        md.setText("test")
        md2 = PyMimeData.coerce(md)
        self.assertTrue(md2.hasText())
        self.assertEqual(md2.text(), "test")
        
    def test_coerce_object(self):
        md = PyMimeData.coerce(0)
        self.assertEqual(md._local_instance, 0)
        self.assertTrue(md.hasFormat(PyMimeData.MIME_TYPE))
        self.assertFalse(md.hasFormat(PyMimeData.NOPICKLE_MIME_TYPE))
        self.assertEqual(bytes(md.data(PyMimeData.MIME_TYPE)), dumps(int)+dumps(0))
        
    def test_coerce_unpicklable(self):
        unpicklable = lambda: None
        md = PyMimeData.coerce(unpicklable)
        self.assertEqual(md._local_instance, unpicklable)
        self.assertFalse(md.hasFormat(PyMimeData.MIME_TYPE))
        self.assertTrue(md.hasFormat(PyMimeData.NOPICKLE_MIME_TYPE))
        
    def test_coerce_list(self):
        md = PyMimeData.coerce([0])
        self.assertEqual(md._local_instance, [0])
        self.assertTrue(md.hasFormat(PyMimeData.MIME_TYPE))
        self.assertFalse(md.hasFormat(PyMimeData.NOPICKLE_MIME_TYPE))
        self.assertEqual(bytes(md.data(PyMimeData.MIME_TYPE)), dumps(list)+dumps([0]))
        
    def test_coerce_list_pymimedata(self):
        md = PyMimeData(data=0)
        md2 = PyMimeData.coerce([md])
        self.assertEqual(md2._local_instance, [0])
        self.assertTrue(md2.hasFormat(PyMimeData.MIME_TYPE))
        self.assertFalse(md2.hasFormat(PyMimeData.NOPICKLE_MIME_TYPE))
        self.assertEqual(bytes(md2.data(PyMimeData.MIME_TYPE)), dumps(list)+dumps([0]))
        
    def test_coerce_list_pymimedata_nopickle(self):
        md = PyMimeData(data=0, pickle=False)
        md2 = PyMimeData.coerce([md])
        self.assertEqual(md2._local_instance, [0])
        self.assertFalse(md2.hasFormat(PyMimeData.MIME_TYPE))
        self.assertTrue(md2.hasFormat(PyMimeData.NOPICKLE_MIME_TYPE))
        
    def test_coerce_list_pymimedata_mixed(self):
        md1 = PyMimeData(data=0, pickle=False)
        md2 = PyMimeData(data=0)
        md = PyMimeData.coerce([md1, md2])
        self.assertEqual(md._local_instance, [0, 0])
        self.assertFalse(md.hasFormat(PyMimeData.MIME_TYPE))
        self.assertTrue(md.hasFormat(PyMimeData.NOPICKLE_MIME_TYPE))
        
    def test_subclass_coerce_pymimedata(self):
        md = PyMimeData(data=0)
        md2 = PMDSubclass.coerce(md)
        self.assertTrue(isinstance(md2, PMDSubclass))
        self.assertTrue(md2.hasFormat(PyMimeData.MIME_TYPE))
        self.assertFalse(md2.hasFormat(PyMimeData.NOPICKLE_MIME_TYPE))
        self.assertEqual(bytes(md2.data(PyMimeData.MIME_TYPE)), dumps(int)+dumps(0))
        
    def test_instance(self):
        md = PyMimeData(data=0)
        self.assertEqual(md.instance(), 0)
    
    def test_instance_unpickled(self):
        md = PyMimeData(data=0)
        # remove local instance to simulate cross-process
        md._local_instance = None
        self.assertEqual(md.instance(), 0)
    
    def test_instance_nopickle(self):
        md = PyMimeData(data=0, pickle=False)
        # remove local instance to simulate cross-process
        md._local_instance = None
        self.assertEqual(md.instance(), None)
    
    def test_instance_type(self):
        md = PyMimeData(data=0)
        self.assertEqual(md.instanceType(), int)
    
    def test_instance_type_unpickled(self):
        md = PyMimeData(data=0)
        # remove local instance to simulate cross-process
        md._local_instance = None
        self.assertEqual(md.instanceType(), int)

    def test_instance_type_nopickle(self):
        md = PyMimeData(data=0, pickle=False)
        # remove local instance to simulate cross-process
        md._local_instance = None
        self.assertEqual(md.instanceType(), None)
        

if __name__ == '__main__':
    unittest.main()
