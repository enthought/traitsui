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

import wx 

from traitsui.testing.tester import command
from traitsui.testing.tester.registry import TargetRegistry
from traitsui.testing.tester.wx import helpers
from traitsui.testing.tester.wx.implementation import (
    button_editor,
)


def get_default_registry():
    """ Creates a default registry for UITester that is wx specific.

    Returns
    -------
    registry : TargetRegistry
        The default registry containing implementations for TraitsUI editors
        that is wx specific.  
    """
    registry = get_wobject_registry()

    button_editor.register(registry)
    
    return registry

def get_wobject_registry():
    """ Creates a generic registry for handling/solving wx objects. (i.e.
    this registry is independent of TraitsUI)

    Returns
    -------
    registry : TargetRegistry
        Registry containing wx specific generic handlers and solvers.
    """
    registry = TargetRegistry()

    registry.register_handler(
        target_class=wx.Button,
        interaction_class=command.MouseClick,
        handler=lambda wrapper, _: (
            helpers.mouse_click_button(
                control=wrapper.target, delay=wrapper.delay,
            )
        )
    )

    return registry
