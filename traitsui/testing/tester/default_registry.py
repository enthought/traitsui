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

import importlib

from traitsui.testing.tester.registry import TargetRegistry

def get_default_registry():
    """ Creates a default registry for UITester that is toolkit specific.

    Returns
    -------
    registry : TargetRegistry
        The default registry containing implementations for TraitsUI editors
        that is toolkit specific.  
    """
    # side-effect to determine current toolkit
    from pyface.toolkit import toolkit_object
    from traits.etsconfig.api import ETSConfig

    if ETSConfig.toolkit == "null":
        return TargetRegistry()
    else:
        toolkit = {'wx': 'wx', 'qt4': 'qt4', 'qt': 'qt4'}[ETSConfig.toolkit]
        module = importlib.import_module(".default_registry", "traitsui.testing.tester." + toolkit)
        return module.get_default_registry()
