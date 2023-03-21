# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Define the concrete implementations of the traits Toolkit interface for the
    'null' (do nothing) user interface toolkit. This toolkit is provided to
    handle situations where no recognized traits-compatible UI toolkit is
    installed, but users still want to use traits for non-UI related tasks.
"""

# -------------------------------------------------------------------------
#  Define the reference to the exported GUIToolkit object:
# -------------------------------------------------------------------------


from . import toolkit

toolkit = toolkit.GUIToolkit("traitsui", "null", "traitsui.null")
