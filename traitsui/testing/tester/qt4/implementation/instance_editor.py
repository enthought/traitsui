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
from traitsui.testing.tester.registry_helper import register_nested_ui_solvers
from traitsui.qt4.instance_editor import (
    CustomEditor,
    SimpleEditor
)


def _get_nested_ui_simple(target):
    """ Obtains a nested UI within a Simple Instance Editor.

    Parameters
    ----------
    target : instance of SimpleEditor
    """
    if target._dialog_ui is None:
        target._button.click()
    return target._dialog_ui


def _get_nested_ui_custom(target):
    """ Obtains a nested UI within a Custom Instance Editor.

    Parameters
    ----------
    target : instance of CustomEditor
    """
    return target._ui


def register(registry):
    """ Register interactions for the given registry.

    If there are any conflicts, an error will occur.

    Parameters
    ----------
    registry : TargetRegistry
        The registry being registered to.
    """
    register_nested_ui_solvers(registry, SimpleEditor, _get_nested_ui_simple)
    register_nested_ui_solvers(registry, CustomEditor, _get_nested_ui_custom)
