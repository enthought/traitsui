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

""" Defines the concrete implementations of the traits Toolkit interface for
the PyQt user interface toolkit.
"""

# import pyface.qt before anything else is done so the sipapi
# can be set correctly if needed
from __future__ import absolute_import
import pyface.qt

#----------------------------------------------------------------------------
#  Define the reference to the exported GUIToolkit object:
#----------------------------------------------------------------------------

from . import toolkit

# Reference to the GUIToolkit object for Qt.
toolkit = toolkit.GUIToolkit('traitsui', 'qt4', 'traitsui.qt4')
