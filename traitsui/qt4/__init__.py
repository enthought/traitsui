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

from packaging.version import Version

from traits.etsconfig.api import ETSConfig


# Import hooks for loading traitsui.qt.* in place of a traitsui.qt4.*
# This is just the implementation, it is not connected in this module, but
# is available for applications which want to install it themselves.
# It is here rather than in traitsui.qt4 so it can be imported and used
# without generating the warnings from traitsui.qt4
#
# To use manually:
#
#     import sys
#     sys.meta_path.append(ShadowedModuleFinder())

class ShadowedModuleLoader(Loader):
    """This loads another module into sys.modules with a given name.

    Parameters
    ----------
    fullname : str
        The full name of the module we're trying to import.
        Eg. "traitsui.qt4.foo"
    new_name : str
        The full name of the corresponding "real" module.
        Eg. "traitsui.qt.foo"
    new_spec : ModuleSpec instance
        The spec object for the corresponding "real" module.
    """

    def __init__(self, fullname, new_name, new_spec):
        self.fullname = fullname
        self.new_name = new_name
        self.new_spec = new_spec

    def create_module(self, spec):
        """Create the module object.

        This doesn't create the module object directly, rather it gets the
        underlying "real" module's object, importing it if needed.  This object
        is then returned as the "new" module.
        """
        if self.new_name not in sys.modules:
            import_module(self.new_name)
        return sys.modules[self.new_name]

    def exec_module(self, module):
        """Execute code for the module.

        This is given a module which has already been executed, so we don't
        need to execute anything.  However we do need to remove the __spec__
        that the importlibs machinery has injected into the module and
        replace it with the original spec for the underlying "real" module.
        """
        # patch up the __spec__ with the true module's original __spec__
        if self.new_spec:
            module.__spec__ = self.new_spec
            self.new_spec = None


class ShadowedModuleFinder(MetaPathFinder):
    """MetaPathFinder for shadowing modules in a package

    This finds modules with names that match a package but arranges loading
    from a different package.  By default this is  matches imports from any
    path starting with traitsui.qt4. and returns a loader which will instead
    load from traitsui.qt.*

    The end result is that sys.modules has two entries for pointing to the
    same module object.

    This may be hooked up by code in traitsui.qt4, but it can also be
    installed manually with::

        import sys
        sys.meta_path.append(ShadowedModuleFinder())

    Parameters
    ----------
    package : str
        The prefix of the "shadow" package.
    true_package : str
        The prefix of the "real" package which contains the actual code.
    """

    def __init__(self, package="traitsui.qt4.", true_package="traitsui.qt."):
        self.package = package
        self.true_package = true_package

    def find_spec(self, fullname, path, target=None):
        if fullname.startswith(self.package):
            new_name = fullname.replace(self.package, self.true_package, 1)
            new_spec = find_spec(new_name)
            if new_spec is None:
                return None
            return ModuleSpec(
                name=fullname,
                loader=ShadowedModuleLoader(fullname, new_name, new_spec),
                is_package=(new_spec.submodule_search_locations is not None),
            )


if any(isinstance(finder, ShadowedModuleFinder) for finder in sys.meta_path):
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
    Version(version('pyface')) < Version('8.0')  # our Pyface is old
    or os.environ.get('ETS_QT4_IMPORTS', None)  # environment says we want this
    or os.environ.get('ETS_TOOLKIT', None) == "qt4"  # environment says old qt4
    or ETSConfig.toolkit == "qt4"  # the ETSConfig toolkit says old qt4
):
    # Register our loader.  This is messing with global state that we do not own
    # so we only do it when we have other global state telling us to.

    sys.meta_path.append(ShadowedModuleFinder())

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
- install traitsui.ShadowedModuleFinder() into sys.meta_path
""",
        FutureWarning,
        stacklevel=2,
    )

