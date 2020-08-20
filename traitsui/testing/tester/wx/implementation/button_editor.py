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
from traitsui.wx.button_editor import SimpleEditor, CustomEditor
from traitsui.testing.tester import locator, query
from traitsui.testing.tester.wx import helpers


def register(registry):
    for target_class in [SimpleEditor, CustomEditor]:
        registry.register_solver(
            target_class=target_class,
            locator_class=locator.DefaultTarget,
            solver=lambda wrapper, _: wrapper.target.control,
        )

