#------------------------------------------------------------------------------
# Copyright (c) 2009, Enthought, Inc.
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in enthought/LICENSE.txt and may be redistributed only
# under the conditions described in the aforementioned license.  The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
# Thanks for using Enthought open source!
#------------------------------------------------------------------------------

# Standard library imports
from cStringIO import StringIO
from cPickle import dumps, load, loads

# System library imports
import wx

# ETS imports
from enthought.traits.api import implements
from enthought.pyface.i_clipboard import IClipboard, BaseClipboard

# Data formats
PythonObjectFormat = wx.CustomDataFormat('PythonObject')
TextFormat         = wx.DataFormat(wx.DF_TEXT)
FileFormat         = wx.DataFormat(wx.DF_FILENAME)

# Shortcuts
cb           = wx.TheClipboard


class Clipboard(BaseClipboard):

    implements(IClipboard)

    #---------------------------------------------------------------------------
    #  'data' property methods:
    #---------------------------------------------------------------------------

    def _get_has_data(self):
        result = False
        if cb.Open():
            result = (cb.IsSupported(TextFormat) or
                      cb.IsSupported(FileFormat) or
                      cb.IsSupported(PythonObjectFormat))
            cb.Close()
        return result

    #---------------------------------------------------------------------------
    #  'object_data' property methods:
    #---------------------------------------------------------------------------

    def _get_object_data(self):
        result = None
        if cb.Open():
            try:
                if cb.IsSupported(PythonObjectFormat):
                    cdo = wx.CustomDataObject(PythonObjectFormat)
                    if cb.GetData(cdo):
                        file   = StringIO(cdo.GetData())
                        klass  = load(file)
                        result = load(file)
            finally:
                cb.Close()
        return result

    def _set_object_data(self, data):
        if cb.Open():
            try:
                cdo = wx.CustomDataObject(PythonObjectFormat)
                cdo.SetData(dumps(data.__class__) + dumps(data))
                # fixme: There seem to be cases where the '-1' value creates
                # pickles that can't be unpickled (e.g. some TraitDictObject's)
                #cdo.SetData(dumps(data, -1))
                cb.SetData(cdo)
            finally:
                cb.Close()
                cb.Flush()

    def _get_has_object_data(self):
        return self._has_this_data(PythonObjectFormat)

    def _get_object_type(self):
        result = ''
        if cb.Open():
            try:
                if cb.IsSupported(PythonObjectFormat):
                    cdo = wx.CustomDataObject(PythonObjectFormat)
                    if cb.GetData(cdo):
                        try:
                            # We may not be able to load the required class:
                            result = loads(cdo.GetData())
                        except:
                            pass
            finally:
                cb.Close()
        return result

    #---------------------------------------------------------------------------
    #  'text_data' property methods:
    #---------------------------------------------------------------------------

    def _get_text_data(self):
        result = ''
        if cb.Open():
            if cb.IsSupported(TextFormat):
                tdo = wx.TextDataObject()
                if cb.GetData(tdo):
                    result = tdo.GetText()
            cb.Close()
        return result

    def _set_text_data(self, data):
        if cb.Open():
            cb.SetData(wx.TextDataObject(str(data)))
            cb.Close()
            cb.Flush()

    def _get_has_text_data(self):
        return self._has_this_data(TextFormat)

    #---------------------------------------------------------------------------
    #  'file_data' property methods:
    #---------------------------------------------------------------------------

    def _get_file_data(self):
        result = []
        if cb.Open():
            if cb.IsSupported(FileFormat):
                tfo = wx.FileDataObject()
                if cb.GetData(tfo):
                    result = tfo.GetFilenames()
            cb.Close()
        return result

    def _set_file_data(self, data):
        if cb.Open():
            tfo = wx.FileDataObject()
            if isinstance(data, basestring):
                tfo.AddFile(data)
            else:
                for filename in data:
                    tfo.AddFile(filename)
            cb.SetData(tfo)
            cb.Close()
            cb.Flush()

    def _get_has_file_data(self):
        return self._has_this_data(FileFormat)

    #---------------------------------------------------------------------------
    #  Private helper methods:
    #---------------------------------------------------------------------------

    def _has_this_data(self, format):
        result = False
        if cb.Open():
            result = cb.IsSupported(format)
            cb.Close()
        return result
