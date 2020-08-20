#  Copyright (c) 2005-2020, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
from traitsui.wx.button_editor import SimpleEditor
from traitsui.testing import locator
from traitsui.testing.wx import helpers


def register(registry):
    registry.register_solver(
        target_class=SimpleEditor,
        locator_class=locator.DefaultTarget,
        solver=lambda wrapper, _: wrapper.target.control,
    )

