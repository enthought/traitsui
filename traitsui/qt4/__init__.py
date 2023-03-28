# (C) Copyright 2005-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

from importlib import import_module
from importlib.abc import MetaPathFinder, Loader
from importlib.machinery import ModuleSpec
try:
    from importlib.metadata import version
except ImportError:
    from importlib_metadata import version
from importlib.util import find_spec
import os
import sys
import warnings

try:
    from pyface.ui import ShadowedModuleFinder
except ImportError:
    ShadowedModuleFinder = None
from traits.etsconfig.api import ETSConfig


if any(
    (
        isinstance(finder, ShadowedModuleFinder)
        and finder.package == "traitsui.qt4."
    )
    for finder in sys.meta_path
):
    # Importing from traitsui.qt4.* is deprecated
    # Already have loader registered.
    warnings.warn(
        """The traitsui.qt4.* modules have moved to traitsui.qt.*

Backward compatibility import hooks are in place.  They will be removed in a
future release of Pyface.
""",
        DeprecationWarning,
        stacklevel=2,
    )
elif (
    os.environ.get('ETS_QT4_IMPORTS', None)  # environment says we want this
    or os.environ.get('ETS_TOOLKIT', None) == "qt4"  # environment says old qt4
    or ETSConfig.toolkit == "qt4"  # the ETSConfig toolkit says old qt4
):
    # Register our loader.  This is messing with global state that we do not own
    # so we only do it when we have other global state telling us to.

    sys.meta_path.append(ShadowedModuleFinder(
        package="traitsui.qt4.",
        true_package="traitsui.qt.",
    ))

    # Importing from traitsui.qt4.* is deprecated
    warnings.warn(
        """The traitsui.qt4.* modules have moved to traitsui.qt.*

Backward compatibility import hooks have been automatically applied.
They will be removed in a future release of Pyface.
""",
        DeprecationWarning,
        stacklevel=2,
    )
else:
    # Don't import from this module, use a future warning as we want end-users
    # of ETS apps to see the hints about environment variables.
    warnings.warn(
        """The traitsui.qt4.* modules have moved to traitsui.qt.*.

Applications which require backwards compatibility can either:

- set the ETS_QT4_IMPORTS environment variable
- set the ETS_TOOLKIT environment variable to "qt4",
- the ETSConfig.toolkit to "qt4"
- install a ShadowedModuleFinder into sys.meta_path::

    import sys
    from pyface.ui import ShadowedModuleFinder

    sys.meta_path.append(ShadowedModuleFinder(
        package="traitsui.qt4.",
        true_package="traitsui.qt.",
    ))
""",
        FutureWarning,
        stacklevel=2,
    )

