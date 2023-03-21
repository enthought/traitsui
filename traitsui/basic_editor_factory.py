# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Defines the BasicEditorFactory class, which allows creating editor
    factories that use the same class for creating all editor styles.
"""

from traits.api import Any

from .editor_factory import EditorFactory


class BasicEditorFactory(EditorFactory):
    """Base class for editor factories that use the same class for creating
    all editor styles.
    """

    # -------------------------------------------------------------------------
    #  Trait definitions:
    # -------------------------------------------------------------------------

    # Editor class to be instantiated
    klass = Any()

    # -------------------------------------------------------------------------
    #  Property getters.
    # -------------------------------------------------------------------------

    def _get_simple_editor_class(self):
        """Returns the editor class to use for "simple" style views.
        Overridden to return the value of the 'klass' trait.

        """
        return self.klass

    def _get_custom_editor_class(self):
        """Returns the editor class to use for "custom" style views.
        Overridden to return the value of the 'klass' trait.

        """
        return self.klass

    def _get_text_editor_class(self):
        """Returns the editor class to use for "text" style views.
        Overridden to return the value of the 'klass' trait.

        """
        return self.klass

    def _get_readonly_editor_class(self):
        """Returns the editor class to use for "readonly" style views.
        Overridden to return the value of the 'klass' trait.

        """
        return self.klass

    def __call__(self, *args, **traits):
        new = self.clone_traits()
        new.trait_set(**traits)
        return new
