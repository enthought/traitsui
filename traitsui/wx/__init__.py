#----------------------------------------------------------------------------
#
#  Copyright (c) 2005-2011, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
#  Author: David C. Morrill
#  Date:   10/21/2004
#
#----------------------------------------------------------------------------

""" Defines the concrete implementations of the traits Toolkit interface for
    the wxPython user interface toolkit.
"""

#-------------------------------------------------------------------------
#  Define the reference to the exported GUIToolkit object:
#-------------------------------------------------------------------------

from __future__ import absolute_import
from . import toolkit

# Reference to the GUIToolkit object for wxPython
toolkit = toolkit.GUIToolkit('traitsui', 'wx', 'traitsui.wx')
