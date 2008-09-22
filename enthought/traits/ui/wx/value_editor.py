#------------------------------------------------------------------------------
#
#  Copyright (c) 2006, Enthought, Inc.
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
#  Date:   01/05/2006
# 
#------------------------------------------------------------------------------

""" Defines the tree-based Python value editor and the value editor factory, 
    for the wxPython user interface toolkit.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------
    
from enthought.traits.ui.editors.value_editor \
    import _ValueEditor

from editor import Editor

class SimpleEditor( _ValueEditor, Editor):
    readonly = False
    
class ReadonlyEditor( _ValueEditor, Editor):
    readonly = True