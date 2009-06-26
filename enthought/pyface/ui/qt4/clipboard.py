#------------------------------------------------------------------------------
# Copyright (c) 2009, Enthought, Inc.
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in enthought/LICENSE.txt and may be redistributed only
# under the conditions described in the aforementioned license.  The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
# Thanks for using Enthought open source!
#
# Author: Evan Patterson
# Date: 06/26/09
#------------------------------------------------------------------------------

# Standard library imports
from cStringIO import StringIO
from cPickle import dumps, load, loads

# System library imports
from PyQt4 import QtCore, QtGui

# ETS imports
from enthought.traits.api import implements
from enthought.pyface.i_clipboard import IClipboard, BaseClipboard

# Shortcuts
cb = QtGui.QApplication.clipboard()

# Custom MIME type representing python objects
PYTHON_TYPE = "python/object"


class Clipboard(BaseClipboard):
    
    implements(IClipboard)

    #---------------------------------------------------------------------------
    #  'data' property methods:
    #---------------------------------------------------------------------------

    def _get_has_data(self):
        return self.has_object_data or self.has_text_data or self.has_file_data

    #---------------------------------------------------------------------------
    #  'object_data' property methods:
    #---------------------------------------------------------------------------

    def _get_object_data(self):
        obj = None
        mime_data = cb.mimeData()
        if mime_data.hasFormat(PYTHON_TYPE):
            serialized_data = StringIO(str(mime_data.data(PYTHON_TYPE)))
            klass = load(serialized_data)
            obj = load(serialized_data)
        return obj

    def _set_object_data(self, data):
        mime_data = QtCore.QMimeData()
        serialized_data = dumps(data.__class__) + dumps(data)
        mime_data.setData(PYTHON_TYPE, QtCore.QByteArray(serialized_data))
        cb.setMimeData(mime_data)

    def _get_has_object_data(self):
        return cb.mimeData().hasFormat(PYTHON_TYPE)

    def _get_object_type(self):
        result = ''
        mime_data = cb.mimeData()
        if mime_data.hasFormat(PYTHON_TYPE):
            try:
                # We may not be able to load the required class:
                result = loads(str(mime_data.data(PYTHON_TYPE)))
            except:
                pass
        return result

    #---------------------------------------------------------------------------
    #  'text_data' property methods:
    #---------------------------------------------------------------------------

    def _get_text_data(self):
        return str(cb.text())

    def _set_text_data(self, data):
        cb.setText(data)

    def _get_has_text_data(self):
        return cb.mimeData().hasText()

    #---------------------------------------------------------------------------
    #  'file_data' property methods:
    #---------------------------------------------------------------------------
    
    def _get_file_data(self):
        mime_data = cb.mimeData()
        if mime_data.hasUrls():
            return [ str(url.toString()) for url in mime_data.urls() ]
        else:
            return []

    def _set_file_data(self, data):
        if isinstance(data, basestring):
            data = [ data ]
        mime_data = QtCore.QMimeData()
        mime_data.setUrls([ QtCore.QUrl(path) for path in data ])
        cb.setMimeData(mime_data)

    def _get_has_file_data (self):
        return cb.mimeData().hasUrls()
