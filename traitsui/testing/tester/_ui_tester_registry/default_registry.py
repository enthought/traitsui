# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import importlib

from traits.etsconfig.api import ETSConfig

from traitsui.testing.tester.target_registry import TargetRegistry
from traitsui.testing.tester._ui_tester_registry._traitsui_ui import (
    register_traitsui_ui_solvers,
)
from traitsui.ui import UI


def get_default_registries():
    """Creates a default registry for UITester that is toolkit specific.

    Returns
    -------
    registries : list of AbstractTargetRegistry
        The default registries containing implementations for TraitsUI editors
        that are toolkit specific.
    """
    # side-effect to determine current toolkit
    from pyface.toolkit import toolkit_object  # noqa

    if ETSConfig.toolkit == "null":
        registries = []
    else:
        toolkit = {'wx': 'wx', 'qt4': 'qt', 'qt': 'qt'}[ETSConfig.toolkit]
        this_package, _ = __name__.rsplit(".", 1)
        module = importlib.import_module(
            ".default_registry", this_package + '.' + toolkit
        )
        registries = module.get_default_registries()

    ui_registry = TargetRegistry()
    register_traitsui_ui_solvers(
        registry=ui_registry,
        target_class=UI,
        traitsui_ui_getter=lambda target: target,
    )
    return [ui_registry] + registries
