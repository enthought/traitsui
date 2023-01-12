# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Defines the editor factory used to wrap a non-Traits based custom control.
"""

from traits.api import Callable, Tuple, Property

from traitsui.basic_editor_factory import BasicEditorFactory
from traitsui.toolkit import toolkit_object


class CustomEditor(BasicEditorFactory):
    """Editor factory for custom editors."""

    #: Editor class to be instantiated.
    klass = Property()

    #: Factory function used to create the custom control
    factory = Callable()

    #: Arguments to be passed to the user's custom editor factory
    args = Tuple()

    def __init__(self, *args, **traits):
        if len(args) >= 1:
            self.factory = args[0]
            self.args = args[1:]
        super().__init__(**traits)

    # -------------------------------------------------------------------------
    #  Property getters
    # -------------------------------------------------------------------------
    def _get_klass(self):
        """Returns the editor class to be created."""
        return toolkit_object("custom_editor:CustomEditor")


# This alias is deprecated and will be removed in TraitsUI 8.
ToolkitEditorFactory = CustomEditor
