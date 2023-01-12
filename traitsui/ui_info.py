# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Defines the UIInfo class used to represent the object and editor content of
    an active Traits-based user interface.
"""

from traits.api import HasPrivateTraits, Instance, Constant, Bool


class UIInfo(HasPrivateTraits):
    """Represents the object and editor content of an active Traits-based
    user interface
    """

    # -------------------------------------------------------------------------
    #  Trait definitions:
    # -------------------------------------------------------------------------

    #: Bound to a UI object at UIInfo construction time
    ui = Instance("traitsui.ui.UI", allow_none=True)

    #: Indicates whether the UI has finished initialization
    initialized = Bool(False)

    def bind_context(self):
        """Binds all of the associated context objects as traits of the
        object.
        """
        for name, value in self.ui.context.items():
            self.bind(name, value)

    def bind(self, name, value, id=None):
        """Binds a name to a value if it is not already bound."""
        if id is None:
            id = name

        if not hasattr(self, name):
            self.add_trait(name, Constant(value))
            if id != "":
                self.ui._names.append(id)
