#------------------------------------------------------------------------------
# Copyright (c) 2007, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD license.
# However, when used with the GPL version of PyQt the additional terms described in the PyQt GPL exception also apply

#
# Author: Riverbank Computing Limited
#------------------------------------------------------------------------------

""" Implements a wrapper around the PyQt clipboard that handles Python objects
using pickle.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from cPickle import dumps, load, loads, PickleError
from cStringIO import StringIO
import warnings

from pyface.qt import QtCore, QtGui

from traits.api import HasTraits, Instance, Property

#-------------------------------------------------------------------------------
#  'PyMimeData' class:
#-------------------------------------------------------------------------------

class PyMimeData(QtCore.QMimeData):
    """ The PyMimeData wraps a Python instance as MIME data.
    """
    # The MIME type for instances.
    MIME_TYPE = 'application/x-ets-qt4-instance'
    NOPICKLE_MIME_TYPE = 'application/x-ets-qt4-instance-no-pickle'

    def __init__(self, data=None, pickle=True):
        """ Initialise the instance.
        """
        QtCore.QMimeData.__init__(self)

        # Keep a local reference to be returned if possible.
        self._local_instance = data

        if pickle:
            if data is not None:
                # We may not be able to pickle the data.
                try:
                    pdata = dumps(data)
                    # This format (as opposed to using a single sequence) allows
                    # the type to be extracted without unpickling the data.
                    self.setData(self.MIME_TYPE, dumps(data.__class__) + pdata)
                except (PickleError, TypeError):
                    # if pickle fails, still try to create a draggable
                    warnings.warn(("Could not pickle dragged object %s, " +
                            "using %s mimetype instead") % (repr(data),
                            self.NOPICKLE_MIME_TYPE), RuntimeWarning)
                    self.setData(self.NOPICKLE_MIME_TYPE, str(id(data)))

        else:
            self.setData(self.NOPICKLE_MIME_TYPE, str(id(data)))

    @classmethod
    def coerce(cls, md):
        """ Wrap a QMimeData or a python object to a PyMimeData.
        """
        # See if the data is already of the right type.  If it is then we know
        # we are in the same process.
        if isinstance(md, cls):
            return md

        if isinstance(md, PyMimeData):
            # if it is a PyMimeData, migrate all its data, subclasses should
            # override this method if it doesn't do thgs correctly for them
            data = md.instance()
            nmd = cls()
            nmd._local_instance = data
            for format in md.formats():
                nmd.setData(format, md.data(format))
        elif isinstance(md, QtCore.QMimeData):
            # if it is a QMimeData, migrate all its data
            nmd = cls()
            for format in md.formats():
                nmd.setData(format, md.data(format))
        else:
            # by default, try to pickle the coerced object
            pickle = True
    
            # See if the data is a list, if so check for any items which are
            # themselves of the right type.  If so, extract the instance and
            # track whether we should pickle.
            # XXX lists should suffice for now, but may want other containers
            if isinstance(md, list):
                pickle = not any(item.hasFormat(cls.NOPICKLE_MIME_TYPE)
                        for item in md if isinstance(item, QtCore.QMimeData))
                md = [item.instance() if isinstance(item, PyMimeData) else item
                        for item in md]
    
            # Arbitrary python object, wrap it into PyMimeData
            nmd = cls(md, pickle)

        return nmd

    def instance(self):
        """ Return the instance.
        """
        if self._local_instance is not None:
            return self._local_instance

        if not self.hasFormat(self.MIME_TYPE):
            # We have no pickled python data defined.
            return None

        io = StringIO(str(self.data(self.MIME_TYPE)))

        try:
            # Skip the type.
            load(io)

            # Recreate the instance.
            return load(io)
        except PickleError:
            pass

        return None

    def instanceType(self):
        """ Return the type of the instance.
        """
        if self._local_instance is not None:
            return self._local_instance.__class__

        try:
            if self.hasFormat(self.MIME_TYPE):
                return loads(str(self.data(self.MIME_TYPE)))
        except PickleError:
            pass

        return None

    def localPaths(self):
        """ The list of local paths from url list, if any.
        """
        ret = []
        for url in self.urls():
            if url.scheme() == 'file':
                ret.append(url.toLocalFile())
        return ret

#-------------------------------------------------------------------------------
#  '_Clipboard' class:
#-------------------------------------------------------------------------------

class _Clipboard(HasTraits):
    """ The _Clipboard class provides a wrapper around the PyQt clipboard.
    """

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # The instance on the clipboard (if any).
    instance = Property

    # Set if the clipboard contains an instance.
    has_instance = Property

    # The type of the instance on the clipboard (if any).
    instance_type = Property

    # The application clipboard.
    clipboard = Instance(QtGui.QClipboard)

    #---------------------------------------------------------------------------
    #  Instance property methods:
    #---------------------------------------------------------------------------

    def _get_instance(self):
        """ The instance getter.
        """
        md = PyMimeData.coerce(self.clipboard.mimeData())
        if md is None:
            return None

        return md.instance()

    def _set_instance(self, data):
        """ The instance setter.
        """
        self.clipboard.setMimeData(PyMimeData(data))

    def _get_has_instance(self):
        """ The has_instance getter.
        """
        return self.clipboard.mimeData().hasFormat(PyMimeData.MIME_TYPE)

    def _get_instance_type(self):
        """ The instance_type getter.
        """
        md = PyMimeData.coerce(self.clipboard.mimeData())
        if md is None:
            return None

        return md.instanceType()

    #---------------------------------------------------------------------------
    #  Other trait handlers:
    #---------------------------------------------------------------------------

    def _clipboard_default(self):
        """ Initialise the clipboard.
        """
        return QtGui.QApplication.clipboard()

#-------------------------------------------------------------------------------
#  The singleton clipboard instance.
#-------------------------------------------------------------------------------

clipboard = _Clipboard()
