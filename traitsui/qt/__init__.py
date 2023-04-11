# (C) Copyright 2008-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

# ------------------------------------------------------------------------------
# Copyright (c) 2007, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD license.
# However, when used with the GPL version of PyQt the additional terms
# described in the PyQt GPL exception also apply

#
# Author: Riverbank Computing Limited
# ------------------------------------------------------------------------------

""" Defines the concrete implementations of the traits Toolkit interface for
the PyQt user interface toolkit.
"""

# import pyface.qt before anything else is done so the sipapi
# can be set correctly if needed
import pyface.qt

# ----------------------------------------------------------------------------
#  Define the reference to the exported GUIToolkit object:
# ----------------------------------------------------------------------------

from . import toolkit

# Reference to the GUIToolkit object for Qt.
toolkit = toolkit.GUIToolkit("traitsui", "qt", "traitsui.qt")
