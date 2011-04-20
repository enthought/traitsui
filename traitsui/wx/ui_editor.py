#------------------------------------------------------------------------------
#
#  Copyright (c) 2005, Enthought, Inc.
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
#  Date:   03/03/2006
#
#------------------------------------------------------------------------------

""" Defines the BasicUIEditor class, which allows creating editors that define
    their function by creating an embedded Traits UI.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from traitsui.ui_editor \
    import UIEditor as BaseUIEditor

from editor \
    import Editor

#-------------------------------------------------------------------------------
#  'UIEditor' base class:
#-------------------------------------------------------------------------------

class UIEditor ( BaseUIEditor, Editor ):
    """ An editor that creates an embedded Traits UI.
    """
    pass

#-- End UI preference save/restore interface -----------------------------------

