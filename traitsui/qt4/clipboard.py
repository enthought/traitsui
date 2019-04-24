#------------------------------------------------------------------------------
# Copyright (c) 2007, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD license.
# However, when used with the GPL version of PyQt the additional terms
# described in the PyQt GPL exception also apply

#
# Author: Riverbank Computing Limited
#------------------------------------------------------------------------------

""" Implements a wrapper around the PyQt clipboard that handles Python objects
using pickle.
"""

from __future__ import absolute_import
from pyface.qt import QtGui
from pyface.ui.qt4.mimedata import PyMimeData, str2bytes
from traits.api import HasTraits, Instance, Property


#-------------------------------------------------------------------------
#  '_Clipboard' class:
#-------------------------------------------------------------------------

class _Clipboard(HasTraits):
    """ The _Clipboard class provides a wrapper around the PyQt clipboard.
    """

    #-------------------------------------------------------------------------
    #  Trait definitions:
    #-------------------------------------------------------------------------

    # The instance on the clipboard (if any).
    instance = Property

    # Set if the clipboard contains an instance.
    has_instance = Property

    # The type of the instance on the clipboard (if any).
    instance_type = Property

    # The application clipboard.
    clipboard = Instance(QtGui.QClipboard)

    #-------------------------------------------------------------------------
    #  Instance property methods:
    #-------------------------------------------------------------------------

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

    #-------------------------------------------------------------------------
    #  Other trait handlers:
    #-------------------------------------------------------------------------

    def _clipboard_default(self):
        """ Initialise the clipboard.
        """
        return QtGui.QApplication.clipboard()

#-------------------------------------------------------------------------
#  The singleton clipboard instance.
#-------------------------------------------------------------------------

clipboard = _Clipboard()
