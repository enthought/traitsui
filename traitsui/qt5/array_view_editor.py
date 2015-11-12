#------------------------------------------------------------------------------
#
#  Copyright (c) 2009, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
#------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from traitsui.ui_editors.array_view_editor \
    import _ArrayViewEditor as BaseArrayViewEditor

from ui_editor import UIEditor

#-------------------------------------------------------------------------------
#  '_ArrayViewEditor' class:
#-------------------------------------------------------------------------------

class _ArrayViewEditor(BaseArrayViewEditor, UIEditor):
    pass
