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
from traitsui.testing.tester import locator
from traitsui.qt4.button_editor import CustomEditor, SimpleEditor


def register(registry):
    """ Register actions for the given registry.

    If there are any conflicts, an error will occur.
    """
    registry.register_solver(
        target_class=SimpleEditor,
        locator_class=locator.DefaultTarget,
        solver=lambda wrapper, _: wrapper.editor.control,
    )
    registry.register_solver(
        target_class=CustomEditor,
        locator_class=locator.DefaultTarget,
        solver=lambda wrapper, _: wrapper.editor.control,
    )
